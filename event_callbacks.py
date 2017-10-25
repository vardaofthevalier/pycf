from __future__ import unicode_literals

import os
import json
import shutil
import base64
import requests
import subprocess
from ruamel.yaml import YAML
from tempfile import mkdtemp, NamedTemporaryFile
from utils import write_stdout, gather_facts, push_apps


s = requests.Session()

K8S_NAMESPACES_API_PATH = "/api/v1/namespaces"
K8S_SECRETS_API_PATH = "/api/v1/namespaces/{namespace}/secrets"
K8S_SERVICES_API_PATH = "/api/v1/namespaces/{namespace}/services"
K8S_DEPLOYMENT_API_PATH = "/apis/apps/v1beta1/namespaces/{namespace}/deployments"

CF_SSH_GATEWAY_MANIFEST = {
    "applications": [
        {
            "name": "ssh-gateway",
            "random-route": True,
            "instances": 1,
            "memory": "64M",
            "disk_quota": "64M",
            "buildpack": "staticfile_buildpack",
            "stack": "cflinuxfs2"
        }
    ]
}

CF_EXPORTER_SECRET_SCRIPT_HASH_TEMPLATE = '''
export HOST_APPNAME=ssh-gateway
export SVC_HOSTNAME={service_hostname}
export INTERNAL_PORT={internal_port}
export EXTERNAL_PORT={external_port}
export CF_SPACE={cf_space}
export CF_ORGANIZATION={cf_organization}
export CF_USERNAME={cf_username}
export CF_PASSWORD={cf_password}
export API_DOMAIN={api_domain}
export USERNAME={username}
export PASSWORD={password}
'''

CF_MYSQL_EXPORTER_ENTRYPOINT = '''
chmod u+x /cf-exporter-secrets/script && \
source /cf-exporter-secrets/script && \
while ! echo exit | nc localhost 3306; do sleep 10; done
cat > my.cnf <<EOM
[client]
host = localhost
user = $USERNAME
password = $PASSWORD
EOM
export DATASOURCE="${USERNAME}:${PASSWORD}@(localhost:3306)/" && \
./mysqld_exporter -web.listen-address=:80 -config.my-cnf ./my.cnf -collect.info_schema.tables.databases '*'
'''

CF_REDIS_EXPORTER_ENTRYPOINT = '''
chmod u+x /cf-exporter-secrets/script && source /cf-exporter-secrets/script && REDIS_ADDR=localhost:$INTERNAL_PORT REDIS_PASSWORD=$PASSWORD ./redis_exporter -web.listen-address=:$EXPOSED_PORT
'''


def deploy_exporter(cf, event_data, cf_org=None, cf_space=None, cf_locality=None, cf_service_key_guid=None, cf_service_instance_guid=None, namespace='metrics-export', kubectl_proxy_port='8001'):
    exception_message_template = "WARNING: couldn't deploy exporter! -- {}"

    if 'KUBECTL_PROXY_PORT' in os.environ.keys():
        KUBECTL_PROXY_BASE_URL = "http://localhost:" + os.environ["KUBECTL_PROXY_PORT"]

    else:
        KUBECTL_PROXY_BASE_URL = "http://localhost:" + kubectl_proxy_port  # run `kubectl proxy --port <kubectl_proxy_port> to enable this to work

    if 'CF_LOCALITY' in os.environ.keys():
        cf_locality = os.environ['CF_LOCALITY']

    elif not cf_locality:
        raise Exception(exception_message_template.format('No CF locality specified!'))

    if not cf_org:
        cf_org = cf.organizations.get(event_data['entity']['organization_guid']).json()['entity']['name']

    if not cf_space:
        cf_space = cf.spaces.get(event_data['entity']['space_guid']).json()['entity']['name']
        cf_apps_facts = gather_facts(
            cf,
            'apps',
            params={'q': 'space_guid IN ' + event_data['entity']['space_guid']}
        )

    else:
        cf_spaces_facts = gather_facts(cf, 'spaces')
        cf_apps_facts = gather_facts(
            cf,
            'apps',
            params={'q': 'space_guid IN ' + cf_spaces_facts[cf_space]}
        )

    if not cf_service_key_guid:
        cf_service_key = cf.service_keys.get(event_data['entity']['actee']).json()

    else:
        cf_service_key = cf.service_keys.get(cf_service_key_guid).json()

    if not cf_service_instance_guid:
        cf_service_instance = cf.service_instances.get(
            event_data['entity']['metadata']['request']['service_instance_guid']
        ).json()

    else:
        cf_service_instance = cf.service_instances.get(
            cf_service_instance_guid
        ).json()

    cf_service = cf.services.get(cf_service_instance['entity']['service_guid']).json()
    cf_service_credentials = cf_service_key['entity']['credentials']

    if event_data:
        deploy_ssh_gateway(cf, event_data)

    else:
        deploy_ssh_gateway(cf, event_data, cf_org=cf_org, cf_space=cf_space)

    if 'MySQL' in cf_service['entity']['tags']:
        internal_port = 3306
        cf_service_type = "mysql"
        password = cf_service_credentials['password']
        cf_service_hostname = cf_service_credentials['hostname']
        cf_service_username = cf_service_credentials['username']
        cf_exporter_script = CF_MYSQL_EXPORTER_ENTRYPOINT

    elif 'redis' in cf_service['entity']['tags']:
        internal_port = 6379
        cf_service_type = "redis"
        password = cf_service_credentials['password']
        cf_service_hostname = cf_service_credentials['host']
        cf_service_username = ""
        cf_exporter_script = CF_REDIS_EXPORTER_ENTRYPOINT

    else:
        raise NotImplementedError("Unsupported DB type!")

    # create the k8s objects

    # required variables

    ## SECRETS

    secret_name = "cf-service-key-{}".format(cf_service_key['entity']['name'])
    env_script = CF_EXPORTER_SECRET_SCRIPT_HASH_TEMPLATE.format(
        external_port=cf_service_credentials['port'],
        internal_port=internal_port,
        service_hostname=cf_service_hostname,
        username=cf_service_username,
        password=password,
        cf_space=cf_space,
        cf_organization=cf_org,
        cf_username=cf.username,
        cf_password=cf.password,
        api_domain=cf.api_domain
    )
    secret_data = base64.b64encode(env_script)

    ## DEPLOYMENT
    deployment_name = "cf-exporter-{}-{}-{}".format(
        cf_locality,
        cf_space,
        cf_service_key['entity']['name']
    )

    ## API OBJECTS
    api_objects = [
        {
            "path": KUBECTL_PROXY_BASE_URL + K8S_NAMESPACES_API_PATH,
            "data": {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": namespace
                }
            }
        },
        {
            "path": KUBECTL_PROXY_BASE_URL + K8S_SECRETS_API_PATH.format(namespace=namespace),
            "data": {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": secret_name,
                    "namespace": namespace
                },
                "type": "Opaque",
                "data": {
                    "script": secret_data
                }
            }
        },
        {
            "path": KUBECTL_PROXY_BASE_URL + K8S_DEPLOYMENT_API_PATH.format(namespace=namespace),
            "data": {
                "apiVersion": "apps/v1beta1",
                "kind": "Deployment",
                "metadata": {
                    "name": deployment_name,
                    "namespace": namespace
                },
                "spec": {
                    "replicas": 1,
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": deployment_name,
                                "cf_space": cf_space,
                                "cf_locality": cf_locality,
                                "cf_service_name": cf_service_instance['entity']['name'],
                                "cf_service_type": cf_service_type
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "cf-ssh",
                                    "image": "onelouder/cf-ssh-bash",
                                    "env": [
                                        {
                                            "name": "SCRIPT",
                                            "value": "chmod u+x /cf-exporter-secrets/script && source /cf-exporter-secrets/script && /cf-ssh.sh"
                                        }
                                    ],
                                    "command": ["bash", "-c", "$(SCRIPT)"],
                                    "volumeMounts": [
                                        {
                                            "name": "cf-exporter-secrets",
                                            "mountPath": "/cf-exporter-secrets"
                                        }
                                    ],
                                    "tty": True,
                                    "stdin": True
                                },
                                {
                                    "name": "cf-{}-exporter".format(cf_service_type),
                                    "image": "onelouder/cf-{}-exporter".format(cf_service_type),
                                    "env": [
                                        {
                                            "name": "SCRIPT",
                                            "value": cf_exporter_script
                                        }
                                    ],
                                    "command": ["bash", "-c", "$(SCRIPT)"],
                                    "volumeMounts": [
                                        {
                                            "name": "cf-exporter-secrets",
                                            "mountPath": "/cf-exporter-secrets"
                                        }
                                    ],
                                    "ports": [
                                        {
                                            "name": "exporter",
                                            "containerPort": 80
                                        }
                                    ]
                                }
                            ],
                            "volumes": [
                                {
                                    "name": "cf-exporter-secrets",
                                    "secret": {
                                        "secretName": secret_name
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    ]

    def idempotently_create(url, data):
        response = s.get(url).json()
        write_stdout("Received response: " + str(response))
        if 'items' in response.keys():
            thing_found = filter(lambda x: True if x['metadata']['name'] == data['metadata']['name'] else False, s.get(url).json()['items'])

        else:
            thing_found = []

        if len(thing_found) == 0:
            response = s.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))

            if response.status_code not in [200, 201, 204]:
                raise Exception("{} creation failed! (Status: {}, Message: {})".format(data['kind'], response.status_code, response.content))

    # attempt to create all of the objects above

    for o in api_objects:
        try:
            idempotently_create(o['path'], o['data'])

        except Exception as e:
            raise Exception("Couldn't deploy exporter: " + e.message)

    write_stdout("Successfully deployed exporter '{}'!".format(deployment_name))


def destroy_exporter(cf, event_data, namespace='metrics-export'):
    KUBECTL_PROXY_BASE_URL = "http://localhost:" + os.environ["KUBECTL_PROXY_PORT"]

    # delete the deployment
    deployment_name = "/cf-exporter-{}-{}-{}".format(
        os.environ["CF_LOCALITY"],
        cf.spaces.get(event_data['entity']['space_guid']).json()['entity']['name'],
        event_data['entity']['actee']
    )
    r = s.delete(
        KUBECTL_PROXY_BASE_URL + K8S_DEPLOYMENT_API_PATH.format(namespace=namespace) + deployment_name
    )

    if r.status_code != 200:
        write_stdout("WARNING: couldn't delete deployment '{}': {}".format(deployment_name, r.content))

    # delete the secret
    secret_name = "cf-service-key-{}".format(event_data['entity']['actee'])
    r = s.delete(
        KUBECTL_PROXY_BASE_URL + K8S_SECRETS_API_PATH.format(namespace=namespace) + secret_name
    )

    if r.status_code != 200:
        write_stdout("WARNING: couldn't delete secret '{}': {}".format(secret_name, r.content))


def deploy_ssh_gateway(cf, event_data, cf_org=None, cf_space=None):
    # gather cf facts
    if not cf_org:
        cf_org = cf.organizations.get(
            event_data['entity']['organization_guid']
        ).json()['entity']['name']

    if not cf_space:
        cf_space = cf.spaces.get(
            event_data['entity']['space_guid']
        ).json()['entity']['name']
        space_guid = event_data['entity']['space_guid']

    else:
        cf_spaces_facts = gather_facts(cf, 'spaces')
        space_guid = cf_spaces_facts[cf_space]

    cf_service_instances_facts = gather_facts(
        cf,
        'service_instances',
        params={'q': 'space_guid IN ' + space_guid}
    )

    bind_to_services = cf_service_instances_facts.keys()

    if len(bind_to_services) > 0:
        CF_SSH_GATEWAY_MANIFEST["applications"][0]["services"] = bind_to_services

    t = NamedTemporaryFile(delete=False)
    YAML().dump(CF_SSH_GATEWAY_MANIFEST, t)

    d = mkdtemp()
    subprocess.call(["touch", os.path.join(d, "Staticfile")])
    subprocess.call(["bash", "-c", "echo \"It works!\" > {}".format(os.path.join(d, "index.html"))])
    push_apps(cf, cf_org, cf_space, t.name, d, False)

    os.remove(t.name)
    shutil.rmtree(d)

    # create service keys if necessary
    for name, guid in cf_service_instances_facts.iteritems():
        service_keys = cf.service_instances.list_service_keys(guid).json()['resources']
        if len(service_keys) < 1:
            write_stdout("No service key found for service '{}'... creating one now!".format(cf_service_instances_facts[name]))
            d = {
                'service_instance_guid': guid,
                'name': '{}-access'.format(name)
            }
            cf.service_keys.create(data=d)

import os
import sys
import json
import redis
import sqlalchemy
import subprocess
import SimpleHTTPServer
import SocketServer
from time import sleep
from requests import get
from datetime import datetime, timedelta
from pycf.exceptions import CloudFoundryError
#from jinja2 import Template


def write_stdout(s):
    sys.stdout.write(s + '\n')
    sys.stdout.flush()


def utc_to_epoch(ts):
    epoch_time = datetime(1970, 1, 1)
    utc_time = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    return (utc_time - epoch_time).total_seconds()


def epoch_to_utc(s):
    epoch_time = datetime(1970, 1, 1)
    return datetime.strftime(epoch_time + timedelta(seconds=int(s)), "%Y-%m-%dT%H:%M:%SZ")


def get_service_credentials(retries=5, interval=15):
    vcap_services = None

    while retries > 0:
        try:
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])

        except KeyError:
            write_stdout("WARNING: VCAP_SERVICES variable not set!")
            sleep(interval)
            retries -= 1

    if vcap_services is None:
        raise Exception("Couldn't get vcap services from environment!")

    return vcap_services


def get_redis_db(index, platform):
    if platform == "cloudfoundry":
        vcap_services = get_service_credentials()

        try:
            redis_connection = json.loads(vcap_services)['hsdp-redis'][0]['credentials']

        except KeyError:
            write_stdout("WARNING: redis credentials not yet available!")

    elif platform == "kubernetes":  # Assume redis is running in the same pod
        redis_connection = {
            'host': 'localhost',
            'port': 6379,
            'password': None,
            'db': index
        }

    else:
        raise NotImplementedError("Platform '{}' not recognized!".format(platform))

    retries = 5
    while retries > 0:
        try:
            r = redis.StrictRedis(**redis_connection)
        except Exception:
            retries -= 1
            sleep(5)

        else:
            break

    return r


def get_db_engine(db_type, db_name, platform):
    if platform == 'cloudfoundry':
        vcap_services = get_service_credentials()

        if db_type in vcap_services.keys():
            connection_info = filter(lambda x: x['name'] == db_name, vcap_services[db_type])

            if len(connection_info) == 0:
                write_stdout("WARNING: given database name not found in VCAP_SERVICES variable!")
                return None

            elif len(connection_info) > 1:
                write_stdout("WARNING: more than one database was found with the same name!")
                return None

            else:
                db_credentials = connection_info[0]['credentials']
                engine = sqlalchemy.create_engine(db_credentials['uri'])  # TODO: include steps in deployment automation for this monitoring service to ensure that each db of interest has a corresponding service key and ups

                return engine

        else:
            write_stdout("WARNING: given database type not found in VCAP_SERVICES variable!")

            return None

    elif platform == "kubernetes":  # Assume redis is running in the same pod
        pass # TODO: figure out how to make this happen

    else:
        raise NotImplementedError("Platform '{}' not recognized!".format(platform))


def dictionary_dot_lookup(d, dot_string):
    lookup_list = dot_string.split('.')

    r = d
    for l in lookup_list:
        r = r.get(l)

    return r


def get_paginated_results(api_domain, auth_token, current_page):
    headers = {
        'Authorization': auth_token
    }

    results = current_page['resources']
    total_pages = current_page['total_pages']

    while total_pages > 1:
        current_page = get(api_domain + current_page['next_url'], headers=headers).json()
        results.extend(current_page['resources'])
        total_pages -= 1

    return results


def gather_facts(cf, api, mapping_schema='entity.name:metadata.guid', params=None):
    nlookup, glookup = mapping_schema.split(':')

    resources = {}
    for resource in get_paginated_results(cf.api_domain, cf.auth.access_token, getattr(cf, api).list(params=params).json()):
        l = dictionary_dot_lookup(resource, nlookup)
        r = dictionary_dot_lookup(resource, glookup)

        resources[l] = r

    return resources

# def render_html_index(template_file_path, **kwargs):
#     # template file path = os.path.join(os.path.dirname(__file__), 'index.html.j2')
#     try:
#         with open(template_file_path) as f:
#             t = Template(f.read())
#
#         with open('index.html', 'w') as f:
#             f.write(t.render(**kwargs))
#
#     except Exception as e:
#         write_stdout('{} raised: {}'.format(type(e).__name__, e))


def serve_endpoint(component):
    write_stdout("Preparing to serve data for {} on port {}...".format(component, os.environ['PORT']))
    SocketServer.TCPServer(('0.0.0.0', int(os.environ['PORT'])), SimpleHTTPServer.SimpleHTTPRequestHandler).serve_forever()


def wait_on_service_creation(cf, service_guid):
    poll_interval = 20
    retries = 50

    while retries > 0:
        status = cf.service_instances.get(
            service_guid
        ).json()

        if status['entity']['last_operation']['state'] != 'in progress':
            break

        sleep(poll_interval)
        retries -= 1


def wait_on_service_deletion(cf, service_guid):
    poll_interval = 20
    retries = 50

    while retries > 0:
        try:
            status = cf.service_instances.get(
                service_guid
            )

        except CloudFoundryError:
            break

        else:
            if status.status_code >= 400:
                break

            sleep(poll_interval)
            retries -= 1


def create_service_key(cf, service_name, service_guid):
    cf.service_keys.create(data={'service_instance_guid': service_guid, 'name': '{}-access'.format(service_name)})


def push_apps(cf, org, target, manifest_path, push_directory, no_start):
    # cf login
    os.chdir(push_directory)

    print "Logging into Cloud Foundry ..."

    try:
        subprocess.call(
            ["cf", "login", "-a", cf.api_domain, "-u", cf.username, "-p", cf.password, "-s", target, "-o", org])

    except subprocess.CalledProcessError as e:
        raise Exception("There was a problem logging into Cloud Foundry: " + e.message)

    # cf push

    print "Deploying manifest to Cloud Foundry ..."

    if no_start:
        cmd = ["cf", "push", "--no-start", "-v", "-f", manifest_path]

    else:
        cmd = ["cf", "push", "-v", "-f", manifest_path]

    status = subprocess.call(cmd)

    if status != 0:
        raise Exception("There was a problem with the push operation!")

    print "Manifest successfully deployed!"
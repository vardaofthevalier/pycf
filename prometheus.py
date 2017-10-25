import os
import json
from requests import get
from datetime import datetime, timedelta
from pycf.utils import gather_facts, get_paginated_results, utc_to_epoch, write_stdout


class ApplicationResourceUtilization(object):
    def __init__(self, resource):
        self.resource = resource
        self.help = '# HELP %s_utilization Current CPU utilization for a Cloud Foundry application\n' % resource
        self.type = '# TYPE %s_utilization gauge\n' % resource
        self.metric_template = '%s_utilization{space_name="%s", app_name="%s", app_index="%s"} %s\n'

    def generate_metric(self, space_name, app_name, app_index, value):
        return self.metric_template % (self.resource, space_name, app_name, app_index, value)


class AppStatus(object):
    def __init__(self):
        self.help = '# HELP application_status The current status of a Cloud Foundry application\n'
        self.type = '# TYPE application_status gauge\n'
        self.metric_template = 'application_status{space_name="%s", app_name="%s", app_index="%s", created_by="%s", last_updated_by="%s", status_text="%s"} %s\n'

    def generate_metric(self, space_name, app_name, app_index, created_by, last_updated_by, status_text, up):
        return self.metric_template % (space_name, app_name, app_index, created_by, last_updated_by, status_text, up)


class ServiceInstanceStatus(object):
    def __init__(self):
        self.help = '# HELP service_instance_status The current status of a Cloud Foundry application\n'
        self.type = '# TYPE service_instance_status gauge\n'
        self.metric_template = 'service_instance_status{space_name="%s", service_instance_name="%s", service_plan_name="%s", create_time="%s", created_by="%s", last_updated_by="%s"} %s\n'

    def generate_metric(self, space_name, service_instance_name, service_plan_name, create_time, created_by, last_updated_by, bound):
        return self.metric_template % (space_name, service_instance_name, service_plan_name, create_time, created_by, last_updated_by, bound)


class ServiceInstanceCost(object):
    def __init__(self):
        self.help = '# HELP service_instance_cost The current monthly cost (in USD) for currently deployed service instances\n'
        self.type = '# TYPE service_instance_cost gauge\n'
        self.metric_template = 'service_instance_cost{space_name="%s", service_instance_name="%s", service_instance_status="%s", service_plan_name="%s"} %s\n'

    def generate_metric(self, space_name, service_instance_name, service_instance_status, service_plan_name, cost):
        return self.metric_template % (space_name, service_instance_name, service_instance_status, service_plan_name, cost)


def app_metrics(cf, org):
    def generate_response(cf, org):
        # gather facts about the given cf organization
        org_guid = _get_org_guid(cf, org)

        search_params = {
            'q': 'organization_guid IN {}'.format(org_guid)
        }

        spaces_facts = gather_facts(cf, 'spaces', params=search_params, mapping_schema='metadata.guid:entity.name')

        # compute metrics
        cpu_utilization = ApplicationResourceUtilization('cpu')
        cpu_utilization_block = []

        mem_utilization = ApplicationResourceUtilization('mem')
        mem_utilization_block = []

        disk_utilization = ApplicationResourceUtilization('disk')
        disk_utilization_block = []

        app_status = AppStatus()
        app_status_block = []

        service_instance_status = ServiceInstanceStatus()
        service_instance_status_block = []

        service_instance_cost = ServiceInstanceCost()
        service_instance_cost_block = []

        # app metrics
        apps = get_paginated_results(cf.api_domain, cf.auth.access_token, cf.apps.list(params=search_params).json())

        for app_info in apps:
            space_name = spaces_facts[app_info['entity']['space_guid']]
            app_guid = app_info['metadata']['guid']
            app_name = app_info['entity']['name']
            app_instances = app_info['entity']['instances']
            app_event_search_params = {
                'q': 'actee:{}'.format(app_guid),
                'order-by': 'timestamp',
                'order-direction': 'desc'
            }
            app_events = get_paginated_results(cf.api_domain, cf.auth.access_token, cf.events.list(params=app_event_search_params).json())
            app_create_events = filter(
                lambda x: x['entity']['type'] == 'audit.app.create',
                app_events
            )

            if len(app_create_events) > 0:
                created_by = app_create_events[0]['entity']['actor_name']

            else:
                created_by = "NaN"

            app_update_events = filter(
                lambda x: x['entity']['type'] == 'audit.app.update',
                app_events
            )

            if len(app_update_events) > 0:
                last_updated_by = app_update_events[0]['entity']['actor_name']

            else:
                last_updated_by = created_by

            status_text = app_info['entity']['state']

            if status_text == 'STARTED':
                up = str(1)
                app_stats = cf.apps.stats(app_guid).json()
                for app_index, data in app_stats.iteritems():
                    app_index = str(app_index)
                    cpu_utilization_block.append(
                        cpu_utilization.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            str(data['stats']['usage']['cpu'])
                        )
                    )
                    mem_utilization_block.append(
                        mem_utilization.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            str(
                                float(data['stats']['usage']['mem'])/data['stats']['mem_quota']
                            )
                        )
                    )
                    disk_utilization_block.append(
                        disk_utilization.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            str(
                                float(data['stats']['usage']['disk'])/data['stats']['disk_quota']
                            )
                        )
                    )
                    app_status_block.append(
                        app_status.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            created_by,
                            last_updated_by,
                            status_text,
                            up
                        )
                    )

            else:
                up = str(0)
                for i in range(0, app_instances + 1):
                    app_index = str(i)
                    cpu_utilization_block.append(
                        cpu_utilization.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            str(0)
                        )
                    )
                    mem_utilization_block.append(
                        mem_utilization.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            str(0)
                        )
                    )
                    disk_utilization_block.append(
                        disk_utilization.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            str(0)
                        )
                    )
                    app_status_block.append(
                        app_status.generate_metric(
                            space_name,
                            app_name,
                            app_index,
                            created_by,
                            last_updated_by,
                            status_text,
                            up
                        )
                    )

        # service and service plan metrics
        services = get_paginated_results(
            cf.api_domain,
            cf.auth.access_token,
            cf.service_instances.list(
                params=search_params
            ).json()
        )

        service_bindings_search_params = {
            'q': 'app_guid IN {}'.format(
                ','.join(
                    map(lambda x: x['metadata']['guid'], filter(lambda x: True if x['entity']['name'] != 'ssh-gateway' else False, apps))
                )
            )
        }
        service_bindings = gather_facts(
            cf,
            'service_bindings',
            params=service_bindings_search_params,
            mapping_schema='metadata.guid:entity.service_instance_guid'
        )

        for service_info in services:
            service_instance_guid = service_info['metadata']['guid']
            space_name = spaces_facts[service_info['entity']['space_guid']]
            service_plan_name = cf.service_plans.get(service_info['entity']['service_plan_guid']).json()['entity']['name']
            create_time = str(int(utc_to_epoch(service_info['metadata']['created_at'])))
            service_instance_name = service_info['entity']['name']
            service_event_search_params = {
                'q': 'actee:{}'.format(service_instance_guid),
                'order-by': 'timestamp',
                'order-direction': 'desc'
            }
            service_instance_events = get_paginated_results(cf.api_domain, cf.auth.access_token, cf.events.list(params=service_event_search_params).json())
            service_create_events = filter(
                lambda x: x['entity']['type'] == 'audit.service_instance.create',
                service_instance_events
            )

            if len(service_create_events) > 0:
                created_by = service_create_events[0]['entity']['actor_name']

            else:
                created_by = "NaN"

            service_update_events = filter(
                lambda x: x['entity']['type'] == 'audit.service_instance.update',
                service_instance_events
            )

            if len(service_update_events) > 0:
                last_updated_by = service_update_events[0]['entity']['actor_name']

            else:
                last_updated_by = "NaN"

            if service_instance_guid in service_bindings.values():
                bound = str(1)

            else:
                bound = str(0)

            service_instance_status_block.append(
                service_instance_status.generate_metric(
                    space_name,
                    service_instance_name,
                    service_plan_name,
                    create_time,
                    created_by,
                    last_updated_by,
                    bound
                )
            )

            service_plan = cf.service_plans.get(service_info['entity']['service_plan_guid']).json()
            service_plan_cost = json.loads(service_plan['entity']['extra'])['costs'][0]['amount']['usd']

            current_time = datetime.utcnow()
            total_seconds_this_month = (datetime(current_time.year, current_time.month + 1, 1, 0, 0, 0, 0) - datetime(current_time.year, current_time.month, 1, 0, 0, 0, 0)).total_seconds()
            seconds_this_month = (current_time - datetime(current_time.year, current_time.month, 1, 0, 0, 0, 0)).total_seconds()
            seconds_since_creation = (current_time - datetime.strptime(service_info['metadata']['created_at'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()

            if seconds_since_creation >= seconds_this_month:
                seconds_charged = seconds_this_month

            else:
                seconds_charged = seconds_since_creation

            current_cost = service_plan_cost * (float(seconds_charged)/float(total_seconds_this_month))

            service_instance_cost_block.append(
                service_instance_cost.generate_metric(
                    space_name,
                    service_info['entity']['name'],
                    bound,
                    service_plan['entity']['name'],
                    current_cost
                )
            )

        return cpu_utilization.help + \
               cpu_utilization.type + \
               ''.join(cpu_utilization_block) + \
               mem_utilization.help + \
               mem_utilization.type + \
               ''.join(mem_utilization_block) + \
               disk_utilization.help + \
               disk_utilization.type + \
               ''.join(disk_utilization_block) + \
               app_status.help + \
               app_status.type + \
               ''.join(app_status_block) + \
               service_instance_status.help + \
               service_instance_status.type + \
               ''.join(service_instance_status_block) + \
                service_instance_cost.help + \
                service_instance_cost.type + \
                ''.join(service_instance_cost_block)

    return generate_response(cf, org)


def quota_metrics(cf, org):
    def generate_response(cf, org):
        service_instance_quota_block = (
            '# HELP service_instance_quota_usage The proportion of allowed service instances currently in use\n'
            '# TYPE service_instance_quota_usage gauge\n'
            'service_instance_quota_usage {service_instance_quota_usage}\n'
        )

        routes_quota_block = (
            '# HELP routes_quota_usage The proportion of allowed routes currently in use\n'
            '# TYPE routes_quota_usage gauge\n'
            'routes_quota_usage {routes_quota_usage}\n'
        )

        private_domains_quota_block = (
            '# HELP private_domains_quota_usage The proportion of allowed private domains currently in use\n'
            '# TYPE private_domains_quota_usage gauge\n'
            'private_domains_quota_usage {private_domains_quota_usage}\n'
        )

        memory_quota_block = (
            '# HELP memory_quota_usage The proportion of allocated memory currently in use\n'
            '# TYPE memory_quota_usage gauge\n'
            'memory_quota_usage {memory_quota_usage}\n'
        )

        app_instances_quota_block = (
            '# HELP app_instances_quota_usage The proportion of allowed app instances currently in use\n'
            '# TYPE app_instances_quota_usage gauge\n'
            'app_instances_quota_usage {app_instances_quota_usage}\n'
        )

        service_keys_quota_block = (
            '# HELP service_keys_quota_usage The proportion of allowed service keys currently in use\n'
            '# TYPE service_keys_quota_usage gauge\n'
            'service_keys_quota_usage {service_keys_quota_usage}\n'
        )

        response = []
        org_guid = _get_org_guid(cf, org)
        org_info = cf.organizations.get(org_guid).json()

        if len(org_info) == 0:
            return "ERROR: unknown organization '{}'".format(org), 404

        quota_definition_guid = os.path.basename(org_info['entity']['quota_definition_url'])
        org_quota_definition = cf.organization_quota_definitions.get(quota_definition_guid).json()

        if org_quota_definition['entity']['total_services'] != -1:
            total_service_instances = cf.service_instances.list().json()['total_results']
            response.append(
                service_instance_quota_block.format(
                    service_instance_quota_usage=float(total_service_instances)/org_quota_definition['entity']['total_services']
                )
            )

        if org_quota_definition['entity']['total_routes'] != -1:
            total_routes = cf.routes.list().json()['total_results']
            response.append(
                routes_quota_block.format(
                    routes_quota_usage=float(total_routes)/org_quota_definition['entity']['total_routes']
                )
            )

        if org_quota_definition['entity']['total_private_domains'] != -1:
            total_private_domains = cf.private_domains.list().json()['total_results']
            response.append(
                private_domains_quota_block.format(
                    private_domains_quota_usage=float(total_private_domains)/org_quota_definition['entity']['total_private_domains']
                )
            )

        if org_quota_definition['entity']['memory_limit'] != -1:
            total_memory = cf.organizations.memory_usage(org_guid).json()['memory_usage_in_mb']
            response.append(
                memory_quota_block.format(
                    memory_quota_usage=float(total_memory)/org_quota_definition['entity']['memory_limit']
                )
            )

        if org_quota_definition['entity']['app_instance_limit'] != -1:
            total_app_instances = cf.organizations.instance_usage(org_guid).json()['instance_usage']
            response.append(
                app_instances_quota_block.format(
                    app_instances_quota_usage=float(total_app_instances)/org_quota_definition['entity']['app_instance_limit']
                )
            )

        if org_quota_definition['entity']['total_service_keys'] != -1:
            total_service_keys = cf.service_keys.list().json()['total_results']
            response.append(
                service_keys_quota_block.format(
                    service_keys_quota_usage=float(total_service_keys)/org_quota_definition['entity']['total_service_keys']
                )
            )

        # total_reserved_route_ports = None  not sure how to find this info
        # total_app_tasks = None not sure how to find this info

        return ''.join(response)

    return generate_response(cf, org)


def _get_org_guid(cf, org):
    org = filter(lambda x: True if x['entity']['name'] == org else False, cf.organizations.list().json()['resources'])

    if len(org) == 0:
        return "ERROR: unknown organization '{}'".format(org), 404

    return org[-1]['metadata']['guid']


def _get_mysql_db_size(service_key):

    mysql_uri = "mysql://{}:{}@{}:{}".format(
        service_key['credentials']['username'],
        service_key['credentials']['password'],
        service_key['credentials']['hostname'],
        service_key['credentials']['port']
    )

    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError

    q = 'SELECT table_schema "Data Base Name", sum(data_length + index_length) "Data Base Size in bytes", sum(data_free) "Free Space in bytes" FROM information_schema.TABLES GROUP BY table_schema'

    tunnel = Tunnel('ssh-gateway', service_key['credentials']['hostname'], os.environ['INTERNAL_PORT'], service_key['credentials']['port'])
    tunnel.connect()

    engine = create_engine(mysql_uri, connect_args={'connect_timeout': 15})

    try:
        connection = engine.connect()

    except OperationalError as e:
        write_stdout("WARNING: couldn't connect to MySQL db service '{}' -- skipping analysis".format(cf.service_instances.get(service_key['service_instance_guid']).json()['entity']['name']))
        return "NaN"
    else:
        results = connection.execute(q)
        tunnel.disconnect()
        return sum([float(x[1]) for x in results])


def _get_redis_db_size(service_key):
    redis_host = service_key['credentials']['host']
    redis_port = service_key['credentials']['port']
    redis_password = service_key['credentials']['password']

    import re
    import redis

    tunnel = Tunnel('ssh-gateway', service_key['credentials']['hostname'], os.environ['INTERNAL_PORT'], service_key['credentials']['port'])
    tunnel.connect()

    r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)
    dbs_info = dict(filter(lambda x: True if re.match('^db[0-9]*$', x[0]) else False, r.info().iteritems()))
    total_length = 0

    for db in dbs_info.keys():
        db_num = int(db.split('db')[-1])
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=db_num)
        total_length += sum([int(r.debug_object(key)['serializedlength']) for key in r.keys()])

    tunnel.disconnect()
    return total_length
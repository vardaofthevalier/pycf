import requests
from urlparse import urljoin

from pycf.auth import CloudFoundryAuth
from requests_api_wrapper.base import ApiWrapper


class CloudFoundry(ApiWrapper):
    def __init__(self, api_domain=None, auth=None, username=None, password=None):
        if api_domain and username and password and not auth:
            auth_endpoint = requests.get(urljoin(api_domain, "v2/info")).json()['authorization_endpoint']
            auth = CloudFoundryAuth(username, password, auth_endpoint)

        self.api_domain = api_domain
        self.username = username
        self.password = password

        super(CloudFoundry, self).__init__(api_domain=api_domain, auth=auth)
        self.api_spec = {
            "info": {
                'endpoint': 'v2/info',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "apps": {
                'endpoint': 'v2/apps',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'events': {
                        'http_method': requests.get,
                        'path_spec': '%s/events',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200, 201]
                    },
                    'associate_route': {
                        'http_method': requests.put,
                        'path_spec': '%s/routes/%s',
                        'args': ['guid', 'route_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'copy_bits': {
                        'http_method': requests.post,
                        'path_spec': '%s/copy_bits',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'download_bits': {  # TODO: test to verify that requests module appropriately handles the redirect -- may need to modify the second request
                        'http_method': requests.get,
                        'path_spec': '%s/download',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params']
                    },
                    'download_droplet': {  # TODO: test to verify that requests module appropriately handles the redirect -- may need to modify the second request
                        'http_method': requests.get,
                        'path_spec': '%s/droplet/download',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params']
                    },
                    'summary': {
                        'http_method': requests.get,
                        'path_spec': '%s/summary',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'stats': {
                        'http_method': requests.get,
                        'path_spec': '%s/stats',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'env': {
                        'http_method': requests.get,
                        'path_spec': '%s/env',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'instances': {
                        'http_method': requests.get,
                        'path_spec': '%s/instances',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'routes': {
                        'http_method': requests.get,
                        'path_spec': '%s/routes',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'service_bindings': {
                        'http_method': requests.get,
                        'path_spec': '%s/routes',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'remove_route': {
                        'http_method': requests.delete,
                        'path_spec': '%s/routes/%s',
                        'args': ['guid', 'route_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_service_binding': {
                        'http_method': requests.delete,
                        'path_spec': '%s/service_bindings/%s',
                        'args': ['guid', 'service_binding_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'restage': {
                        'http_method': requests.post,
                        'path_spec': '%s/restage',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'remove_at_index': {
                        'http_method': requests.delete,
                        'path_spec': '%s/instances/%s',
                        'args': ['guid', 'index'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'upload_bits': {  # TODO: figure out how to handle the multipart upload
                        'http_method': requests.put,
                        'path_spec': '%s/bits',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data']
                    },
                    'upload_droplet': {  # TODO: figure out how to handle the multipart upload
                        'http_method': requests.put,
                        'path_spec': '%s/droplet',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data']
                    },
                    'permissions': {
                        'http_method': requests.get,
                        'path_spec': '%s/permissions',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "routes": {
                'endpoint': 'v2/routes',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'associate_app': {
                        'http_method': requests.put,
                        'path_spec': '%s/apps/%s',
                        'args': ['guid', 'app_guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'route_exists': {
                        'http_method': requests.get,
                        'path_spec': 'reserved/domain/%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'http_route_exists': {
                        'http_method': requests.get,
                        'path_spec': 'reserved/domain/%s/host/%s',
                        'args': ['guid', 'host'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_apps': {
                        'http_method': requests.get,
                        'path_spec': '%s/apps',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'list_route_mappings': {
                        'http_method': requests.get,
                        'path_spec': '%s/route_mappings',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'remove_app': {
                        'http_method': requests.delete,
                        'path_spec': '%s/apps/%s',
                        'args': ['guid', 'app_guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    }
                }
            },
            "services": {
                'endpoint': 'v2/services',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'list_service_plans': {
                        'http_method': requests.get,
                        'path_spec': '%s/service_plans',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    }
                }
            },
            "service_plans": {
                'endpoint': 'v2/service_plans',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'list_service_instances': {
                        'http_method': requests.get,
                        'path_spec': '%s/service_instances',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    }
                }
            },
            "service_instances": {
                'endpoint': 'v2/service_instances',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201, 202]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [202, 204]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201, 202]
                    },
                    'list_routes': {
                        'http_method': requests.get,
                        'path_spec': '%s/routes',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_service_bindings': {
                        'http_method': requests.get,
                        'path_spec': '%s/service_bindings',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_service_keys': {
                        'http_method': requests.get,
                        'path_spec': '%s/service_keys',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'bind_route': {
                        'http_method': requests.put,
                        'path_spec': '%s/routes/%s',
                        'args': ['guid', 'route_guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'unbind_route': {
                        'http_method': requests.delete,
                        'path_spec': '%s/routes/%s',
                        'args': ['guid', 'route_guid'],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'permissions': {
                        'http_method': requests.get,
                        'path_spec': '%s/permissions',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "spaces": {
                'endpoint': 'v2/spaces',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'associate_auditor': {
                        'http_method': requests.put,
                        'path_spec': '%s/auditors/%s',
                        'args': ['guid', 'auditor_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_auditor_by_username': {
                        'http_method': requests.put,
                        'path_spec': '%s/auditors',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'associate_developer': {
                        'http_method': requests.put,
                        'path_spec': '%s/developers/%s',
                        'args': ['guid', 'developer_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_developer_by_username': {
                        'http_method': requests.put,
                        'path_spec': '%s/developers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'associate_manager': {
                        'http_method': requests.put,
                        'path_spec': '%s/managers/%s',
                        'args': ['guid', 'auditor_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_manager_by_username': {
                        'http_method': requests.put,
                        'path_spec': '%s/managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'associate_security_group':{
                        'http_method': requests.put,
                        'path_spec': '%s/security_groups/%s',
                        'args': ['guid', 'security_group_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'summary': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]
                    },
                    'list_apps': {
                        'http_method': requests.get,
                        'path_spec': '%s/apps',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_auditors': {
                        'http_method': requests.get,
                        'path_spec': '%s/auditors',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_developers': {
                        'http_method': requests.get,
                        'path_spec': '%s/developers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_events': {
                        'http_method': requests.get,
                        'path_spec': '%s/events',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_managers': {
                        'http_method': requests.get,
                        'path_spec': '%s/managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_routes': {
                        'http_method': requests.get,
                        'path_spec': '%s/routes',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_security_groups': {
                        'http_method': requests.get,
                        'path_spec': '%s/security_groups',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_service_instances': {
                        'http_method': requests.get,
                        'path_spec': '%s/service_instances',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_services': {
                        'http_method': requests.get,
                        'path_spec': '%s/services',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'remove_auditor': {
                        'http_method': requests.delete,
                        'path_spec': '%s/auditors/%s',
                        'args': ['guid', 'auditor_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_auditor_by_username': {
                        'http_method': requests.delete,
                        'path_spec': '%s/auditors',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'remove_developer': {
                        'http_method': requests.delete,
                        'path_spec': '%s/developers/%s',
                        'args': ['guid', 'developer_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_developer_by_username': {
                        'http_method': requests.delete,
                        'path_spec': '%s/developers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'remove_manager': {
                        'http_method': requests.delete,
                        'path_spec': '%s/managers/%s',
                        'args': ['guid', 'manager_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_manager_by_username': {
                        'http_method': requests.delete,
                        'path_spec': '%s/managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'remove_security_group': {
                        'http_method': requests.delete,
                        'path_spec': '%s/security_groups/%s',
                        'args': ['guid', 'security_group_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list_users_by_role': {
                        'http_method': requests.get,
                        'path_spec': '%s/user_roles',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    }
                }
            },
            "stacks": {
                'endpoint': 'v2/stacks',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    }
                }
            },
            "service_bindings": {
                'endpoint': 'v2/service_bindings',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    }
                }
            },
            "route_mappings": {
                'endpoint': 'v2/route_mappings',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    }
                }
            },  # TODO: implement 'update' method
            "user_provided_service_instances": {
                'endpoint': 'v2/user_provided_service_instances',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'associate_route': {
                        'http_method': requests.put,
                        'path_spec': '%s/routes/%s',
                        'args': ['guid', 'route_guid'],
                        'kwargs': ['headers'],
                        'expected_status': [201]
                    },
                    'list_routes': {
                        'http_method': requests.get,
                        'path_spec': '%s/routes',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_service_bindings': {
                        'http_method': requests.get,
                        'path_spec': '%s/service_bindings',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'remove_route': {
                        'http_method': requests.delete,
                        'path_spec': '%s/routes/%s',
                        'args': ['guid', 'route_guid'],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    }
                }
            },
            "buildpacks": {
                'endpoint': 'v2/buildpacks',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]

                    },
                    'upload_bits': None # TODO: implement later -- the API documentation doesn't show how this is supposed to work.  May need to consult the Go code directly.
                }
            },
            "app_usage_event": {
                'endpoint': 'v2/app_usage_events',
                'api_methods': {
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'purge_and_reseed_all': {
                        'http_method': requests.post,
                        'path_spec': 'destructively_purge_all_and_reseed_started_apps',
                        'args': [],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "blobstores": {
                'endpoint': 'v2/blobstores',
                'api_methods': {
                    'remove_all': {
                        'http_method': requests.delete,
                        'path_spec': 'buildpack_cache',
                        'args': [],
                        'kwargs': ['headers'],
                        'expected_status': [202]
                    }
                }
            },
            "environment_variable_groups": {
                'endpoint': 'v2/config/environment_variable_groups',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['group'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['group'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]

                    }
                }
            },
            "events": {
                'endpoint': 'v2/events',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    }
                }
            },
            "feature_flags": {
                'endpoint': 'v2/config/feature_flags',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['feature_flag'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'set': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['feature_flag'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "files": {
                'endpoint': 'v2/files',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [302]
                    }
                }
            },
            "jobs": {
                'endpoint': 'v2/jobs',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]
                    }
                }
            },
            "organization_quota_definitions": {
                'endpoint': 'v2/quota_definitions',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    }
                }
            },
            "organizations": {
                'endpoint': 'v2/organizations',
                'api_methods': {
                    'associate_auditor': {
                        'http_method': requests.put,
                        'path_spec': '%s/auditors/%s',
                        'args': ['guid', 'auditor_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_auditor_by_username': {
                        'http_method': requests.put,
                        'path_spec': '%s/auditors',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'associate_billing_manager': {
                        'http_method': requests.put,
                        'path_spec': '%s/billing_managers/%s',
                        'args': ['guid', 'billing_manager_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_billing_manager_by_username': {
                        'http_method': requests.put,
                        'path_spec': '%s/billing_managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'associate_manager': {
                        'http_method': requests.put,
                        'path_spec': '%s/managers/%s',
                        'args': ['guid', 'manager_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_manager_by_username': {
                        'http_method': requests.put,
                        'path_spec': '%s/managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'associate_private_domain': {
                        'http_method': requests.put,
                        'path_spec': '%s/private_domains/%s',
                        'args': ['guid', 'private_domain_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_user': {
                        'http_method': requests.put,
                        'path_spec': '%s/users/%s',
                        'args': ['guid', 'user_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_user_by_username': {
                        'http_method': requests.put,
                        'path_spec': '%s/users',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'summary': {
                        'http_method': requests.get,
                        'path_spec': '%s/summary',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]
                    },
                    'list_auditors': {
                        'http_method': requests.get,
                        'path_spec': '%s/auditors',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_billing_managers': {
                        'http_method': requests.get,
                        'path_spec': '%s/billing_managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_managers': {
                        'http_method': requests.get,
                        'path_spec': '%s/managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_private_domains': {
                        'http_method': requests.get,
                        'path_spec': '%s/private_domains',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_services': {
                        'http_method': requests.get,
                        'path_spec': '%s/services',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_space_quota_definitionss': {
                        'http_method': requests.get,
                        'path_spec': '%s/space_quota_definitionss',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_spaces': {
                        'http_method': requests.get,
                        'path_spec': '%s/spaces',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_users': {
                        'http_method': requests.get,
                        'path_spec': '%s/users',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'remove_auditor': {
                        'http_method': requests.delete,
                        'path_spec': '%s/auditors/%s',
                        'args': ['guid', 'auditor_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_auditor_by_username': {
                        'http_method': requests.delete,
                        'path_spec': '%s/auditors',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'remove_billing_manager': {
                        'http_method': requests.delete,
                        'path_spec': '%s/billing_managers/%s',
                        'args': ['guid', 'billing_manager_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_billing_manager_by_username': {
                        'http_method': requests.delete,
                        'path_spec': '%s/billing_managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'remove_manager': {
                        'http_method': requests.delete,
                        'path_spec': '%s/managers/%s',
                        'args': ['guid', 'manager_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_manager_by_username': {
                        'http_method': requests.delete,
                        'path_spec': '%s/managers',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'remove_private_domain': {
                        'http_method': requests.delete,
                        'path_spec': '%s/private_domains/%s',
                        'args': ['guid', 'private_domain_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_user': {
                        'http_method': requests.delete,
                        'path_spec': '%s/users/%s',
                        'args': ['guid', 'user_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_user_by_username': {
                        'http_method': requests.delete,
                        'path_spec': '%s/users',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [204]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'instance_usage': {
                        'http_method': requests.get,
                        'path_spec': '%s/instance_usage',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'memory_usage': {
                        'http_method': requests.get,
                        'path_spec': '%s/memory_usage',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'user_roles': {
                        'http_method': requests.get,
                        'path_spec': '%s/user_roles',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    }
                }
            },
            "private_domains": {
                'endpoint': 'v2/private_domains',
                'api_methods': {
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'shared_organizations': {
                        'http_method': requests.get,
                        'path_spec': '%s/shared_organizations',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "resource_match": {
                'endpoint': 'v2/resource_match',
                'api_methods': {
                    'list': {
                        'http_method': requests.put,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [200]
                    }
                }
            },
            "security_group_running_defaults": {
                'endpoint': 'v2/config/running_security_groups',
                'api_methods': {
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'set': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "security_group_staging_defaults": {
                'endpoint': 'v2/config/staging_security_groups',
                'api_methods': {
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'set': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "security_groups": {
                'endpoint': 'v2/security_groups',
                'api_methods': {
                    'associate_space': {
                        'http_method': requests.put,
                        'path_spec': '%s/spaces/%s',
                        'args': ['guid', 'space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_spaces': {
                        'http_method': requests.get,
                        'path_spec': '%s/spaces',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'remove_space': {
                        'http_method': requests.delete,
                        'path_spec': '%s/spaces/%s',
                        'args': ['guid', 'space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    }
                }
            },
            "service_brokers": {
                'endpoint': 'v2/service_brokers',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    }
                }
            },
            "service_keys": {
                'endpoint': 'v2/service_keys',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    }
                }
            },
            "service_plan_visibilities": {
                'endpoint': 'v2/service_plan_visibilities',
                'api_methods': {
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    }
                }
            },
            "service_usage_event": {
                'endpoint': 'v2/service_usage_events',
                'api_methods': {
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [200]
                    },
                    'purge_and_reseed_all': {
                        'http_method': requests.post,
                        'path_spec': 'destructively_purge_all_and_reseed_existing_instances',
                        'args': [],
                        'kwargs': ['headers'],
                        'expected_status': [204]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            "shared_domains": {
                'endpoint': 'v2/shared_domains',
                'api_methods': {
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    }
                }
            },
            'space_quota_definitions': {
                'endpoint': 'v2/space_quota_definitions',
                'api_methods': {
                    'associate_space': {
                        'http_method': requests.put,
                        'path_spec': '%s/spaces/%s',
                        'args': ['guid', 'space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    },
                    'remove': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_spaces': {
                        'http_method': requests.get,
                        'path_spec': '%s/spaces',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'remove_space': {
                        'http_method': requests.delete,
                        'path_spec': '%s/spaces/%s',
                        'args': ['guid', 'space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                }
            },
            "users": {
                'endpoint': 'v2/users',
                'api_methods': {
                    'associate_audited_organization': {
                        'http_method': requests.put,
                        'path_spec': '%s/audited_organizations/%s',
                        'args': ['guid', 'audited_organization_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_audited_space': {
                        'http_method': requests.put,
                        'path_spec': '%s/audited_spaces/%s',
                        'args': ['guid', 'audited_space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_billing_managed_organization': {
                        'http_method': requests.put,
                        'path_spec': '%s/billing_managed_organizations/%s',
                        'args': ['guid', 'billing_managed_organization_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_managed_organization': {
                        'http_method': requests.put,
                        'path_spec': '%s/managed_organizations/%s',
                        'args': ['guid', 'managed_organization_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_managed_space': {
                        'http_method': requests.put,
                        'path_spec': '%s/managed_spaces/%s',
                        'args': ['guid', 'managed_space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_organization': {
                        'http_method': requests.put,
                        'path_spec': '%s/organizations/%s',
                        'args': ['guid', 'organization_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'associate_space': {
                        'http_method': requests.put,
                        'path_spec': '%s/spaces/%s',
                        'args': ['guid', 'space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [201]
                    },
                    'summary': {
                        'http_method': requests.get,
                        'path_spec': '%s/summary',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'get': {
                        'http_method': requests.get,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers'],
                        'expected_status': [200]
                    },
                    'create': {
                        'http_method': requests.post,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'data'],
                        'expected_status': [201]
                    },
                    'delete': {
                        'http_method': requests.delete,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'list_audited_organizations': {
                        'http_method': requests.get,
                        'path_spec': '%s/audited_organizations',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_audited_spaces': {
                        'http_method': requests.get,
                        'path_spec': '%s/audited_spaces',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_billing_managed_organizations': {
                        'http_method': requests.get,
                        'path_spec': '%s/billing_managed_organizations',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_managed_organizations': {
                        'http_method': requests.get,
                        'path_spec': '%s/managed_organizations',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_managed_spaces': {
                        'http_method': requests.get,
                        'path_spec': '%s/managed_spaces',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_organizations': {
                        'http_method': requests.get,
                        'path_spec': '%s/organizations',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list_spaces': {
                        'http_method': requests.get,
                        'path_spec': '%s/spaces',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'list': {
                        'http_method': requests.get,
                        'path_spec': '',
                        'args': [],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [200]
                    },
                    'remove_audited_organization': {
                        'http_method': requests.delete,
                        'path_spec': '%s/audited_organizations/%s',
                        'args': ['guid', 'audited_organization_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_audited_space': {
                        'http_method': requests.delete,
                        'path_spec': '%s/audited_spaces/%s',
                        'args': ['guid', 'audited_space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_billing_managed_organization': {
                        'http_method': requests.delete,
                        'path_spec': '%s/billing_managed_organizations/%s',
                        'args': ['guid', 'billing_managed_organization_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_managed_organization': {
                        'http_method': requests.delete,
                        'path_spec': '%s/managed_organizations/%s',
                        'args': ['guid', 'managed_organization_guid'],
                        'kwargs': ['headers', 'params', 'managed_organization_guid'],
                        'expected_status': [204]
                    },
                    'remove_managed_space': {
                        'http_method': requests.delete,
                        'path_spec': '%s/managed_spaces/%s',
                        'args': ['guid', 'managed_space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_organization': {
                        'http_method': requests.delete,
                        'path_spec': '%s/organizations/%s',
                        'args': ['guid', 'organization_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'remove_space': {
                        'http_method': requests.delete,
                        'path_spec': '%s/spaces/%s',
                        'args': ['guid', 'space_guid'],
                        'kwargs': ['headers', 'params'],
                        'expected_status': [204]
                    },
                    'update': {
                        'http_method': requests.put,
                        'path_spec': '%s',
                        'args': ['guid'],
                        'kwargs': ['headers', 'params', 'data'],
                        'expected_status': [201]
                    }
                }
            }
        }
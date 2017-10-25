import json
import requests
import functools
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApiObjectWrapper(object):
    def __init__(self, api_domain, api_spec, session, auth=None):
        self.api_domain = api_domain
        self.api_spec = api_spec
        self.session = session
        self.auth = auth
        
    def __getattr__(self, attribute):
        if attribute in self.api_spec['api_methods'].keys():
            return functools.partial(self._call_endpoint, attribute)

        else:
            raise AttributeError("No such method '{}'!".format(attribute))

    def _call_endpoint(self, attribute, *args, **kwargs):
        try:
            given_args = len(args)
            expected_args = len(self.api_spec['api_methods'][attribute]['args'])

            given_kwargs = set(kwargs.keys())
            expected_kwargs = set(self.api_spec['api_methods'][attribute]['kwargs'])

            if 'required_headers' in self.api_spec['api_methods'][attribute].keys():
                required_headers = self.api_spec['api_methods'][attribute]['required_headers']

            else:
                required_headers = None

            if 'default_headers' in self.api_spec['api_methods'][attribute].keys():
                default_headers = self.api_spec['api_methods'][attribute]['default_headers']

            else:
                default_headers = None

            if 'default_params' in self.api_spec['api_methods'][attribute].keys():
                default_params = self.api_spec['api_methods'][attribute]['default_params']

            else:
                default_params = None

            if 'default_data' in self.api_spec['api_methods'][attribute].keys():
                default_data = self.api_spec['api_methods'][attribute]['default_data']

            else:
                default_data = None

        except TypeError as e:
            raise NotImplementedError("Method '%s' appears not to have been implemented yet!" % attribute)

        if given_args == expected_args:
                if given_kwargs.issubset(expected_kwargs):
                    if default_headers:
                        try:
                            default_headers.update(kwargs['headers'])

                        except KeyError:
                            pass

                        kwargs['headers'] = default_headers

                    if required_headers:
                        req_set = set(required_headers)
                        given_set = set(kwargs['headers'].keys())

                        if not req_set.issubset(given_set):
                            raise Exception("Required headers {} not provided in request!".format(', '.join(list(req_set - given_set))))

                    if default_params:
                        try:
                            default_params.update(kwargs['params'])

                        except KeyError:
                            pass

                        kwargs['params'] = default_params

                    if default_data:
                        try:
                            default_data.update(kwargs['data'])

                        except KeyError:
                            pass

                        kwargs['data'] = default_data

                    path = '/'.join([self.api_domain, self.api_spec['endpoint'], self.api_spec['api_methods'][attribute]['path_spec']]).rstrip('/') % tuple(args)
                    retries = 3
                    while retries > 0:
                        response = self._request(self.api_spec['api_methods'][attribute]['http_method'],
                                            path,
                                            **kwargs
                                            )

                        if response.status_code >= 400:
                            retries -= 1

                        else:
                            return response

                    raise Exception("Couldn't call endpoint {}! (status code: {}, reason: {})".format(response.url, response.status_code, response.content))

                else:
                    raise TypeError("Unknown parameter(s) '%s' -- refer to the official Cloud Foundry API documentation for additional info." % ', '.join(list(given_kwargs.difference(expected_kwargs))))

        else:
            if expected_args > 1:
                raise TypeError("%s() takes exactly %s arguments (%s given)" % (attribute, str(expected_args), str(given_args)))

            else:
                raise TypeError("%s() takes exactly 1 argument (%s given)" % (attribute, str(given_args)))

    def _request(self, request_type, path, headers=None, params=None, data=None):
        request_data = data

        if type(data) is dict:
            request_data = json.dumps(data)

        elif type(data) is str:
            request_data = data

        elif data is None:
            pass

        else:
            raise ValueError("Request data must be either a string or a dictionary!")

        logger.info("request-headers: " + json.dumps(headers))
        return self.session.request(request_type.__name__,
                                path,
                                headers=headers,
                                params=params,
                                data=request_data,
                                auth=self.auth
                                )


class ApiWrapper(object):
    def __init__(self, api_domain=None, auth=None, session=None):
        if session:
            self.session = session
        else:
            self.session = requests.Session()

        self.auth = auth
        self.api_domain = api_domain

    def __getattr__(self, item):
        if 'api_spec' in self.__dict__.keys():
            if item in self.__dict__['api_spec'].keys():
                return ApiObjectWrapper(self.api_domain, self.api_spec[item], self.session, auth=self.auth)

            else:
                try:
                    return self.__dict__[item]

                except Exception:
                    raise AttributeError("No such attribute '{}'!".format(item))

    def metadata(self, api, method=None, attribute=None):
        if method:
            if attribute:
                try:
                    return dict(filter(lambda x: True if x[0] == attribute else False, self.api_spec[api]['api_methods'][method].iteritems()))[attribute]

                except KeyError:
                    raise AttributeError("No such attribute '{}' in method '{}' metadata!".format(attribute, method))

            else:
                return self.api_spec[api]['api_methods'][method]

        else:
            if attribute:
                try:
                    return self.api_spec[api][attribute]

                except KeyError:
                    raise AttributeError("No such attribute '{}' in api '{}' metadata!".format(attribute, api))
            else:
                return self.api_spec[api]

    def set_auth(self, auth):
        self.auth = auth

    def set_api_domain(self, api_domain):
        self.api_domain = api_domain



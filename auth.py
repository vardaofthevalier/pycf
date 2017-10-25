import time
import json
import base64
import requests

from urllib import urlencode
from urlparse import urljoin


BASIC_AUTH = "Basic {}".format(base64.b64encode("cf:"))


def init_access_token(username, password, endpoint):
    auth_headers = {
        "Authorization": BASIC_AUTH,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    auth_data = {
        "password": password,
        "username": username,
        "grant_type": "password",
        "response_type": "token",
        "scope": ""
    }

    resp = requests.post(
        urljoin(
            endpoint,
            "oauth/token"
        ),
        headers=auth_headers,
        data=urlencode(auth_data)
    )

    if resp.status_code not in [200, 201]:
        raise Exception("Couldn't get new access token! -- {}".format(resp.content))

    return resp


def refresh_access_token(refresh_token, endpoint):
    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    auth_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    resp = requests.post(
        urljoin(
            endpoint,
            "oauth/token"
        ),
        headers=auth_headers,
        data=urlencode(auth_data)
    )

    if resp.status_code not in [200, 201]:
        raise Exception("Couldn't refresh access token! -- {}".format(resp.content))

    return resp


def access_token_expired(token_expiry):
    if int(time.time()) > token_expiry:
        return True

    else:
        return False


class CloudFoundryTokenFileAuth(requests.auth.AuthBase):
    def __init__(self, token_file_path):
        self.token_file_path = token_file_path
        self.default_headers = {
            "Content-Type": "application/json"
        }
        self._load_token_info()

    def __call__(self, r):
        r.headers.update(self.default_headers)
        self._load_token_info()
        r.headers["Authorization"] = self.access_token
        return r

    def _load_token_info(self):
        with open(self.token_file_path) as f:
            token_info = json.load(f)

        self.access_token = "{} {}".format(token_info['token_type'], token_info['access_token'])
        self.refresh_token = token_info['refresh_token']


class CloudFoundryAuth(requests.auth.AuthBase):
    def __init__(self, username=None, password=None, auth_endpoint=None):
        if not username or not password or not auth_endpoint:
            raise Exception("Unable to authenticate to Cloud Foundry (missing credentials)")

        self.username = username
        self.password = password
        self.cf_basic_auth = BASIC_AUTH
        self.access_token = None
        self.refresh_token = None
        self.access_token_expiry = None
        self.auth_endpoint = auth_endpoint
        self.default_headers = {
            "Content-Type": "application/json"
        }

    def __call__(self, r):
        r.headers.update(self.default_headers)
        if self.access_token is None:
            self._init_access_token()

        elif access_token_expired(self.access_token_expiry):
            self._refresh_access_token()

        r.headers["Authorization"] = self.access_token
        return r

    def _init_access_token(self):
        try:
            resp = init_access_token(self.username, self.password, self.auth_endpoint)
            self.access_token = "{} {}".format(resp.json()['token_type'], resp.json()['access_token'])
            self.refresh_token = "{} {}".format(resp.json()['token_type'], resp.json()['refresh_token'])
            self.access_token_expiry = int(time.time()) + int(resp.json()['expires_in'])

        except Exception as e:
            raise Exception("There was a problem retrieving a new access token -- " + e.message)

    def _refresh_access_token(self):
        try:
            resp = refresh_access_token(self.refresh_token, self.auth_endpoint)
            self.access_token = "{} {}".format(resp.json()['token_type'], resp.json()['access_token'])
            self.refresh_token = resp.json()['refresh_token']
            self.access_token_expiry = int(time.time()) + int(resp.json()['expires_in'])

        except Exception as e:
            raise Exception("There was a problem refreshing the access token -- " + e.message)

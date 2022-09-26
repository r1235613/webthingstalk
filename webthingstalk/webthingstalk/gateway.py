import requests
from bs4 import BeautifulSoup

from django.conf import settings


class _Gateway:
    def __init__(self, url, user_token):
        self.url = url.rstrip('/')

        self.user_token = user_token
        self.device_token = ''

    def get_device_token(self):
        url = '{0}/oauth/allow?response_type=code&client_id=local-token&scope=%2Fthings%3Areadwrite&redirect_uri=https%3A%2F%2Fgateway.localhost%2Foauth%2Flocal-token-service&jwt={1}'.format(
            self.url, self.user_token)

        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.text, 'html.parser')
        self.device_token = soup.find('code', id='token').text


class _GatewayHander():
    def __init__(self):
        default_gateway_user_token = self._get_user_token(
            settings.DEFAULT_GATEWAY_URI, settings.DEFAULT_GATEWAY_USERNAME, settings.DEFAULT_GATEWAY_PASSWORD)
        self.default_gateway = _Gateway(
            settings.DEFAULT_GATEWAY_URI, default_gateway_user_token)
        self.default_gateway.get_device_token()

        self._custom_gateway = {}

    def _get_user_token(self, url, username, password):
        url = url + '/login'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        payload = {'email': username, 'password': password}

        r = requests.post(url, headers=headers, json=payload, timeout=3)
        return r.json()['jwt']

    def delete_custom_gateway(self, user_id):
        self._custom_gateway.pop(user_id, None)

    def create_custom_gateway(self, user_id, url, username, password):
        url = url.rstrip('/')
        user_token = self._get_user_token(url, username, password)
        self._custom_gateway[user_id] = _Gateway(url, user_token)
        self._custom_gateway[user_id].get_device_token()

    def create_custom_gateway_by_token(self, user_id, url, user_token):
        self._custom_gateway[user_id] = _Gateway(url, user_token)
        self._custom_gateway[user_id].get_device_token()

    def get_custom_gateway(self, user_id):
        return self._custom_gateway.get(user_id, None)


gateway_hander = _GatewayHander()

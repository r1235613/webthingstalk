import requests
from bs4 import BeautifulSoup

from django.conf import settings


class _Gateway:
    def __init__(self, url, username, password):
        self.url = url.rstrip('/')
        self.username = username
        self.password = password

        self.user_token = ''
        self.device_token = ''

        self._get_user_token()
        self._get_device_token()

    def _get_user_token(self):
        url = self.url + '/login'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        payload = {'email': self.username, 'password': self.password}

        r = requests.post(url, headers=headers, json=payload)
        self.user_token = r.json()['jwt']

    def _get_device_token(self):
        url = '{0}/oauth/allow?response_type=code&client_id=local-token&scope=%2Fthings%3Areadwrite&redirect_uri=https%3A%2F%2Fgateway.localhost%2Foauth%2Flocal-token-service&jwt={1}'.format(
            self.url, self.user_token)

        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        self.device_token = soup.find('code', id='token').text


class _GatewayHander():
    def __init__(self):
        self.default_gateway = _Gateway(
            settings.DEFAULT_GATEWAY_URL,
            settings.DEFAULT_GATEWAY_USERNAME,
            settings.DEFAULT_GATEWAY_PASSWORD
        )

        self._custom_gateway = {}

    def create_custom_gateway(self, user_id, url, username, password):
        url = url.rstrip('/')
        self._custom_gateway[user_id] = _Gateway(url, username, password)

    def get_custom_gateway(self, user_id):
        return self._custom_gateway.get(user_id, None)


gateway_hander = _GatewayHander()

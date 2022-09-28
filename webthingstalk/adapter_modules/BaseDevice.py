import json
import requests
from abc import ABCMeta, abstractmethod


class BaseDevice(object, metaclass=ABCMeta):
    def __init__(
        self,
        iottalk_url,
        webthing_url,
        property_table,
        gateway_token=None,
        device_name=None,
    ):
        self.api_url = '{0}/csm'.format(iottalk_url)
        self.autogen_api_url = '{0}/autogen/create_device/'.format(iottalk_url)
        self.webthing_url = webthing_url.rstrip('/')
        self.property_table = property_table
        self.gateway_token = gateway_token
        self.device_name = device_name

        self.device_type = 'gateway' if self.gateway_token != None else 'native'
        self.headers = {'Accept': 'application/json'} if self.device_type == 'native' else {
            'Authorization': 'Bearer {gateway_token}'.format(gateway_token=self.gateway_token), 'Accept': 'application/json'}

        self._gen_code()

    def create_device(self):
        r = requests.post(self.autogen_api_url, json={'code': self.code})
        token = json.loads(r.text).get('token', 'None')
        return token

    def _get_property_name(self, df):
        for key, value in self.property_table.items():
            if value['idf'] == df or value['odf'] == df:
                return key

    @abstractmethod
    def _gen_code(self):
        pass

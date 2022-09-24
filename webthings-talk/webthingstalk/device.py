import json
import requests
import adapter_modules
from datetime import datetime

from .models import Device
from development.models import User

from .gateway import gateway_hander

device_table = {
    'Light': {
        'properties': {
            'OnOffProperty': {'idf': ['wtOnOff-I'], 'odf': ['wtOnOff-O']},
            'BrightnessProperty': {'idf': ['wtBrightness-I'], 'odf': ['wtBrightness-O']},
            'ColorModeProperty': {'idf': ['wtColorMode-I'], 'odf': []},
            'ColorProperty': {'idf': ['wtColor-I'], 'odf': ['wtColor-O']},
            'ColorTemperatureProperty': {
                'idf': ['wtColorTemp-I'],
                'odf': ['wtColorTemp-O']
            },
        },
        'device_model': 'WT_Light',
        'module': adapter_modules.Light,
    },
    'OnOffSwitch': {
        'properties': {'OnOffProperty': {'idf': ['wtOnOff-I'], 'odf': ['wtOnOff-O']}},
        'device_model': 'WT_OnOffSwitch',
        'module': adapter_modules.OnOffSwitch,
    },
    'ColorControl': {
        'properties': {
            'ColorModeProperty': {'idf': ['wtColorMode-I'], 'odf': []},
            'ColorProperty': {'idf': ['wtColor-I'], 'odf': ['wtColor-O']},
            'ColorTemperatureProperty': {
                'idf': ['wtColorTemp-I'],
                'odf': ['wtColorTemp-O']
            },
        },
        'device_model': 'WT_ColorControl',
        'module': adapter_modules.OnOffSwitch,
    },
    'PushButton': {
        'properties': {
            'PushedProperty': {
                'idf': ['wtPushed-I1', 'wtPushed-I2', 'wtPushed-I3', 'wtPushed-I4'],
                'odf': []
            },
        },
        'device_model': 'WT_PushButton',
        'module': adapter_modules.PushButton,
    },
}


class _Device():
    def __init__(self, device_model, device_base, device_url='', gateway_type=None, gateway_url='', gateway_token='', properties={}):
        self.device_model = device_model
        self.device_base = device_base

        self.device_url = device_url

        self.gateway_type = gateway_type
        self.gateway_url = gateway_url
        self.gateway_token = gateway_token

        self.device_name = ''
        self.device_list = {}
        self.select_device = None

        self.properties = properties

        self.connected = False

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {'device_model': self.device_model, 'base': self.device_base, 'device_url': self.device_url, 'gateway_token': self.gateway_token, 'device_name': self.device_name, 'properties': self.properties, 'device_list': self.device_list, 'select_device': self.select_device}

    def get_gateway_device(self):
        if self.device_base != 'gateway':
            raise ValueError('Not Gateway Device.')

        url = '{0}/things/'.format(self.gateway_url.rstrip('/'))
        headers = {'Authorization': 'Bearer {0}'.format(
            self.gateway_token), 'Accept': 'application/json'}
        r = requests.get(url, timeout=3, headers=headers)
        data = r.json()

        self.device_list = {x['title']: {
            'device_type': x['selectedCapability'], 'device_url': x['href']} for x in data}

    def get_device_info(self):
        origin_device_model = self.device_model

        try:
            self._get_device_info(self.device_base)
        except:
            raise RuntimeError()

        if 'WT_' + self.device_model != origin_device_model:
            raise ValueError()

    def _get_device_info(self, device_base):
        if device_base == 'gateway':
            url = '{0}/things/'.format(self.gateway_url.rstrip('/'))
            headers = {'Authorization': 'Bearer {0}'.format(
                self.gateway_token), 'Accept': 'application/json'}
        else:
            url = self.device_url
            headers = {}

        r = requests.get(url, timeout=3, headers=headers)
        data = r.json()

        if device_base == 'gateway':
            device = list(
                filter(lambda x: x['title'] == self.select_device, data))[0]
            models = {x: len(device_table[x]['properties'])
                      for x in device['@type']}

            self.device_model = max(models, key=models.get)

            self.device_url = self.gateway_url + device['href']
            self.device_name = device['title']
            property_types = {key: value['@type']
                              for key, value in device['properties'].items()}
        else:
            # 選擇最多屬性的裝置
            models = {x: len(device_table[x]['properties'])
                      for x in data['@type']}
            self.device_model = max(models, key=models.get)
            property_types = {key: value['@type']
                              for key, value in data['properties'].items()}
            self.device_name = data['title']

        self.properties = {}
        property_cnt_dict = {}
        for key, value in property_types.items():
            property = device_table[self.device_model]['properties'][value]
            property_cnt = property_cnt_dict.get(value, 0)

            self.properties[key] = {
                'property': value,
                'idf': property['idf'][property_cnt] if property_cnt < len(property['idf']) else None,
                'odf': property['odf'][property_cnt] if property_cnt < len(property['odf']) else None
            }

            property_cnt_dict[value] = property_cnt + 1

        self.connected = True


class _DeviceHander():
    def __init__(self):
        self._user_temp_device = {}

    def create_temp_device(self, user_id, device_model, device_base, device_url=None, gateway_type=None):
        username = User.objects.get(id=user_id).username

        if user_id in self._user_temp_device:
            raise KeyError(
                'User %s has already created temp device.' % username)

        if gateway_type == 'custom':
            gateway = gateway_hander.get_custom_gateway(user_id)
            if gateway != None:
                self._user_temp_device[user_id] = _Device(
                    device_model, device_base, device_url, gateway_type=gateway_type, gateway_url=gateway.url, gateway_token=gateway.device_token)
            else:
                self._user_temp_device[user_id] = _Device(
                    device_model, device_base, device_url, gateway_type=gateway_type)
        elif gateway_type == 'default':
            gateway = gateway_hander.default_gateway
            self._user_temp_device[user_id] = _Device(
                device_model, device_base, device_url, gateway_type=gateway_type, gateway_url=gateway.url, gateway_token=gateway.device_token)
        else:
            self._user_temp_device[user_id] = _Device(
                device_model, device_base, device_url)

    def delete_temp_device(self, user_id):
        self._user_temp_device.pop(user_id, None)

    def update_temp_device(self, user_id, select_device):
        self._user_temp_device[user_id].select_device = select_device

    def get_temp_device(self, user_id):
        return self._user_temp_device.get(user_id, _Device('', ''))

    def temp_device_get_gateway_device(self, user_id):
        self._user_temp_device[user_id].get_gateway_device()

    def temp_device_get_info(self, user_id):
        self._user_temp_device[user_id].get_device_info()

    def create_device(self, user_id):
        username = User.objects.get(id=user_id).username

        if user_id not in self._user_temp_device:
            raise KeyError(
                'User %s has not yet created temp device.' % username)

        temp_dev = self._user_temp_device[user_id]

        token = self._create_device_autogen(temp_dev)

        dev = Device.objects.filter(
            user_id=user_id, device_name=temp_dev.device_name).first()
        if dev == None:
            dev = Device.objects.create(
                device_model=temp_dev.device_model,
                device_base=temp_dev.device_base,
                device_url=temp_dev.device_url,
                user_id=user_id,
                token=token,
                device_name=temp_dev.device_name,
                start_time=datetime.now()
            )
            for key, value in temp_dev.properties.items():
                dev.property.create(
                    name=key, property=value['property'], idf=value['idf'], odf=value['odf'])
        else:
            dev.start_time = datetime.now()

        self.delete_temp_device(user_id)

    def _create_device_autogen(self, device):
        obj = device_table[device.device_model]['module']
        dev = obj(
            'http://192.168.52.151/csm',
            device.device_url,
            device_name=device.device_name,
            property_table=device.properties,
            gateway_token=device.gateway_token if device.device_base == 'gateway' else None
        )
        token = dev.create_device()

        return token

    def delete_device(self, user_id, device_name):
        dev = Device.objects.filter(
            user_id=user_id, device_name=device_name).first()

        r = requests.post(
            'http://192.168.52.151/autogen/delete_device/', json={'token': dev.token})
        print(r.status_code, r.text)
        Device.objects.filter(
            user_id=user_id, device_name=device_name).delete()


device_handler = _DeviceHander()

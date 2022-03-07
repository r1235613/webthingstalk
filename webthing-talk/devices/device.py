import json
from operator import mod
import requests
import iottalk_webthing
from datetime import datetime

from .models import User, Device

device_table = {
    'Light': {
        'properties': {
            'OnOffProperty': {'idf': ['OnOff-I'], 'odf': ['OnOff-O']},
            'BrightnessProperty': {'idf': ['Brightness-I'], 'odf': ['Brightness-O']},
            'ColorModeProperty': {'idf': ['ColorMode-I'], 'odf': []},
            'ColorProperty': {'idf': ['Color-I'], 'odf': ['Color-O']},
            'ColorTemperatureProperty': {
                'idf': ['ColorTemp-I'],
                'odf': ['ColorTemp-O']
            },
        },
        'device_model': 'WT_Light',
        'module': iottalk_webthing.Light,
    },
    'OnOffSwitch': {
        'properties': {'OnOffProperty': {'idf': ['OnOff-I'], 'odf': ['OnOff-O']}},
        'device_model': 'WT_OnOffSwitch',
        'module': iottalk_webthing.OnOffSwitch,
    },
    'ColorControl': {
        'properties': {
            'ColorModeProperty': {'idf': ['ColorMode-I'], 'odf': []},
            'ColorProperty': {'idf': ['Color-I'], 'odf': ['Color-O']},
            'ColorTemperatureProperty': {
                'idf': ['ColorTemp-I'],
                'odf': ['ColorTemp-O']
            },
        },
        'device_model': 'WT_ColorControl',
        'module': iottalk_webthing.OnOffSwitch,
    },
    'PushButton': {
        'properties': {
            'PushedProperty': {
                'idf': ['Pushed-I1', 'Pushed-I2', 'Pushed-I3', 'Pushed-I4'],
                'odf': []
            },
        },
        'device_model': 'WT_PushButton',
        'module': iottalk_webthing.PushButton,
    },
}


class _Device():
    def __init__(self, type, url, token='', name='', claim='', model='', href=None, properties={}):
        self.type = type
        self.url = url
        self.token = token
        self.name = name
        self.claim = claim
        self.model = model

        self.device_list = {}
        self.select_device = None

        self.properties = properties

        self.href = href

        self.checked = False
        self.connected = False

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {'type': self.type, 'url': self.url, 'token': self.token, 'name': self.name, 'claim': self.claim, 'model': self.model, 'properties': self.properties, 'device_list': self.device_list, 'select_device': self.select_device, 'checked': self.checked, 'connected': self.connected}

    def get_gateway_device(self):
        if self.type != 'gateway':
            raise ValueError('Not Gateway Device.')

        self.checked = True
        self.connected = False

        url = '{0}/things/'.format(self.url.rstrip('/'))
        headers = {'Authorization': 'Bearer {0}'.format(
            self.token), 'Accept': 'application/json'}
        r = requests.get(url, timeout=5, headers=headers)
        data = r.json()

        self.device_list = {x['title']: {
            'device_type': x['selectedCapability'], 'device_url': x['href']} for x in data}

        self.connected = True

    def get_device_info(self):
        self.checked = True
        self.connected = False

        if self.type == 'native':
            self._get_native_device_info()
        elif self.type == 'gateway':
            self._get_gateway_device_info()
        else:
            raise ValueError()

        self.connected = True

    def _get_native_device_info(self):
        r = requests.get(self.url, timeout=5)
        data = r.json()

        # 選擇最多屬性的裝置
        models = {x: len(device_table[x]['properties'])for x in data['@type']}
        self.model = max(models, key=models.get)

        property_types = {key: value['@type']
                          for key, value in data['properties'].items()}

        self.properties = {}
        property_cnt_dict = {}
        for key, value in property_types.items():
            property = device_table[self.model]['properties'][value]
            property_cnt = property_cnt_dict.get(value, 0)

            self.properties[key] = {
                'property': value,
                'idf': property['idf'][property_cnt] if property_cnt < len(property['idf']) else None,
                'odf': property['odf'][property_cnt] if property_cnt < len(property['odf']) else None
            }

            property_cnt_dict[value] = property_cnt + 1

    def _get_gateway_device_info(self):
        url = '{0}/things/'.format(self.url.rstrip('/'))
        headers = {'Authorization': 'Bearer {0}'.format(
            self.token), 'Accept': 'application/json'}
        r = requests.get(url, timeout=5, headers=headers)
        data = r.json()

        device = list(
            filter(lambda x: x['title'] == self.select_device, data))[0]
        models = {x: len(device_table[x]['properties'])
                  for x in device['@type']}
        self.model = max(models, key=models.get)
        self.href = device['href']

        property_types = {key: value['@type']
                          for key, value in device['properties'].items()}

        self.properties = {}
        property_cnt_dict = {}
        for key, value in property_types.items():
            property = device_table[self.model]['properties'][value]
            property_cnt = property_cnt_dict.get(value, 0)

            self.properties[key] = {
                'property': value,
                'idf': property['idf'][property_cnt] if property_cnt < len(property['idf']) else None,
                'odf': property['odf'][property_cnt] if property_cnt < len(property['odf']) else None
            }

            property_cnt_dict[value] = property_cnt + 1


class _DeviceHander():
    def __init__(self):
        self._user_temp_device = {}
        self._device_processes = {}

        devices = list(Device.objects.all())
        for d in devices:
            properties = {x.name: {'property': x.property, 'idf': x.idf,
                                   'odf': x.odf} for x in list(d.property.all())}
            self._user_temp_device[d.user_id] = _Device(
                d.type, d.url, d.token, d.name, d.claim, model=d.model, href=d.href, properties=properties)
            self.create_device(d.user_id)

    def create_temp_device(self, user_id, type, url, token='', name='', claim='', model=''):
        username = User.objects.get(id=user_id).username

        if user_id in self._user_temp_device:
            raise KeyError(
                'User %s has already created temp device.' % username)

        self._user_temp_device[user_id] = _Device(
            type, url, token, name, claim, model)

    def delete_temp_device(self, user_id):
        self._user_temp_device.pop(user_id, None)

    def update_temp_device(self, user_id, name, claim, select_device):
        self._user_temp_device[user_id].name = name
        self._user_temp_device[user_id].claim = claim
        self._user_temp_device[user_id].select_device = select_device

    def get_temp_device(self, user_id):
        return self._user_temp_device.get(user_id, _Device('native', ''))

    def check_device_name_existed(self, user_id, name):
        return Device.objects.filter(user_id=user_id, name=name).count() > 0

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

        if user_id not in self._device_processes:
            self._device_processes[user_id] = {}

        self._create_device_process(user_id, temp_dev)

        dev = Device.objects.filter(
            user_id=user_id, name=temp_dev.name).first()
        if dev == None:
            dev = Device.objects.create(
                type=temp_dev.type,
                url=temp_dev.url,
                user_id=user_id,
                token=temp_dev.token,
                name=temp_dev.name,
                model=temp_dev.model,
                claim=temp_dev.claim,
                href=temp_dev.href,
                start_time=datetime.now()
            )
            for key, value in temp_dev.properties.items():
                dev.property.create(
                    name=key, property=value['property'], idf=value['idf'], odf=value['odf'])
        else:
            dev.start_time = datetime.now()

        self.delete_temp_device(user_id)

    def _create_device_process(self, user_id, device):
        username = User.objects.get(id=user_id).username
        obj = device_table[device.model]['module']
        proc = obj(
            'http://192.168.52.140/csm',
            device.url.rstrip(
                '/') + device.href if device.type == 'gateway' else device.url,
            device_name=device.name,
            username=username if device.claim == 'on' else None,
            property_table=device.properties,
            gateway_token=device.token if device.type == 'gateway' else None
        )
        self._device_processes[user_id][device.name] = proc
        self._device_processes[user_id][device.name].start()

    def delete_device(self, user_id, name):
        proc = self._device_processes[user_id].pop(name, None)
        if proc:
            proc.terminate()
            proc.join()

        Device.objects.filter(user_id=user_id, name=name).delete()


device_handler = _DeviceHander()

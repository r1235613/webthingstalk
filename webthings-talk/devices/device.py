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
    def __init__(self, device_model, device_base, device_url, token='', href=None, properties={}):
        self.device_model = device_model
        self.device_base = device_base
        self.device_url = device_url
        self.token = token
        self.device_name = ''

        self.device_list = {}
        self.select_device = None

        self.properties = properties

        self.href = href

        self.connected = False

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {'device_model': self.device_model, 'base': self.device_base, 'device_url': self.device_url, 'token': self.token, 'device_name': self.device_name, 'properties': self.properties, 'device_list': self.device_list, 'select_device': self.select_device}

    def get_gateway_device(self):
        if self.device_base != 'gateway':
            raise ValueError('Not Gateway Device.')

        url = '{0}/things/'.format(self.device_url.rstrip('/'))
        headers = {'Authorization': 'Bearer {0}'.format(
            self.token), 'Accept': 'application/json'}
        r = requests.get(url, timeout=5, headers=headers)
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
            url = '{0}/things/'.format(self.device_url.rstrip('/'))
            headers = {'Authorization': 'Bearer {0}'.format(
                self.token), 'Accept': 'application/json'}
        else:
            url = self.device_url
            headers = {}

        r = requests.get(url, timeout=5, headers=headers)
        data = r.json()

        if device_base == 'gateway':
            device = list(
                filter(lambda x: x['title'] == self.select_device, data))[0]
            models = {x: len(device_table[x]['properties'])
                      for x in device['@type']}

            if self.device_model != max(models, key=models.get):
                raise
            self.href = device['href']
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
        self._device_processes = {}

        # devices = list(Device.objects.all())
        # for d in devices:
        #     properties = {x.name: {'property': x.property, 'idf': x.idf,
        #                            'odf': x.odf} for x in list(d.property.all())}
        #     self._user_temp_device[d.user_id] = _Device(
        #         d.device_model, d.device_base, d.url, d.token, href=d.href, properties=properties)
        #     self.create_device(d.user_id)

    def create_temp_device(self, user_id, device_model, device_base, device_url='', token=''):
        username = User.objects.get(id=user_id).username

        if user_id in self._user_temp_device:
            raise KeyError(
                'User %s has already created temp device.' % username)

        self._user_temp_device[user_id] = _Device(
            device_model, device_base, device_url, token)

    def delete_temp_device(self, user_id):
        self._user_temp_device.pop(user_id, None)

    def update_temp_device(self, user_id, device_url, select_device):
        self._user_temp_device[user_id].device_url = device_url
        self._user_temp_device[user_id].select_device = select_device

    def get_temp_device(self, user_id):
        return self._user_temp_device.get(user_id, _Device('', 'native', ''))

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
            user_id=user_id, device_name=temp_dev.device_name).first()
        if dev == None:
            dev = Device.objects.create(
                device_model=temp_dev.device_model,
                device_base=temp_dev.device_base,
                url=temp_dev.device_url,
                user_id=user_id,
                token=temp_dev.token,
                device_name=temp_dev.device_name,
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
        obj = device_table[device.device_model]['module']
        proc = obj(
            'http://192.168.52.140/csm',
            device.device_url.rstrip(
                '/') + device.href if device.device_base == 'gateway' else device.device_url,
            device_name=device.device_name,
            property_table=device.properties,
            gateway_token=device.token if device.device_base == 'gateway' else None
        )
        self._device_processes[user_id][device.device_name] = proc
        self._device_processes[user_id][device.device_name].start()

    def delete_device(self, user_id, device_name):
        proc = self._device_processes[user_id].pop(device_name, None)
        if proc:
            proc.terminate()
            proc.join()

        Device.objects.filter(
            user_id=user_id, device_name=device_name).delete()


device_handler = _DeviceHander()

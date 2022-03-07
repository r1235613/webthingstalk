import json
import requests
from iottalkpy.dai import DAI
from iottalkpy.dan import DeviceFeature


class Light(DAI):
    def __init__(
        self,
        api_url,
        webthing_url,
        property_table,
        gateway_token=None,
        device_addr=None,
        device_name=None,
        username=None,
        register_callback=None,
        on_register=None,
        on_deregister=None,
        on_connect=None,
        on_disconnect=None,
        push_interval=1,
        interval=None,
    ):
        device_features = {
            "Brightness-I": DeviceFeature(
                "Brightness-I",
                "idf",
                [None],
                self.Brightness_I,
                None
            ),
            "Color-I": DeviceFeature(
                "Color-I",
                "idf",
                [None],
                self.Color_I,
                None
            ),
            "ColorMode-I": DeviceFeature(
                "ColorMode-I",
                "idf",
                [None],
                self.ColorMode_I,
                None
            ),
            "ColorTemp-I": DeviceFeature(
                "ColorTemp-I",
                "idf",
                [None],
                self.ColorTemp_I,
                None
            ),
            "OnOff-I": DeviceFeature(
                "OnOff-I",
                "idf",
                [None],
                self.OnOff_I,
                None
            ),
            "Brightness-O": DeviceFeature(
                "Brightness-O",
                "odf",
                [None],
                None,
                self.Brightness_O
            ),
            "Color-O": DeviceFeature(
                "Color-O",
                "odf",
                [None],
                None,
                self.Color_O
            ),
            "ColorTemp-O": DeviceFeature(
                "ColorTemp-O",
                "odf",
                [None],
                None,
                self.ColorTemp_O
            ),
            "OnOff-O": DeviceFeature(
                "OnOff-O",
                "odf",
                [None],
                None,
                self.OnOff_O
            ),
        }

        super().__init__(
            api_url=api_url,
            device_model="WT_Light",
            device_addr=device_addr,
            device_name=device_name,
            persistent_binding=False,
            username=username,
            extra_setup_webpage="",
            device_webpage="",
            profile={},
            register_callback=register_callback,
            on_register=on_register,
            on_deregister=on_deregister,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            push_interval=push_interval,
            interval=interval,
            device_features=device_features,
        )

        self.webthing_url = webthing_url.rstrip('/')
        self.gateway_token = gateway_token
        self.property_table = property_table
        self.device_type = 'gateway' if gateway_token != None else 'native'
        self.headers = {'Accept': 'application/json'} if self.device_type == 'native' else {
            'Authorization': 'Bearer {0}'.format(gateway_token), 'Accept': 'application/json'}

    def _get_property_name(self, df):
        for key, value in self.property_table.items():
            if value['idf'] == df or value['odf'] == df:
                return key

    def Brightness_I(self):
        property_name = self._get_property_name('Brightness-I')

        if property_name != None:
            r = requests.get(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), headers=self.headers)

            return json.loads(r.text).get(
                property_name, 'None') if self.device_type == 'native' else json.loads(r.text)

    def Color_I(self):
        property_name = self._get_property_name('Color-I')

        if property_name != None:
            r = requests.get(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), headers=self.headers)

            hex_rgb_str = json.loads(r.text).get(
                property_name, 'None') if self.device_type == 'native' else json.loads(r.text)

            print(list(int(hex_rgb_str.lstrip('#')[
                i:i+2], 16) for i in (0, 2, 4)))

            return list(int(hex_rgb_str.lstrip('#')[
                i:i+2], 16) for i in (0, 2, 4))

    def ColorMode_I(self):
        property_name = self._get_property_name('ColorMode-I')

        if property_name != None:
            r = requests.get(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), headers=self.headers)

            return json.loads(r.text).get(
                property_name, 'None') if self.device_type == 'native' else json.loads(r.text)

    def ColorTemp_I(self):
        property_name = self._get_property_name('ColorTemp-I')

        if property_name != None:
            r = requests.get(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), headers=self.headers)

            return json.loads(r.text).get(
                property_name, 'None') if self.device_type == 'native' else json.loads(r.text)

    def OnOff_I(self):
        property_name = self._get_property_name('OnOff-I')

        if property_name != None:
            r = requests.get(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), headers=self.headers)

            return json.loads(r.text).get(
                property_name, 'None') if self.device_type == 'native' else json.loads(r.text)

    def Brightness_O(self, data):
        property_name = self._get_property_name('Brightness-O')

        if property_name != None:
            payload = json.dumps({property_name: int(
                data[0])}) if self.device_type == 'native' else json.dumps(int(data[0]))
            requests.put(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), payload, headers=self.headers)

    def Color_O(self, data):
        property_name = self._get_property_name('Color-O')

        if property_name != None:
            hex_rgb_str = '#%02x%02x%02x'.format(data[0], data[1], data[2])
            payload = json.dumps(
                {property_name: hex_rgb_str}) if self.device_type == 'native' else json.dumps(hex_rgb_str)
            requests.put(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), payload, headers=self.headers)

    def ColorTemp_O(self, data):
        property_name = self._get_property_name('ColorTemp-O')

        if property_name != None:
            payload = json.dumps({property_name: int(
                data[0])}) if self.device_type == 'native' else json.dumps(int(data[0]))
            requests.put(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), payload, headers=self.headers)

    def OnOff_O(self, data):
        property_name = self._get_property_name('OnOff-O')

        if property_name != None:
            payload = json.dumps({property_name: bool(
                data[0])}) if self.device_type == 'native' else json.dumps(bool(data[0]))
            requests.put(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), payload, headers=self.headers)

    def set_webthing_brightness(self, data: list):
        if self.gateway_token != None:
            payload = json.dumps({'brightness': int(float(data[0]) * 100)})
            requests.put(
                '{0}/properties/brightness'.format(self.webthing_url), payload)
        else:
            payload = json.dumps({'brightness': int(float(data[0]) * 100)})
            requests.put(
                '{0}/properties/brightness'.format(self.webthing_url), payload)

    def set_webthing_on(self, data: list):
        if self.gateway_token != None:
            payload = json.dumps({'on': bool(data[0])})
            requests.put(
                '{0}/properties/on'.format(self.webthing_url), payload)

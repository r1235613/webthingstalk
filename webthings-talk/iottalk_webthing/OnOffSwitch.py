from email import header
import json
import requests
from iottalkpy.dai import DAI
from iottalkpy.dan import DeviceFeature


class OnOffSwitch(DAI):
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
            "wtOnOff-I": DeviceFeature(
                "wtOnOff-I",
                "idf",
                [None],
                self.OnOff_I,
                None
            ),
            "wtOnOff-O": DeviceFeature(
                "wtOnOff-O",
                "odf",
                [None],
                None,
                self.OnOff_O
            ),
        }

        super().__init__(
            api_url=api_url,
            device_model="WT_OnOffSwitch",
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

    def OnOff_I(self):
        property_name = self._get_property_name('wtOnOff-I')

        if property_name != None:
            r = requests.get(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), headers=self.headers)

            return json.loads(r.text).get(
                property_name, 'None') if self.device_type == 'native' else json.loads(r.text)

    def OnOff_O(self, data):
        property_name = self._get_property_name('wtOnOff-O')

        if property_name != None:
            r = requests.get(
                '{0}/properties/{1}'.format(self.webthing_url, property_name), headers=self.headers)

            status = json.loads(r.text)
            if status == bool(data[0]):
                return

            payload = json.dumps({property_name: bool(
                data[0])}) if self.device_type == 'native' else bool(data[0])
            requests.put(
                '{0}/properties/{1}'.format(self.webthing_url, property_name),
                json=payload if self.device_type == 'gateway' else None,
                data=payload if self.device_type == 'native' else None,
                headers=self.headers
            )

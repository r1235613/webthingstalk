import json
import requests
from iottalkpy.dai import DAI
from iottalkpy.dan import DeviceFeature


class Light(DAI):
    def __init__(
        self,
        api_url,
        webthing_url,
        device_addr=None,
        device_name=None,
        username=None,
        register_callback=None,
        on_register=None,
        on_deregister=None,
        on_connect=None,
        on_disconnect=None,
        push_interval=1,
        interval=1,
    ):
        device_features = {
            "Brightness-I": DeviceFeature(
                "Brightness-I",
                "idf",
                [None],
                self.get_webthing_brightness,
                None
            ),
            "OnOff-I": DeviceFeature(
                "OnOff-I",
                "idf",
                [None],
                self.get_webthing_on,
                None
            ),
            "Brightness-O": DeviceFeature(
                "Brightness-O",
                "odf",
                [None],
                None,
                self.set_webthing_brightness
            ),
            "OnOff-O": DeviceFeature(
                "OnOff-O",
                "odf",
                [None],
                None,
                self.set_webthing_on
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

        self.webthing_url = webthing_url

    def set_webthing_brightness(self, data: list):
        payload = json.dumps({'brightness': int(float(data[0]) * 100)})
        requests.put(
            '{0}/properties/brightness'.format(self.webthing_url), payload)

    def set_webthing_on(self, data: list):
        payload = json.dumps({'on': bool(data[0])})
        requests.put(
            '{0}/properties/on'.format(self.webthing_url), payload)

    def get_webthing_brightness(self):
        r = requests.get('{0}/properties/brightness'.format(self.webthing_url))
        return json.loads(r.text)['brightness']

    def get_webthing_on(self):
        r = requests.get('{0}/properties/on'.format(self.webthing_url))
        return json.loads(r.text)['on']

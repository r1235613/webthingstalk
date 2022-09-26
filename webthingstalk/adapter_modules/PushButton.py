from .BaseDevice import BaseDevice


class PushButton(BaseDevice):
    def __init__(
        self,
        iottalk_url,
        webthing_url,
        property_table,
        gateway_token=None,
        device_name=None,
    ):
        super().__init__(iottalk_url, webthing_url,
                         property_table, gateway_token, device_name)

    def _gen_code(self):
        pushed1_property_name = self._get_property_name('wtPushed-I1')
        pushed2_property_name = self._get_property_name('wtPushed-I2')
        pushed3_property_name = self._get_property_name('wtPushed-I3')
        pushed4_property_name = self._get_property_name('wtPushed-I4')

        with open('adapter_modules/PushButton.txt') as f:
            code_template = f.read()

        self.code = code_template.format(
            api_url=self.api_url,
            device_name=self.device_name,
            webthing_url=self.webthing_url,
            headers=self.headers,
            pushed1_property_name=pushed1_property_name,
            pushed2_property_name=pushed2_property_name,
            pushed3_property_name=pushed3_property_name,
            pushed4_property_name=pushed4_property_name
        )

from .BaseDevice import BaseDevice


class ColorControl(BaseDevice):
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
        color_property_name = self._get_property_name('wtColor-I')
        color_mode_property_name = self._get_property_name('wtColorMode-I')
        color_temperature_name = self._get_property_name(
            'wtColorTemperature-I')

        with open('adapter_modules/ColorControl.txt') as f:
            code_template = f.read()

        self.code = code_template.format(
            api_url=self.api_url,
            device_name=self.device_name,
            webthing_url=self.webthing_url,
            headers=self.headers,
            color_property_name=color_property_name,
            color_mode_property_name=color_mode_property_name,
            color_temperature_name=color_temperature_name
        )

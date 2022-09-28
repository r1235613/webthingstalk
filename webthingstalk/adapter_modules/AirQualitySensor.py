import os
from django.conf import settings
from .BaseDevice import BaseDevice


class AirQualitySensor(BaseDevice):
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
        concentration_property_name = self._get_property_name('wtConcentration-I')
        density_property_name = self._get_property_name('wtDensity-I')

        with open(os.path.join(settings.BASE_DIR, 'adapter_modules/AirQualitySensor.txt')) as f:
            code_template = f.read()

        self.code = code_template.format(
            api_url=self.api_url,
            device_name=self.device_name,
            webthing_url=self.webthing_url,
            headers=self.headers,
            concentration_property_name=concentration_property_name,
            density_property_name=density_property_name
        )

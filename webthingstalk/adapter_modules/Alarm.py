import os
from django.conf import settings
from .BaseDevice import BaseDevice


class Alarm(BaseDevice):
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
        alarm_property_name = self._get_property_name('wtAlarm-I')

        with open(os.path.join(settings.BASE_DIR, 'adapter_modules/Alarm.txt')) as f:
            code_template = f.read()

        self.code = code_template.format(
            api_url=self.api_url,
            device_name=self.device_name,
            webthing_url=self.webthing_url,
            headers=self.headers,
            alarm_property_name=alarm_property_name
        )

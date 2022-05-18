import json
import requests

class OnOffSwitch():
    def __init__(
        self,
        api_url,
        webthing_url,
        property_table,
        gateway_token=None,
        device_name=None,
    ):
        self.api_url = api_url
        self.webthing_url = webthing_url.rstrip('/')
        self.property_table = property_table
        self.gateway_token = gateway_token
        self.device_name = device_name
        
        self._gen_code()

    def create_device(self):
        r = requests.post('http://192.168.52.140/autogen/create_device/', json={'code': self.code})

        token = json.loads(r.text).get('token', 'None')
        return token

    def _get_property_name(self, df):
        for key, value in self.property_table.items():
            if value['idf'] == df or value['odf'] == df:
                return key

    def _gen_code(self):
        device_type = 'gateway' if self.gateway_token != None else 'native'
        headers = {'Accept': 'application/json'} if device_type == 'native' else {
            'Authorization': 'Bearer {gateway_token}'.format(gateway_token=self.gateway_token), 'Accept': 'application/json'}

        on_off_i_property_name = self._get_property_name('wtOnOff-I')
        on_off_i_return_code = "json.loads(r.text).get('{on_off_i_property_name}', 'None')".format(on_off_i_property_name=on_off_i_property_name) if device_type == 'native' else "json.loads(r.text)"

        on_off_o_property_name = self._get_property_name('wtOnOff-O')
        payload = 'json.dumps({{"{on_off_o_property_name}": bool(data[0])}})'.format(
            on_off_o_property_name=on_off_o_property_name) if device_type == 'native' else 'bool(data[0])'
        on_off_o_request_code = "requests.put('{webthing_url}/properties/{on_off_o_property_name}', json={json_payload}, data={data_payload}, headers={headers})".format(
            webthing_url=self.webthing_url,
            on_off_o_property_name=on_off_o_property_name,
            json_payload=payload if device_type == 'gateway' else None,
            data_payload=payload if device_type == 'native' else None,
            headers=headers
        )

        self.code = """
import json
import requests

api_url = '{api_url}'
device_name = '{device_name}'
device_model = 'WT_OnOffSwitch'

idf_list = ['wtOnOff-I']
odf_list = ['wtOnOff-O']

def wtOnOff_I():
    r = requests.get('{webthing_url}/properties/{on_off_i_property_name}', headers={headers})
    return {on_off_i_return_code}

def wtOnOff_O(data):
    r = requests.get('{webthing_url}/properties/{on_off_o_property_name}', headers={headers})

    status = json.loads(r.text)
    if status == bool(data[0]):
        return

    {on_off_o_request_code}""".format(
            api_url=self.api_url,
            device_name=self.device_name,
            webthing_url=self.webthing_url,
            on_off_i_property_name=on_off_i_property_name,
            headers=headers,
            on_off_i_return_code=on_off_i_return_code,
            on_off_o_property_name=on_off_o_property_name,
            on_off_o_request_code=on_off_o_request_code)


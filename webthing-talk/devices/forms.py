from django import forms

DEVICE_TYPE_CHOICES = [('0', 'Native WebThing Device'),
                       ('1', 'WebThings Gateway Device')]


class DeviceForm(forms.Form):
    device_type = forms.ChoiceField(label='device_type', choices=DEVICE_TYPE_CHOICES,
                                    widget=forms.Select(attrs={'onChange': 'showGatewayBlock()', 'aria-label': 'Device Type'}))
    gateway_token = forms.CharField(label='gateway_token',
                                    widget=forms.TextInput(attrs={'size': 54}))
    device_url = forms.CharField(label='device_url',
                                 widget=forms.TextInput(attrs={'placeholder': 'http://192.168.0.100:8888', 'size': 54}))
    gateway_device = forms.ChoiceField(label='gateway_device', widget=forms.Select(
        attrs={'aria-label': 'Gateway Device'}))
    device_name = forms.CharField(label='device_name', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Light1, OnOffSwith2 ...', 'size': 64}))


class DeviceDeleteForm(forms.Form):
    key = forms.CharField()

from django import forms

TYPE_CHOICES = [('native', 'Native WebThing Device'),
                ('gateway', 'WebThings Gateway Device')]


class MyCustomChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass


class DeviceForm(forms.Form):
    type = forms.ChoiceField(label='type', choices=TYPE_CHOICES,
                             widget=forms.Select(attrs={'onChange': 'showGatewayBlock()', 'aria-label': 'Device Type'}))
    token = forms.CharField(label='token', required=False,
                            widget=forms.TextInput(attrs={'size': 47, 'aria-label': 'Gateway Token'}))
    url = forms.CharField(label='url',
                          widget=forms.TextInput(attrs={'placeholder': 'http://192.168.0.100:8888', 'size': 47, 'aria-label': 'Url'}))
    select_device = MyCustomChoiceField(label='select_device', choices=[], required=False, widget=forms.Select(
        attrs={'aria-label': 'Gateway Device'}))
    name = forms.CharField(label='name', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Light1, OnOffSwith2 ...', 'size': 64, 'aria-label': 'Device Device'}))
    claim = forms.BooleanField(label='claim', required=False,
                               widget=forms.CheckboxInput(attrs={'aria-label': 'Claim'}))

    def __init__(self, *args, **kwargs):
        device_choices = kwargs.pop('device_choices', [])
        name_required = kwargs.pop('name_required', [])
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['select_device'].choices = device_choices
        self.fields['name'].required = name_required


class DeviceDeleteForm(forms.Form):
    key = forms.CharField()

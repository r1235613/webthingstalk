from django import forms
from django.utils.html import format_html
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe


from .device import device_table


DEVICE_MODELS_CHOICES = [(x['device_model'], x['device_model'])
                         for _, x in device_table.items()]

DEVICE_BASE_CHOICES = [('gateway', 'Gateway Base'), ('native', 'Native Base')]


class MyCustomChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass


class CustomSelect(forms.Select):
    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        if option.get('value') == '':
            option['attrs']['disabled'] = True

        return option


class DeviceForm(forms.Form):
    device_model = forms.ChoiceField(label='device_model', choices=DEVICE_MODELS_CHOICES, widget=forms.Select(
        attrs={'aria-label': 'Device Model'}))
    device_base = forms.ChoiceField(label='device_base', choices=DEVICE_BASE_CHOICES, widget=forms.Select(
        attrs={'onChange': 'form.action="/device-base"; form.submit();', 'aria-label': 'Device Base'}))
    native_url_list = MyCustomChoiceField(label='native_url_list', choices=[], widget=CustomSelect(
        attrs={'aria-label': 'Device URL List'}))
    native_device_url = forms.CharField(label='native_device_url', required=False,
                                        widget=forms.TextInput(attrs={'placeholder': 'http://192.168.0.100:8888', 'aria-label': 'Native Device Url', 'style': 'width: 100%;'}))
    # token = forms.CharField(label='token', required=False,
    #                         widget=forms.TextInput(attrs={'size': 47, 'aria-label': 'Gateway Token'}))
    # device_url_list = MyCustomChoiceField(label='device_url_list', choices=[], widget=forms.Select(
    #     attrs={'aria-label': 'Device URL List'}))
    # select_gateway_device = MyCustomChoiceField(label='select_gateway_device', choices=[], required=False, widget=forms.Select(
    #     attrs={'aria-label': 'Gateway Device'}))

    def __init__(self, *args, **kwargs):
        native_url_choices = kwargs.pop('native_url_choices', [])
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['native_url_list'].choices = native_url_choices


class DeviceDeleteForm(forms.Form):
    device_name = forms.CharField()

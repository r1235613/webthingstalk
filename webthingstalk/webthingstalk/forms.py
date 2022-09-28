from django import forms
from django.utils.html import format_html
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe


from .device import device_table


DEVICE_MODELS_CHOICES = [(x, 'WT_{0}'.format(x)) for x in device_table.keys()]

DEVICE_BASE_CHOICES = [('', 'select...'), ('native',
                                           'Direct (Native Device)'), ('gateway', 'Indirect (Via Gateway)')]

GATEWAY_CHOICES = [('default', 'Default Gateway'),
                   ('custom', 'Custom Gateway')]


class CustomChoiceField(forms.ChoiceField):
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
    device_base = forms.ChoiceField(label='device_base', choices=DEVICE_BASE_CHOICES, widget=CustomSelect(
        attrs={'onChange': 'form.action="/device-base"; form.submit();', 'aria-label': 'Device Base'}))

    native_url_list = CustomChoiceField(label='native_url_list', choices=[], widget=CustomSelect(
        attrs={'aria-label': 'Device URL List'}))
    native_device_url = forms.CharField(label='native_device_url', required=False,
                                        widget=forms.TextInput(attrs={'placeholder': 'http://192.168.0.100:8888', 'aria-label': 'Native Device Url', 'style': 'width: 100%;'}))

    gateway_type = CustomChoiceField(label='gateway_type', choices=GATEWAY_CHOICES, widget=CustomSelect(
        attrs={'onChange': 'form.action="/gateway-type"; form.submit();', 'aria-label': 'Gateway Type'}))
    gateway_url_list = CustomChoiceField(label='gateway_url_list', choices=[], widget=CustomSelect(
        attrs={'aria-label': 'Gateway URL List'}))
    custom_gateway_url = forms.CharField(label='custom_gateway_url', required=False,
                                         widget=forms.TextInput(attrs={'placeholder': 'http://192.168.0.100:8080', 'aria-label': 'Custom Gateway Url', 'style': 'width: 100%;'}))
    custom_gateway_username = forms.CharField(label='custom_gateway_username', required=False,
                                              widget=forms.TextInput(attrs={'placeholder': 'Username', 'aria-label': 'Custom Gateway Username', 'style': 'width: 100%;'}))
    custom_gateway_password = forms.CharField(label='custom_gateway_password', required=False,
                                              widget=forms.PasswordInput(
                                                  attrs={'placeholder': 'Password', 'aria-label': 'Custom Gateway Password', 'style': 'width: 100%;'}))
    gateway_device_list = CustomChoiceField(label='gateway_device_list', choices=[
    ], required=False, widget=CustomSelect(attrs={'onChange': 'form.action="/connect-gateway-device"; form.submit();', 'aria-label': 'Gateway Device List'}))

    def __init__(self, *args, **kwargs):
        native_url_choices = kwargs.pop('native_url_choices', [])
        gateway_url_choices = kwargs.pop('gateway_url_choices', [])
        gateway_device_choices = kwargs.pop('gateway_device_choices', [])
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['native_url_list'].choices = native_url_choices
        self.fields['gateway_url_list'].choices = gateway_url_choices
        self.fields['gateway_device_list'].choices = gateway_device_choices


class DeviceDeleteForm(forms.Form):
    device_name = forms.CharField()

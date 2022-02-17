from django import forms

class DeviceCheckForm(forms.Form):
    url = forms.CharField()

class DeviceAddForm(forms.Form):
    url = forms.CharField()
    name = forms.CharField()

class DeviceDeleteForm(forms.Form):
    key = forms.CharField()
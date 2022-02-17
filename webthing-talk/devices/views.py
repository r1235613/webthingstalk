from django.shortcuts import render

from django.http import HttpResponse, request
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.contrib import messages


from xtalk_template.views import IndexView

import iottalk_webthing

from .forms import DeviceForm, DeviceDeleteForm


import requests

device_table = {'Light': {'properties': ['OnOffProperty', 'BrightnessProperty',
                                         'ColorModeProperty', 'ColorProperty', 'ColorTemperatureProperty'], 'module': iottalk_webthing.Light},
                'OnOffSwitch': {'properties': ['OnOffProperty', ], 'module': iottalk_webthing.OnOffSwitch}}
user_devices = {}


class IndexView(IndexView):
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if self.request.user.username not in user_devices.keys():
            user_devices[self.request.user.username] = {}

        context['temp_device'] = self.request.session.get(
            'temp_device', {'claim': False})
        context['user_devices'] = user_devices[self.request.user.username]

        print(self.request.session.get('temp_device', {}))
        print(user_devices)

        context['form'] = DeviceForm

        return context


class DeviceCheckView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def __get_device_info(self, url):
        r = requests.get(url, timeout=5)
        data = r.json()

        device_type = data['selectedCapability'][0]

        property_types = [data['properties'][x]['@type']
                          for x in data['properties'].keys()]

        property_use = {
            x: x in property_types for x in device_table[device_type]['properties']}

        return device_type, property_use

    def form_valid(self, form):
        data = {}
        data['url'] = form.data['url']
        data['name'] = form.data['name']
        data['claim'] = bool(form.data.get('claim', False))
        try:
            data['device_type'], data['property_use'] = self.__get_device_info(
                data['url'])

            data['checked'] = True
            data['device_connted'] = True
        except:
            data['checked'] = True
            data['device_connted'] = False

        self.request.session['temp_device'] = data

        return super().form_valid(form)


class DeviceAddView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def __check_device_name_existed(self, name):
        return name in user_devices[self.request.user.username].keys()

    def form_valid(self, form):
        if self.__check_device_name_existed(form.data['name']):
            messages.error(
                self.request, 'Device name {0} already exists!'.format(form.data['name']))
            return super().form_valid(form)

        temp_device = self.request.session['temp_device']

        temp_device['name'] = form.data['name']
        temp_device['claim'] = bool(form.data.get('claim', False))

        obj = device_table[temp_device['device_type']]['module']
        print(
            "QQ", self.request.user.username if temp_device['claim'] else None)
        device = obj('http://192.168.52.140/csm',
                     temp_device['url'], device_name=temp_device['name'], username=self.request.user.username if temp_device['claim'] else None)

        device.start()

        user_devices[self.request.user.username][temp_device['name']] = {
            'device_type': temp_device['device_type'],
            'properties': [x[0] for x in temp_device['property_use'].items() if x[1]],
            'device': device
        }

        self.request.session['temp_device'] = {}

        return super().form_valid(form)


class DeviceDeleteView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceDeleteForm
    success_url = '/'

    def form_valid(self, form):
        device = user_devices[self.request.user.username][form.data['key']]['device']
        device.terminate()
        device.join()

        del user_devices[self.request.user.username][form.data['key']]

        return super().form_valid(form)

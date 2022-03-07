from operator import mod
from django.shortcuts import render

from django.http import HttpResponse, request
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.contrib import messages


from xtalk_template.views import IndexView

from .forms import DeviceForm, DeviceDeleteForm

from .models import User, Device
from .device import device_handler


user_temp_device = {}


class IndexView(IndexView):
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if self.request.user.username == '':
            return context
        user_id = User.objects.get(username=self.request.user.username).id

        context['temp_device'] = device_handler.get_temp_device(user_id)
        context['user_devices'] = Device.objects.filter(
            user_id=user_id).all()

        print('temp_device', context['temp_device'])

        context['form'] = DeviceForm(
            device_choices=[
                (name, name) for name, _ in context['temp_device'].device_list.items()],
            name_required=context['temp_device'].checked,
            initial={
                'type': context['temp_device'].type,
                'url': context['temp_device'].url,
                'token': context['temp_device'].token,
                'select_device': context['temp_device'].select_device,
                'name': context['temp_device'].name,
                'claim': context['temp_device'].claim
            })

        return context


class NativeDeviceCheckView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        url = form.data.get('url', '')
        name = form.data.get('name', '')
        claim = form.data.get('claim', '')

        device_handler.delete_temp_device(user_id)
        device_handler.create_temp_device(
            user_id, 'native', url, '', name, claim)

        try:
            device_handler.temp_device_get_info(user_id)
        except:
            messages.error(
                self.request, 'Connection failed, please check Device Type and URL.')
            return super().form_valid(form)

        return super().form_valid(form)


class ConnectGatewayView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        type = form.data.get('type', 'native')
        url = form.data.get('url', '')
        token = form.data.get('token', '')
        name = form.data.get('name', '')
        claim = form.data.get('claim', '')

        device_handler.delete_temp_device(user_id)
        device_handler.create_temp_device(
            user_id, 'gateway', url, token, name, claim)

        try:
            device_handler.temp_device_get_gateway_device(user_id)
        except:
            messages.error(
                self.request, 'Connection failed, please check Device Type, Gateway URL and Token.')
            return super().form_valid(form)

        return super().form_valid(form)


class GatewayDeviceCheckView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        name = form.data.get('name', '')
        claim = form.data.get('claim', '')
        select_device = form.data.get('select_device', '')

        device_handler.update_temp_device(user_id, name, claim, select_device)
        device_handler.temp_device_get_info(user_id)

        return super().form_valid(form)


class DeviceAddView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id
        temp_dev = device_handler.get_temp_device(user_id)

        name = form.data.get('name', '')
        claim = form.data.get('claim', '')
        model = temp_dev.model

        if device_handler.check_device_name_existed(user_id, name):
            messages.error(
                self.request, 'Device name {0} already exists!'.format(form.data.get('name', '')))
            return super().form_valid(form)

        device_handler.update_temp_device(user_id, name, claim, model)
        device_handler.create_device(user_id)

        return super().form_valid(form)


class DeviceDeleteView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceDeleteForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id
        name = form.data.get('key', '')

        device_handler.delete_device(user_id, name)

        return super().form_valid(form)

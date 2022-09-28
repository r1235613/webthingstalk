from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.shortcuts import render

from xtalk_template.views import TEMPLATE_DIRECTORY_PREFIX, oauth2_client

from .forms import DeviceForm, DeviceDeleteForm
from .models import Device, DeviceUrl, GatewayUrl

from development.models import User

from .device import device_handler
from .gateway import gateway_hander


class IndexView(TemplateView):
    template_name = '{}/index.html'.format(TEMPLATE_DIRECTORY_PREFIX)

    def _gen_form(self, user_id):
        temp_device = device_handler.get_temp_device(user_id)

        native_urls = [(x['url'], x['url'])
                       for x in DeviceUrl.objects.filter(user_id=user_id).values()]
        gateway_urls = [(x['url'], x['url'])
                        for x in GatewayUrl.objects.filter(user_id=user_id).values()]

        return DeviceForm(
            native_url_choices=[
                ('', 'select...'), ('add', 'Add new device'), *native_urls],
            gateway_url_choices=[
                ('', 'select...'), ('add', 'Add new gateway'), *gateway_urls],
            gateway_device_choices=[
                ('', 'select...'), *[(name, name)
                                     for name, _ in temp_device.device_list.items()]
            ],
            initial={
                'device_model': temp_device.device_model,
                'device_base': temp_device.device_base,
                'native_url_list': temp_device.device_url,
                'gateway_type': temp_device.gateway_type,
                'gateway_url_list': temp_device.gateway_url,
                'gateway_device_list': temp_device.device_name
            }
        )

    http_method_names = [
        'get',
    ]

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return oauth2_client.iottalk.authorize_redirect(
                request,
                redirect_uri=settings.XTALK_OAUTH2_REDIRECT_URI
            )

        user_id = User.objects.get(username=request.user.username).id

        return render(
            request,
            '{}/index.html'.format(TEMPLATE_DIRECTORY_PREFIX),
            {
                'temp_device': device_handler.get_temp_device(user_id),
                'user_devices': Device.objects.filter(user_id=user_id).all(),
                'default_gateway_username': settings.DEFAULT_GATEWAY_USERNAME,
                'default_gateway_password': settings.DEFAULT_GATEWAY_PASSWORD,
                'form': self._gen_form(user_id)
            }
        )


class DeviceBaseView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        device_model = form.data.get('device_model', '')
        device_base = form.data.get('device_base', 'gateway')

        device_handler.delete_temp_device(user_id)

        if device_base == 'gateway':
            device_handler.create_temp_device(
                user_id, device_model, device_base, gateway_type='default')
            device_handler.temp_device_get_gateway_device(user_id)  # 先幫 Default Gateway 抓一次 DeviceList
        else:
            device_handler.create_temp_device(
                user_id, device_model, device_base)

        return super().form_valid(form)


class ConnectNativeDeviceView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def _check_device_url_exist(self,  device_url):
        return len(DeviceUrl.objects.filter(url=device_url, user_id=self.user_id)) >= 1

    def form_valid(self, form):
        self.user_id = User.objects.get(username=self.request.user.username).id

        device_model = form.data.get('device_model', '')
        device_base = form.data.get('device_base', 'native')

        if form.data['native_url_list'] == 'add':
            device_url = form.data['native_device_url'].rstrip('/')
        else:
            device_url = form.data['native_url_list']

        device_handler.delete_temp_device(self.user_id)
        device_handler.create_temp_device(
            self.user_id, device_model, device_base, device_url)

        try:
            device_handler.temp_device_get_info(self.user_id)
        except RuntimeError:
            messages.error(
                self.request, 'Connection failed, please check Device URL.')
            return super().form_valid(form)
        except ValueError:
            temp_device_model = device_handler.get_temp_device(
                self.user_id).device_model
            messages.warning(
                self.request, 'Device Model mismatch, the device is WT_{0}.'.format(temp_device_model))

        if form.data['native_url_list'] == 'add' and not self._check_device_url_exist(device_url):
            DeviceUrl.objects.create(
                url=device_url,
                user_id=self.user_id,
                create_time=datetime.now()
            )

        return super().form_valid(form)


class DeleteNativeDeviceUrlView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        device_url = form.data.get('native_url_list', '')
        DeviceUrl.objects.filter(url=device_url, user_id=user_id).delete()

        device_handler.delete_temp_device(user_id)

        return super().form_valid(form)


class GatewayTypeView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        device_model = form.data.get('device_model', '')
        device_base = form.data.get('device_base', 'gateway')
        gateway_type = form.data.get('gateway_type', 'default')

        gateway_hander.delete_custom_gateway(user_id)
        device_handler.delete_temp_device(user_id)

        device_handler.create_temp_device(
            user_id, device_model, device_base, gateway_type=gateway_type)

        if gateway_type == 'default':
            device_handler.temp_device_get_gateway_device(user_id)

        return super().form_valid(form)


class ConnectGatewayView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def _check_gateway_url_exist(self,  gateway_url):
        return len(GatewayUrl.objects.filter(url=gateway_url, user_id=self.user_id)) >= 1

    def form_valid(self, form):
        self.user_id = User.objects.get(username=self.request.user.username).id

        device_model = form.data.get('device_model', '')
        device_base = form.data.get('device_base', 'gateway')
        gateway_type = form.data.get('gateway_type', 'default')
        gateway_username = form.data.get('custom_gateway_username', '')
        gateway_password = form.data.get('custom_gateway_password', '')

        if form.data['gateway_url_list'] == 'add':
            gateway_url = form.data.get('custom_gateway_url', '').rstrip('/')
        else:
            gateway_url = form.data['gateway_url_list']

        try:
            if gateway_type == 'custom' and form.data['gateway_url_list'] == 'add':
                gateway_hander.create_custom_gateway(
                    self.user_id, gateway_url, gateway_username, gateway_password)
            elif gateway_type == 'custom' and form.data['gateway_url_list'] != 'add':
                user_token = GatewayUrl.objects.filter(
                    url=gateway_url).first().token
                gateway_hander.create_custom_gateway_by_token(
                    self.user_id, gateway_url, user_token)
        except:
            device_handler.delete_temp_device(self.user_id)
            device_handler.create_temp_device(
                self.user_id, device_model, device_base, gateway_type=gateway_type)
            messages.error(
                self.request, 'Connection failed, please check Gateway URL, Username and Password.')
            return super().form_valid(form)

        device_handler.delete_temp_device(self.user_id)
        device_handler.create_temp_device(
            self.user_id, device_model, device_base, gateway_type=gateway_type)

        try:
            device_handler.temp_device_get_gateway_device(self.user_id)
        except:
            messages.error(
                self.request, 'Connection failed, please check Device Type, Gateway URL and Token.')
            return super().form_valid(form)

        if form.data['gateway_url_list'] == 'add' and not self._check_gateway_url_exist(gateway_url):
            GatewayUrl.objects.create(
                url=gateway_url,
                user_id=self.user_id,
                token=gateway_hander.get_custom_gateway(
                    self.user_id).user_token,
                create_time=datetime.now()
            )

        return super().form_valid(form)


class DeleteGatewayUrlView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        gateway_url = form.data.get('gateway_url_list', '')
        GatewayUrl.objects.filter(url=gateway_url, user_id=user_id).delete()

        device_handler.delete_temp_device(user_id)

        return super().form_valid(form)


class ConnectGatewayDeviceView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        gateway_device = form.data.get('gateway_device_list', '')
        device_handler.update_temp_device(user_id, gateway_device)

        try:
            device_handler.temp_device_get_gateway_device(user_id)
            device_handler.temp_device_get_info(user_id)
        except ValueError:
            temp_device_model = device_handler.get_temp_device(
                user_id).device_model
            messages.warning(
                self.request, 'Device Model mismatch, the device is WT_{0}.'.format(temp_device_model))

        return super().form_valid(form)


class AddDeviceView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def _check_device_exist(self, device_name):
        return len(Device.objects.filter(device_name=device_name, user_id=self.user_id)) >= 1

    def form_valid(self, form):
        self.user_id = User.objects.get(username=self.request.user.username).id

        temp_device_name = device_handler.get_temp_device(
            self.user_id).device_name

        if self._check_device_exist(temp_device_name):
            messages.error(
                self.request, 'Device {0} already exists!'.format(temp_device_name))
        else:
            device_handler.create_device(self.user_id)

        return super().form_valid(form)


class DeleteDeviceView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceDeleteForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id
        device_name = form.data.get('device_name', '')

        device_handler.delete_device(user_id, device_name)

        return super().form_valid(form)

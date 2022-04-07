from datetime import datetime

from django.contrib import messages
from django.views.generic.edit import FormView

from xtalk_template.views import IndexView

from .forms import DeviceForm, DeviceDeleteForm
from .models import User, Device, DeviceUrl
from .device import device_handler


user_temp_device = {}


class IndexView(IndexView):
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if self.request.user.username == '':
            return context

        user_id = User.objects.get(username=self.request.user.username).id

        context['temp_device'] = device_handler.get_temp_device(user_id)
        context['user_devices'] = Device.objects.filter(user_id=user_id).all()

        native_urls = [(x['url'], x['url'])
                       for x in DeviceUrl.objects.filter(user_id=user_id).values()]

        context['form'] = DeviceForm(
            native_url_choices=[
                ('', 'select...'), ('add', 'Add new device'), *native_urls],
            # device_choices=[
            #     (name, name) for name, _ in context['temp_device'].device_list.items()],
            initial={
                'device_model': context['temp_device'].device_model,
                'device_base': context['temp_device'].device_base,
                'native_url_list': context['temp_device'].device_url,
            }
        )

        return context


class DeviceBaseView(FormView):
    template_name = 'xtalk/index.html'
    form_class = DeviceForm
    success_url = '/'

    def form_valid(self, form):
        user_id = User.objects.get(username=self.request.user.username).id

        device_model = form.data.get('device_model', '')
        device_base = form.data.get('device_base', 'gateway')

        device_handler.delete_temp_device(user_id)
        device_handler.create_temp_device(user_id, device_model, device_base)

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
        device_base = form.data.get('device_base', 'gateway')

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
            device_handler.delete_temp_device(self.user_id)
            device_handler.create_temp_device(
                self.user_id, device_model, device_base)
            messages.error(
                self.request, 'Connection failed, please check Device URL.')
            return super().form_valid(form)
        except ValueError:
            temp_device_model = device_handler.get_temp_device(
                self.user_id).device_model
            messages.warning(
                self.request, 'Device Model mismatch, the device is WT_{0}.'.format(temp_device_model))

        if form.data['native_url_list'] == 'add' and not self._check_device_url_exist(device_url):
            dev = DeviceUrl.objects.create(
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

        device_handler.delete_temp_device(user_id)
        device_handler.create_temp_device(
            user_id, 'gateway', url, token, name)

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
        select_device = form.data.get('select_device', '')

        device_handler.update_temp_device(user_id, name, select_device)
        device_handler.temp_device_get_info(user_id)

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

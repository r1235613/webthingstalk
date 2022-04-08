from django.urls import include, path

from xtalk_template.views import IndexView, AuthRedirectionView, AuthCallbackView, LogoutView
from . import views

app_name = 'xtalk_template'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('device-base', views.DeviceBaseView.as_view(),
         name='device_base_endpoint'),
    path('connect-native-device', views.ConnectNativeDeviceView.as_view(),
         name='native_device_connect_endpoint'),
    path('delete-native-device-url', views.DeleteNativeDeviceUrlView.as_view(),
         name='delete_native_device_url'),
    path('connect-gateway', views.ConnectGatewayView.as_view(),
         name='connect_gateway_endpoint'),
    path('connect-gateway-device', views.ConnectGatewayDeviceView.as_view(),
         name='connect_gateway_device'),
    path('add', views.AddDeviceView.as_view(), name='device_add_endpoint'),
    path('delete', views.DeleteDeviceView.as_view(),
         name='device_delete_endpoint'),
    path('auth', AuthRedirectionView.as_view(), name='auth_redirect_endpoint'),
    path(
        'auth/callback',
        AuthCallbackView.as_view(),
        name='oauth2_redirect_endpoint'
    ),
    path('logout', LogoutView.as_view(), name='logout_endpoint')
]

from django.urls import include, path

from xtalk_template.views import IndexView, AuthRedirectionView, AuthCallbackView, LogoutView
from . import views

app_name = 'xtalk_template'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('check-native-device', views.NativeDeviceCheckView.as_view(),
         name='native_device_check_endpoint'),
    path('connect-gateway', views.ConnectGatewayView.as_view(),
         name='connect_gateway_endpoint'),
    path('check-gateway-device', views.GatewayDeviceCheckView.as_view(),
         name='gateway_device_check_endpoint'),
    path('add', views.DeviceAddView.as_view(), name='device_add_endpoint'),
    path('delete', views.DeviceDeleteView.as_view(),
         name='device_delete_endpoint'),
    path('auth', AuthRedirectionView.as_view(), name='auth_redirect_endpoint'),
    path(
        'auth/callback',
        AuthCallbackView.as_view(),
        name='oauth2_redirect_endpoint'
    ),
    path('logout', LogoutView.as_view(), name='logout_endpoint'),
]

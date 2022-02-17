from django.urls import include, path

from xtalk_template.views import IndexView, AuthRedirectionView, AuthCallbackView, LogoutView
from . import views

app_name = 'xtalk_template'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('check', views.DeviceCheckView.as_view(), name='device_check_endpost'),
    path('add', views.DeviceAddView.as_view(), name='device_add_endpost'),
    path('delete', views.DeviceDeleteView.as_view(),
         name='device_delete_endpost'),
    path('auth', AuthRedirectionView.as_view(), name='auth_redirect_endpoint'),
    path(
        'auth/callback',
        AuthCallbackView.as_view(),
        name='oauth2_redirect_endpoint'
    ),
    path('logout', LogoutView.as_view(), name='logout_endpoint'),
]

from django.urls import include, path

from xtalk_template.views import IndexView, AuthRedirectionView, AuthCallbackView, LogoutView
from . import views

app_name = 'xtalk_template'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('auth', AuthRedirectionView.as_view(), name='auth_redirect_endpoint'),
    path(
        'auth/callback',
        AuthCallbackView.as_view(),
        name='oauth2_redirect_endpoint'
    ),
    path('logout', LogoutView.as_view(), name='logout_endpoint'),
]

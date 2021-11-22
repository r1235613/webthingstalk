from django.urls import include, path

from . import views

urlpatterns = [
    path('', include('xtalk_template.urls', namespace='xtalk_template')),
]

from django.urls import path, include

from . import views

urlpatterns = [
    path('', include('xtalk_template.urls', namespace='xtalk_template')),
]

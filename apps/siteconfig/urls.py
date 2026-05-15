from django.urls import path
from . import views

app_name = 'siteconfig'

urlpatterns = [
    path('', views.config_view, name='config'),
]

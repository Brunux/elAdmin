from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('new/', views.payment_create, name='create'),
    path('submit/', views.payment_select, name='select'),
    path('<int:pk>/', views.payment_detail, name='detail'),
    path('<int:pk>/edit/', views.payment_edit, name='edit'),
    path('<int:pk>/confirm/', views.payment_confirm, name='confirm'),
]

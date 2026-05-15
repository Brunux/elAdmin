from django.urls import path
from . import views

app_name = 'units'

urlpatterns = [
    path('', views.apartment_list, name='list'),
    path('new/', views.apartment_create, name='create'),
    path('<int:pk>/', views.apartment_detail, name='detail'),
    path('<int:pk>/edit/', views.apartment_edit, name='edit'),
    path('<int:pk>/delete/', views.apartment_delete, name='delete'),
]

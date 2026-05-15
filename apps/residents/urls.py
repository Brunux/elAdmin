from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    path('', views.resident_list, name='list'),
    path('new/', views.resident_create, name='create'),
    path('<int:pk>/', views.resident_detail, name='detail'),
    path('<int:pk>/edit/', views.resident_edit, name='edit'),
    path('<int:pk>/delete/', views.resident_delete, name='delete'),
    path('api/apartments/', views.apartments_by_type, name='apartments_by_type'),
    path('invite/', views.invite_create, name='invite_create'),
    path('invite/sent/', views.invitation_list, name='invitation_list'),
    path('invite/<uuid:token>/', views.invite_accept, name='invite_accept'),
]

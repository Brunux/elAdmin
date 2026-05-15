from django.urls import path
from . import views

app_name = 'towers'

urlpatterns = [
    path('', views.tower_list, name='list'),
    path('new/', views.tower_create, name='create'),
    path('<int:pk>/', views.tower_detail, name='detail'),
    path('<int:pk>/edit/', views.tower_edit, name='edit'),
    path('<int:pk>/delete/', views.tower_delete, name='delete'),
]

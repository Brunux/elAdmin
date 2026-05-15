from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('', views.issue_list, name='list'),
    path('new/', views.issue_create, name='create'),
    path('<int:pk>/', views.issue_detail, name='detail'),
    path('<int:pk>/edit/', views.issue_edit, name='edit'),
    path('<int:pk>/delete/', views.issue_delete, name='delete'),
]

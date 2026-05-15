from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account, name='account'),
    path('manual/', views.manual_index, name='manual_index'),
    path('manual/administrador/', views.manual_admin, name='manual_admin'),
    path('manual/staff/', views.manual_staff, name='manual_staff'),
    path('manual/residente/', views.manual_resident, name='manual_resident'),
]

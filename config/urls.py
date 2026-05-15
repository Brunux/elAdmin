from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


class SuperuserAdminSite(AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


admin.site.__class__ = SuperuserAdminSite

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('residents/', include('apps.residents.urls', namespace='residents')),
    path('towers/', include('apps.towers.urls', namespace='towers')),
    path('apartments/', include('apps.units.urls', namespace='units')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('announcements/', include('apps.announcements.urls', namespace='announcements')),
    path('issues/', include('apps.issues.urls', namespace='issues')),
    path('config/', include('apps.siteconfig.urls', namespace='siteconfig')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

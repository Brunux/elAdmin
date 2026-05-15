from django.contrib import admin
from .models import Tower


@admin.register(Tower)
class TowerAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'floors', 'apartment_count']
    search_fields = ['name']

    @admin.display(description='Apartamentos')
    def apartment_count(self, obj):
        return obj.apartments.count()

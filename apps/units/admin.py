from django.contrib import admin
from .models import Apartment


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tower', 'floor', 'monthly_fee']
    list_filter = ['tower']
    search_fields = ['number', 'tower__name']

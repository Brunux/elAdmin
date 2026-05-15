from django.contrib import admin
from .models import Resident, Invitation


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'resident_type', 'status']
    list_filter = ['status', 'resident_type']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    raw_id_fields = ['user']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'resident_type', 'apartment', 'is_used', 'created_by', 'created_at']
    list_filter = ['is_used', 'resident_type']
    readonly_fields = ['token', 'created_at']

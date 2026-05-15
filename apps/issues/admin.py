from django.contrib import admin
from .models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'category', 'priority', 'status', 'apartment', 'reported_by', 'created_at']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']

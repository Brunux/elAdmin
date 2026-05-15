from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['apartment', 'resident', 'payment_type', 'period', 'amount', 'status', 'due_date']
    list_filter = ['status', 'payment_type']
    search_fields = ['apartment__number', 'period', 'reference']

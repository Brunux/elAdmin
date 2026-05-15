from django import forms
from apps.core.mixins import TablerFormMixin
from .models import SiteConfiguration, TowerMaintenanceFee


class SiteConfigurationForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            'company_name', 'company_rfc', 'company_address',
            'company_phone', 'company_email',
            'auto_payments_enabled', 'payment_type', 'payment_due_day',
            'overdue_check_enabled',
        ]


class TowerMaintenanceFeeForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = TowerMaintenanceFee
        fields = ['amount']

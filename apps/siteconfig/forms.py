from django import forms
from apps.core.mixins import TablerFormMixin
from .models import SiteConfiguration, TowerMaintenanceFee


class SiteConfigurationForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            'auto_payments_enabled', 'payment_type', 'payment_due_day',
            'overdue_check_enabled',
        ]


class TowerMaintenanceFeeForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = TowerMaintenanceFee
        fields = ['amount']

from django import forms
from apps.core.mixins import TablerFormMixin
from .models import Apartment


class ApartmentForm(TablerFormMixin, forms.ModelForm):
    custom_monthly_fee = forms.BooleanField(
        label='Cuota de mantenimiento mensual personalizada',
        required=False,
    )

    class Meta:
        model = Apartment
        fields = ['tower', 'number', 'floor', 'area_sqm', 'monthly_fee', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        tower_fees = kwargs.pop('tower_fees', {})
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.tower_id:
            default = tower_fees.get(self.instance.tower_id, 0)
            if self.instance.monthly_fee != default:
                self.initial['custom_monthly_fee'] = True

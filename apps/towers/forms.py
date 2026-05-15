from django import forms
from apps.core.mixins import TablerFormMixin
from .models import Tower


class TowerForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = Tower
        fields = ['name', 'number', 'floors', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

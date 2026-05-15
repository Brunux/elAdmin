from django import forms
from apps.core.mixins import TablerFormMixin
from .models import Announcement


class AnnouncementForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'is_active', 'expiry_date']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

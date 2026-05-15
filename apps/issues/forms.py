from django import forms
from django.contrib.auth.models import User
from django.db import models
from apps.core.mixins import TablerFormMixin
from .models import Issue


class IssueQuickUpdateForm(forms.Form):
    status = forms.ChoiceField(label='Estado', choices=[])
    note = forms.CharField(
        label='Nota',
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Agrega una nota (opcional)…'}),
        required=False,
    )

    def __init__(self, *args, issue=None, is_staff=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_status = issue.status if issue else None
        if is_staff:
            self.fields['status'].choices = [
                c for c in Issue.STATUS_CHOICES if c[0] != 'closed'
            ]
        else:
            self.fields['status'].choices = [
                c for c in Issue.STATUS_CHOICES if c[0] in ('open', 'closed')
            ]
        if issue:
            self.fields['status'].initial = issue.status

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('status') != self._current_status and not cleaned.get('note', '').strip():
            self.add_error('note', 'La nota es obligatoria al cambiar el estado.')
        return cleaned


class IssueReportForm(TablerFormMixin, forms.ModelForm):
    """Form for residents — apartment and reporter are set automatically from the logged-in user."""

    note = forms.CharField(label='Nota', widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Toda actualización debe incluir una nota'}), required=False)

    class Meta:
        model = Issue
        fields = ['title', 'description', 'photo', 'category', 'priority', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            c for c in Issue.STATUS_CHOICES if c[0] in ('open', 'closed')
        ]


class IssueAdminForm(TablerFormMixin, forms.ModelForm):
    """Staff/admin create form — includes apartment and reported_by."""

    class Meta:
        model = Issue
        fields = [
            'title', 'description', 'photo', 'category', 'priority', 'status',
            'apartment', 'reported_by', 'assigned_to',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    note = forms.CharField(label='Nota', widget=forms.Textarea(attrs={'rows': 2}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_active=True
        ).filter(
            models.Q(is_staff=True) | models.Q(is_superuser=True)
        ).order_by('first_name', 'last_name')


class IssueAdminEditForm(TablerFormMixin, forms.ModelForm):
    """Staff/admin edit form — apartment and reported_by are shown but locked."""

    class Meta:
        model = Issue
        fields = [
            'apartment', 'reported_by',
            'title', 'description', 'photo', 'category', 'priority', 'status',
            'duplicate_of', 'assigned_to',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'photo': forms.FileInput(),
        }

    note = forms.CharField(label='Nota', widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Toda actualización debe incluir una nota'}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['apartment'].disabled = True
        self.fields['reported_by'].disabled = True
        self.fields['title'].disabled = True
        self.fields['description'].disabled = True
        self.fields['status'].choices = [
            c for c in Issue.STATUS_CHOICES if c[0] != 'closed'
        ]
        self.fields['duplicate_of'].queryset = Issue.objects.select_related(
            'apartment__tower'
        ).exclude(
            pk=self.instance.pk if self.instance.pk else None
        ).order_by('-created_at')
        self.fields['duplicate_of'].required = False
        self.fields['duplicate_of'].label_from_instance = lambda obj: (
            f'#{obj.pk} — {obj.title}'
            + (f' ({obj.apartment.tower} {obj.apartment.number})' if obj.apartment else '')
        )
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_active=True
        ).filter(
            models.Q(is_staff=True) | models.Q(is_superuser=True)
        ).order_by('first_name', 'last_name')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('status') == 'duplicated' and not cleaned.get('duplicate_of'):
            self.add_error('duplicate_of', 'Selecciona el reporte original para marcar como duplicado.')
        return cleaned

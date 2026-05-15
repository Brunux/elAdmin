from django import forms
from apps.core.mixins import TablerFormMixin
from .models import Payment


class PaymentForm(TablerFormMixin, forms.ModelForm):
    """Full form for staff/admins."""
    class Meta:
        model = Payment
        fields = ['apartment', 'resident', 'payment_type', 'amount', 'status',
                  'due_date', 'paid_date', 'period', 'reference', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'paid_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PaymentResidentCreateForm(TablerFormMixin, forms.ModelForm):
    """Resident creates a new payment record."""
    class Meta:
        model = Payment
        fields = ['payment_type', 'amount', 'period', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PaymentResidentSubmitForm(TablerFormMixin, forms.ModelForm):
    """Resident logs proof of payment — transitions to submitted."""
    class Meta:
        model = Payment
        fields = ['paid_date', 'reference', 'receipt', 'notes']
        widgets = {
            'paid_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

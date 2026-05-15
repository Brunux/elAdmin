from django.template.loader import render_to_string
from django.utils import timezone


def _next_invoice_number():
    from .models import Invoice
    year = timezone.now().year
    last = Invoice.objects.filter(invoice_number__startswith=f'INV-{year}-').order_by('-invoice_number').first()
    if last:
        try:
            seq = int(last.invoice_number.split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f'INV-{year}-{seq:04d}'


def generate_invoice(payment):
    from .models import Invoice
    from apps.siteconfig.models import SiteConfiguration
    if hasattr(payment, 'invoice'):
        return payment.invoice
    invoice_number = _next_invoice_number()
    now = timezone.now()
    config = SiteConfiguration.get()
    html = render_to_string('payments/invoice.html', {
        'payment': payment,
        'config': config,
        'invoice': type('_Inv', (), {
            'invoice_number': invoice_number,
            'issued_at': now,
        })(),
    })
    invoice = Invoice.objects.create(
        payment=payment,
        invoice_number=invoice_number,
        html_content=html,
    )
    return invoice

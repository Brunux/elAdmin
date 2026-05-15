from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count

PAGE_SIZE = 20
from apps.core.decorators import staff_required, admin_required
from .models import Payment
from .forms import PaymentForm, PaymentResidentCreateForm, PaymentResidentSubmitForm
from .emails import notify_owner_payment_pending, notify_staff_payment_submitted, notify_owner_payment_confirmed


def _is_staff(user):
    return user.is_staff or user.is_superuser


@login_required
def payment_select(request):
    """For normal users: choose a pending/overdue payment to submit a proof of payment."""
    if _is_staff(request.user):
        return redirect('payments:create')
    resident = getattr(request.user, 'resident', None)
    pending = Payment.objects.filter(
        resident=resident, status__in=('pending', 'overdue')
    ).select_related('apartment__tower').order_by('due_date') if resident else Payment.objects.none()
    return render(request, 'payments/select.html', {'pending': pending})


@login_required
def payment_list(request):
    from django.db import models as db_models
    from apps.towers.models import Tower
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    period_filter = request.GET.get('period', '').strip()
    tower_filter = request.GET.get('tower', '').strip()
    all_periods = Payment.objects.order_by('-period').values_list('period', flat=True).distinct()
    towers = Tower.objects.order_by('number')
    qs = Payment.objects.select_related('apartment__tower', 'resident__user')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if period_filter:
        qs = qs.filter(period=period_filter)
    if tower_filter:
        qs = qs.filter(apartment__tower_id=tower_filter)

    if q:
        matched_statuses = [k for k, v in Payment.STATUS_CHOICES if q.lower() in v.lower() or q.lower() in k.lower()]
        matched_types = [k for k, v in Payment.TYPE_CHOICES if q.lower() in v.lower() or q.lower() in k.lower()]
        q_filter = (
            db_models.Q(period__icontains=q) |
            db_models.Q(reference__icontains=q) |
            db_models.Q(apartment__number__icontains=q) |
            db_models.Q(apartment__tower__name__icontains=q) |
            db_models.Q(resident__user__first_name__icontains=q) |
            db_models.Q(resident__user__last_name__icontains=q)
        )
        if matched_statuses:
            q_filter |= db_models.Q(status__in=matched_statuses)
        if matched_types:
            q_filter |= db_models.Q(payment_type__in=matched_types)
        qs = qs.filter(q_filter)

    count_qs = Payment.objects
    if period_filter:
        count_qs = count_qs.filter(period=period_filter)
    if tower_filter:
        count_qs = count_qs.filter(apartment__tower_id=tower_filter)
    counts = {s: count_qs.filter(status=s).count() for s, _ in Payment.STATUS_CHOICES}

    resident = getattr(request.user, 'resident', None)
    own_payments = qs.filter(resident=resident) if resident else qs.none()
    other_qs = qs.exclude(resident=resident) if resident else qs.all()
    page_obj = Paginator(other_qs, PAGE_SIZE).get_page(request.GET.get('page'))

    return render(request, 'payments/list.html', {
        'own_payments': own_payments,
        'other_payments': page_obj,
        'page_obj': page_obj,
        'counts': counts,
        'status_filter': status_filter,
        'period_filter': period_filter,
        'tower_filter': tower_filter,
        'all_periods': all_periods,
        'towers': towers,
        'q': q,
    })


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments/detail.html', {'payment': payment})


@login_required
def payment_create(request):
    is_staff = _is_staff(request.user)
    FormClass = PaymentForm if is_staff else PaymentResidentCreateForm
    form = FormClass(request.POST or None)
    if form.is_valid():
        payment = form.save(commit=False)
        if not is_staff:
            resident = getattr(request.user, 'resident', None)
            payment.resident = resident
            payment.apartment = resident.apartments.first() if resident else None
            payment.status = 'pending'
        payment.save()
        notify_owner_payment_pending(request, payment)
        messages.success(request, 'Pago registrado correctamente.')
        return redirect('payments:list')
    return render(request, 'payments/form.html', {'form': form, 'title': 'Registrar Pago'})


@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    is_staff = _is_staff(request.user)
    resident = getattr(request.user, 'resident', None)

    if not is_staff:
        if not resident or payment.resident != resident:
            raise PermissionDenied
        # Residents can only submit when pending or overdue
        if payment.status not in ('pending', 'overdue'):
            messages.info(request, 'Este pago ya no puede ser modificado.')
            return redirect('payments:detail', pk=pk)

    prev_status = payment.status
    FormClass = PaymentForm if is_staff else PaymentResidentSubmitForm
    form = FormClass(request.POST or None, request.FILES or None, instance=payment)

    if form.is_valid():
        updated = form.save(commit=False)
        if not is_staff:
            updated.status = 'submitted'
        updated.save()

        new_status = updated.status
        if not is_staff and new_status == 'submitted':
            notify_staff_payment_submitted(request, updated)
        elif is_staff and new_status == 'paid' and prev_status != 'paid':
            notify_owner_payment_confirmed(request, updated)

        messages.success(request, 'Pago actualizado correctamente.')
        return redirect('payments:detail', pk=pk)

    title = 'Registrar comprobante' if not is_staff else 'Editar Pago'
    return render(request, 'payments/form.html', {'form': form, 'title': title, 'payment': payment})


@login_required
def payment_confirm(request, pk):
    if not _is_staff(request.user):
        raise PermissionDenied
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST' and payment.status != 'paid':
        payment.status = 'paid'
        from django.utils import timezone
        payment.paid_date = payment.paid_date or timezone.now().date()
        payment.save()
        notify_owner_payment_confirmed(request, payment)
        messages.success(request, 'Pago confirmado correctamente.')
    return redirect('payments:detail', pk=pk)

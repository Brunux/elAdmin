import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from apps.core.decorators import staff_required, admin_required
from .models import Tower
from .forms import TowerForm


def _payment_chart_context(qs, period=None):
    from apps.payments.models import Payment

    all_periods = (
        Payment.objects.order_by('-period')
        .values_list('period', flat=True)
        .distinct()
    )

    stat_qs = qs.filter(period=period) if period else qs

    status_counts = {s: 0 for s, _ in Payment.STATUS_CHOICES}
    status_amounts = {s: 0 for s, _ in Payment.STATUS_CHOICES}
    for row in stat_qs.values('status').annotate(n=Count('id'), total=Sum('amount')):
        status_counts[row['status']] = row['n']
        status_amounts[row['status']] = row['total'] or 0

    monthly = (
        qs
        .annotate(month=TruncMonth('due_date'))
        .values('month', 'status')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    months_set, paid_map, pending_map, overdue_map = set(), {}, {}, {}
    for row in monthly:
        label = row['month'].strftime('%b %Y')
        months_set.add((row['month'], label))
        if row['status'] == 'paid':
            paid_map[label] = float(row['total'])
        elif row['status'] in ('pending', 'submitted'):
            pending_map[label] = pending_map.get(label, 0) + float(row['total'])
        elif row['status'] == 'overdue':
            overdue_map[label] = float(row['total'])

    month_labels = [label for _, label in sorted(months_set)]
    return {
        'status_counts': status_counts,
        'status_amounts': status_amounts,
        'all_periods': all_periods,
        'selected_period': period or '',
        'chart_labels': json.dumps(month_labels),
        'chart_paid': json.dumps([paid_map.get(l, 0) for l in month_labels]),
        'chart_pending': json.dumps([pending_map.get(l, 0) for l in month_labels]),
        'chart_overdue': json.dumps([overdue_map.get(l, 0) for l in month_labels]),
    }


@login_required
def tower_list(request):
    from apps.payments.models import Payment
    towers = Tower.objects.prefetch_related('apartments').all()
    period = request.GET.get('period', '').strip() or None
    ctx = _payment_chart_context(Payment.objects.all(), period=period)
    ctx['towers'] = towers
    return render(request, 'towers/list.html', ctx)


@login_required
def tower_detail(request, pk):
    from apps.payments.models import Payment
    tower = get_object_or_404(Tower, pk=pk)
    apartments = tower.apartments.prefetch_related('residents__user').all()
    apartments_data = []
    for apt in apartments:
        owner, tenant = None, None
        for r in apt.residents.all():
            if r.resident_type == 'owner' and not owner:
                owner = r
            elif r.resident_type == 'tenant' and not tenant:
                tenant = r
        apartments_data.append({'apt': apt, 'owner': owner, 'tenant': tenant})
    period = request.GET.get('period', '').strip() or None
    ctx = _payment_chart_context(Payment.objects.filter(apartment__tower=tower), period=period)
    ctx.update({'tower': tower, 'apartments': apartments, 'apartments_data': apartments_data})
    return render(request, 'towers/detail.html', ctx)


@staff_required
def tower_create(request):
    form = TowerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Torre creada correctamente.')
        return redirect('towers:list')
    return render(request, 'towers/form.html', {'form': form, 'title': 'Nueva Torre'})


@staff_required
def tower_edit(request, pk):
    tower = get_object_or_404(Tower, pk=pk)
    form = TowerForm(request.POST or None, instance=tower)
    if form.is_valid():
        form.save()
        messages.success(request, 'Torre actualizada.')
        return redirect('towers:detail', pk=pk)
    return render(request, 'towers/form.html', {'form': form, 'title': 'Editar Torre', 'tower': tower})


@admin_required
def tower_delete(request, pk):
    tower = get_object_or_404(Tower, pk=pk)
    if request.method == 'POST':
        tower.delete()
        messages.success(request, 'Torre eliminada.')
        return redirect('towers:list')
    return render(request, 'towers/confirm_delete.html', {'tower': tower})

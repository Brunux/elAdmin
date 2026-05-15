import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
from apps.core.decorators import staff_required, admin_required
from .models import Apartment
from .forms import ApartmentForm

PAGE_SIZE = 20


def _tower_fees():
    from apps.siteconfig.models import TowerMaintenanceFee
    return {f.tower_id: float(f.amount) for f in TowerMaintenanceFee.objects.all()}

@login_required
def apartment_list(request):
    q = request.GET.get('q', '').strip()
    apartments = Apartment.objects.select_related('tower').all()
    if q:
        apartments = apartments.filter(
            models.Q(number__icontains=q) |
            models.Q(tower__name__icontains=q) |
            models.Q(tower__number__icontains=q)
        )
    page_obj = Paginator(apartments, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'units/list.html', {'page_obj': page_obj, 'apartments': page_obj, 'q': q})


@login_required
def apartment_detail(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    return render(request, 'units/detail.html', {'apartment': apartment})


@staff_required
def apartment_create(request):
    fees = _tower_fees()
    form = ApartmentForm(request.POST or None, tower_fees=fees)
    if form.is_valid():
        apt = form.save(commit=False)
        if not form.cleaned_data.get('custom_monthly_fee'):
            apt.monthly_fee = fees.get(apt.tower_id, 0)
        apt.save()
        messages.success(request, 'Apartamento creado correctamente.')
        return redirect('units:list')
    return render(request, 'units/form.html', {
        'form': form,
        'title': 'Nuevo Apartamento',
        'tower_fees_json': json.dumps(fees),
    })


@staff_required
def apartment_edit(request, pk):
    fees = _tower_fees()
    apartment = get_object_or_404(Apartment, pk=pk)
    form = ApartmentForm(request.POST or None, instance=apartment, tower_fees=fees)
    if form.is_valid():
        apt = form.save(commit=False)
        if not form.cleaned_data.get('custom_monthly_fee'):
            apt.monthly_fee = fees.get(apt.tower_id, 0)
        apt.save()
        messages.success(request, 'Apartamento actualizado.')
        return redirect('units:detail', pk=pk)
    return render(request, 'units/form.html', {
        'form': form,
        'title': 'Editar Apartamento',
        'apartment': apartment,
        'tower_fees_json': json.dumps(fees),
    })


@admin_required
def apartment_delete(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    if request.method == 'POST':
        apartment.delete()
        messages.success(request, 'Apartamento eliminado.')
        return redirect('units:list')
    return render(request, 'units/confirm_delete.html', {'apartment': apartment})

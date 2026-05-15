from django.shortcuts import render, redirect
from django.contrib import messages
from django.forms import modelformset_factory
from apps.core.decorators import admin_required
from apps.towers.models import Tower
from .models import SiteConfiguration, TowerMaintenanceFee
from .forms import SiteConfigurationForm, TowerMaintenanceFeeForm


def _ensure_fee_records():
    for tower in Tower.objects.all():
        TowerMaintenanceFee.objects.get_or_create(tower=tower)


@admin_required
def config_view(request):
    _ensure_fee_records()
    config = SiteConfiguration.get()
    FeeFormSet = modelformset_factory(TowerMaintenanceFee, form=TowerMaintenanceFeeForm, extra=0)
    fee_qs = TowerMaintenanceFee.objects.select_related('tower').order_by('tower__name')

    config_form = SiteConfigurationForm(request.POST or None, instance=config)
    fee_formset = FeeFormSet(request.POST or None, queryset=fee_qs, prefix='fees')

    if request.method == 'POST':
        config_ok = config_form.is_valid()
        fees_ok = fee_formset.is_valid()
        if config_ok and fees_ok:
            config_form.save()
            fee_formset.save()
            messages.success(request, 'Configuración guardada correctamente.')
            return redirect('siteconfig:config')

    return render(request, 'siteconfig/config.html', {
        'form': config_form,
        'config': config,
        'fee_formset': fee_formset,
    })

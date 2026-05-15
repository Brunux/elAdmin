from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings

PAGE_SIZE = 20
from apps.core.decorators import staff_required, admin_required
from .models import Resident, Invitation
from .forms import UserCreateForm, UserEditForm, ResidentProfileForm, InvitationForm, InviteAcceptForm


@login_required
def resident_list(request):
    from apps.towers.models import Tower
    q = request.GET.get('q', '').strip()
    tower_filter = request.GET.get('tower', '').strip()
    residents = Resident.objects.select_related('user').prefetch_related('apartments__tower').all()
    if tower_filter:
        residents = residents.filter(apartments__tower_id=tower_filter).distinct()
    if q:
        residents = residents.filter(
            models.Q(user__first_name__icontains=q) |
            models.Q(user__last_name__icontains=q) |
            models.Q(user__email__icontains=q) |
            models.Q(phone__icontains=q) |
            models.Q(apartments__number__icontains=q) |
            models.Q(apartments__tower__name__icontains=q)
        ).distinct()
    towers = Tower.objects.order_by('number')
    page_obj = Paginator(residents, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'residents/list.html', {
        'page_obj': page_obj, 'residents': page_obj,
        'q': q, 'tower_filter': tower_filter, 'towers': towers,
    })


@login_required
def resident_detail(request, pk):
    from apps.issues.models import Issue
    resident = get_object_or_404(Resident.objects.select_related('user').prefetch_related('apartments__tower'), pk=pk)
    issues = Issue.objects.filter(reported_by=resident).order_by('-created_at')
    return render(request, 'residents/detail.html', {'resident': resident, 'issues': issues})


@staff_required
def resident_create(request):
    user_form = UserCreateForm(request.POST or None)
    resident_form = ResidentProfileForm(request.POST or None, request.FILES or None)
    if user_form.is_valid() and resident_form.is_valid():
        user = user_form.save()
        resident = resident_form.save(commit=False)
        resident.user = user
        resident.status = 'active'
        resident.save()
        resident_form.save_m2m()
        messages.success(request, f'Residente {resident.full_name} creado correctamente.')
        return redirect('residents:detail', pk=resident.pk)
    return render(request, 'residents/form.html', {
        'user_form': user_form,
        'resident_form': resident_form,
        'title': 'Nuevo Residente',
    })


@staff_required
def resident_edit(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    user_form = UserEditForm(request.POST or None, instance=resident.user)
    resident_form = ResidentProfileForm(request.POST or None, request.FILES or None, instance=resident)
    if user_form.is_valid() and resident_form.is_valid():
        user_form.save()
        resident_form.save()
        messages.success(request, 'Residente actualizado correctamente.')
        return redirect('residents:detail', pk=pk)
    return render(request, 'residents/form.html', {
        'user_form': user_form,
        'resident_form': resident_form,
        'title': 'Editar Residente',
        'resident': resident,
    })


@admin_required
def resident_delete(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        resident.user.delete()
        messages.success(request, 'Residente eliminado.')
        return redirect('residents:list')
    return render(request, 'residents/confirm_delete.html', {'resident': resident})


@login_required
def apartments_by_type(request):
    from apps.units.models import Apartment
    resident_type = request.GET.get('type', '')
    apts = Apartment.objects.all().order_by('tower__name', 'number')
    if resident_type in ('owner', 'tenant'):
        # Exclude apartments that already have an active resident of this type
        occupied_ids = (
            Resident.objects.filter(resident_type=resident_type, status='active')
            .values_list('apartments__id', flat=True)
        )
        apts = apts.exclude(pk__in=occupied_ids)
    data = [
        {'id': apt.pk, 'label': f'{apt.tower} — {apt}'}
        for apt in apts
    ]
    return JsonResponse(data, safe=False)


@staff_required
def invite_create(request):
    form = InvitationForm(request.POST or None)
    if form.is_valid():
        invitation = form.save(commit=False)
        invitation.created_by = request.user
        invitation.save()
        accept_url = request.build_absolute_uri(
            reverse('residents:invite_accept', kwargs={'token': invitation.token})
        )
        manual_url = request.build_absolute_uri(reverse('core:manual_resident'))
        send_mail(
            subject='Invitación para registrarte en El Admin',
            message=(
                f'Hola,\n\n'
                f'Has sido invitado a registrarte en El Admin.\n\n'
                f'Haz clic en el siguiente enlace para completar tu registro:\n{accept_url}\n\n'
                f'Este enlace es de un solo uso.\n\n'
                f'También puedes consultar el manual del residente antes de ingresar:\n{manual_url}\n\n'
                f'Saludos,\nEl Admin'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )
        messages.success(request, f'Invitación enviada a {invitation.email}.')
        return redirect('residents:list')
    return render(request, 'residents/invite_form.html', {'form': form, 'title': 'Invitar Residente'})


def invite_accept(request, token):
    invitation = get_object_or_404(Invitation, token=token, is_used=False)

    existing_user = User.objects.filter(email=invitation.email).first()

    if existing_user:
        # User already has an account — just add the apartment and log them in
        if request.method == 'POST':
            resident, _ = Resident.objects.get_or_create(
                user=existing_user,
                defaults={'resident_type': invitation.resident_type, 'status': 'active'},
            )
            if invitation.apartment:
                resident.apartments.add(invitation.apartment)
            invitation.is_used = True
            invitation.save()
            login(request, existing_user)
            messages.success(request, f'¡Bienvenido de nuevo, {existing_user.first_name}! El apartamento ha sido añadido a tu cuenta.')
            return redirect('core:dashboard')
        return render(request, 'residents/invite_accept.html', {
            'invitation': invitation,
            'existing_user': existing_user,
        })

    # New user — full registration form
    form = InviteAcceptForm(request.POST or None)
    if form.is_valid():
        user = User.objects.create_user(
            username=invitation.email,
            email=invitation.email,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password'],
        )
        resident = Resident.objects.create(
            user=user,
            resident_type=invitation.resident_type,
            status='active',
        )
        if invitation.apartment:
            resident.apartments.add(invitation.apartment)
        invitation.is_used = True
        invitation.save()
        login(request, user)
        messages.success(request, f'¡Bienvenido, {user.first_name}! Tu cuenta ha sido creada.')
        return redirect('core:dashboard')
    return render(request, 'residents/invite_accept.html', {'form': form, 'invitation': invitation})


@login_required
def invitation_list(request):
    from apps.towers.models import Tower
    q = request.GET.get('q', '').strip()
    tower_filter = request.GET.get('tower', '').strip()
    invitations = Invitation.objects.select_related('apartment__tower', 'created_by').all()
    if tower_filter:
        invitations = invitations.filter(apartment__tower_id=tower_filter)
    if q:
        invitations = invitations.filter(
            models.Q(email__icontains=q) |
            models.Q(apartment__number__icontains=q) |
            models.Q(apartment__tower__name__icontains=q)
        )
    towers = Tower.objects.order_by('number')
    page_obj = Paginator(invitations, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'residents/invitation_list.html', {
        'page_obj': page_obj, 'invitations': page_obj,
        'q': q, 'tower_filter': tower_filter, 'towers': towers,
    })

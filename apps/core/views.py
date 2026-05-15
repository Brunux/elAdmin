from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from apps.core.decorators import admin_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('core:dashboard')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('core:login')


@login_required
def dashboard(request):
    from apps.units.models import Apartment
    from apps.residents.models import Resident
    from apps.payments.models import Payment
    from apps.announcements.models import Announcement
    from apps.issues.models import Issue

    context = {
        'open_issues': Issue.objects.filter(status='open').count(),
        'total_issues': Issue.objects.count(),
        'total_apartments': Apartment.objects.count(),
        'occupied_apartments': Apartment.objects.filter(residents__status='active').distinct().count(),
        'total_residents': Resident.objects.count(),
        'pending_payments': Payment.objects.filter(status='pending').count(),
        'recent_announcements': Announcement.objects.order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def account(request):
    user = request.user
    profile_saved = False
    password_saved = False

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            from django.contrib.auth.models import User as UserModel
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            new_email = request.POST.get('email', '').strip().lower()
            email_changed = new_email and new_email != user.email

            if email_changed and UserModel.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, 'Ese correo ya está en uso por otro usuario.')
            else:
                user.first_name = first_name
                user.last_name = last_name
                update_fields = ['first_name', 'last_name']
                if email_changed:
                    user.email = new_email
                    user.username = new_email
                    update_fields += ['email', 'username']
                user.save(update_fields=update_fields)

                resident = getattr(user, 'resident', None)
                if resident:
                    resident.emergency_contact_name = request.POST.get('emergency_contact_name', '').strip()
                    resident.emergency_contact_phone = request.POST.get('emergency_contact_phone', '').strip()
                    resident.notes = request.POST.get('notes', '').strip()
                    resident.save(update_fields=['emergency_contact_name', 'emergency_contact_phone', 'notes'])

                if email_changed:
                    from django.core.mail import send_mail
                    send_mail(
                        subject='[El Admin] Confirmación de cambio de correo',
                        message=(
                            f'Hola {user.get_full_name() or user.username},\n\n'
                            f'Tu correo electrónico ha sido actualizado correctamente.\n\n'
                            f'Nuevo correo: {new_email}\n\n'
                            f'Si no realizaste este cambio, contacta al administrador de inmediato.'
                        ),
                        from_email=None,
                        recipient_list=[new_email],
                        fail_silently=True,
                    )

                messages.success(request, 'Perfil actualizado correctamente.')
                profile_saved = True

        elif 'save_password' in request.POST:
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, 'Contraseña actualizada correctamente.')
                password_saved = True
            else:
                return render(request, 'core/account.html', {
                    'password_form': form,
                    'active_tab': 'password',
                })

    password_form = PasswordChangeForm(user)
    return render(request, 'core/account.html', {
        'password_form': password_form,
        'active_tab': 'password' if password_saved else 'profile',
    })


@login_required
def manual_index(request):
    return render(request, 'core/manual_index.html')


@login_required
def manual_admin(request):
    return render(request, 'core/manual_admin.html')


@login_required
def manual_staff(request):
    return render(request, 'core/manual_staff.html')


@login_required
def manual_resident(request):
    return render(request, 'core/manual_resident.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.core.decorators import staff_required, admin_required
from .models import Announcement
from .forms import AnnouncementForm


@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'announcements/list.html', {'announcements': announcements})


@login_required
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    return render(request, 'announcements/detail.html', {'announcement': announcement})


@staff_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None)
    if form.is_valid():
        announcement = form.save(commit=False)
        announcement.author = request.user
        announcement.save()
        messages.success(request, 'Anuncio publicado correctamente.')
        return redirect('announcements:list')
    return render(request, 'announcements/form.html', {'form': form, 'title': 'Nuevo Anuncio'})


@staff_required
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    form = AnnouncementForm(request.POST or None, instance=announcement)
    if form.is_valid():
        form.save()
        messages.success(request, 'Anuncio actualizado.')
        return redirect('announcements:detail', pk=pk)
    return render(request, 'announcements/form.html', {'form': form, 'title': 'Editar Anuncio', 'announcement': announcement})


@admin_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Anuncio eliminado.')
        return redirect('announcements:list')
    return render(request, 'announcements/confirm_delete.html', {'announcement': announcement})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone

PAGE_SIZE = 20
from apps.core.decorators import staff_required, admin_required
from .models import Issue, IssueNote
from .forms import IssueReportForm, IssueAdminForm, IssueAdminEditForm, IssueQuickUpdateForm
from .emails import notify_staff_new_issue, notify_staff_issue_reopened, notify_owner_status_changed


@login_required
def issue_list(request):
    from django.db import models as db_models
    status_filter = request.GET.get('status', '')
    period_filter = request.GET.get('period', '').strip()
    q = request.GET.get('q', '').strip()

    all_periods = [
        d.strftime('%Y-%m')
        for d in Issue.objects.dates('created_at', 'month', order='DESC')
    ]

    qs = Issue.objects.select_related('apartment__tower', 'reported_by__user', 'assigned_to')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if period_filter:
        year, month = period_filter.split('-')
        qs = qs.filter(created_at__year=year, created_at__month=month)
    if q:
        matched_statuses = [k for k, v in Issue.STATUS_CHOICES if q.lower() in v.lower() or q.lower() in k.lower()]
        matched_categories = [k for k, v in Issue.CATEGORY_CHOICES if q.lower() in v.lower() or q.lower() in k.lower()]
        matched_priorities = [k for k, v in Issue.PRIORITY_CHOICES if q.lower() in v.lower() or q.lower() in k.lower()]
        q_filter = (
            db_models.Q(title__icontains=q) |
            db_models.Q(description__icontains=q) |
            db_models.Q(apartment__number__icontains=q) |
            db_models.Q(apartment__tower__name__icontains=q) |
            db_models.Q(reported_by__user__first_name__icontains=q) |
            db_models.Q(reported_by__user__last_name__icontains=q)
        )
        if matched_statuses:
            q_filter |= db_models.Q(status__in=matched_statuses)
        if matched_categories:
            q_filter |= db_models.Q(category__in=matched_categories)
        if matched_priorities:
            q_filter |= db_models.Q(priority__in=matched_priorities)
        qs = qs.filter(q_filter)

    count_base = Issue.objects
    if period_filter:
        count_base = count_base.filter(created_at__year=year, created_at__month=month)
    counts = {
        'open':        count_base.filter(status='open').count(),
        'in_progress': count_base.filter(status='in_progress').count(),
        'resolved':    count_base.filter(status='resolved').count(),
        'closed':      count_base.filter(status='closed').count(),
        'duplicated':  count_base.filter(status='duplicated').count(),
    }

    resident = getattr(request.user, 'resident', None)
    own_issues = qs.filter(reported_by=resident) if resident else qs.none()
    other_qs = qs.exclude(reported_by=resident) if resident else qs.all()
    page_obj = Paginator(other_qs, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'issues/list.html', {
        'own_issues': own_issues,
        'other_issues': page_obj,
        'page_obj': page_obj,
        'counts': counts,
        'status_filter': status_filter,
        'period_filter': period_filter,
        'all_periods': all_periods,
        'q': q,
    })


@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    notes = issue.notes.select_related('created_by').all()
    is_staff = _is_staff(request.user)
    resident = getattr(request.user, 'resident', None)
    can_update = is_staff or (resident and issue.reported_by == resident)

    quick_form = IssueQuickUpdateForm(issue=issue, is_staff=is_staff) if can_update else None

    if request.method == 'POST' and can_update:
        quick_form = IssueQuickUpdateForm(request.POST, issue=issue, is_staff=is_staff)
        if quick_form.is_valid():
            prev_status = issue.status
            new_status = quick_form.cleaned_data['status']
            note_body = quick_form.cleaned_data.get('note', '')
            issue.status = new_status
            if new_status == 'resolved' and prev_status != 'resolved':
                issue.resolved_at = timezone.now()
            issue.save()
            if new_status != prev_status or note_body:
                IssueNote.objects.create(
                    issue=issue, status=new_status,
                    body=note_body,
                    created_by=request.user,
                )
                if is_staff:
                    notify_owner_status_changed(request, issue, updated_by=request.user)
                elif new_status == 'open':
                    notify_staff_issue_reopened(request, issue, updated_by=request.user)
            messages.success(request, 'Reporte actualizado.')
            return redirect('issues:detail', pk=pk)

    return render(request, 'issues/detail.html', {
        'issue': issue,
        'notes': notes,
        'quick_form': quick_form,
        'can_update': can_update,
        'is_staff': is_staff,
    })


def _is_staff(user):
    return user.is_staff or user.is_superuser


@login_required
def issue_create(request):
    is_staff = _is_staff(request.user)
    FormClass = IssueAdminForm if is_staff else IssueReportForm
    form = FormClass(request.POST or None, request.FILES or None)
    if form.is_valid():
        issue = form.save(commit=False)
        if not is_staff:
            resident = getattr(request.user, 'resident', None)
            issue.reported_by = resident
            issue.apartment = resident.apartments.first() if resident else None
        issue.save()
        IssueNote.objects.create(
            issue=issue, status=issue.status,
            body=form.cleaned_data.get('note', ''),
            created_by=request.user,
        )
        notify_staff_new_issue(request, issue)
        messages.success(request, 'Reporte enviado correctamente.')
        return redirect('issues:list')
    return render(request, 'issues/form.html', {'form': form, 'title': 'Nuevo Reporte'})


@login_required
def issue_edit(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    is_staff = _is_staff(request.user)
    resident = getattr(request.user, 'resident', None)

    # Normal users can only edit issues they reported
    if not is_staff and (not resident or issue.reported_by != resident):
        raise PermissionDenied

    FormClass = IssueAdminEditForm if is_staff else IssueReportForm
    prev_status = issue.status
    orig_apartment = issue.apartment_id
    orig_reported_by = issue.reported_by_id
    orig_title = issue.title
    orig_description = issue.description
    form = FormClass(request.POST or None, request.FILES or None, instance=issue)
    if form.is_valid():
        updated = form.save(commit=False)
        updated.apartment_id = orig_apartment
        updated.reported_by_id = orig_reported_by
        updated.title = orig_title
        updated.description = orig_description
        new_status = updated.status
        if is_staff and new_status == 'closed':
            new_status = prev_status
            updated.status = prev_status
        if new_status == 'resolved' and prev_status != 'resolved':
            updated.resolved_at = timezone.now()
        updated.save()
        note_body = form.cleaned_data.get('note', '')
        if new_status != prev_status or note_body:
            IssueNote.objects.create(
                issue=updated, status=new_status,
                body=note_body,
                created_by=request.user,
            )
            if is_staff:
                notify_owner_status_changed(request, updated, updated_by=request.user)
            elif new_status == 'open':
                notify_staff_issue_reopened(request, updated, updated_by=request.user)
        messages.success(request, 'Reporte actualizado.')
        return redirect('issues:detail', pk=pk)
    return render(request, 'issues/form.html', {'form': form, 'title': 'Editar Reporte', 'issue': issue})


@admin_required
def issue_delete(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        issue.delete()
        messages.success(request, 'Reporte eliminado.')
        return redirect('issues:list')
    return render(request, 'issues/confirm_delete.html', {'issue': issue})

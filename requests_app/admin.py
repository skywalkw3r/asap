# requests_app/admin.py

from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from .models import ServerRequest, AuditLog
from .awx_utils import trigger_awx_job

@admin.register(ServerRequest)
class ServerRequestAdmin(admin.ModelAdmin):
    list_display = ('fqdn', 'status', 'site', 'primary_contact', 'requested_at', 'approved_denied_by')
    list_filter = ('status', 'site', 'backup_required', 'monitoring_required', 'requested_at', 'approved_denied_by')
    search_fields = ('fqdn', 'primary_contact', 'secondary_contact', 'group_contact', 'asap_number', 'vlan', 'admin_notes')
    ordering = ('-requested_at',)
    readonly_fields = ('requested_at', 'updated_at', 'approved_denied_at', 'approved_denied_by', 'awx_job_id')
    date_hierarchy = 'requested_at'

    fieldsets = (
        ('Request Details (Submitted by User)', {
            'fields': (
                'fqdn', 'vlan', 'site', 'primary_contact', 'secondary_contact',
                'group_contact', 'notes', 'backup_required', 'monitoring_required', 'asap_number'
            )
        }),
        ('Approval Status & Tracking', {
            'fields': (
                'status', 'admin_notes', 'approved_denied_by', 'approved_denied_at', 'awx_job_id',
                'requested_at', 'updated_at'
            )
        }),
    )

    def save_model(self, request, obj: ServerRequest, form, change):
        original_status = None
        action_performed = False

        if obj.pk:
            try:
                original_obj = ServerRequest.objects.get(pk=obj.pk)
                original_status = original_obj.status
            except ServerRequest.DoesNotExist:
                pass

        # Determine if status is changing before super().save_model potentially changes it
        new_status = form.cleaned_data.get('status')

        # Check if status changed specifically *to* APPROVED
        if new_status == 'APPROVED' and original_status != 'APPROVED':
            obj.approved_denied_by = request.user
            obj.approved_denied_at = timezone.now()
            obj.status = 'APPROVED'
            action_performed = True

            AuditLog.objects.create(
                level='INFO', action='Request Approved',
                message=f"Request ID {obj.id} ({obj.fqdn}) approved.",
                user=request.user, related_request=obj
            )

            awx_job_id = trigger_awx_job(obj)

            if awx_job_id:
                obj.awx_job_id = awx_job_id
                obj.status = 'PROVISIONING'
                messages.success(request, f"Request approved. AWX Job {awx_job_id} launched successfully.")
                AuditLog.objects.create(
                    level='SUCCESS', action='AWX Job Triggered',
                    message=f"Launched AWX Job {awx_job_id} for request {obj.id} ({obj.fqdn}).",
                    user=request.user, related_request=obj, related_awx_job_id=awx_job_id
                )
            else:
                obj.status = 'APPROVED'
                messages.error(request, "Request approved, but FAILED to launch AWX job.")
                AuditLog.objects.create(
                    level='ERROR', action='AWX Trigger Failed',
                    message=f"Failed to launch AWX job for approved request {obj.id} ({obj.fqdn}).",
                    user=request.user, related_request=obj
                )

        # Check if status changed specifically *to* DENIED
        elif new_status == 'DENIED' and original_status != 'DENIED':
            obj.approved_denied_by = request.user
            obj.approved_denied_at = timezone.now()
            obj.status = 'DENIED'
            action_performed = True
            messages.info(request, "Request has been denied.")
            AuditLog.objects.create(
                level='INFO', action='Request Denied',
                message=f"Request ID {obj.id} ({obj.fqdn}) denied.",
                user=request.user, related_request=obj
            )

        # Check if only admin_notes changed without changing status from PENDING
        elif original_status == 'PENDING' and new_status == 'PENDING':
            if 'admin_notes' in form.changed_data:
                 messages.info(request, "Admin notes updated.")

        # Save the object if we performed an action or if other fields changed
        if action_performed or form.has_changed():
             obj.save()
             # We handle saving explicitly when action_performed is True
             # If only other fields changed, form.has_changed() is True, and obj.save() handles it.
             # Avoid calling super().save_model() to prevent potential double saves/signals.
        # Need to handle initial object creation
        elif not obj.pk:
            super().save_model(request, obj, form, change) # Let Django handle initial save


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'action', 'user_link', 'request_link', 'related_awx_job_id', 'message_short')
    list_filter = ('level', 'action', 'timestamp', 'user')
    search_fields = ('action', 'message', 'user__username', 'related_request__fqdn', 'related_awx_job_id')
    readonly_fields = ('timestamp', 'level', 'action', 'message', 'user', 'related_request', 'related_awx_job_id')
    date_hierarchy = 'timestamp'
    list_per_page = 50

    def message_short(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    message_short.short_description = 'Message'

    def user_link(self, obj):
        if obj.user:
            link = reverse("admin:auth_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user.username)
        return "-"
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user'

    def request_link(self, obj):
        if obj.related_request:
            link = reverse("admin:requests_app_serverrequest_change", args=[obj.related_request.id])
            return format_html('<a href="{}">{} ({})</a>', link, obj.related_request.id, obj.related_request.fqdn)
        return "-"
    request_link.short_description = 'Related Request'
    request_link.admin_order_field = 'related_request'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Allow viewing detail page but not changing
        # return request.method in ['GET', 'HEAD'] # More permissive if detail view needed
        return False # Disallow changes completely


    def has_delete_permission(self, request, obj=None):
        return False

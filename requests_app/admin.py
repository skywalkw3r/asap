# requests_app/admin.py

from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import ServerRequest, AuditLog # <-- Import AuditLog
from .awx_utils import trigger_awx_job

@admin.register(ServerRequest)
class ServerRequestAdmin(admin.ModelAdmin):
    # ... (keep list_display, list_filter, search_fields, ordering, readonly_fields, fieldsets) ...

    # Override save_model to trigger AWX and create audit logs
    def save_model(self, request, obj: ServerRequest, form, change):
        """
        Override save_model to handle status changes, trigger AWX, and log actions.
        """
        original_status = None
        action_performed = False # Flag to track if we need to save obj later

        if obj.pk:
            try:
                original_obj = ServerRequest.objects.get(pk=obj.pk)
                original_status = original_obj.status
            except ServerRequest.DoesNotExist:
                pass

        # Check if status changed specifically *to* APPROVED
        if form.cleaned_data.get('status') == 'APPROVED' and original_status != 'APPROVED':
            obj.approved_denied_by = request.user
            obj.approved_denied_at = timezone.now()
            obj.status = 'APPROVED' # Set status before triggering AWX
            action_performed = True

            # Log approval action
            AuditLog.objects.create(
                level='INFO',
                action='Request Approved',
                message=f"Request ID {obj.id} ({obj.fqdn}) approved.",
                user=request.user,
                related_request=obj
            )

            # Trigger AWX Job
            awx_job_id = trigger_awx_job(obj)

            if awx_job_id:
                obj.awx_job_id = awx_job_id
                obj.status = 'PROVISIONING' # Update status after successful launch
                messages.success(request, f"Request approved. AWX Job {awx_job_id} launched successfully.")
                # Log AWX success
                AuditLog.objects.create(
                    level='SUCCESS',
                    action='AWX Job Triggered',
                    message=f"Launched AWX Job {awx_job_id} for request {obj.id} ({obj.fqdn}).",
                    user=request.user, # Logged as the approving user
                    related_request=obj,
                    related_awx_job_id=awx_job_id
                )
            else:
                # Keep status as APPROVED but show error and log failure
                obj.status = 'APPROVED' # Or revert: obj.status = 'PENDING'
                messages.error(request, "Request approved, but FAILED to launch AWX job. Please check AWX settings/logs.")
                # Log AWX failure
                AuditLog.objects.create(
                    level='ERROR',
                    action='AWX Trigger Failed',
                    message=f"Failed to launch AWX job for approved request {obj.id} ({obj.fqdn}).",
                    user=request.user,
                    related_request=obj
                )

        # Check if status changed specifically *to* DENIED
        elif form.cleaned_data.get('status') == 'DENIED' and original_status != 'DENIED':
            obj.approved_denied_by = request.user
            obj.approved_denied_at = timezone.now()
            obj.status = 'DENIED' # Ensure status is set
            action_performed = True
            messages.info(request, "Request has been denied.")
            # Log denial action
            AuditLog.objects.create(
                level='INFO',
                action='Request Denied',
                message=f"Request ID {obj.id} ({obj.fqdn}) denied.",
                user=request.user,
                related_request=obj
            )

        # Check if only admin_notes changed without changing status from PENDING
        elif original_status == 'PENDING' and form.cleaned_data.get('status') == 'PENDING':
            if 'admin_notes' in form.changed_data:
                 messages.info(request, "Admin notes updated.")
                 # Log note update (optional)
                 # AuditLog.objects.create(...)

        # Call the original save_model *only if* we haven't already handled the status change
        # or if other fields were changed. If we handled status, save obj directly.
        if action_performed or form.has_changed():
             # Save the ServerRequest object with the updates we made
             obj.save()
             # We avoid calling super().save_model() here to prevent double saves
             # or potential conflicts if super() also tried to change status.
        # If no relevant action was performed and only non-status fields changed,
        # let the default save happen (though this case is less likely now)
        elif form.has_changed():
             super().save_model(request, obj, form, change)


# +++ Add the AuditLogAdmin class below +++

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'action', 'user_link', 'request_link', 'related_awx_job_id', 'message_short')
    list_filter = ('level', 'action', 'timestamp', 'user') # Add filters
    search_fields = ('action', 'message', 'user__username', 'related_request__fqdn', 'related_awx_job_id') # Allow searching relevant fields
    readonly_fields = ('timestamp', 'level', 'action', 'message', 'user', 'related_request', 'related_awx_job_id') # Make logs immutable in admin
    date_hierarchy = 'timestamp' # Add date drilldown
    list_per_page = 50 # Show more logs per page

    # Custom method to display a shorter message in list view
    def message_short(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    message_short.short_description = 'Message'

    # Custom method to link to user (if exists)
    def user_link(self, obj):
        if obj.user:
            from django.urls import reverse
            from django.utils.html import format_html
            link = reverse("admin:auth_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user.username)
        return "-"
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user' # Allow sorting by user

    # Custom method to link to request (if exists)
    def request_link(self, obj):
        if obj.related_request:
            from django.urls import reverse
            from django.utils.html import format_html
            link = reverse("admin:requests_app_serverrequest_change", args=[obj.related_request.id])
            return format_html('<a href="{}">{} ({})</a>', link, obj.related_request.id, obj.related_request.fqdn)
        return "-"
    request_link.short_description = 'Related Request'
    request_link.admin_order_field = 'related_request' # Allow sorting

    # Prevent adding/changing/deleting logs via admin interface
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Allow viewing but not changing
        return False # To prevent edits completely
        # return request.method == 'GET' # Alternative: Allow viewing detail page

    def has_delete_permission(self, request, obj=None):
        return False
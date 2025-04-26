# requests_app/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class ServerRequest(models.Model):
    """Model to store server provisioning requests."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved - Queued for Provisioning'),
        ('DENIED', 'Denied'),
        ('PROVISIONING', 'Provisioning in Progress'),
        ('COMPLETED', 'Provisioning Completed'),
        ('FAILED', 'Provisioning Failed'),
    ]

    # User submitted fields
    fqdn = models.CharField(max_length=255, unique=True, help_text="Fully Qualified Domain Name (e.g., server1.example.com)")
    vlan = models.CharField(max_length=100, help_text="VLAN ID or Name")
    site = models.CharField(max_length=100, help_text="Datacenter or Site Location")
    primary_contact = models.EmailField(max_length=255, help_text="Primary Contact Email Address")
    secondary_contact = models.CharField(max_length=255, blank=True, help_text="Secondary Contact Email Address")
    group_contact = models.CharField(max_length=255, blank=True, help_text="Group Contact / DL (Optional)")
    notes = models.TextField(blank=True, help_text="Any additional notes or requirements")
    backup_required = models.BooleanField(default=False)
    monitoring_required = models.BooleanField(default=False)
    asap_number = models.CharField(max_length=100, blank=True, help_text="ASAP/Remedy/ServiceNow Ticket Number (Optional)")

    # Internal tracking fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Tracks last model save
    approved_denied_at = models.DateTimeField(null=True, blank=True)
    approved_denied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests'
    )
    admin_notes = models.TextField(blank=True, help_text="Internal notes for IT Admins")
    awx_job_id = models.IntegerField(null=True, blank=True, help_text="ID of the launched AWX Job")

    def __str__(self):
        return f"Request for {self.fqdn} ({self.status})"

    class Meta:
        ordering = ['-requested_at'] # Show newest requests first
        verbose_name = "Server Request"
        verbose_name_plural = "Server Requests"

class AuditLog(models.Model):
    """Model to store audit log entries for significant actions."""

    LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('SUCCESS', 'Success'), # Added for clarity on success
    ]

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    action = models.CharField(max_length=255, help_text="Short description of the action performed.")
    message = models.TextField(help_text="Detailed log message.")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Keep log even if user is deleted
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action (if applicable)."
    )
    related_request = models.ForeignKey(
        ServerRequest,
        on_delete=models.CASCADE, # Delete logs if the request is deleted
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="The server request this log pertains to (if applicable)."
    )
    # Store the specific job ID here too for easier log searching/correlation
    related_awx_job_id = models.IntegerField(null=True, blank=True, help_text="AWX Job ID related to this log entry (if applicable).")

    def __str__(self):
        user_str = f" by {self.user.username}" if self.user else ""
        req_str = f" (Req: {self.related_request.id})" if self.related_request else ""
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} [{self.level}] {self.action}{user_str}{req_str}"

    class Meta:
        ordering = ['-timestamp'] # Show newest logs first
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log Entries"
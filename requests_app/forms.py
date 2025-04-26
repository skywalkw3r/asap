# requests_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import ServerRequest
import re

EMPTY_LABEL = "--------- Select ---------"

# --- Form for Step 1: OS and Resources ---
class ServerRequestStep1Form(forms.ModelForm):
    """Form for Step 1: OS, Resources, basic details."""
    class Meta:
        model = ServerRequest
        fields = [
            'fqdn', 'vlan', 'location',
            'backup_required', 'monitoring_required',
            'os_type', 'cpu_cores', 'memory_gb', 'os_disk_gb', 'data_disk_gb',
            'patching_group', 'hypervisor_type',
        ]
        widgets = {
            'os_disk_gb': forms.NumberInput(attrs={'min': '100', 'max': '500'}),
            'data_disk_gb': forms.NumberInput(attrs={'min': '100', 'max': '750'}),
            'backup_required': forms.CheckboxInput(),
            'monitoring_required': forms.CheckboxInput(),
        }
        labels = {
            'fqdn': 'Desired FQDN',
            'os_disk_gb': 'OS Disk Size (GB)',
            'data_disk_gb': 'Data Disk Size (GB)',
            'memory_gb': 'Memory (RAM)',
            'location': 'Location',
            'hypervisor_type': 'Hypervisor Type',
        }
        help_texts = {
             'fqdn': 'Uppercase enforced.',
             'vlan': 'Select the VLAN.',
             'data_disk_gb': 'Optional. Enter size in GB (100-750). Leave blank if no data disk needed.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty labels
        self.fields['vlan'].empty_label = EMPTY_LABEL
        self.fields['location'].empty_label = EMPTY_LABEL
        self.fields['os_type'].empty_label = EMPTY_LABEL
        self.fields['cpu_cores'].empty_label = EMPTY_LABEL
        self.fields['memory_gb'].empty_label = EMPTY_LABEL
        self.fields['patching_group'].empty_label = EMPTY_LABEL
        # Since hypervisor has only one choice and a default, make it read-only
        self.fields['hypervisor_type'].disabled = True

        # Set required status based on model (blank=False means required)
        self.fields['fqdn'].required = True
        self.fields['vlan'].required = True
        self.fields['location'].required = True
        self.fields['os_type'].required = True
        self.fields['cpu_cores'].required = True
        self.fields['memory_gb'].required = True
        self.fields['os_disk_gb'].required = True
        self.fields['patching_group'].required = True
        self.fields['hypervisor_type'].required = False # Disabled, default will be used
        self.fields['data_disk_gb'].required = False # Now optional

    def clean_fqdn(self):
        fqdn = self.cleaned_data.get('fqdn')
        if fqdn: return fqdn.upper()
        return fqdn

    def clean_vlan(self):
        # No longer need uppercase as it's a dropdown
        return self.cleaned_data.get('vlan')

    def clean_data_disk_gb(self):
        data_disk = self.cleaned_data.get('data_disk_gb')
        if data_disk is None: return None
        if not (100 <= data_disk <= 750):
             raise ValidationError("If specified, Data Disk size must be between 100 and 750 GB.", code='invalid_data_disk_range')
        return data_disk


# --- Form for Step 2: Contacts, Notes, Ticket, Users, Terms ---
class ServerRequestStep2Form(forms.ModelForm):
    """Form for Step 2: Contacts and other info."""
    terms_accepted = forms.BooleanField(required=True, label="Terms and Conditions")

    class Meta:
        model = ServerRequest
        fields = [
            'primary_contact', 'secondary_contact', 'group_contact',
            'ticket_number', 'user_ids', 'notes',
            'terms_accepted',
        ]
        widgets = {
            'primary_contact': forms.EmailInput(),
            'secondary_contact': forms.EmailInput(),
            'group_contact': forms.EmailInput(),
            'user_ids': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'ticket_number': 'Ticket #',
            'user_ids': 'User IDs',
        }
        help_texts = {
             'ticket_number': 'JIRA/ServiceNow Ticket Number (Optional)',
             'user_ids': 'Enter UserIDs/Usernames (comma-separated).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ticket_number'].required = False
        self.fields['user_ids'].required = False

    def clean_group_contact(self):
        group_email = self.cleaned_data.get('group_contact')
        if group_email:
            try: validate_email(group_email)
            except ValidationError: raise ValidationError("Invalid email for group contact.", code='invalid_group_email')
        return group_email

    def clean_user_ids(self):
        user_ids_text = self.cleaned_data.get('user_ids', '')
        if not user_ids_text: return ''

        user_ids_list = [uid.strip() for uid in user_ids_text.split(',') if uid.strip()]
        valid_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
        invalid_ids = [uid for uid in user_ids_list if not valid_pattern.match(uid)]
        if invalid_ids:
            raise ValidationError(f"Invalid User ID format found for: {', '.join(invalid_ids)}. Use letters, numbers, underscores, hyphens.", code='invalid_user_id')
        return ",".join(user_ids_list)

    def clean(self):
        cleaned_data = super().clean()
        primary = cleaned_data.get("primary_contact")
        secondary = cleaned_data.get("secondary_contact")

        if secondary and primary and secondary.strip().lower() == primary.strip().lower():
            self.add_error('secondary_contact', "Secondary contact email cannot be the same as the primary contact.")

        # Removed disk range checks here as they belong to Step 1 form or model validators
        return cleaned_data

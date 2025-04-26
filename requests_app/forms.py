# requests_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import ServerRequest

class ServerRequestForm(forms.ModelForm):
    """Form for end-users to submit server requests."""

    # Make terms required explicitly in the form
    terms_accepted = forms.BooleanField(required=True, label="Terms and Conditions")

    class Meta:
        model = ServerRequest
        fields = [
            'fqdn', 'vlan', 'site', 'primary_contact', 'secondary_contact',
            'group_contact', 'notes', 'backup_required', 'monitoring_required',
            'asap_number',
            'os_type', 'cpu_cores', 'memory_gb', 'os_disk_gb', 'data_disk_gb',
            'terms_accepted',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 5}),
            'primary_contact': forms.EmailInput(),
            'secondary_contact': forms.EmailInput(),
            'group_contact': forms.EmailInput(),
            'os_disk_gb': forms.NumberInput(attrs={'min': '100', 'max': '500'}),
            'data_disk_gb': forms.NumberInput(attrs={'min': '100', 'max': '750'}),
            'backup_required': forms.CheckboxInput(),
            'monitoring_required': forms.CheckboxInput(),
        }
        labels = {
            'os_disk_gb': 'OS Disk Size (GB)',
            'data_disk_gb': 'Data Disk Size (GB)',
            'memory_gb': 'Memory (RAM)',
        }
        help_texts = {
             'fqdn': 'Enter the desired Fully Qualified Domain Name (e.g., server.site.company.com). Will be converted to uppercase.',
             'vlan': 'Enter the VLAN ID or Name. Will be converted to uppercase.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fqdn'].required = True
        self.fields['vlan'].required = True
        self.fields['site'].required = True
        self.fields['os_type'].required = True
        self.fields['cpu_cores'].required = True
        self.fields['memory_gb'].required = True
        self.fields['os_disk_gb'].required = True
        self.fields['data_disk_gb'].required = True

    # --- Validation Methods ---

    def clean_fqdn(self):
        fqdn = self.cleaned_data.get('fqdn')
        if fqdn:
            return fqdn.upper()
        return fqdn

    def clean_vlan(self):
        vlan = self.cleaned_data.get('vlan')
        if vlan:
            return vlan.upper()
        return vlan

    def clean_group_contact(self):
        group_email = self.cleaned_data.get('group_contact')
        if group_email:
            try:
                validate_email(group_email)
            except ValidationError:
                raise ValidationError("Please enter a valid email address for the group contact.", code='invalid_group_email')
        return group_email

    # Ensure secondary != primary
    def clean(self):
        cleaned_data = super().clean()
        primary = cleaned_data.get("primary_contact")
        secondary = cleaned_data.get("secondary_contact")

        if secondary and primary and secondary.strip().lower() == primary.strip().lower():
            self.add_error('secondary_contact', "Secondary contact email cannot be the same as the primary contact.")

        # Validate numeric ranges (redundant if model validators work, but good practice)
        os_disk = cleaned_data.get('os_disk_gb')
        if os_disk is not None and not (100 <= os_disk <= 500):
             self.add_error('os_disk_gb', "OS Disk size must be between 100 and 500 GB.")

        data_disk = cleaned_data.get('data_disk_gb')
        if data_disk is not None and not (100 <= data_disk <= 750):
             self.add_error('data_disk_gb', "Data Disk size must be between 100 and 750 GB.")

        return cleaned_data # Return cleaned data
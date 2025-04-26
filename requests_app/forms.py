# requests_app/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import ServerRequest

class ServerRequestForm(forms.ModelForm):
    """Form for end-users to submit server requests."""
    class Meta:
        model = ServerRequest
        fields = [
            'fqdn', 'vlan', 'site', 'primary_contact', 'secondary_contact',
            'group_contact', 'notes', 'backup_required', 'monitoring_required',
            'asap_number',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'primary_contact': forms.EmailInput(), # Use EmailInput widget
            'secondary_contact': forms.EmailInput(), # Use EmailInput for hint
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Model field `primary_contact` is EmailField, making it required by default
        self.fields['fqdn'].required = True
        self.fields['vlan'].required = True
        self.fields['site'].required = True

    def clean_secondary_contact(self):
        secondary_email = self.cleaned_data.get('secondary_contact')
        if secondary_email: # Only validate if something was entered
            try:
                validate_email(secondary_email)
            except ValidationError:
                raise ValidationError("Please enter a valid email address for the secondary contact.", code='invalid')
        return secondary_email

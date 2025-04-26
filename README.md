Okay, providing full, production-ready code for an entire application is extensive and requires iterative development. However, I can provide a solid starting point using Django and its built-in admin for the IT backend, covering the core requirements you outlined.

This will be a single Django project with one app.

Assumptions:

You have Python and pip installed.

You understand basic Django concepts (or are willing to learn them as you go).

AWX is running and accessible from where you run this Django app.

You have an AWX Job Template created for server provisioning and know its ID.

You have generated an AWX API Token with permissions to launch the job template.

Project Structure:

provisioning_portal/
├── provisioning_portal/ # Django Project Directory
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── requests_app/        # Django App Directory
│   ├── __init__.py
│   ├── admin.py         # <-- Admin configuration here
│   ├── apps.py
│   ├── forms.py         # <-- User form definition here
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py        # <-- Database model definition here
│   ├── templates/
│   │   └── requests_app/
│   │       ├── base.html
│   │       ├── request_form.html
│   │       └── request_success.html
│   ├── urls.py          # <-- App-specific URLs here
│   ├── views.py         # <-- View logic here
│   └── awx_utils.py     # <-- Utility for AWX API calls
├── manage.py
└── requirements.txt


1. Setup Project and App

# Create the project directory
mkdir provisioning_portal
cd provisioning_portal

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`

# Install Django and requests
pip install django requests python-dotenv

# Create the Django project
django-admin startproject provisioning_portal .

# Create the Django app
python manage.py startapp requests_app

# Create templates directory
mkdir -p requests_app/templates/requests_app
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

2. requirements.txt

Create requirements.txt in the project root:

Django>=4.0,<5.0
requests>=2.20.0
python-dotenv>=0.19.0
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END

(Install again if needed: pip install -r requirements.txt)

3. provisioning_portal/settings.py

# provisioning_portal/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv # Add this line

# Load environment variables from .env file
load_dotenv() # Add this line

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Generate your own secret key
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-dev') # Modified

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True' # Modified

ALLOWED_HOSTS = ['*'] # Adjust for production

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Add our app
    'requests_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'provisioning_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Add the app's template directory
        'DIRS': [BASE_DIR / 'requests_app/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'provisioning_portal.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Use SQLite for simple local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Consider PostgreSQL for production/Openshift

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC' # Adjust as needed

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles' # Needed for production collection

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- AWX Configuration ---
# **IMPORTANT**: Use environment variables for sensitive data in production!
# Create a .env file in the project root for these
AWX_URL = os.getenv('AWX_URL', 'YOUR_AWX_URL_HERE') # e.g., https://awx.example.com
AWX_TOKEN = os.getenv('AWX_TOKEN', 'YOUR_AWX_API_TOKEN_HERE')
# The *numeric ID* of the Job Template in AWX to launch
AWX_JOB_TEMPLATE_ID = os.getenv('AWX_JOB_TEMPLATE_ID', 'YOUR_JOB_TEMPLATE_ID_HERE')
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

4. Create .env file

In the project root (provisioning_portal/), create a file named .env:

# .env file
DJANGO_SECRET_KEY='your-very-secret-django-key-change-me' # Generate a strong key
DJANGO_DEBUG=True # Set to False in production

# --- Fill in your actual AWX details ---
AWX_URL=https://your-awx-instance.com
AWX_TOKEN=your_secret_awx_api_token
AWX_JOB_TEMPLATE_ID=123 # Replace with your actual job template ID
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Env
IGNORE_WHEN_COPYING_END

Important: Add .env to your .gitignore file to avoid committing secrets.

5. requests_app/models.py

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
    primary_contact = models.CharField(max_length=255, help_text="Primary Contact Person/Email/Group")
    secondary_contact = models.CharField(max_length=255, blank=True, help_text="Secondary Contact (Optional)")
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
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

6. requests_app/forms.py

# requests_app/forms.py

from django import forms
from .models import ServerRequest

class ServerRequestForm(forms.ModelForm):
    """Form for end-users to submit server requests."""
    class Meta:
        model = ServerRequest
        fields = [
            'fqdn',
            'vlan',
            'site',
            'primary_contact',
            'secondary_contact',
            'group_contact',
            'notes',
            'backup_required',
            'monitoring_required',
            'asap_number',
        ]
        # You can add widgets here for customization if needed, e.g.:
        # widgets = {
        #     'notes': forms.Textarea(attrs={'rows': 4}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required or customize labels if needed
        self.fields['fqdn'].required = True
        self.fields['vlan'].required = True
        self.fields['site'].required = True
        self.fields['primary_contact'].required = True
        # Add Bootstrap classes or other attributes if using a CSS framework
        # for field_name, field in self.fields.items():
        #     field.widget.attrs['class'] = 'form-control'
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

7. requests_app/awx_utils.py

# requests_app/awx_utils.py

import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def trigger_awx_job(server_request):
    """
    Triggers the specified AWX Job Template with server_request details.

    Args:
        server_request: The ServerRequest model instance.

    Returns:
        The AWX Job ID if successfully launched, otherwise None.
    """
    awx_url = settings.AWX_URL
    awx_token = settings.AWX_TOKEN
    template_id = settings.AWX_JOB_TEMPLATE_ID

    if not all([awx_url, awx_token, template_id]):
        logger.error("AWX settings (URL, Token, Template ID) are not fully configured.")
        return None

    # Ensure template_id is an integer if it came from env var
    try:
        template_id = int(template_id)
    except (ValueError, TypeError):
         logger.error(f"Invalid AWX_JOB_TEMPLATE_ID: {template_id}. Must be an integer.")
         return None

    launch_url = f"{awx_url.rstrip('/')}/api/v2/job_templates/{template_id}/launch/"
    headers = {
        'Authorization': f'Bearer {awx_token}',
        'Content-Type': 'application/json',
    }

    # Prepare extra_vars based on the request model
    # **IMPORTANT**: Adjust these keys to match EXACTLY what your
    #              Ansible playbook expects in `extra_vars`.
    extra_vars = {
        "target_fqdn": server_request.fqdn,
        "target_vlan": server_request.vlan,
        "target_site": server_request.site,
        "req_primary_contact": server_request.primary_contact,
        "req_secondary_contact": server_request.secondary_contact,
        "req_group_contact": server_request.group_contact,
        "req_notes": server_request.notes,
        "req_backup": server_request.backup_required,
        "req_monitoring": server_request.monitoring_required,
        "req_asap_number": server_request.asap_number,
        "request_portal_id": server_request.id # Useful for potential callbacks
    }

    payload = {
        "extra_vars": json.dumps(extra_vars)
        # Add other launch parameters if needed (e.g., inventory, limit)
        # "inventory": 1,
        # "limit": server_request.fqdn,
    }

    try:
        logger.info(f"Attempting to launch AWX Job Template {template_id} for request {server_request.id} ({server_request.fqdn})")
        response = requests.post(launch_url, headers=headers, json=payload, verify=False) # Set verify=True for production with valid certs
        response.raise_for_status() # Raises HTTPError for bad responses (4XX, 5XX)

        job_data = response.json()
        job_id = job_data.get('job')

        if job_id:
            logger.info(f"Successfully launched AWX Job {job_id} for request {server_request.id}")
            return job_id
        else:
            logger.error(f"AWX job launch response did not contain a job ID. Response: {job_data}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error launching AWX job for request {server_request.id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"AWX Response Status Code: {e.response.status_code}")
            logger.error(f"AWX Response Body: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during AWX job launch for request {server_request.id}: {e}")
        return None
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

8. requests_app/admin.py

# requests_app/admin.py

from django.contrib import admin
from django.utils import timezone
from django.contrib import messages # Import messages framework
from .models import ServerRequest
from .awx_utils import trigger_awx_job # Import the utility function

@admin.register(ServerRequest)
class ServerRequestAdmin(admin.ModelAdmin):
    list_display = ('fqdn', 'status', 'site', 'primary_contact', 'requested_at', 'approved_denied_by')
    list_filter = ('status', 'site', 'backup_required', 'monitoring_required', 'requested_at')
    search_fields = ('fqdn', 'primary_contact', 'secondary_contact', 'group_contact', 'asap_number')
    ordering = ('-requested_at',)
    readonly_fields = ('requested_at', 'updated_at', 'approved_denied_at', 'approved_denied_by', 'awx_job_id')

    # Organize the admin form view
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

    # Override save_model to trigger AWX on approval
    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle status changes and trigger AWX.
        'request' is the HTTP request, 'obj' is the model instance being saved,
        'form' is the ModelForm instance, 'change' is True if editing an existing object.
        """
        original_status = None
        if obj.pk: # If the object already exists, get its original status
            try:
                original_status = ServerRequest.objects.get(pk=obj.pk).status
            except ServerRequest.DoesNotExist:
                pass # Should not happen during save of existing object

        # Check if status changed specifically *to* APPROVED
        if form.cleaned_data.get('status') == 'APPROVED' and original_status != 'APPROVED':
            obj.approved_denied_by = request.user
            obj.approved_denied_at = timezone.now()
            obj.status = 'APPROVED' # Ensure status is set

            # Trigger AWX Job
            awx_job_id = trigger_awx_job(obj)

            if awx_job_id:
                obj.awx_job_id = awx_job_id
                obj.status = 'PROVISIONING' # Update status after successful launch
                messages.success(request, f"Request approved. AWX Job {awx_job_id} launched successfully.")
            else:
                # Decide: revert status or leave as approved but warn?
                # Option 1: Revert status (safer if launch MUST succeed for approval)
                # obj.status = 'PENDING' # Revert if launch failed
                # messages.error(request, "Request approved, but FAILED to launch AWX job. Status remains Pending.")
                # Option 2: Keep Approved but warn (allows manual trigger later)
                 messages.error(request, "Request approved, but FAILED to launch AWX job. Please check AWX settings/logs and potentially trigger manually.")
                 # obj.status = 'APPROVED' # Keep as approved

        # Check if status changed specifically *to* DENIED
        elif form.cleaned_data.get('status') == 'DENIED' and original_status != 'DENIED':
            obj.approved_denied_by = request.user
            obj.approved_denied_at = timezone.now()
            messages.info(request, "Request has been denied.")

        # Check if only admin_notes changed without changing status from PENDING
        # (prevents accidentally setting approval user/time if only notes are added)
        elif original_status == 'PENDING' and form.cleaned_data.get('status') == 'PENDING':
            if 'admin_notes' in form.changed_data:
                 messages.info(request, "Admin notes updated.")
            # Don't set approval fields if status remains PENDING

        super().save_model(request, obj, form, change) # Call the original save_model

    # Optional: Add admin actions for bulk approve/deny (more advanced)
    # def make_approved(self, request, queryset): ...
    # actions = [make_approved]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

9. requests_app/views.py

# requests_app/views.py

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from .forms import ServerRequestForm
from django.contrib import messages # Import messages framework

class ServerRequestView(FormView):
    template_name = 'requests_app/request_form.html'
    form_class = ServerRequestForm
    success_url = reverse_lazy('request_success') # Use reverse_lazy for class attributes

    def form_valid(self, form):
        # Called when the form is valid. Save the form data to create the ServerRequest object.
        # The model's default status is 'PENDING', so we don't need to set it here.
        form.save()
        messages.success(self.request, "Your server request has been submitted successfully! IT will review it shortly.")
        return super().form_valid(form)

    def form_invalid(self, form):
         messages.error(self.request, "Please correct the errors in the form.")
         return super().form_invalid(form)

class RequestSuccessView(TemplateView):
    template_name = 'requests_app/request_success.html'
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

10. Templates

requests_app/templates/requests_app/base.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Server Provisioning Portal{% endblock %}</title>
    <!-- Add Bootstrap or other CSS framework links here if desired -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 20px; }
        .container { max-width: 800px; }
        .alert { margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Server Provisioning Portal</h1>

        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{% if message.tags %}{{ message.tags }}{% else %}info{% endif %}" role="alert">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}
        {% endblock %}
    </div>
    <!-- Add Bootstrap JS if needed -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Html
IGNORE_WHEN_COPYING_END

requests_app/templates/requests_app/request_form.html

{% extends "requests_app/base.html" %}

{% block title %}Request a New Server{% endblock %}

{% block content %}
    <h2>Request a New Server</h2>
    <p>Please fill out the form below to request a new server. All fields marked with * are required.</p>

    <form method="post" novalidate>
        {% csrf_token %}

        {% comment %} Render form fields using Bootstrap styling {% endcomment %}
        {% for field in form %}
            <div class="mb-3">
                <label for="{{ field.id_for_label }}" class="form-label">{{ field.label }}{% if field.field.required %} <span class="text-danger">*</span>{% endif %}</label>
                {{ field }}
                {% if field.help_text %}
                    <div class="form-text">{{ field.help_text }}</div>
                {% endif %}
                {% if field.errors %}
                    <div class="invalid-feedback d-block">
                        {{ field.errors|striptags }}
                    </div>
                {% endif %}
            </div>
        {% endfor %}

        <button type="submit" class="btn btn-primary">Submit Request</button>
    </form>
{% endblock %}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Html
IGNORE_WHEN_COPYING_END

(Self-correction: Added Bootstrap styling example to make the form look decent)

requests_app/templates/requests_app/request_success.html

{% extends "requests_app/base.html" %}

{% block title %}Request Submitted{% endblock %}

{% block content %}
    <h2>Request Submitted Successfully!</h2>
    <p>Thank you for your request. The IT department has been notified and will review your request.</p>
    <p><a href="{% url 'request_server' %}" class="btn btn-secondary">Submit another request</a></p>
{% endblock %}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Html
IGNORE_WHEN_COPYING_END

11. URL Configuration

requests_app/urls.py (Create this file)

# requests_app/urls.py

from django.urls import path
from .views import ServerRequestView, RequestSuccessView

urlpatterns = [
    path('', ServerRequestView.as_view(), name='request_server'),
    path('success/', RequestSuccessView.as_view(), name='request_success'),
]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

provisioning_portal/urls.py (Modify existing file)

# provisioning_portal/urls.py

from django.contrib import admin
from django.urls import path, include # Add include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the app's URLs for the user-facing part
    path('', include('requests_app.urls')),
]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

12. Run Migrations and Create Superuser

# Make sure your virtual environment is active
# source venv/bin/activate

# Create database migrations based on models.py
python manage.py makemigrations requests_app

# Apply migrations to create database tables
python manage.py migrate

# Create an admin user to log into /admin/
python manage.py createsuperuser
# Follow prompts for username, email, password
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

13. Run the Development Server

python manage.py runserver
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Accessing the Portal:

User Request Form: Open your browser to http://127.0.0.1:8000/

Admin Backend: Open your browser to http://127.0.0.1:8000/admin/ and log in with the superuser credentials you created.

How it Works:

Users go to / and fill out the ServerRequestForm.

Upon valid submission, a ServerRequest object is created in the database with status='PENDING'.

The user is redirected to /success/.

IT staff log in to /admin/.

They navigate to the "Server Requests" section.

They can view pending requests, click on one to see details.

To approve: They change the Status dropdown to Approved - Queued for Provisioning and click "Save".

The save_model override in admin.py detects this change.

It calls trigger_awx_job from awx_utils.py.

trigger_awx_job makes a REST API call to your AWX instance to launch the specified job template, passing request details as extra_vars.

If the AWX API call is successful and returns a job ID, the request status is updated to PROVISIONING, the awx_job_id is stored, and a success message is shown in the admin.

If the AWX API call fails, an error message is shown in the admin.

To deny: They change the Status to Denied and click "Save". The save_model override updates the timestamp and user, and shows an info message.

Next Steps & Considerations:

Security: DO NOT run with DEBUG=True or the default SECRET_KEY in production. Use environment variables for all secrets (SECRET_KEY, AWX_TOKEN, Database credentials). Configure ALLOWED_HOSTS.

Database: Switch from SQLite to PostgreSQL (or another robust DB) for production/Openshift. Use dj-database-url package to easily configure from environment variables.

AWX Status Feedback: This code only launches the job. You'll need a mechanism (AWX Callbacks/Webhooks hitting a new Django API endpoint, or a periodic task like Celery Beat) to check the AWX job status and update the ServerRequest.status to COMPLETED or FAILED.

Error Handling: Improve error handling in awx_utils.py and provide clearer feedback.

Styling: Customize the base.html and potentially use Django template tags or widgets for better form rendering if Bootstrap isn't sufficient.

User Authentication (User Portal): The current user portal has no auth. You might add Django's standard auth or SSO later if needed.

Deployment (Openshift):

Containerize the Django app using a Dockerfile.

Use Gunicorn or uWSGI as the application server inside the container.

Configure Openshift DeploymentConfig, Service, Route.

Manage secrets (AWX_TOKEN, SECRET_KEY, DB password) using Openshift Secrets.

Use Openshift ConfigMap for non-sensitive settings (like AWX_URL, AWX_JOB_TEMPLATE_ID).

Configure a PostgreSQL database instance within Openshift or connect to an external one.

Set up persistent storage (PersistentVolumeClaim) for the database and potentially static/media files if needed.

Testing: Write unit and integration tests.

This provides a comprehensive starting point for your Django-based provisioning portal. Remember to adapt the extra_vars keys in awx_utils.py to match your specific Ansible playbook variables.
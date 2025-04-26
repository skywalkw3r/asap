# requests_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from .forms import ServerRequestStep1Form, ServerRequestStep2Form # Import new forms
from .models import ServerRequest, AuditLog # Import models
from django.contrib import messages
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

SESSION_KEY_STEP1 = 'server_request_step1_data'

# --- Step 1 View ---
class ServerRequestStep1View(View):
    form_class = ServerRequestStep1Form
    template_name = 'requests_app/request_form_step1.html'

    def get(self, request, *args, **kwargs):
        initial_data = request.session.get(SESSION_KEY_STEP1, {})
        form = self.form_class(initial=initial_data)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            request.session[SESSION_KEY_STEP1] = form.cleaned_data
            logger.info(f"Step 1 data stored in session: {form.cleaned_data}")
            return redirect('request_server_step2')
        else:
            logger.warning(f"Step 1 form invalid: {form.errors}")
            messages.error(request, "Please correct the errors in Step 1.")
            return render(request, self.template_name, {'form': form})

# --- Step 2 View ---
class ServerRequestStep2View(View):
    form_class = ServerRequestStep2Form
    template_name = 'requests_app/request_form_step2.html'

    def get(self, request, *args, **kwargs):
        step1_data = request.session.get(SESSION_KEY_STEP1)
        if not step1_data:
            messages.warning(request, "Please complete Step 1 first.")
            return redirect('request_server_step1')
        form = self.form_class() # Initialize empty or with session if needed
        return render(request, self.template_name, {'form': form, 'step1_data': step1_data})

    def post(self, request, *args, **kwargs):
        step1_data = request.session.get(SESSION_KEY_STEP1)
        if not step1_data:
            messages.error(request, "Session data missing. Please start from Step 1.")
            return redirect('request_server_step1')

        form = self.form_class(request.POST)

        if form.is_valid():
            final_data = {**step1_data, **form.cleaned_data}
             # Handle potential None for data_disk_gb if field was left blank
            if 'data_disk_gb' in final_data and final_data['data_disk_gb'] == '':
                final_data['data_disk_gb'] = None
            logger.info(f"Step 2 form valid. Combined data ready for saving.")

            try:
                # Create ServerRequest instance but don't save yet if needing manipulation
                # server_request = ServerRequest(**final_data) # This works if keys match model fields
                server_request = form.save(commit=False) # Start with step 2 instance
                # Populate with step 1 data
                for key, value in step1_data.items():
                     setattr(server_request, key, value)
                # Save the complete object
                server_request.save()
                logger.info(f"Server request {server_request.id} ({server_request.fqdn}) created and saved.")

                # --- Send Emails ---
                try:
                    admin_path = reverse('admin:requests_app_serverrequest_change', args=[server_request.id])
                    admin_url = self.request.build_absolute_uri(admin_path)
                    status_path = reverse('request_status', kwargs={'pk': server_request.id})
                    status_url = self.request.build_absolute_uri(status_path)
                    context = {'request': server_request, 'admin_url': admin_url, 'status_url': status_url}

                    # IT Notification
                    it_subject = f"New ASAP Server Request Submitted: {server_request.fqdn} (ID: {server_request.id})"
                    it_html_content = render_to_string('requests_app/email/it_notification.html', context)
                    it_text_content = strip_tags(it_html_content)
                    it_recipients = [mail.strip() for mail in settings.IT_EMAIL_DISTRO_LIST.split(',') if mail.strip()]
                    msg_it = EmailMultiAlternatives(it_subject, it_text_content, settings.DEFAULT_FROM_EMAIL, it_recipients)
                    msg_it.attach_alternative(it_html_content, "text/html")
                    msg_it.send(fail_silently=False)
                    logger.info(f"IT notification sent for request {server_request.id}")

                    # User Confirmation
                    user_subject = f"ASAP Server Request Submitted (ID: {server_request.id})"
                    user_html_content = render_to_string('requests_app/email/user_confirmation.html', context)
                    user_text_content = strip_tags(user_html_content)
                    user_recipients = [server_request.primary_contact]
                    if server_request.secondary_contact and server_request.secondary_contact.lower() != server_request.primary_contact.lower():
                        user_recipients.append(server_request.secondary_contact)
                    msg_user = EmailMultiAlternatives(user_subject, user_text_content, settings.DEFAULT_FROM_EMAIL, user_recipients)
                    msg_user.attach_alternative(user_html_content, "text/html")
                    msg_user.send(fail_silently=False)
                    logger.info(f"User confirmation sent for request {server_request.id}")

                    messages.success(self.request, "Your server request has been submitted successfully! Confirmation emails have been sent.")

                except Exception as e:
                    logger.error(f"Failed to send email for request {server_request.id}: {e}", exc_info=True)
                    messages.warning(self.request, "Request submitted, but failed to send confirmation emails.")
                # --- End Send Emails ---

                if SESSION_KEY_STEP1 in request.session:
                    del request.session[SESSION_KEY_STEP1] # Clear session

                return redirect('request_success')

            except Exception as e:
                 logger.error(f"Error saving combined server request form data: {e}", exc_info=True)
                 messages.error(self.request, "An critical error occurred while saving your complete request. Please contact IT.")
                 return render(request, self.template_name, {'form': form, 'step1_data': step1_data})
        else:
            logger.warning(f"Step 2 form invalid: {form.errors}")
            messages.error(request, "Please correct the errors in Step 2.")
            return render(request, self.template_name, {'form': form, 'step1_data': step1_data})

# --- Success View ---
class RequestSuccessView(TemplateView):
    template_name = 'requests_app/request_success.html'

# --- Status View ---
def request_status_view(request, pk):
    server_request = get_object_or_404(ServerRequest, pk=pk)
    audit_logs = server_request.audit_logs.all().order_by('timestamp')
    context = {'request': server_request, 'audit_logs': audit_logs}
    return render(request, 'requests_app/status.html', context)

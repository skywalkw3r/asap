# requests_app/views.py

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView
from .forms import ServerRequestForm
from django.contrib import messages
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class ServerRequestView(FormView):
    template_name = 'requests_app/request_form.html'
    form_class = ServerRequestForm
    success_url = reverse_lazy('request_success')

    def form_valid(self, form):
        try:
            # Save the form and get the request object
            server_request = form.save()
            logger.info(f"Server request {server_request.id} ({server_request.fqdn}) saved successfully.")
        except Exception as e:
             logger.error(f"Error saving server request form: {e}", exc_info=True)
             messages.error(self.request, "An error occurred while saving your request. Please try again.")
             # Return the invalid form response
             return super().form_invalid(form)

        # Proceed with email sending only if save was successful
        try:
            # Build URLs needed for emails
            admin_path = reverse('admin:requests_app_serverrequest_change', args=[server_request.id])
            admin_url = self.request.build_absolute_uri(admin_path)
            status_path = reverse('request_status', kwargs={'pk': server_request.id})
            status_url = self.request.build_absolute_uri(status_path)

            context = {
                'request': server_request,
                'admin_url': admin_url,
                'status_url': status_url,
            }

            # 1. Send notification to IT
            it_subject = f"New ASAP Server Request Submitted: {server_request.fqdn} (ID: {server_request.id})"
            it_html_content = render_to_string('requests_app/email/it_notification.html', context)
            it_text_content = strip_tags(it_html_content) # Use strip_tags for simple text version
            it_recipients = [mail.strip() for mail in settings.IT_EMAIL_DISTRO_LIST.split(',') if mail.strip()] # Handle comma-separated list

            msg_it = EmailMultiAlternatives(it_subject, it_text_content, settings.DEFAULT_FROM_EMAIL, it_recipients)
            msg_it.attach_alternative(it_html_content, "text/html")
            msg_it.send(fail_silently=False)
            logger.info(f"IT notification sent for request {server_request.id} to {settings.IT_EMAIL_DISTRO_LIST}")

            # 2. Send confirmation to User(s)
            user_subject = f"ASAP Server Request Submitted (ID: {server_request.id})"
            user_html_content = render_to_string('requests_app/email/user_confirmation.html', context)
            user_text_content = strip_tags(user_html_content) # Use strip_tags for simple text version
            user_recipients = [server_request.primary_contact]
            if server_request.secondary_contact:
                if server_request.secondary_contact.lower() != server_request.primary_contact.lower():
                     user_recipients.append(server_request.secondary_contact)

            msg_user = EmailMultiAlternatives(user_subject, user_text_content, settings.DEFAULT_FROM_EMAIL, user_recipients)
            msg_user.attach_alternative(user_html_content, "text/html")
            msg_user.send(fail_silently=False)
            logger.info(f"User confirmation sent for request {server_request.id} to {', '.join(user_recipients)}")

            messages.success(self.request, "Your server request has been submitted successfully! Confirmation emails have been sent.")

        except Exception as e:
            # Log the error but don't prevent the user from seeing the success page
            logger.error(f"Failed to send email for request {server_request.id}: {e}", exc_info=True)
            # Notify user that request was saved but email failed
            messages.warning(self.request, "Your server request was submitted, but there was an error sending confirmation emails. Please contact IT if needed.")

        # Redirect to the success URL after everything (even if emails failed)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
         messages.error(self.request, "Please correct the errors in the form.")
         return super().form_invalid(form)

class RequestSuccessView(TemplateView):
    template_name = 'requests_app/request_success.html'

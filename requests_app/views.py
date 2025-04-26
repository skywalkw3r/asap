# requests_app/views.py
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from .forms import ServerRequestStep1Form, ServerRequestStep2Form
from .models import ServerRequest
from django.contrib import messages
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)
SESSION_KEY_STEP1 = 'server_request_step1_data'

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
            logger.info(f"Step 1 data stored in session.") # Avoid logging data
            return redirect('request_server_step2')
        else:
            logger.warning(f"Step 1 form invalid: {form.errors}")
            messages.error(request, "Please correct the errors in Step 1.")
            return render(request, self.template_name, {'form': form})

class ServerRequestStep2View(View):
    form_class = ServerRequestStep2Form
    template_name = 'requests_app/request_form_step2.html'
    def get(self, request, *args, **kwargs):
        step1_data = request.session.get(SESSION_KEY_STEP1)
        if not step1_data:
            messages.warning(request, "Please complete Step 1 first.")
            return redirect('request_server_step1')
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'step1_data': step1_data})
    def post(self, request, *args, **kwargs):
        step1_data = request.session.get(SESSION_KEY_STEP1)
        if not step1_data:
            messages.error(request, "Session data missing. Please start from Step 1.")
            return redirect('request_server_step1')
        form = self.form_class(request.POST)
        if form.is_valid():
            final_data = {**step1_data, **form.cleaned_data}
            if 'hypervisor_type' not in final_data or not final_data['hypervisor_type']:
                 final_data['hypervisor_type'] = ServerRequest._meta.get_field('hypervisor_type').get_default()
            logger.info(f"Step 2 form valid. Combined data ready for save.")
            try:
                server_request = ServerRequest(**final_data); server_request.save()
                logger.info(f"Server request {server_request.id} ({server_request.fqdn}) created.")
                self.send_notifications(request, server_request)
                if SESSION_KEY_STEP1 in request.session: del request.session[SESSION_KEY_STEP1]
                return redirect('request_success')
            except Exception as e:
                 logger.error(f"Error saving combined server request: {e}", exc_info=True)
                 messages.error(self.request, "An critical error occurred saving your request. Contact IT.")
                 return render(request, self.template_name, {'form': form, 'step1_data': step1_data})
        else:
            logger.warning(f"Step 2 form invalid: {form.errors}")
            messages.error(request, "Please correct the errors in Step 2.")
            return render(request, self.template_name, {'form': form, 'step1_data': step1_data})
    def send_notifications(self, request, server_request):
        try:
            admin_path=reverse('admin:requests_app_serverrequest_change',args=[server_request.id]); admin_url=request.build_absolute_uri(admin_path)
            status_path=reverse('request_status',kwargs={'pk': server_request.id}); status_url=request.build_absolute_uri(status_path)
            context={'request':server_request,'admin_url':admin_url,'status_url':status_url}
            it_subject=f"New ASAP Server Request: {server_request.fqdn} (ID: {server_request.id})"; it_html=render_to_string('requests_app/email/it_notification.html',context); it_text=strip_tags(it_html)
            it_recipients=[mail.strip() for mail in settings.IT_EMAIL_DISTRO_LIST.split(',') if mail.strip()]
            msg_it=EmailMultiAlternatives(it_subject,it_text,settings.DEFAULT_FROM_EMAIL,it_recipients); msg_it.attach_alternative(it_html,"text/html"); msg_it.send(fail_silently=False); logger.info(f"IT mail sent for req {server_request.id}")
            user_subject=f"ASAP Server Request Submitted (ID: {server_request.id})"; user_html=render_to_string('requests_app/email/user_confirmation.html',context); user_text=strip_tags(user_html)
            user_recipients=[server_request.primary_contact]
            if server_request.secondary_contact and server_request.secondary_contact.lower()!=server_request.primary_contact.lower(): user_recipients.append(server_request.secondary_contact)
            msg_user=EmailMultiAlternatives(user_subject,user_text,settings.DEFAULT_FROM_EMAIL,user_recipients); msg_user.attach_alternative(user_html,"text/html"); msg_user.send(fail_silently=False); logger.info(f"User mail sent for req {server_request.id}")
            messages.success(request, "Request submitted successfully! Emails sent.")
        except Exception as e: logger.error(f"Failed sending email for req {server_request.id}: {e}", exc_info=True); messages.warning(request, "Request submitted, but failed sending emails.")

class RequestSuccessView(TemplateView): template_name = 'requests_app/request_success.html'

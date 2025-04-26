# requests_app/urls.py
from django.urls import path
from django.views.generic import TemplateView
from .views import ServerRequestStep1View, ServerRequestStep2View, RequestSuccessView
urlpatterns = [
    path('', ServerRequestStep1View.as_view(), name='request_server_step1'),
    path('step2/', ServerRequestStep2View.as_view(), name='request_server_step2'),
    path('success/', RequestSuccessView.as_view(), name='request_success'),
    path('status/<int:pk>/', TemplateView.as_view(template_name="requests_app/status_placeholder.html"), name='request_status'),
    path('terms/', TemplateView.as_view(template_name="requests_app/terms.html"), name='terms_conditions'),
]

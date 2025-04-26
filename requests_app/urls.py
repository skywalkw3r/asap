# requests_app/urls.py
from django.urls import path
from django.views.generic import TemplateView
from .views import ServerRequestView, RequestSuccessView

urlpatterns = [
    path('', ServerRequestView.as_view(), name='request_server'),
    path('success/', RequestSuccessView.as_view(), name='request_success'),
    path(
        'status/<int:pk>/',
        TemplateView.as_view(template_name="requests_app/status_placeholder.html"),
        name='request_status'
    ),
    # Add URL for terms and conditions
    path(
        'terms/',
        TemplateView.as_view(template_name="requests_app/terms.html"),
        name='terms_conditions'
    ),
]
# provisioning_portal/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('requests_app.urls')), # Include app URLs
]

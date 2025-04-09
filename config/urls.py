from django.contrib import admin
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from llmchatbot.views import *
from .health import health_check


urlpatterns = [
    path("admin/", admin.site.urls),
    path('team3/llmchatbot/', include('llmchatbot.urls')),
    path('',  TemplateView.as_view(template_name="main.html"), name="root"),
    path('actuator/health/', health_check),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
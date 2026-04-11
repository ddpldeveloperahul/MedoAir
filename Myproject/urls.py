"""
URL configuration for Myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from api.views import (
    ai_assistant_page,
    ai_daily_dashboard_page,
    ai_medicines_page,
    ai_patient_timeline_page,
    ai_weekly_report_page,
)

urlpatterns = [
    
    path("admin/", admin.site.urls),
    path('ai/assistant/', ai_assistant_page, name='ai-assistant-page'),
    path('ai/dashboard/', ai_daily_dashboard_page, name='ai-daily-dashboard-page'),
    path('ai/medicines/', ai_medicines_page, name='ai-medicines-page'),
    path('ai/weekly-report/', ai_weekly_report_page, name='ai-weekly-report-page'),
    path('ai/patient-timeline/', ai_patient_timeline_page, name='ai-patient-timeline-page'),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # path('reports/', include('reports.urls')),
    
    
 

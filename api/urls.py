"""
Unified URLs - All API endpoints consolidated into one app
"""

from django.urls import path
from .views import (
    # Home
    home,
    
    # Authentication Views
    UserSignupAPIView, 
    DoctorSignupAPIView,
    LoginAPIView, 
    ForgotPasswordAPIView, 
    ResetPasswordAPIView, 
    ResendOTPAPIView,
    
    # Patient Views
    PatientProfileAPIView, 
    PatientDetailAPIView, 
    PatientMyProfileAPIView,
    PatientHealthSummaryAPIView, 
    PatientHealthMetricsAPIView,
    PatientBulkHealthUpdateAPIView,
    
    # Doctor Views
    DoctorProfileView,
    DoctorDashboardAPIView,
    CompletedPatientsView,
    
    # Appointment & Slot Views
    AppointmentAPIView, 
    SlotAPIView,
    
    # Message & Chat Views
    MessageListAPIView,
    ChatAPIView,
    ChatHistoryAPIView,
    DeleteMessageAPIView,
    
    # Report Views
    ReportAPIView,
    
    # Super Admin Views
    SuperAdminDashboardAPIView, 
    SuperAdminUserAPIView, 
    SuperAdminDoctorAPIView, 
    SuperAdminPatientAPIView, 
    SuperAdminAppointmentAPIView,
    
    # Video Call
    video_call,
)

urlpatterns = [
    # ========== HOME/INDEX ==========
    path('index/', home, name='home'),  # API root endpoint for navigation
    
    # ========== AUTHENTICATION ENDPOINTS ==========
    path('user/signup/', UserSignupAPIView.as_view(), name='user-signup'),
    path('doctor/signup/', DoctorSignupAPIView.as_view(), name='doctor-signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('resend-otp/', ResendOTPAPIView.as_view(), name='resend-otp'),
    
    # ========== PATIENT PROFILE ENDPOINTS ==========
    path('patients/', PatientProfileAPIView.as_view(), name='patient-list'),
    path('patients/<int:patient_id>/', PatientDetailAPIView.as_view(), name='patient-detail'),
    path('patients/me/', PatientMyProfileAPIView.as_view(), name='patient-my-profile'),
    path('patients/health-summary/', PatientHealthSummaryAPIView.as_view(), name='patient-health-summary'),
    path('patients/<int:patient_id>/health-metrics/', PatientHealthMetricsAPIView.as_view(), name='patient-health-metrics'),
    path('patients/health-update/', PatientBulkHealthUpdateAPIView.as_view(), name='patient-health-update'),
    
    # ========== DOCTOR PROFILE ENDPOINTS ==========
    path('doctors/', DoctorProfileView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>/', DoctorProfileView.as_view(), name='doctor-detail'),
    path('doctor/completed-patients/', CompletedPatientsView.as_view(), name='doctor-completed-patients'),
    path('doctor/dashboard/', DoctorDashboardAPIView.as_view(), name='doctor-dashboard'),
    
    # ========== APPOINTMENT & SLOT ENDPOINTS ==========
    path('slots/', SlotAPIView.as_view(), name='slot-list'),
    path('slots/<int:pk>/', SlotAPIView.as_view(), name='slot-detail'),
    path('appointments/', AppointmentAPIView.as_view(), name='appointment-list'),
    path('appointments/<int:pk>/', AppointmentAPIView.as_view(), name='appointment-detail'),
    
    # ========== MESSAGE/CHAT ENDPOINTS ==========
    path('api/appointments/<int:appointment_id>/messages/', MessageListAPIView.as_view(), name='message-list'),
    path('chat/<int:appointment_id>/', ChatAPIView.as_view(), name='chat-detail'),
    path('chat2/<int:appointment_id>/', ChatHistoryAPIView.as_view(), name='chat-history'),
    path('messages/<int:message_id>/', DeleteMessageAPIView.as_view(), name='message-delete'),
    path('video_call/', video_call, name='video_call'),
    
    # ========== REPORT ENDPOINTS ==========
    path('reports/', ReportAPIView.as_view(), name='report-list'),
    path('reports/<int:report_id>/', ReportAPIView.as_view(), name='report-detail'),
    
    # ========== SUPER ADMIN ENDPOINTS ==========
    path('admin/dashboard/', SuperAdminDashboardAPIView.as_view(), name='admin-dashboard'),
    path('admin/users/', SuperAdminUserAPIView.as_view(), name='admin-user-list'),
    path('admin/users/<int:user_id>/', SuperAdminUserAPIView.as_view(), name='admin-user-detail'),
    path('admin/doctors/', SuperAdminDoctorAPIView.as_view(), name='admin-doctor-list'),
    path('admin/doctors/<int:doctor_id>/', SuperAdminDoctorAPIView.as_view(), name='admin-doctor-detail'),
    path('admin/patients/', SuperAdminPatientAPIView.as_view(), name='admin-patient-list'),
    path('admin/patients/<int:patient_id>/', SuperAdminPatientAPIView.as_view(), name='admin-patient-detail'),
    path('admin/appointments/', SuperAdminAppointmentAPIView.as_view(), name='admin-appointment-list'),
    path('admin/appointments/<int:appointment_id>/', SuperAdminAppointmentAPIView.as_view(), name='admin-appointment-detail'),
]

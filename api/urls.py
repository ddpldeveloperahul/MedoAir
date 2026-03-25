"""
Unified URLs - All API endpoints consolidated into one app
"""

from django.urls import path
from .views import (
    # User CRUD
    AppointmentAPIView, DoctorDashboardAPIView, SlotAPIView, DoctorProfileView, PatientProfileAPIView, UserListAPIView, UserDetailAPIView, CurrentUserAPIView,
    ChangePasswordAPIView, UserProfileStatsAPIView,
    
    # Authentication
    UserSignupAPIView, LoginAPIView, DoctorSignupAPIView,
    ForgotPasswordAPIView, VerifyOTPAPIView, ResetPasswordAPIView, ResendOTPAPIView,
    
    # Patient
    PatientProfileAPIView, PatientDetailAPIView, PatientMyProfileAPIView,
    PatientHealthSummaryAPIView, PatientHealthMetricsAPIView,
    PatientBulkHealthUpdateAPIView,
    
    # Appointment
    AppointmentAPIView, DoctorProfileView    ,
    
    # Messages
    MessageListAPIView,
    
    # Reports
    ReportListAPIView,
)

urlpatterns = [
    # ========== USER CRUD ENDPOINTS ==========
    path('api/users/', UserListAPIView.as_view(), name='user-list'),
    path('api/users/<int:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('api/users/me/', CurrentUserAPIView.as_view(), name='current-user'),
    path('api/users/change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('api/users/profile-stats/', UserProfileStatsAPIView.as_view(), name='profile-stats'),
    
    # ========== AUTHENTICATION ENDPOINTS ==========
    path('user/signup/', UserSignupAPIView.as_view(), name='user-signup'),
    path('doctor/signup/', DoctorSignupAPIView.as_view(), name='doctor-signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('resend-otp/', ResendOTPAPIView.as_view(), name='resend-otp'),
    
    # ========== PATIENT PROFILE ENDPOINTS ==========
    path('patients/', PatientProfileAPIView.as_view(), name='patient-list'),
    path('patients/<int:patient_id>/', PatientDetailAPIView.as_view(), name='patient-detail'),
    path('patients/me/', PatientMyProfileAPIView.as_view(), name='patient-my-profile'),
    path('patients/health-summary/', PatientHealthSummaryAPIView.as_view(), name='patient-health-summary'),
    path('patients/<int:patient_id>/health-metrics/', PatientHealthMetricsAPIView.as_view(), name='patient-health-metrics'),
    path('patients/health-update/', PatientBulkHealthUpdateAPIView.as_view(), name='patient-health-update'),
    
    
    #====================== APPOINTMENT ENDPOINTS ==========
    path('doctors/', DoctorProfileView.as_view()),          # LIST + CREATE
    path('doctors/<int:pk>/', DoctorProfileView.as_view()), # DETAIL + UPDATE + DELETE
    
    
    
    # ========== APPOINTMENT ENDPOINTS ==========
    path('api/slots/', SlotAPIView.as_view()),          # GET list + POST
    path('api/slots/<int:pk>/', SlotAPIView.as_view()),  # GET one + PUT + DELETE
    
    
    path('api/appointments/', AppointmentAPIView.as_view()),        # LIST + CREATE
    path('api/appointments/<int:pk>/', AppointmentAPIView.as_view()), # DETAIL + UPDATE + DELETE
    path('api/doctor/dashboard/', DoctorDashboardAPIView.as_view()),
    
    # ========== MESSAGE/CHAT ENDPOINTS ==========
    path('api/appointments/<int:appointment_id>/messages/', MessageListAPIView.as_view(), name='message-list'),
    
    # ========== REPORT ENDPOINTS ==========
    path('api/reports/', ReportListAPIView.as_view(), name='report-list'),
]

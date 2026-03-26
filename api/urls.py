"""
Unified URLs - All API endpoints consolidated into one app
"""

from django.urls import path
from .views import (
    # User CRUD
    AppointmentAPIView, DoctorDashboardAPIView, ReportAPIView, SlotAPIView, DoctorProfileView, PatientProfileAPIView, UserListAPIView, UserDetailAPIView, CurrentUserAPIView,
    ChangePasswordAPIView, UserProfileStatsAPIView,
    
    # Authentication
    UserSignupAPIView, LoginAPIView, DoctorSignupAPIView,
    ForgotPasswordAPIView, ResetPasswordAPIView, ResendOTPAPIView,
    
    # Patient
    PatientProfileAPIView, PatientDetailAPIView, PatientMyProfileAPIView,
    PatientHealthSummaryAPIView, PatientHealthMetricsAPIView,
    PatientBulkHealthUpdateAPIView,
    
    # Appointment
    AppointmentAPIView, DoctorProfileView    ,
    
    # Messages
    MessageListAPIView,
    
    # Reports
    ReportAPIView,
)


from  api import views
urlpatterns = [
    path('index/', views.home, name='home'),  # API root endpoint for navigation
    # ========== USER CRUD ENDPOINTS ==========
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/me/', CurrentUserAPIView.as_view(), name='current-user'),
    path('users/change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('users/profile-stats/', UserProfileStatsAPIView.as_view(), name='profile-stats'),
    
    # ========== AUTHENTICATION ENDPOINTS ==========
    path('user/signup/', UserSignupAPIView.as_view(), name='user-signup'),
    path('doctor/signup/', DoctorSignupAPIView.as_view(), name='doctor-signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    # path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
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
    path('slots/', SlotAPIView.as_view()),          # GET list + POST
    path('slots/<int:pk>/', SlotAPIView.as_view()),  # GET one + PUT + DELETE
    
    
    path('appoinments/', AppointmentAPIView.as_view()),        # LIST + CREATE
    path('appoinments/<int:pk>/', AppointmentAPIView.as_view()), # DETAIL + UPDATE + DELETE
    path('doctor/dashboard/', DoctorDashboardAPIView.as_view()),
    
    # ========== MESSAGE/CHAT ENDPOINTS ==========
    path('api/appointments/<int:appointment_id>/messages/', MessageListAPIView.as_view(), name='message-list'),
    
    # ========== REPORT ENDPOINTS ==========
    path('reports/', ReportAPIView.as_view()),
    path('reports/<int:report_id>/', ReportAPIView.as_view()),
]

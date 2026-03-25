from django.contrib import admin
from .models import (
    User, PasswordResetOTP, PatientProfile, DoctorProfile, Department,
    Appointment, Message, Report, Slot  # Slot add kiya agar use kar rahe ho
)

# ================= USER =================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','email', 'username', 'role', 'date_joined']
    list_filter = ['role']
    search_fields = ['email', 'first_name', 'username']
    readonly_fields = ['date_joined', 'last_login']


# ================= OTP =================
@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'otp', 'is_used', 'created_at']
    list_filter = ['is_used']
    search_fields = ['user__email']
    readonly_fields = ['created_at']


# ================= PATIENT =================
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'blood_group', 'activity', 'stress', 'updated_at']
    list_filter = ['blood_group', 'activity', 'stress']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


# ================= DEPARTMENT =================
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


# ================= DOCTOR =================
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'department', 'specialization', 'experience', 'is_online']
    list_filter = ['department', 'is_online']
    search_fields = ['user__email', 'specialization']


# ================= SLOT =================
@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'date', 'start_time','end_time', 'is_booked']
    list_filter = ['date', 'is_booked']
    search_fields = ['doctor__email']


# ================= APPOINTMENT =================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'slot', 'status', 'appointment_type']
    list_filter = ['status', 'appointment_type']
    search_fields = ['patient__email', 'doctor__email']
    readonly_fields = ['created_at', 'updated_at']


# ================= MESSAGE =================
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'chat', 'created_at', 'is_read']
    list_filter = ['is_read']
    search_fields = ['sender__email', 'message']
    readonly_fields = ['created_at']


# ================= REPORT =================
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['user__email', 'title']
    readonly_fields = ['uploaded_at']
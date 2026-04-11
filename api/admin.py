from django.contrib import admin
from .models import (
    User, PasswordResetOTP, PatientProfile, DoctorProfile, Department,
    Appointment, Message, Report, Slot, AIAnalysisRecord,
    DailyHealthLog, MedicationSchedule, MedicationDoseLog  # Slot add kiya agar use kar rahe ho
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
    list_display = ['id', 'sender',"receiver","message", 'chat', 'created_at', 'is_read']
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


# ================= AI ANALYSIS =================
@admin.register(AIAnalysisRecord)
class AIAnalysisRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'short_input_message',
        'short_assistant_response',
        'detected_problem',
        'risk_probability',
        'response_language',
        'created_at',
    ]
    list_display_links = [
        'id',
        'user',
        'short_input_message',
        'short_assistant_response',
        'detected_problem',
        'risk_probability',
        'response_language',
        'created_at',
    ]
    list_filter = ['response_language', 'detected_problem', 'created_at']
    search_fields = ['user__email', 'input_message', 'detected_problem', 'assistant_response']
    readonly_fields = [
        'user',
        'log_date',
        'input_message',
        'symptoms',
        'symptoms_text',
        'notes',
        'food_type',
        'water_intake_glasses',
        'sleep_hours',
        'sleep_quality',
        'stress_level',
        'energy_level',
        'matched_symptoms',
        'detected_problem',
        'risk_probability',
        'model_name',
        'top_predictions',
        'reference_symptoms',
        'care_guidance',
        'medicine_guidance',
        'warning_signs',
        'submitted_context',
        'follow_up_questions',
        'assistant_response',
        'response_language',
        'created_at',
    ]
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'log_date', 'created_at', 'response_language')
        }),
        ('User Input', {
            'fields': (
                'input_message',
                'symptoms',
                'symptoms_text',
                'notes',
            )
        }),
        ('Lifestyle Context', {
            'fields': (
                'food_type',
                'water_intake_glasses',
                'sleep_hours',
                'sleep_quality',
                'stress_level',
                'energy_level',
            )
        }),
        ('Prediction Output', {
            'fields': (
                'detected_problem',
                'risk_probability',
                'model_name',
                'matched_symptoms',
                'top_predictions',
                'reference_symptoms',
            )
        }),
        ('Guidance Output', {
            'fields': (
                'care_guidance',
                'medicine_guidance',
                'warning_signs',
                'follow_up_questions',
                'assistant_response',
                'submitted_context',
            )
        }),
    )
    ordering = ['-created_at']

    def short_input_message(self, obj):
        value = (obj.input_message or '').strip()
        if len(value) <= 50:
            return value or '-'
        return f"{value[:50]}..."

    short_input_message.short_description = 'Input Message'

    def short_assistant_response(self, obj):
        value = (obj.assistant_response or '').strip()
        if len(value) <= 90:
            return value or '-'
        return f"{value[:90]}..."

    short_assistant_response.short_description = 'Output Preview'


# ================= DAILY HEALTH LOG =================
@admin.register(DailyHealthLog)
class DailyHealthLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'log_date',
        'short_symptoms',
        'food_type',
        'water_intake_glasses',
        'sleep_hours',
        'stress_level',
        'energy_level',
        'updated_at',
    ]
    list_filter = ['log_date', 'food_type', 'sleep_quality', 'stress_level', 'energy_level']
    search_fields = ['user__email', 'symptoms_text', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-log_date', '-updated_at']

    def short_symptoms(self, obj):
        items = obj.symptoms or []
        if not items:
            return '-'
        text = ", ".join(items[:4])
        if len(items) > 4:
            text += "..."
        return text

    short_symptoms.short_description = 'Symptoms'


# ================= MEDICATION SCHEDULE =================
@admin.register(MedicationSchedule)
class MedicationScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'name',
        'dose',
        'duration_days',
        'start_date',
        'end_date',
        'source',
        'is_active',
        'created_at',
    ]
    list_filter = ['source', 'is_active', 'start_date', 'created_at']
    search_fields = ['user__email', 'name', 'dose', 'instructions']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


# ================= MEDICATION DOSE LOG =================
@admin.register(MedicationDoseLog)
class MedicationDoseLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'medication',
        'dose_date',
        'timing',
        'status',
        'marked_at',
    ]
    list_filter = ['status', 'timing', 'dose_date', 'marked_at']
    search_fields = ['medication__user__email', 'medication__name', 'medication__dose']
    readonly_fields = ['marked_at']
    ordering = ['-dose_date', '-marked_at']

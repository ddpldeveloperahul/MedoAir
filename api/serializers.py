"""
Unified Serializers - All serializers consolidated into one file
"""

from rest_framework import serializers # type: ignore
from decimal import Decimal
from .models import (
    User,
    PasswordResetOTP,
    PatientProfile,
    DoctorProfile,
    Department,
    Appointment,
    Message,
    Report,
    DailyHealthLog,
    AIAnalysisRecord,
    MedicationSchedule,
    MedicationDoseLog,
)
from django.contrib.auth import get_user_model
import re
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


# ============== USER SERIALIZERS ==============

class UserSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username',
            'phone', 'address', 'profile_image',
            'profile_image_url', 'date_of_birth',
            'gender', 'role'
        ]
        read_only_fields = ['id']

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url) if request else obj.profile_image.url
        return None


class UserSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_username(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters")

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")

        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        if len(password) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")

        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError("Password must contain at least 1 number")

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['username'],  # ✅ FIX (IMPORTANT)
            role='patient'
        )

        return user
    
# ============== PASSWORD RESET SERIALIZERS ==============

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email not registered")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp_record = PasswordResetOTP.objects.filter(
            user=user,
            otp=data['otp'],
            is_used=False
        ).first()

        if not otp_record:
            raise serializers.ValidationError("Invalid OTP")

        # expiry check (15 min)
        if timezone.now() - otp_record.created_at > timedelta(minutes=15):
            raise serializers.ValidationError("OTP expired")

        data['user'] = user
        data['otp_record'] = otp_record
        return data
# serializers.py


from django.contrib.auth.password_validation import validate_password

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        validate_password(data["new_password"])
        return data


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email not registered")
        return value

# ============== DOCTOR SERIALIZERS ==============

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    class Meta:
        model = Department
        fields = ['id', 'name']

class DoctorSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    department_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'department_id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters")
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # password match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        # password strength
        if len(password) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")

        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError("Password must contain at least 1 number")

        # department validation
        try:
            data['department'] = Department.objects.get(id=data['department_id'])
        except Department.DoesNotExist:
            raise serializers.ValidationError("Invalid department")

        return data

    def create(self, validated_data):
        department = validated_data.pop('department')
        validated_data.pop('confirm_password')
        validated_data.pop('department_id')

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],   # ✅ username added
            password=validated_data['password'],
            role='doctor'
        )

        DoctorProfile.objects.create(
            user=user,
            department=department
        )

        return user

class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id',
            'user',
            'specialization',
            'experience',
            'phone',
            'about',
            'department',
            'department_name',
            "available_days",
            'is_online'
        ]
        read_only_fields = ['id', 'user', 'department_name']
        
class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    # 👇 USER fields
    phone = serializers.CharField(source='user.phone', required=False)
    address = serializers.CharField(source='user.address', required=False)
    profile_image = serializers.ImageField(source='user.profile_image', required=False)
    date_of_birth = serializers.DateField(source='user.date_of_birth', required=False)
    gender = serializers.CharField(source='user.gender', required=False)
    available_days = serializers.CharField(required=False)
    class Meta:
        model = DoctorProfile
        fields = [
            'specialization',
            'experience',
            'about',
            'phone',
            'address',
            'profile_image',
            'date_of_birth',
            'gender',
            'department_id',
            "available_days",
            'is_online'

        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        # 🔹 Update USER fields
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        # 🔹 Update DoctorProfile fields
        return super().update(instance, validated_data)  

# class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
#     department_id = serializers.IntegerField(write_only=True, required=False)

#     class Meta:
#         model = DoctorProfile
#         fields = [
#             'specialization',
#             'experience',
#             'phone',
#             'about',
#             'department_id'
#         ]

#     def update(self, instance, validated_data):
#         dept_id = validated_data.pop('department_id', None)

#         if dept_id:
#             try:
#                 instance.department = Department.objects.get(id=dept_id)
#             except Department.DoesNotExist:
#                 raise serializers.ValidationError({"department": "Invalid department"})

#         return super().update(instance, validated_data)


# ============== PATIENT SERIALIZERS ==============

class PatientProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    bmi = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = [
            'id',
            'user_email',
            'username',
            'age',
            'height',
            'weight',
            'blood_group',
            'activity',
            'diet',
            'stress',
            'sleep_hours',
            'smoking',
            'alcohol',
            'medical_history',
            'allergies',
            'current_medications',
            'family_history',
            'created_at',
            'updated_at',
            'bmi'
        ]
        read_only_fields = [
            'id', 'user_email', 'username',
            'created_at', 'updated_at', 'bmi'
        ]

    # 🔹 BMI
    def get_bmi(self, obj):
        return obj.calculate_bmi()

    # 🔹 FIELD LEVEL VALIDATIONS

    def validate_age(self, value):
        if value is not None:
            if value <= 0 or value > 120:
                raise serializers.ValidationError("Age must be between 1 and 120")
        return value

    def validate_height(self, value):
        if value is not None:
            if value <= 0 or value > 300:
                raise serializers.ValidationError("Height must be between 1 and 300 cm")
        return value

    def validate_weight(self, value):
        if value is not None:
            if value <= 0 or value > 500:
                raise serializers.ValidationError("Weight must be between 1 and 500 kg")
        return value

    def validate_sleep_hours(self, value):
        if value is not None:
            if value < 0 or value > 24:
                raise serializers.ValidationError("Sleep hours must be between 0 and 24")
        return value

    def validate_blood_group(self, value):
        allowed = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if value and value not in allowed:
            raise serializers.ValidationError("Invalid blood group")
        return value

    # 🔹 OBJECT LEVEL VALIDATION

    def validate(self, data):
        height = data.get('height')
        weight = data.get('weight')

        if height is not None and weight is not None:
            height_m = height / 100
            bmi = weight / (height_m ** 2)

            if bmi < 10 or bmi > 60:
                raise serializers.ValidationError({
                    "bmi": "Unrealistic BMI values"
                })

        return data


class PatientProfileCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientProfile
        exclude = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        height = data.get('height')
        weight = data.get('weight')

        if height and height <= 0:
            raise serializers.ValidationError("Height must be positive")

        if weight and weight <= 0:
            raise serializers.ValidationError("Weight must be positive")

        return data


class PatientHealthSummarySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    bmi = serializers.FloatField(source='bmi', read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user_email', 'user_name',
            'age', 'height', 'weight', 'blood_group', 'bmi',
            'activity', 'diet', 'stress', 'updated_at'
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email



# ============== APPOINTMENT SERIALIZERS ==============
#get doctor name and patient email for easy access in frontend

from .models import Appointment, Slot
class AppointmentSerializer(serializers.ModelSerializer):
    # ✅ Patient
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    patient_name = serializers.SerializerMethodField()

    # ✅ Doctor (FULL INFO)
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)
    doctor_email = serializers.CharField(source='doctor.email', read_only=True)
    doctor_name = serializers.SerializerMethodField()

    # ✅ Slot timing
    slot_id = serializers.IntegerField(source='slot.id', read_only=True)  # 🔥 added
    start_time = serializers.TimeField(source='slot.start_time', read_only=True)
    end_time = serializers.TimeField(source='slot.end_time', read_only=True)
    date = serializers.DateField(source='slot.date', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',

            # patient
            'patient_id',
            'patient_email',
            'patient_name',

            # doctor
            'doctor_id',
            'doctor_email',
            'doctor_name',

            # slot
            'slot_id',   # 🔥 added
            'date',
            'start_time',
            'end_time',

            'appointment_type',
            'status',
            'is_paid',
            'notes',
            'created_at'
        ]

    def get_patient_name(self, obj):
        name = f"{obj.patient.first_name} {obj.patient.last_name}".strip()
        return name if name else obj.patient.email

    def get_doctor_name(self, obj):
        name = f"{obj.doctor.first_name} {obj.doctor.last_name}".strip()
        
        if name:
            return f"Dr. {name}"

        return f"Dr. {obj.doctor.email.split('@')[0]}"
    
#CREATE APPOINTMENT
class AppointmentCreateSerializer(serializers.ModelSerializer):
    slot_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Appointment
        fields = ['slot_id', 'appointment_type', 'notes']

    def validate(self, data):
        request = self.context['request']
        patient = request.user

        slot_id = data.get('slot_id')

        try:
            slot = Slot.objects.get(id=slot_id)
        except Slot.DoesNotExist:
            raise serializers.ValidationError("Invalid slot")

        # ❌ Slot already booked
        if slot.is_booked:
            raise serializers.ValidationError("Slot already booked")

        # 🔥 MAX 3 APPOINTMENTS PER DAY
        appointment_count = Appointment.objects.filter(
            patient=patient,
            slot__date=slot.date,
            status__in=['scheduled']  # only active appointments
        ).count()

        if appointment_count >= 3:
            raise serializers.ValidationError(
                "You can only book maximum 3 appointments per day"
            )

        data['slot'] = slot
        return data

    def create(self, validated_data):
        request = self.context['request']
        slot = validated_data.pop('slot')

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=slot.doctor,
            slot=slot,
            **validated_data
        )

        # mark slot booked
        slot.is_booked = True
        slot.save()

        return appointment
class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['notes', 'status', 'appointment_type']  # only updatable fields

# ============== MESSAGE/CHAT SERIALIZERS ==============

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'appointment',
            'sender_email',
            'sender_name',
            'text',
            'created_at',
            'is_read'
        ]
        read_only_fields = ['id', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.email


class MessageCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['appointment', 'text']

    def validate(self, data):
        request = self.context.get('request')
        appointment = data.get('appointment')

        # ❗ Check user belongs to appointment
        if request.user != appointment.patient and request.user != appointment.doctor.user:
            raise serializers.ValidationError("You are not part of this chat")

        # ❗ Empty message check
        if not data.get('text'):
            raise serializers.ValidationError("Message cannot be empty")

        return data

    def create(self, validated_data):
        request = self.context.get('request')

        return Message.objects.create(
            sender=request.user,  # ✅ auto set sender
            **validated_data
        )

# ============== REPORT SERIALIZERS ==============

class ReportSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'user_email',
            'file',
            'file_url',
            'title',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'user_email', 'uploaded_at', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ReportCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['file', 'title']

    def validate_file(self, value):
        allowed_types = {
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/jpg',
            'image/pjpeg',
            'image/x-png',
        }
        content_type = str(getattr(value, 'content_type', '') or '').lower()
        file_name = str(getattr(value, 'name', '') or '').lower()

        if content_type not in allowed_types and not file_name.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed.")

        return value

    def create(self, validated_data):
        request = self.context.get('request')

        return Report.objects.create(
            user=request.user,
            **validated_data
        )
        
        
class CompletedPatientSerializer(serializers.ModelSerializer):
    last_visit = serializers.DateTimeField()
    total_visits = serializers.IntegerField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'last_visit',
            'total_visits'
        ]


class DiseasePredictionRequestSerializer(serializers.Serializer):
    symptoms = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    symptoms_text = serializers.CharField(required=False, allow_blank=False)
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=5, default=3)

    def validate(self, attrs):
        symptoms = attrs.get('symptoms') or []
        symptoms_text = attrs.get('symptoms_text', '').strip()

        if not symptoms and not symptoms_text:
            raise serializers.ValidationError("Provide `symptoms` list or `symptoms_text`.")

        cleaned_symptoms = [item.strip() for item in symptoms if item and item.strip()]
        if symptoms and not cleaned_symptoms:
            raise serializers.ValidationError({"symptoms": "At least one valid symptom is required."})

        attrs['symptoms'] = cleaned_symptoms
        attrs['symptoms_text'] = symptoms_text
        return attrs


class AIAssistantMessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)
    log_date = serializers.DateField(required=False)
    symptoms = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False
    )
    symptoms_text = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    food_type = serializers.ChoiceField(required=False, choices=DailyHealthLog.FOOD_CHOICES)
    water_intake_glasses = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=40)
    sleep_hours = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=4,
        decimal_places=1,
        min_value=Decimal("0"),
        max_value=Decimal("24"),
    )
    sleep_quality = serializers.ChoiceField(required=False, choices=DailyHealthLog.SLEEP_QUALITY_CHOICES)
    stress_level = serializers.ChoiceField(required=False, choices=DailyHealthLog.LEVEL_CHOICES)
    energy_level = serializers.ChoiceField(required=False, choices=DailyHealthLog.ENERGY_CHOICES)
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=5, default=3)

    def validate_message(self, value):
        cleaned_message = value.strip()
        return cleaned_message

    def validate_attachment(self, value):
        if value is None:
            return value

        allowed_types = {
            'application/pdf',
            'image/jpeg',
            'image/png',
        }
        content_type = str(getattr(value, 'content_type', '') or '').lower()
        file_name = str(getattr(value, 'name', '') or '').lower()

        if content_type not in allowed_types and not file_name.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed.")
        return value

    def validate(self, attrs):
        message = (attrs.get("message") or "").strip()
        symptoms = attrs.get("symptoms") or []
        symptoms_text = (attrs.get("symptoms_text") or "").strip()
        notes = (attrs.get("notes") or "").strip()
        attachment = attrs.get("attachment")

        cleaned_symptoms = [item.strip() for item in symptoms if item and item.strip()]

        if not any([message, cleaned_symptoms, symptoms_text, notes, attachment]):
            raise serializers.ValidationError(
                "Please enter your symptoms, message, upload a report, or add check-in details before analysis."
            )

        attrs["message"] = message
        attrs["symptoms"] = cleaned_symptoms
        attrs["symptoms_text"] = symptoms_text
        attrs["notes"] = notes
        return attrs


class AIAnalysisRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisRecord
        fields = [
            'id',
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
        read_only_fields = fields


class PrescriptionUploadSerializer(serializers.Serializer):
    attachment = serializers.FileField()

    def validate_attachment(self, value):
        content_type = str(getattr(value, "content_type", "") or "").lower()
        file_name = str(getattr(value, "name", "") or "").lower()
        if content_type != "application/pdf" and not file_name.endswith((".pdf", ".jpg", ".jpeg", ".png")):
            raise serializers.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed.")
        return value


class ExtractedMedicationItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    dose = serializers.CharField(required=False, allow_blank=True)
    duration_days = serializers.IntegerField(required=False, min_value=1, max_value=365, default=5)
    timings = serializers.ListField(
        child=serializers.ChoiceField(choices=MedicationSchedule.TIMING_CHOICES),
        required=False,
        allow_empty=True,
    )
    instructions = serializers.CharField(required=False, allow_blank=True)


class PrescriptionMedicationSaveSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, default=timezone.localdate)
    medicines = ExtractedMedicationItemSerializer(many=True)


class DailyHealthLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyHealthLog
        fields = [
            'id',
            'log_date',
            'symptoms',
            'symptoms_text',
            'food_type',
            'water_intake_glasses',
            'sleep_hours',
            'sleep_quality',
            'stress_level',
            'energy_level',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_symptoms(self, value):
        cleaned = []
        for item in value or []:
            text = str(item or '').strip()
            if text:
                cleaned.append(text)
        return cleaned

    def validate_water_intake_glasses(self, value):
        if value < 0 or value > 40:
            raise serializers.ValidationError("Water intake must be between 0 and 40 glasses.")
        return value

    def validate_sleep_hours(self, value):
        if value is not None and (value < 0 or value > 24):
            raise serializers.ValidationError("Sleep hours must be between 0 and 24.")
        return value


class MedicationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationSchedule
        fields = [
            'id',
            'name',
            'dose',
            'duration_days',
            'timings',
            'start_date',
            'end_date',
            'source',
            'instructions',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'end_date', 'created_at', 'updated_at']

    def validate_timings(self, value):
        allowed = {choice[0] for choice in MedicationSchedule.TIMING_CHOICES}
        cleaned = []
        for item in value or []:
            timing = str(item or '').strip().lower()
            if timing not in allowed:
                raise serializers.ValidationError(f"Invalid timing `{timing}`.")
            if timing not in cleaned:
                cleaned.append(timing)

        if not cleaned:
            raise serializers.ValidationError("At least one timing is required.")

        return cleaned

    def validate_duration_days(self, value):
        if value < 1 or value > 365:
            raise serializers.ValidationError("Duration must be between 1 and 365 days.")
        return value


class MedicationDoseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationDoseLog
        fields = [
            'id',
            'dose_date',
            'timing',
            'status',
            'marked_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'marked_at', 'created_at', 'updated_at']


class MedicationDoseStatusSerializer(serializers.Serializer):
    dose_date = serializers.DateField(required=False)
    timing = serializers.ChoiceField(choices=MedicationSchedule.TIMING_CHOICES)
    status = serializers.ChoiceField(choices=MedicationDoseLog.STATUS_CHOICES)

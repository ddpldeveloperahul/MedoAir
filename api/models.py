"""
Unified Models - All models consolidated into one app
"""

from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from pydantic_core import ValidationError

# ============= USER MODELS =============
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, role='user', **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,   # ✅ added
            role=role,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            email=email,
            username=username,
            password=password,
            role='admin',
            **extra_fields
        )


class User(AbstractUser):
    email = models.EmailField(unique=True)

    # ✅ username back
    username = models.CharField(max_length=150, unique=True)

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(null=True, blank=True)

    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']   # ✅ important

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.username}) - {self.role}"



from django.utils import timezone
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"


# ============= PATIENT MODELS =============

class PatientProfile(models.Model):
    """Patient profile with health metrics"""
    ACTIVITY_CHOICES = [
        ('Sedentary', 'Sedentary'),
        ('Lightly Active', 'Lightly Active'),
        ('Moderately Active', 'Moderately Active'),
        ('Very Active', 'Very Active'),
    ]
    
    DIET_CHOICES = [
        ('Vegetarian', 'Vegetarian'),
        ('Non-Vegetarian', 'Non-Vegetarian'),
        ('Vegan', 'Vegan'),
        ('Mixed', 'Mixed'),
    ]
    
    STRESS_CHOICES = [
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
    ]
    
    ALCOHOL_CHOICES = [
    ('No', 'No'),
    ('Occasional', 'Occasional'),
    ('Frequent', 'Frequent'),
    ]
    SMOKING_CHOICES = [
    ('No', 'No'),
    ('Occasional', 'Occasional'),
    ('Frequent', 'Frequent'),
    ]
    BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    # Health Metrics
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)

    # Lifestyle
    activity = models.CharField(max_length=50, choices=ACTIVITY_CHOICES, default='Moderately Active')
    diet = models.CharField(max_length=50, choices=DIET_CHOICES, default='Mixed')
    stress = models.CharField(max_length=50, choices=STRESS_CHOICES, default='Moderate')
    sleep_hours = models.IntegerField(null=True, blank=True, help_text="Average sleep hours per day")
    smoking = models.CharField(max_length=20, choices=SMOKING_CHOICES, default='No')
    alcohol = models.CharField(max_length=20, choices=ALCOHOL_CHOICES, default='No')

    # Medical History
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)
    
    # # Additional
    # emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    # emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    # insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    # insurance_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} - Patient Profile"
    
    def calculate_bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return None


# ============= DOCTOR MODELS =============

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    specialization = models.CharField(max_length=150, blank=True)

    experience = models.PositiveIntegerField(default=0)

    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?\d{10,15}$')],
        blank=True
    )

    about = models.TextField(blank=True)

    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    available_days = models.JSONField(default=list)  
    # ["Mon", "Tue", "Wed"]

    is_online = models.BooleanField(default=False)

    is_profile_completed = models.BooleanField(default=False)

    last_seen = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


# ============= APPOINTMENT MODELS =============

class Slot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.email} - {self.date} {self.start_time} to {self.end_time}"

    def clean(self):
        # ✅ 1. Time validation
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be greater than start time")

        # ✅ 2. Overlap check (exclude self during update)
        overlapping = Slot.objects.filter(
            doctor=self.doctor,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError("Slot overlaps with existing slot")

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation everywhere
        super().save(*args, **kwargs)
        
        
class Appointment(models.Model):

    APPOINTMENT_TYPE = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )

    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )

    slot = models.OneToOneField(
        Slot,
        on_delete=models.CASCADE
    )

    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPE,
        default='online'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    is_paid = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)

    cancellation_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.email} → {self.doctor.email}"

# ============= CHAT MODELS =============

class Chat(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='chat'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat - {self.appointment.id}"
    

class Message(models.Model):

    MESSAGE_TYPE_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
    )

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )

    message = models.TextField(blank=True)

    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text'
    )

    file = models.FileField(upload_to='chat/', null=True, blank=True)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.email} → {self.receiver.email}"


# ============= REPORT MODELS =============

class Report(models.Model):
    """Report model for storing medical reports"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    file = models.FileField(upload_to='reports/')
    title = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.email} - {self.title or 'Report'}"

"""
Tests for unified API app
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import PatientProfile, DoctorProfile, Department

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='user'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'user')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str(self):
        self.assertIn('test@example.com', str(self.user))


class PatientProfileTest(TestCase):
    """Test PatientProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='patient@example.com',
            password='testpass123',
            role='user'
        )
        self.patient = PatientProfile.objects.create(
            user=self.user,
            height=170,
            weight=70,
            blood_group='O+'
        )
    
    def test_bmi_calculation(self):
        bmi = self.patient.calculate_bmi()
        expected_bmi = round(70 / ((170 / 100) ** 2), 2)
        self.assertEqual(bmi, expected_bmi)


class DoctorProfileTest(TestCase):
    """Test DoctorProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='doctor@example.com',
            password='testpass123',
            role='doctor'
        )
        self.dept = Department.objects.create(name='Cardiology')
        self.doctor = DoctorProfile.objects.create(
            user=self.user,
            department=self.dept,
            specialization='Heart'
        )
    
    def test_doctor_creation(self):
        self.assertEqual(self.doctor.user.email, 'doctor@example.com')
        self.assertEqual(self.doctor.department.name, 'Cardiology')

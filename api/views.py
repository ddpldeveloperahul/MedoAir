"""
Unified Views - All API views consolidated into one file using APIView pattern
"""

from django.shortcuts import get_object_or_404,render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from .models import *
from .serializers import *
from django.db.models import Q, Count

from .permissions import IsSuperAdmin



def home(request):
    return render(request, 'home.html')

# ============== USER CRUD VIEWS ==============


# class UserListAPIView(APIView):
#     """List and create users"""
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """List all users"""
#         try:
#             users = User.objects.all()
#             serializer = UserSerializer(users, many=True, context={'request': request})
#             return Response({
#                 "message": "Users retrieved successfully",
#                 "count": len(serializer.data),
#                 "results": serializer.data
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({
#                 "error": f"Failed to retrieve users: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         """Create new user"""
#         try:
#             serializer = UserSignupSerializer(data=request.data)
#             if serializer.is_valid():
#                 user = serializer.save()
#                 return Response({
#                     "message": "User created successfully",
#                     "user": {
#                         "id": user.id,
#                         "name": user.first_name,
#                         "email": user.email,
#                         "role": user.role
#                     }
#                 }, status=status.HTTP_201_CREATED)
#             return Response({
#                 "message": "Validation failed",
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 "error": f"Failed to create user: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class UserDetailAPIView(APIView):
#     """Retrieve, update, or delete specific user"""
#     permission_classes = [IsAuthenticated]

#     def get_user_or_404(self, user_id):
#         try:
#             return User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return None

#     def check_permission(self, request, user):
#         if user.id != request.user.id and not request.user.is_staff:
#             return False
#         return True

#     def get(self, request, user_id):
#         """Get user details"""
#         user = self.get_user_or_404(user_id)
#         if not user:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         if not self.check_permission(request, user):
#             return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
#         try:
#             serializer = UserSerializer(user, context={'request': request})
#             return Response({
#                 "message": "User retrieved successfully",
#                 "user": serializer.data
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def put(self, request, user_id):
#         """Update user (full update)"""
#         user = self.get_user_or_404(user_id)
#         if not user:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         if not self.check_permission(request, user):
#             return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
#         try:
#             serializer = UserUpdateSerializer(user, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     "message": "User updated successfully",
#                     "user": UserSerializer(user, context={'request': request}).data
#                 }, status=status.HTTP_200_OK)
#             return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def patch(self, request, user_id):
#         """Update user (partial update)"""
#         user = self.get_user_or_404(user_id)
#         if not user:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         if not self.check_permission(request, user):
#             return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
#         try:
#             serializer = UserUpdateSerializer(user, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     "message": "User updated successfully",
#                     "user": UserSerializer(user, context={'request': request}).data
#                 }, status=status.HTTP_200_OK)
#             return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def delete(self, request, user_id):
#         """Delete user"""
#         user = self.get_user_or_404(user_id)
#         if not user:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         if not self.check_permission(request, user):
#             return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
#         try:
#             user_email = user.email
#             user.delete()
#             return Response({"message": f"User {user_email} deleted successfully"}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CurrentUserAPIView(APIView):
#     """Get current logged-in user"""
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """Get current user details"""
#         serializer = UserSerializer(request.user, context={'request': request})
#         return Response({
#             "message": "Current user retrieved",
#             "user": serializer.data
#         }, status=status.HTTP_200_OK)


# class ChangePasswordAPIView(APIView):
#     """Change user password"""
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """Change user password"""
#         user = request.user
#         old_password = request.data.get('old_password')
#         new_password = request.data.get('new_password')
#         confirm_password = request.data.get('confirm_password')

#         if not all([old_password, new_password, confirm_password]):
#             return Response({"error": "All fields required"}, status=status.HTTP_400_BAD_REQUEST)

#         if not user.check_password(old_password):
#             return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

#         if new_password != confirm_password:
#             return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

#         if len(new_password) < 6:
#             return Response({"error": "Password too short"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user.set_password(new_password)
#             user.save()
#             return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class UserProfileStatsAPIView(APIView):
#     """Get user profile statistics"""
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """Get user profile statistics"""
#         user = request.user
#         return Response({
#             "message": "Profile statistics retrieved",
#             "stats": {
#                 "user_id": user.id,
#                 "email": user.email,
#                 "full_name": f"{user.first_name} {user.last_name}".strip(),
#                 "role": user.role,
#                 "is_verified": user.is_verified,
#                 "last_login": user.last_login,
#                 "account_age_days": (timezone.now() - user.date_joined).days if user.date_joined else 0
#             }
#         }, status=status.HTTP_200_OK)


# ============== AUTHENTICATION VIEWS ==============

class UserSignupAPIView(APIView):
    """User registration"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register new user"""
        try:
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "name": user.username,
                        "email": user.email,
                        "role": user.role
                    }
                }, status=status.HTTP_201_CREATED)
            return Response({"message": "Registration failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoctorSignupAPIView(APIView):
    """Doctor registration"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register new doctor"""
        try:
            serializer = DoctorSignupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                doctor = DoctorProfile.objects.get(user=user)

                return Response({
                    "message": "Doctor registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "department": doctor.department.name if doctor.department else None
                    }
                }, status=status.HTTP_201_CREATED)
            return Response({"message": "Registration failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginAPIView(APIView):
    """User login with JWT tokens"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Login user and return JWT tokens"""
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = authenticate(email=email, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                user_data = UserSerializer(user, context={'request': request}).data

                return Response({
                    "message": "Login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": user_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 🔹 1. FORGOT PASSWORD (SEND OTP)

class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))

    def send_otp_email(self, email, otp):
        subject = "Password Reset OTP - MedoAir"
        message = f"""
Hi,

Your OTP for password reset is: {otp}

This OTP is valid for 15 minutes.

If you didn't request this, ignore this email.

- MedoAir Team
"""
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        # 🔐 Security: don't reveal if user exists
        if not user:
            return Response({"message": "If email exists, OTP sent"})

        # ⏳ Cooldown (60 sec)
        last_otp = PasswordResetOTP.objects.filter(user=user).first()
        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < 60:
            return Response({"error": "Wait before requesting another OTP"}, status=429)

        otp = self.generate_otp()

        # Delete old unused OTP
        PasswordResetOTP.objects.filter(user=user, is_used=False).delete()

        PasswordResetOTP.objects.create(user=user, otp=otp)

        self.send_otp_email(email, otp)

        return Response({"message": "OTP sent successfully"})


# 🔹 2. RESET PASSWORD (OTP VERIFY + RESET)

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "Invalid email or OTP"}, status=400)

        try:
            otp_record = PasswordResetOTP.objects.get(
                user=user,
                otp=otp,
                is_used=False
            )
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        # ⏳ Expiry check
        if otp_record.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        # ✅ Reset password
        user.set_password(new_password)
        user.save()

        # ✅ Mark OTP used
        otp_record.is_used = True
        otp_record.save()

        return Response({"message": "Password reset successful"})

class ResendOTPAPIView(APIView):
    """Resend OTP for password reset"""
    permission_classes = [AllowAny]

    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))

    def send_otp_email(self, email, otp):
        subject = "Password Reset OTP - MedoAir"
        message = f"Your new OTP is: {otp}\n\nValid for 15 minutes only."
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

    def post(self, request):
        """Resend OTP"""
        try:
            serializer = ResendOTPSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                user = User.objects.get(email=email)

                otp = self.generate_otp()
                PasswordResetOTP.objects.filter(user=user, is_used=False).delete()
                PasswordResetOTP.objects.create(user=user, otp=otp)

                try:
                    self.send_otp_email(email, otp)
                    return Response({"message": "New OTP sent to your email", "email": email}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"error": f"Failed to send OTP: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============== PATIENT PROFILE VIEWS ==============

class PatientProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 🔹 GET
    def get(self, request):
        user = request.user

        if user.role != 'patient':
            return Response({"error": "Access denied"}, status=403)

        try:
            profile = PatientProfile.objects.get(user=user)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        serializer = PatientProfileSerializer(profile, context={'request': request})

        return Response({
            "message": "Profile fetched successfully",
            "data": serializer.data
        })

    # 🔹 POST (Create)
    def post(self, request):
        user = request.user

        # ✅ Role validation
        if user.role != 'patient':
            return Response({"error": "Only patients can create profile"}, status=403)

        # ✅ Already exists
        if PatientProfile.objects.filter(user=user).exists():
            return Response({"error": "Profile already exists"}, status=400)

        serializer = PatientProfileCreateUpdateSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.save(user=user)

            return Response({
                "message": "Profile created successfully",
                "data": PatientProfileSerializer(profile).data
            }, status=201)

        return Response(serializer.errors, status=400)

    # 🔹 PUT (Update)
    def put(self, request):
        user = request.user

        if user.role != 'patient':
            return Response({"error": "Access denied"}, status=403)

        try:
            profile = PatientProfile.objects.get(user=user)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        serializer = PatientProfileCreateUpdateSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response({
                "message": "Profile updated successfully",
                "data": PatientProfileSerializer(profile).data
            })

        return Response(serializer.errors, status=400)

    # 🔹 DELETE
    def delete(self, request):
        user = request.user

        if user.role != 'patient':
            return Response({"error": "Access denied"}, status=403)

        try:
            profile = PatientProfile.objects.get(user=user)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        profile.delete()

        return Response({
            "message": "Profile deleted successfully"
        })

class PatientDetailAPIView(APIView):
    """Retrieve, update, or delete patient profile"""
    permission_classes = [IsAuthenticated]

    def get_patient_or_404(self, patient_id):
        try:
            return PatientProfile.objects.get(id=patient_id)
        except PatientProfile.DoesNotExist:
            return None

    def check_permission(self, request, patient):
        if patient.user.id != request.user.id and not request.user.is_staff:
            return False
        return True

    def get(self, request, patient_id):
        """Get patient profile details"""
        patient = self.get_patient_or_404(patient_id)
        if not patient:
            return Response({"error": "Patient profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not self.check_permission(request, patient):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            serializer = PatientProfileSerializer(patient, context={'request': request})
            return Response({
                "message": "Patient profile retrieved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, patient_id):
        """Update patient profile (full update)"""
        patient = self.get_patient_or_404(patient_id)
        if not patient:
            return Response({"error": "Patient profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not self.check_permission(request, patient):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            serializer = PatientProfileCreateUpdateSerializer(patient, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Patient profile updated successfully",
                    "profile": PatientProfileSerializer(patient, context={'request': request}).data
                }, status=status.HTTP_200_OK)
            return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, patient_id):
        """Update patient profile (partial update)"""
        patient = self.get_patient_or_404(patient_id)
        if not patient:
            return Response({"error": "Patient profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not self.check_permission(request, patient):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            serializer = PatientProfileCreateUpdateSerializer(patient, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Patient profile updated successfully",
                    "profile": PatientProfileSerializer(patient, context={'request': request}).data
                }, status=status.HTTP_200_OK)
            return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, patient_id):
        """Delete patient profile"""
        patient = self.get_patient_or_404(patient_id)
        if not patient:
            return Response({"error": "Patient profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not self.check_permission(request, patient):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user_email = patient.user.email
            patient.delete()
            return Response({"message": f"Patient profile for {user_email} deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientMyProfileAPIView(APIView):
    """Get current user's patient profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user's patient profile"""
        try:
            patient = PatientProfile.objects.get(user=request.user)
            serializer = PatientProfileSerializer(patient, context={'request': request})
            return Response({"message": "Your patient profile", "profile": serializer.data}, status=status.HTTP_200_OK)
        except PatientProfile.DoesNotExist:
            return Response({"error": "No patient profile found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientHealthSummaryAPIView(APIView):
    """Get health summary for current user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get health summary"""
        try:
            patient = PatientProfile.objects.get(user=request.user)
            serializer = PatientHealthSummarySerializer(patient)
            return Response({"message": "Your health summary", "summary": serializer.data}, status=status.HTTP_200_OK)
        except PatientProfile.DoesNotExist:
            return Response({"error": "No patient profile found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientHealthMetricsAPIView(APIView):
    """Get detailed health metrics"""
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        """Get detailed health metrics"""
        try:
            patient = PatientProfile.objects.get(id=patient_id)
            
            if patient.user.id != request.user.id and not request.user.is_staff:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
            bmi = patient.calculate_bmi()
            bmi_category = "Normal"
            if bmi:
                if bmi < 18.5:
                    bmi_category = "Underweight"
                elif 18.5 <= bmi < 25:
                    bmi_category = "Normal"
                elif 25 <= bmi < 30:
                    bmi_category = "Overweight"
                else:
                    bmi_category = "Obese"
            
            return Response({
                "message": "Health metrics retrieved successfully",
                "metrics": {
                    "height_cm": patient.height,
                    "weight_kg": patient.weight,
                    "bmi": bmi,
                    "bmi_category": bmi_category,
                    "blood_group": patient.blood_group,
                    "activity_level": patient.activity,
                    "sleep_hours": patient.sleep_hours,
                    "stress_level": patient.stress
                }
            }, status=status.HTTP_200_OK)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Patient profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientBulkHealthUpdateAPIView(APIView):
    """Quick update health metrics"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Update health metrics"""
        try:
            patient = PatientProfile.objects.get(user=request.user)
            serializer = PatientProfileCreateUpdateSerializer(patient, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Health metrics updated successfully",
                    "profile": PatientProfileSerializer(patient, context={'request': request}).data
                }, status=status.HTTP_200_OK)
            return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except PatientProfile.DoesNotExist:
            return Response({"error": "Patient profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#============== DOCTOR PROFILE VIEWS ==============

class DoctorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # ✅ GET → current doctor profile
    def get(self, request):
        try:
            doctor = DoctorProfile.objects.select_related('user', 'department').get(user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        return Response(DoctorProfileSerializer(doctor).data)

    # ✅ CREATE → only if not exists
    def post(self, request):
        user = request.user

        if DoctorProfile.objects.filter(user=user).exists():
            return Response({"error": "Profile already exists"}, status=400)

        serializer = DoctorProfileUpdateSerializer(data=request.data)

        if serializer.is_valid():
            dept_id = serializer.validated_data.pop('department_id', None)

            doctor = serializer.save(user=user)

            if dept_id:
                try:
                    doctor.department = Department.objects.get(id=dept_id)
                    doctor.save()
                except Department.DoesNotExist:
                    return Response({"error": "Invalid department"}, status=400)

            return Response(DoctorProfileSerializer(doctor).data, status=201)

        return Response(serializer.errors, status=400)

    # ✅ UPDATE → current user only
    def put(self, request):
        try:
            doctor = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        serializer = DoctorProfileUpdateSerializer(
            doctor,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(DoctorProfileSerializer(doctor).data)

        return Response(serializer.errors, status=400)

    # ✅ DELETE → current user only
    def delete(self, request):
        try:
            doctor = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        doctor.delete()
        return Response({"message": "Deleted successfully"}, status=204)

# ============== APPOINTMENT VIEWS ==============
# we will be check the avilable slots for the doctor and then book the appointment 
# for the patient and doctor and also we will be update the slot is_booked to true when 
#  the appointment is booked and also we will be free the slot when the appointment is cancelled

class SlotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # ✅ LIST + DETAIL
    def get(self, request, pk=None):
        doctor_id = request.query_params.get('doctor')
        date = request.query_params.get('date')

        # 👉 SINGLE SLOT
        if pk:
            slot = get_object_or_404(Slot, pk=pk)
            data = {
                "slot_id": slot.id,
                "doctor_id": slot.doctor.id,
                "date": slot.date,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "is_booked": slot.is_booked
            }
            return Response(data)

        # 👉 LIST SLOTS (FILTERED)
        if not doctor_id or not date:
            return Response(
                {"error": "doctor and date required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots = Slot.objects.filter(
            doctor_id=doctor_id,
            date=date
        )

        data = [
            {
                "slot_id": slot.id,
                "doctor_id": slot.doctor.id,
                "date": slot.date,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "is_booked": slot.is_booked
            }
            for slot in slots
        ]

        return Response(data)

    # ✅ CREATE SLOT (only doctor can create the slot)
    def post(self, request):
        # 🔥 ADD THIS CHECK
        if request.user.role != "doctor":
            return Response(
                {"error": "Only doctors can create slots you are a patient"},
                status=403
            )

        doctor = request.user

        date = request.data.get("date")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")

        if not date or not start_time or not end_time:
            return Response(
                {"error": "date, start_time, end_time required"},
                status=400
            )

        slot = Slot(
            doctor=doctor,
            date=date,
            start_time=start_time,
            end_time=end_time
        )

        try:
            slot.save()
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response(
            {
                "message": "Slot created", 
                "doctor_id": doctor.id,
                "slot_id": slot.id,
                "date": slot.date,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
            },
            status=201
        )

    # ✅ UPDATE SLOT
    def put(self, request, pk):
        slot = get_object_or_404(Slot, pk=pk)

        # optional: only doctor can update
        if slot.doctor != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        slot.date = request.data.get("date", slot.date)
        slot.start_time = request.data.get("start_time", slot.start_time)
        slot.end_time = request.data.get("end_time", slot.end_time)

        try:
            slot.save()
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Slot updated"})

    # ✅ DELETE SLOT
    def delete(self, request, pk):
        slot = get_object_or_404(Slot, pk=pk)

        if slot.doctor != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        if slot.is_booked:
            return Response(
                {"error": "Cannot delete booked slot"},
                status=400
            )

        slot.delete()
        return Response({"message": "Slot deleted"}, status=204)
    
    

class AppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # ✅ LIST + DETAIL
    def get(self, request, pk=None):
        if pk:
            appointment = get_object_or_404(Appointment, pk=pk)
            return Response(AppointmentSerializer(appointment).data)

        if request.user.is_staff:
            appointments = Appointment.objects.all()
        else:
            appointments = Appointment.objects.filter(
                Q(patient=request.user) | Q(doctor=request.user)
            )

        return Response(AppointmentSerializer(appointments, many=True).data)

    # ✅ CREATE
    def post(self, request):
        serializer = AppointmentCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            appointment = serializer.save()
            return Response(
                AppointmentSerializer(appointment).data,
                status=201
            )

        return Response(serializer.errors, status=400)

    # ✅ UPDATE (SMART PERMISSION)
    def put(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        # 🔥 Doctor can update status
        if "status" in request.data:
            if request.user != appointment.doctor:
                return Response(
                    {"error": "Only doctor can update status"},
                    status=403
                )

        # 🔥 Patient can update notes
        elif request.user != appointment.patient:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        serializer = AppointmentUpdateSerializer(
            appointment,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(AppointmentSerializer(appointment).data)

        return Response(serializer.errors, status=400)

    # ✅ PATCH → CANCEL / RESCHEDULE
    def patch(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        if request.user != appointment.patient:
            return Response({"error": "Unauthorized"}, status=403)

        action = request.data.get("action")

        # ❌ Prevent actions on completed
        if appointment.status == "completed":
            return Response({"error": "Already completed"}, status=400)

        # 🔥 CANCEL
        if action == "cancel":
            appointment.status = "cancelled"
            appointment.cancellation_reason = request.data.get("reason", "")

            appointment.slot.is_booked = False
            appointment.slot.save()

            appointment.save()

            return Response({"message": "Appointment cancelled"})

        # 🔥 RESCHEDULE
        if action == "reschedule":
            new_slot_id = request.data.get("slot_id")

            if not new_slot_id:
                return Response({"error": "slot_id required"}, status=400)

            try:
                new_slot = Slot.objects.get(id=new_slot_id)
            except Slot.DoesNotExist:
                return Response({"error": "Invalid slot"}, status=400)

            if new_slot.is_booked:
                return Response({"error": "Slot already booked"}, status=400)

            # free old slot
            appointment.slot.is_booked = False
            appointment.slot.save()

            # assign new slot
            appointment.slot = new_slot
            appointment.doctor = new_slot.doctor

            new_slot.is_booked = True
            new_slot.save()

            appointment.status = "scheduled"
            appointment.save()

            return Response({
                "message": "Appointment rescheduled",
                "new_slot_id": new_slot.id
            })

        return Response({"error": "Invalid action"}, status=400)

    # ✅ DELETE
    def delete(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        if request.user != appointment.patient:
            return Response({"error": "Unauthorized"}, status=403)

        appointment.slot.is_booked = False
        appointment.slot.save()

        appointment.delete()
        return Response({"message": "Deleted"}, status=204)
    
    
class DoctorDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor = request.user

        # 🔹 Slots
        slots = Slot.objects.filter(doctor=doctor)

        slot_data = [
            {
                "slot_id": s.id,
                "date": s.date,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "is_booked": s.is_booked
            }
            for s in slots
        ]

        # 🔹 Slot counts
        total_slots = slots.count()
        booked_slots = slots.filter(is_booked=True).count()
        free_slots = slots.filter(is_booked=False).count()

        # 🔹 Appointments
        appointments = Appointment.objects.filter(doctor=doctor)

        appointment_data = [
            {
                "appointment_id": a.id,
                "patient_id": a.patient.id,
                "patient_name": f"{a.patient.first_name} {a.patient.last_name}".strip(),
                "patient_email": a.patient.email,
                "status": a.status,
                "date": a.slot.date,
                "start_time": a.slot.start_time,
                "end_time": a.slot.end_time,
                "notes": a.notes
            }
            for a in appointments
        ]

        # 🔹 Appointment counts
        counts = appointments.aggregate(
            scheduled=Count('id', filter=Q(status='scheduled')),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            no_show=Count('id', filter=Q(status='no_show'))
        )

        return Response({
            "doctor_id": doctor.id,

            # ✅ COUNTS
            "total_slots": total_slots,
            "booked_slots": booked_slots,
            "free_slots": free_slots,
            "appointments_count": counts,

            # ✅ FULL DATA
            "slots": slot_data,
            "appointments": appointment_data
        })
        

# ============== MESSAGE/CHAT VIEWS ==============

class MessageListAPIView(APIView):
    """List and create messages for appointment"""
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        """Get messages for appointment"""
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            if appointment.patient != request.user and appointment.doctor.user != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
            messages = Message.objects.filter(appointment=appointment)
            serializer = MessageSerializer(messages, many=True)
            return Response({
                "message": "Messages retrieved",
                "count": len(serializer.data),
                "results": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, appointment_id):
        """Send message"""
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            if appointment.patient != request.user and appointment.doctor.user != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data.copy()
            data['appointment'] = appointment_id
            
            serializer = MessageCreateSerializer(data=data)
            if serializer.is_valid():
                message = serializer.save(sender=request.user, appointment=appointment)
                return Response({
                    "message": "Message sent",
                    "message_data": MessageSerializer(message).data
                }, status=status.HTTP_201_CREATED)
            return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============== REPORT VIEWS ==============

class ReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, report_id):
        try:
            return Report.objects.get(id=report_id, user=request.user)
        except Report.DoesNotExist:
            return None

    # 🔹 GET → list OR single
    def get(self, request, report_id=None):
        if report_id:
            report = self.get_object(request, report_id)

            if not report:
                return Response({"error": "Report not found"}, status=404)

            serializer = ReportSerializer(report, context={'request': request})
            return Response(serializer.data)

        # list all
        reports = Report.objects.filter(user=request.user)
        serializer = ReportSerializer(
            reports,
            many=True,
            context={'request': request}
        )

        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })

    # 🔹 POST → create
    def post(self, request):
        serializer = ReportCreateUpdateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            report = serializer.save()

            return Response({
                "message": "Report created",
                "data": ReportSerializer(report, context={'request': request}).data
            }, status=201)

        return Response(serializer.errors, status=400)

    # 🔹 PUT → update
    def put(self, request, report_id=None):
        if not report_id:
            return Response({"error": "Report ID required"}, status=400)

        report = self.get_object(request, report_id)

        if not report:
            return Response({"error": "Report not found"}, status=404)

        serializer = ReportCreateUpdateSerializer(
            report,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Report updated"})

        return Response(serializer.errors, status=400)

    # 🔹 DELETE → delete
    def delete(self, request, report_id=None):
        if not report_id:
            return Response({"error": "Report ID required"}, status=400)

        report = self.get_object(request, report_id)

        if not report:
            return Response({"error": "Report not found"}, status=404)

        report.delete()
        return Response({"message": "Report deleted"})
    
    
    
    
class SuperAdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "total_patients": User.objects.filter(role='patient').count(),
            "total_doctors": User.objects.filter(role='doctor').count(),

            "appointments": {
                "total": Appointment.objects.count(),
                "scheduled": Appointment.objects.filter(status='scheduled').count(),
                "completed": Appointment.objects.filter(status='completed').count(),
                "cancelled": Appointment.objects.filter(status='cancelled').count(),
            },

            "slots": {
                "total": Slot.objects.count(),
                "booked": Slot.objects.filter(is_booked=True).count(),
                "free": Slot.objects.filter(is_booked=False).count(),
            }
        })
        
        
# class SuperAdminUserAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def get(self, request):
#         users = User.objects.all()

#         # 🔥 COUNTS
#         total_users = users.count()
#         total_doctors = users.filter(role='doctor').count()
#         total_patients = users.filter(role='patient').count()
#         total_admins = users.filter(role='admin').count()

#         return Response({
#             "summary": {
#                 "total_users": total_users,
#                 "total_doctors": total_doctors,
#                 "total_patients": total_patients,
#                 "total_admins": total_admins
#             },
#             "users": UserSerializer(users, many=True).data
#         })

#     def delete(self, request, user_id):
#         user = get_object_or_404(User, id=user_id)
#         user.delete()
#         return Response({"message": "User deleted"})

class SuperAdminUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, user_id=None):

        # ✅ SINGLE USER
        if user_id:
            user = get_object_or_404(User, id=user_id)

            return Response({
                "summary": {
                    "total_users": User.objects.count()
                },
                "user": UserSerializer(user).data
            })

        # ✅ ALL USERS
        users = User.objects.all()

        return Response({
            "summary": {
                "total_users": users.count(),
                "total_doctors": users.filter(role='doctor').count(),
                "total_patients": users.filter(role='patient').count(),
                "total_admins": users.filter(role='admin').count()
            },
            "users": UserSerializer(users, many=True).data
        })

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({"message": "User deleted"})
    
    
class SuperAdminDoctorAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, doctor_id=None):

        # ✅ SINGLE
        if doctor_id:
            doctor = get_object_or_404(DoctorProfile, id=doctor_id)

            return Response({
                "summary": {
                    "total_doctors": DoctorProfile.objects.count()
                },
                "doctor": DoctorProfileSerializer(doctor).data
            })

        # ✅ ALL
        doctors = DoctorProfile.objects.select_related('user', 'department')

        return Response({
            "summary": {
                "total_doctors": doctors.count()
            },
            "doctors": DoctorProfileSerializer(doctors, many=True).data
        })

    def delete(self, request, doctor_id):
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        doctor.user.delete()
        return Response({"message": "Doctor deleted"})
    
class SuperAdminPatientAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, patient_id=None):

        # ✅ SINGLE
        if patient_id:
            patient = get_object_or_404(PatientProfile, id=patient_id)

            return Response({
                "summary": {
                    "total_patients": PatientProfile.objects.count()
                },
                "patient": PatientProfileSerializer(patient).data
            })

        # ✅ ALL
        patients = PatientProfile.objects.select_related('user')

        return Response({
            "summary": {
                "total_patients": patients.count()
            },
            "patients": PatientProfileSerializer(patients, many=True).data
        })

    def put(self, request, patient_id):
        patient = get_object_or_404(PatientProfile, id=patient_id)

        serializer = PatientProfileCreateUpdateSerializer(
            patient,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Updated",
                "data": serializer.data
            })

        return Response(serializer.errors, status=400)

    def delete(self, request, patient_id):
        patient = get_object_or_404(PatientProfile, id=patient_id)
        patient.user.delete()
        return Response({"message": "Patient deleted"})
    
# class SuperAdminAppointmentAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def get(self, request):
#         appointments = Appointment.objects.all()
#         return Response(AppointmentSerializer(appointments, many=True).data)

#     def delete(self, request, appointment_id):
#         appointment = get_object_or_404(Appointment, id=appointment_id)

#         appointment.slot.is_booked = False
#         appointment.slot.save()

#         appointment.delete()

#         return Response({"message": "Appointment deleted"})

class SuperAdminAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    # ✅ GET ALL + SINGLE
    def get(self, request, appointment_id=None):

        # 🔹 SINGLE APPOINTMENT
        if appointment_id:
            appointment = get_object_or_404(Appointment, id=appointment_id)

            return Response({
                "summary": {
                    "total_appointments": Appointment.objects.count()
                },
                "appointment": AppointmentSerializer(appointment).data
            })

        # 🔹 ALL APPOINTMENTS
        appointments = Appointment.objects.select_related(
            'patient', 'doctor', 'slot'
        )

        return Response({
            "summary": {
                "total_appointments": appointments.count(),
                "scheduled": appointments.filter(status='scheduled').count(),
                "completed": appointments.filter(status='completed').count(),
                "cancelled": appointments.filter(status='cancelled').count(),
                "no_show": appointments.filter(status='no_show').count(),
            },
            "appointments": AppointmentSerializer(appointments, many=True).data
        })

    # ✅ DELETE APPOINTMENT
    def delete(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # 🔥 free slot
        appointment.slot.is_booked = False
        appointment.slot.save()

        appointment.delete()

        return Response({"message": "Appointment deleted successfully"})
    
    
# views.py

# class ChatAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     # 🔹 GET MESSAGES
#     def get(self, request, appointment_id):
#         try:
#             appointment = get_object_or_404(Appointment, id=appointment_id)

#             if request.user != appointment.patient and request.user != appointment.doctor:
#                 return Response({"error": "Not allowed"}, status=403)

#             chat, _ = Chat.objects.get_or_create(appointment=appointment)

#             messages = chat.messages.all()

#             data = []
#             for msg in messages:
#                 data.append({
#                     "id": msg.id,
#                     "sender": msg.sender.email,
#                     "receiver": msg.receiver.email,
#                     "message": msg.message,
#                     "type": msg.message_type,
#                     "file": msg.file.url if msg.file else None,
#                     "is_read": msg.is_read,
#                     "created_at": msg.created_at
#                 })

#             return Response({
#                 "count": len(data),
#                 "messages": data
#             })

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

#     # 🔹 SEND MESSAGE
#     def post(self, request, appointment_id):
#         try:
#             appointment = get_object_or_404(Appointment, id=appointment_id)

#             if request.user == appointment.patient:
#                 sender = appointment.patient
#                 receiver = appointment.doctor
#             elif request.user == appointment.doctor:
#                 sender = appointment.doctor
#                 receiver = appointment.patient
#             else:
#                 return Response({"error": "Not allowed"}, status=403)

#             chat, _ = Chat.objects.get_or_create(appointment=appointment)

#             message = Message.objects.create(
#                 chat=chat,
#                 sender=sender,
#                 receiver=receiver,
#                 message=request.data.get("message"),
#                 message_type=request.data.get("message_type", "text"),
#                 file=request.FILES.get("file")
#             )

#             return Response({
#                 "message": "Message sent",
#                 "data": {
#                     "sender": sender.email,
#                     "receiver": receiver.email,
#                     "message": message.message
#                 }
#             })

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

#     # 🔹 MARK AS READ
#     def put(self, request, message_id):
#         msg = get_object_or_404(Message, id=message_id, receiver=request.user)

#         msg.is_read = True
#         msg.save()

#         return Response({"message": "Seen"})

#     # 🔹 DELETE MESSAGE
#     def delete(self, request, message_id):
#         msg = get_object_or_404(Message, id=message_id, sender=request.user)
#         msg.delete()

#         return Response({"message": "Deleted"})
    
    
class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 🔹 GET MESSAGES
    def get(self, request, appointment_id):
        try:
            appointment = get_object_or_404(Appointment, id=appointment_id)

            # ✅ Access control
            if request.user != appointment.patient and request.user != appointment.doctor:
                return Response({"error": "Not allowed"}, status=403)

            chat, _ = Chat.objects.get_or_create(appointment=appointment)

            messages = chat.messages.all()

            # ✅ AUTO MARK AS READ (IMPORTANT ADD)
            for msg in messages:
                if msg.receiver == request.user and not msg.is_read:
                    msg.is_read = True
                    msg.save()

            # ✅ RESPONSE
            data = []
            for msg in messages:
                data.append({
                    "id": msg.id,
                    "sender": msg.sender.username,
                    "receiver": msg.receiver.username,
                    "message": msg.message,
                    "type": msg.message_type,
                    "file": msg.file.url if msg.file else None,
                    "is_read": msg.is_read,
                    "created_at": msg.created_at
                })

            return Response({
                "count": len(data),
                "messages": data
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    # 🔹 SEND MESSAGE
    def post(self, request, appointment_id):
        try:
            appointment = get_object_or_404(Appointment, id=appointment_id)

            if request.user == appointment.patient:
                sender = appointment.patient
                receiver = appointment.doctor
            elif request.user == appointment.doctor:
                sender = appointment.doctor
                receiver = appointment.patient
            else:
                return Response({"error": "Not allowed"}, status=403)

            chat, _ = Chat.objects.get_or_create(appointment=appointment)

            message = Message.objects.create(
                chat=chat,
                sender=sender,
                receiver=receiver,
                message=request.data.get("message"),
                message_type=request.data.get("message_type", "text"),
                file=request.FILES.get("file")
            )

            return Response({
                "message": "Message sent",
                "data": {
                    "id": message.id,
                    "sender": sender.email,
                    "receiver": receiver.email,
                    "message": message.message,
                    "is_read": message.is_read
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    # 🔹 MARK AS READ (manual)
    # def put(self, request, message_id):
    #     msg = get_object_or_404(Message, id=message_id, receiver=request.user)

    #     msg.is_read = True
    #     msg.save()

    #     return Response({"message": "Seen (manual)"})
    def put(self, request, message_id):
        msg = get_object_or_404(Message, id=message_id)

        # optional security
        if msg.sender != request.user:
            return Response({"error": "Only sender can edit message"}, status=403)

        # 🔥 UPDATE MESSAGE TEXT
        msg.message = request.data.get("message", msg.message)

        # 🔥 OPTIONAL: mark as read
        msg.is_read = True

        msg.save()

        return Response({
            "message": "Updated successfully",
            "data": {
                "id": msg.id,
                "message": msg.message,
                "is_read": msg.is_read
            }
        })

    # 🔹 DELETE MESSAGE
    def delete(self, request, message_id):
        msg = get_object_or_404(Message, id=message_id, sender=request.user)
        msg.delete()

        return Response({"message": "Deleted"})
    
    
class DeleteMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        try:
            msg = Message.objects.get(id=message_id)

            if request.user != msg.sender:
                return Response({"error": "Not allowed"}, status=403)

            msg.delete()
            return Response({"message": "Deleted"})

        except Message.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        
        
        





class ChatHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if request.user not in [appointment.patient, appointment.doctor]:
            return Response({"error": "Not allowed"}, status=403)

        chat, _ = Chat.objects.get_or_create(appointment=appointment)

        messages = chat.messages.all()

        data = [
            {
                "id": m.id,
                "sender": m.sender.username,
                "receiver": m.receiver.username,
                "message": m.message,
                "is_read": m.is_read,
                "created_at": m.created_at
            }
            for m in messages
        ]

        return Response({"messages": data})


from .pagination import StandardPagination
from django.db.models import Max, Count, Q

class CompletedPatientsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get(self, request):
        doctor = request.user
        search = request.GET.get('search')

        # ✅ Step 1: filter completed appointments
        queryset = User.objects.filter(
            patient_appointments__doctor=doctor,
            patient_appointments__status='completed'
        ).annotate(
            last_visit=Max('patient_appointments__created_at'),
            total_visits=Count('patient_appointments')
        ).distinct().order_by('-last_visit')

        # ✅ Step 2: search
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )

        # ✅ Step 3: pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = CompletedPatientSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


def video_call(request):
    return render(request, 'chat.html')



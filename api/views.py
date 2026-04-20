"""
Unified Views - All API views consolidated into one file using APIView pattern
"""

from datetime import datetime

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework import status # type: ignore
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.core.mail import send_mail
from django.conf import settings
import random
import re
import string
from .models import *
from .serializers import *
from .health_tracking_service import health_tracking_ai_service
from .ml_service import disease_prediction_service
from .document_reader import document_reader_service
from .clinical_document_ai import clinical_document_ai_service
from .weekly_report_pdf import build_weekly_report_pdf
from django.db.models import Q, Count
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

from .permissions import IsSuperAdmin
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def home(request):
    if request.user.is_authenticated:
        return redirect('/api/video_call/')
    return render(request, 'home.html')


def _flatten_validation_errors(detail):
    if isinstance(detail, dict):
        parts = []
        for key, value in detail.items():
            child = _flatten_validation_errors(value)
            if child:
                parts.append(f"{key}: {child}")
        return " | ".join(parts)
    if isinstance(detail, list):
        return " ".join(_flatten_validation_errors(item) for item in detail if _flatten_validation_errors(item))
    return str(detail)


def _get_appointment_slot_status(appointment, now=None):
    now = now or timezone.localtime()
    slot_start = timezone.make_aware(
        datetime.combine(appointment.slot.date, appointment.slot.start_time)
    )
    slot_end = timezone.make_aware(
        datetime.combine(appointment.slot.date, appointment.slot.end_time)
    )

    is_scheduled = appointment.status == "scheduled"
    has_started = now >= slot_start
    has_ended = now >= slot_end
    is_active = is_scheduled and has_started and not has_ended

    if not is_scheduled:
        reason = f"Appointment is {appointment.status.replace('_', ' ')}."
    elif now < slot_start:
        reason = "Slot has not started yet."
    elif has_ended:
        reason = "Slot time has ended."
    else:
        reason = "Slot is active."

    return {
        "is_active": is_active,
        "has_started": has_started,
        "has_ended": has_ended,
        "appointment_status": appointment.status,
        "reason": reason,
        "slot_date": appointment.slot.date,
        "start_time": appointment.slot.start_time,
        "end_time": appointment.slot.end_time,
        "server_time": now,
        "starts_at": slot_start,
        "ends_at": slot_end,
    }


@csrf_exempt

def ai_assistant_page(request):
    return render(request, 'ai_assistant.html')


def ai_daily_dashboard_page(request):
    return render(request, 'ai_daily_dashboard.html')


def ai_medicines_page(request):
    return render(request, 'ai_medicines.html')


def ai_weekly_report_page(request):
    return render(request, 'ai_weekly_report.html')


def ai_patient_timeline_page(request):
    return render(request, 'ai_patient_timeline.html')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/api/video_call/')
    return render(request, 'login.html')


def signup_page(request):
    if request.user.is_authenticated:
        return redirect('/api/video_call/')
    departments = Department.objects.all().order_by("name")
    return render(request, 'signup.html', {
        "departments": departments,
    })


class DiseasePredictionMetadataAPIView(APIView):
    permission_classes = [AllowAny]
    @csrf_exempt
    def get(self, request):
        try:
            return Response({
                "message": "Disease prediction model metadata fetched successfully",
                "data": disease_prediction_service.metadata(),
                "note": "This model provides symptom-based suggestions only and is not a medical diagnosis."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiseasePredictionAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = DiseasePredictionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            symptoms = serializer.validated_data.get("symptoms") or []
            symptoms_text = serializer.validated_data.get("symptoms_text", "")
            top_k = serializer.validated_data.get("top_k", 3)

            if symptoms_text:
                text_symptoms = [
                    item.strip()
                    for item in re.split(r"[\n,]+", symptoms_text)
                    if item.strip()
                ]
                symptoms.extend(text_symptoms)

            result = disease_prediction_service.predict(symptoms=symptoms, top_k=top_k)

            return Response({
                "message": "Disease prediction generated successfully",
                "data": result,
                "note": "This is an AI-based prediction and should not replace professional medical advice."
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                "error": _flatten_validation_errors(e.detail),
                "errors": e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIAssistantAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = AIAssistantMessageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = serializer.validated_data
            attachment = payload.get("attachment")
            extracted_text = document_reader_service.extract_text(attachment) if attachment else ""
            attachment_context = document_reader_service.build_attachment_context(attachment, extracted_text) if attachment else {}
            extracted_medicines = clinical_document_ai_service.extract_prescription_medicines(extracted_text) if extracted_text else []
            extracted_metrics = clinical_document_ai_service.extract_lab_metrics(extracted_text) if extracted_text else []

            combined_message_parts = [payload.get("message", "")]
            if extracted_text:
                combined_message_parts.append(extracted_text)

            combined_message = "\n".join(part for part in combined_message_parts if part).strip()
            combined_symptoms_text = payload.get("symptoms_text", "")
            if extracted_text:
                combined_symptoms_text = "\n".join(part for part in [combined_symptoms_text, extracted_text] if part).strip()

            result = disease_prediction_service.assistant_reply(
                message=combined_message,
                symptoms=payload.get("symptoms") or [],
                symptoms_text=combined_symptoms_text,
                notes=payload.get("notes", ""),
                log_date=payload.get("log_date"),
                food_type=payload.get("food_type", ""),
                water_intake_glasses=payload.get("water_intake_glasses"),
                sleep_hours=payload.get("sleep_hours"),
                sleep_quality=payload.get("sleep_quality", ""),
                stress_level=payload.get("stress_level", ""),
                energy_level=payload.get("energy_level", ""),
                top_k=payload.get("top_k", 3),
            )
            analysis_record = AIAnalysisRecord.objects.create(
                user=request.user if request.user.is_authenticated else None,
                log_date=payload.get("log_date"),
                input_message=payload.get("message", ""),
                symptoms=payload.get("symptoms") or [],
                symptoms_text=payload.get("symptoms_text", ""),
                notes=payload.get("notes", ""),
                food_type=payload.get("food_type", ""),
                water_intake_glasses=payload.get("water_intake_glasses"),
                sleep_hours=payload.get("sleep_hours"),
                sleep_quality=payload.get("sleep_quality", ""),
                stress_level=payload.get("stress_level", ""),
                energy_level=payload.get("energy_level", ""),
                matched_symptoms=result.get("matched_symptoms") or [],
                detected_problem=result.get("detected_problem") or "",
                risk_probability=result.get("prediction", {}).get("confidence") or 0,
                model_name=result.get("prediction", {}).get("model") or "LogisticRegression",
                top_predictions=result.get("prediction", {}).get("top_predictions") or [],
                reference_symptoms=result.get("dataset_reference_symptoms") or [],
                care_guidance=result.get("care_guidance") or [],
                medicine_guidance=result.get("medicine_guidance") or [],
                warning_signs=result.get("warning_signs") or [],
                submitted_context=(result.get("submitted_context") or []) + (
                    [f"Attachment reviewed: {attachment_context.get('filename')}"] if attachment_context.get("filename") else []
                ),
                follow_up_questions=result.get("follow_up_questions") or [],
                assistant_response=result.get("assistant_response") or "",
                response_language=result.get("response_language") or "english",
            )

            result["risk_probability"] = result.get("prediction", {}).get("confidence") or 0
            result["analysis_record"] = AIAnalysisRecordSerializer(analysis_record).data
            result["attachment_context"] = attachment_context
            result["attachment_analysis"] = {
                "medicines": extracted_medicines,
                "report_metrics": extracted_metrics,
            }
            attachment_read_detail = ""
            if attachment_context.get("filename"):
                attachment_read_detail = f" after reading {attachment_context.get('filename')}"
            result["analysis_steps"] = [
                {
                    "step": "User enters symptoms",
                    "status": "completed",
                    "detail": payload.get("message") or payload.get("symptoms_text") or attachment_context.get("filename") or "Symptoms received successfully.",
                },
                {
                    "step": "System stores symptom data",
                    "status": "completed",
                    "detail": f"Analysis record #{analysis_record.id} saved for future health tracking.",
                },
                {
                    "step": "AI engine analyzes patterns",
                    "status": "completed",
                    "detail": f"{result.get('prediction', {}).get('model', 'AI model')} matched symptom patterns from the dataset{attachment_read_detail}.",
                },
                {
                    "step": "Platform provides disease insight and risk probability",
                    "status": "completed",
                    "detail": f"{result.get('detected_problem', 'Insight ready')} with {result.get('prediction', {}).get('confidence', 0)}% risk probability.",
                },
            ]

            return Response({
                "message": "AI assistant response generated successfully",
                "data": result,
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                "error": _flatten_validation_errors(e.detail),
                "errors": e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIDailyCheckInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requested_date = parse_date(request.GET.get("log_date", "")) or timezone.localdate()
        dashboard = health_tracking_ai_service.build_daily_dashboard(request.user, requested_date)
        return Response({
            "message": "Today's AI health dashboard fetched successfully",
            "data": dashboard,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        requested_date = request.data.get("log_date") or timezone.localdate()
        existing_log = DailyHealthLog.objects.filter(
            user=request.user,
            log_date=requested_date,
        ).first()

        serializer = DailyHealthLogSerializer(existing_log, data=request.data, partial=bool(existing_log))
        serializer.is_valid(raise_exception=True)
        daily_log = serializer.save(user=request.user)

        dashboard = health_tracking_ai_service.build_daily_dashboard(request.user, daily_log.log_date)
        return Response({
            "message": "Daily health check-in saved successfully",
            "data": {
                "log": DailyHealthLogSerializer(daily_log).data,
                "dashboard": dashboard,
            },
        }, status=status.HTTP_200_OK)


class AIMedicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        medications = MedicationSchedule.objects.filter(user=request.user).order_by("-created_at")
        serializer = MedicationScheduleSerializer(medications, many=True)
        return Response({
            "message": "Medicine schedules fetched successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MedicationScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        medication = serializer.save(user=request.user)
        return Response({
            "message": "Medicine schedule created successfully",
            "data": MedicationScheduleSerializer(medication).data,
        }, status=status.HTTP_201_CREATED)


class AIMedicationPrescriptionExtractAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PrescriptionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment = serializer.validated_data["attachment"]
        extracted_text = document_reader_service.extract_text(attachment)
        medicines = clinical_document_ai_service.extract_prescription_medicines(extracted_text)

        return Response({
            "message": "Prescription analyzed successfully",
            "data": {
                "filename": attachment.name,
                "extracted_text_preview": extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""),
                "medicines": medicines,
            },
        }, status=status.HTTP_200_OK)


class AIMedicationPrescriptionSaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PrescriptionMedicationSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["start_date"]
        created = []
        for item in serializer.validated_data["medicines"]:
            medication = MedicationSchedule.objects.create(
                user=request.user,
                name=item["name"],
                dose=item.get("dose", ""),
                duration_days=item.get("duration_days", 5),
                timings=item.get("timings") or ["morning", "night"],
                start_date=start_date,
                instructions=item.get("instructions", ""),
                source="prescription_upload",
            )
            created.append(MedicationScheduleSerializer(medication).data)

        return Response({
            "message": "Prescription medicines saved successfully",
            "data": created,
        }, status=status.HTTP_201_CREATED)


class AIMedicationDoseStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, medication_id):
        medication = get_object_or_404(MedicationSchedule, id=medication_id, user=request.user)
        serializer = MedicationDoseStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        timing = serializer.validated_data["timing"]
        if timing not in medication.timings:
            return Response({
                "error": "This timing is not configured for the selected medicine."
            }, status=status.HTTP_400_BAD_REQUEST)

        dose_date = serializer.validated_data.get("dose_date") or timezone.localdate()
        dose_log, _ = MedicationDoseLog.objects.update_or_create(
            medication=medication,
            dose_date=dose_date,
            timing=timing,
            defaults={
                "status": serializer.validated_data["status"],
                "marked_at": timezone.now(),
            },
        )

        dashboard = health_tracking_ai_service.build_daily_dashboard(request.user, dose_date)
        return Response({
            "message": "Medicine dose updated successfully",
            "data": {
                "dose_log": MedicationDoseLogSerializer(dose_log).data,
                "dashboard": dashboard,
            },
        }, status=status.HTTP_200_OK)


class AIWeeklyHealthReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requested_end_date = parse_date(request.GET.get("end_date", "")) or timezone.localdate()
        report = health_tracking_ai_service.build_weekly_report(request.user, requested_end_date)
        return Response({
            "message": "Weekly AI health report generated successfully",
            "data": report,
        }, status=status.HTTP_200_OK)


class AIWeeklyHealthReportPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requested_end_date = parse_date(request.GET.get("end_date", "")) or timezone.localdate()
        report = health_tracking_ai_service.build_weekly_report(request.user, requested_end_date)
        pdf_bytes = build_weekly_report_pdf(
            report,
            patient_label=request.user.email,
            end_date=requested_end_date,
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="medoair-weekly-report-{requested_end_date.isoformat()}.pdf"'
        )
        return response


class AIPatientTimelineAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        patient_user = get_object_or_404(User, id=patient_id, role='patient')

        has_access = (
            request.user.id == patient_user.id
            or request.user.is_staff
            or (
                request.user.role == 'doctor'
                and Appointment.objects.filter(
                    doctor=request.user,
                    patient=patient_user,
                ).exists()
            )
        )

        if not has_access:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        timeline = health_tracking_ai_service.build_doctor_timeline(patient_user)
        return Response({
            "message": "Patient AI timeline fetched successfully",
            "data": timeline,
        }, status=status.HTTP_200_OK)

# ============== AUTHENTICATION VIEWS ==============

class UserSignupAPIView(APIView):
    """User registration"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register new user"""
        try:
            serializer = UserSignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
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
        except IntegrityError:
            return Response({
                "message": "Registration failed",
                "errors": {
                    "username": ["Username already taken. Please choose another username."]
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({
                "message": "Registration failed",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoctorSignupAPIView(APIView):
    """Doctor registration"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register new doctor"""
        try:
            serializer = DoctorSignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
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
        except IntegrityError:
            return Response({
                "message": "Registration failed",
                "errors": {
                    "username": ["Username already taken. Please choose another username."]
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({
                "message": "Registration failed",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
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
                login(request, user)
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
            slot_status = _get_appointment_slot_status(appointment)

            if not slot_status["is_active"]:
                return Response({
                    "error": f"Chat is unavailable. {slot_status['reason']}"
                }, status=400)

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

        for message in messages:
            if message.receiver == request.user and not message.is_read:
                message.is_read = True
                message.save(update_fields=["is_read"])

        data = [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "sender": m.sender.username,
                "receiver_id": m.receiver_id,
                "receiver": m.receiver.username,
                "message": m.message,
                "is_read": m.is_read,
                "created_at": m.created_at
            }
            for m in messages
        ]

        return Response({"messages": data})


class AppointmentCommunicationStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if request.user not in [appointment.patient, appointment.doctor]:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        slot_status = _get_appointment_slot_status(appointment)
        return Response({
            "appointment_id": appointment.id,
            "chat_enabled": slot_status["is_active"],
            "audio_enabled": slot_status["is_active"],
            "video_enabled": slot_status["is_active"],
            "slot_status": slot_status,
        }, status=status.HTTP_200_OK)


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


@login_required
def video_call(request):
    appointment_id = request.GET.get("appointment_id", "")
    stun_url = getattr(settings, "WEBRTC_STUN_URL", "stun:stun.relay.metered.ca:80")
    turn_url_tcp = getattr(settings, "WEBRTC_TURN_URL_TCP", "turn:global.relay.metered.ca:80")
    turn_url_tls = getattr(settings, "WEBRTC_TURN_URL_TLS", "turn:global.relay.metered.ca:443")
    turn_username = getattr(settings, "WEBRTC_TURN_USERNAME", "")
    turn_credential = getattr(settings, "WEBRTC_TURN_CREDENTIAL", "")
    ice_servers = [{"urls": stun_url}]

    if turn_username and turn_credential:
        ice_servers.extend([
            {
                "urls": turn_url_tcp,
                "username": turn_username,
                "credential": turn_credential,
            },
            {
                "urls": turn_url_tls,
                "username": turn_username,
                "credential": turn_credential,
            },
        ])

    return render(request, 'chat2.html', {
        "current_user_id": request.user.id,
        "current_username": request.user.username,
        "prefill_appointment_id": appointment_id,
        "turn_config": {
            "iceServers": ice_servers
        }
    })






class UserDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctors = DoctorProfile.objects.select_related('user').all().order_by('user__username')
        serializer = DoctorDashboardSerializer(
            doctors,
            many=True,
            context={'request': request}
        )
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        }, status=status.HTTP_200_OK)

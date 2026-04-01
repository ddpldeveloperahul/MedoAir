# MedoAir Complete CRUD API Documentation

**Last Updated:** April 2026  
**API Version:** 1.0 (Consolidated)  
**Status:** All endpoints consolidated into unified `api` app

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Most endpoints require JWT Bearer token authentication:
```
Authorization: Bearer <access_token>
```

## Quick Endpoint Reference

| Category | Count | Key Endpoints |
|----------|-------|---------------|
| User Management | 5 | /users/, /users/me/, /users/{id}/ |
| Authentication | 6 | /login/, /user/signup/, /doctor/signup/, /forgot-password/, /reset-password/ |
| Patient Profiles | 6 | /patients/, /patients/me/, /patients/{id}/health-metrics/ |
| Doctor Profiles | 2 | /doctors/, /doctors/{id}/ |
| Appointments | 4 | /appointments/, /appointments/{id}/, /slots/, /slots/{id}/ |
| Messages | 1 | /api/appointments/{id}/messages/ |
| Reports | 2 | /reports/, /reports/{id}/ |
| Admin Dashboard | 8 | /admin/dashboard/, /admin/users/, /admin/doctors/, /admin/patients/, /admin/appointments/ |
| Chat/Video | 4 | /chat/{id}/, /chat2/{id}/, /messages/{id}/, /video_call/ |
| **TOTAL** | **38+** | Complete patient-doctor ecosystem |

---

## 🔐 AUTHENTICATION ENDPOINTS

### 1. User Signup
**Endpoint:** `POST /api/user/signup/`

**Description:** Register a new patient user

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**Response (201):**
```json
{
  "msg": "User created successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

---

### 2. Doctor Signup
**Endpoint:** `POST /api/doctor/signup/`

**Description:** Register a new doctor with department

**Request Body:**
```json
{
  "name": "Dr. Smith",
  "email": "doctor@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "department_id": 1
}
```

**Response (201):**
```json
{
  "msg": "Doctor created successfully",
  "user": {
    "id": 2,
    "name": "Dr. Smith",
    "email": "doctor@example.com",
    "role": "doctor",
    "department": "Cardiology"
  }
}
```

---

### 3. Login
**Endpoint:** `POST /api/login/`

**Description:** User login to get JWT tokens

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "",
    "address": "",
    "profile_image_url": null,
    "date_of_birth": null,
    "gender": null,
    "role": "user",
    "is_verified": false,
    "date_joined": "2024-03-20T10:00:00Z"
  }
}
```

---

### 4. Forgot Password
**Endpoint:** `POST /api/forgot-password/`

**Description:** Request OTP for password reset

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "msg": "OTP sent to your email",
  "email": "john@example.com"
}
```

---

### 5. Reset Password
**Endpoint:** `POST /api/reset-password/`

**Description:** Reset password using OTP

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response (200):**
```json
{
  "msg": "Password reset successfully"
}
```

---

### 6. Resend OTP
**Endpoint:** `POST /api/resend-otp/`

**Description:** Resend OTP to email

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "msg": "New OTP sent to your email",
  "email": "john@example.com"
}
```

---

## 👥 USER MANAGEMENT ENDPOINTS (CRUD)

### 1. List All Users
**Endpoint:** `GET /api/users/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "1234567890",
      "address": "123 Main St",
      "profile_image": "/media/profiles/john_profile.jpg",
      "profile_image_url": "http://localhost:8000/media/profiles/john_profile.jpg",
      "date_of_birth": "1990-01-15",
      "gender": "Male",
      "role": "user",
      "is_verified": true,
      "date_joined": "2024-03-20T10:00:00Z"
    }
  ]
}
```

---

### 2. Get User Details
**Endpoint:** `GET /api/users/<int:user_id>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "User retrieved successfully",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "address": "123 Main St",
    "profile_image_url": "http://localhost:8000/media/profiles/john_profile.jpg",
    "date_of_birth": "1990-01-15",
    "gender": "Male",
    "role": "user",
    "is_verified": true,
    "date_joined": "2024-03-20T10:00:00Z"
  }
}
```

---

### 3. Get Current User Profile
**Endpoint:** `GET /api/users/me/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get the authenticated user's profile

**Response (200):**
```json
{
  "message": "Current user retrieved",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "address": "123 Main St",
    "profile_image_url": "http://localhost:8000/media/profiles/john_profile.jpg",
    "date_of_birth": "1990-01-15",
    "gender": "Male",
    "role": "user",
    "is_verified": true,
    "date_joined": "2024-03-20T10:00:00Z"
  }
}
```

---

### 4. Change Password
**Endpoint:** `POST /api/users/change-password/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "old_password": "password123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

---

### 5. Get User Profile Statistics
**Endpoint:** `GET /api/users/profile-stats/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get statistics about the user's profile completion and account info

**Response (200):**
```json
{
  "user_id": 1,
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_verified": true,
  "profile_complete": true,
  "last_login": "2024-03-23T10:30:00Z",
  "account_age_days": 3
}
```

---

## 🏥 PATIENT PROFILE ENDPOINTS (CRUD)

---

### 7. Change Password
**Endpoint:** `POST /accounts/api/users/change_password/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "old_password": "password123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

---

### 8. Get User Profile Statistics
**Endpoint:** `GET /accounts/api/users/profile_stats/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "user_id": 1,
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_verified": true,
  "profile_complete": true,
  "last_login": "2024-03-23T10:30:00Z",
  "account_age_days": 3
}
```

---

## 🏥 PATIENT PROFILE ENDPOINTS (CRUD)

### 1. List All Patient Profiles
**Endpoint:** `GET /api/patients/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get list of all patient profiles (admin/doctor access)

**Response (200):**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "1234567890",
        "address": "123 Main St",
        "profile_image_url": "http://localhost:8000/media/profiles/john.jpg",
        "date_of_birth": "1990-01-15",
        "gender": "Male",
        "role": "user",
        "is_verified": true,
        "date_joined": "2024-03-20T10:00:00Z"
      },
      "age": 34,
      "height": 180.0,
      "weight": 75.5,
      "blood_group": "O+",
      "activity": "Moderately Active",
      "diet": "Mixed",
      "stress": "Low",
      "sleep_hours": 8,
      "bmi": 23.3,
      "medical_history": "No major illnesses",
      "allergies": "Peanuts",
      "current_medications": "None",
      "family_history": "Diabetes in family",
      "emergency_contact": "Jane Doe",
      "emergency_contact_phone": "9876543210",
      "insurance_provider": "Blue Cross",
      "insurance_number": "BC123456",
      "created_at": "2024-03-20T10:30:00Z",
      "updated_at": "2024-03-23T10:00:00Z"
    }
  ]
}
```

---

### 2. Get Patient Profile Details
**Endpoint:** `GET /api/patients/<int:patient_id>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get detailed information for a specific patient

**Response (200):**
```json
{
  "message": "Patient profile retrieved successfully",
  "profile": {...}
}
```

---

### 3. Get Current Patient's Own Profile
**Endpoint:** `GET /api/patients/me/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get the authenticated patient's own profile

**Response (200):**
```json
{
  "id": 1,
  "user": {...},
  "age": 34,
  "height": 180.0,
  "weight": 75.5,
  "blood_group": "O+",
  "activity": "Moderately Active",
  "diet": "Mixed",
  "stress": "Low",
  "sleep_hours": 8,
  "bmi": 23.3,
  "medical_history": "No major illnesses",
  "created_at": "2024-03-20T10:30:00Z",
  "updated_at": "2024-03-23T10:00:00Z"
}
```

---

### 4. Get Patient Health Summary
**Endpoint:** `GET /api/patients/health-summary/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get health summary for authenticated patient (BMI, metrics, recommendations)

**Response (200):**
```json
{
  "patient_id": 1,
  "bmi": 23.3,
  "bmi_status": "Normal",
  "weight_status": "Healthy",
  "vital_score": 95,
  "health_recommendations": [
    "Continue current exercise routine",
    "Maintain balanced diet"
  ]
}
```

---

### 5. Get Patient Health Metrics
**Endpoint:** `GET /api/patients/<int:patient_id>/health-metrics/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get detailed health metrics for a specific patient

**Response (200):**
```json
{
  "patient_id": 1,
  "age": 34,
  "height": 180.0,
  "weight": 75.5,
  "bmi": 23.3,
  "blood_group": "O+",
  "blood_pressure": "120/80",
  "heart_rate": 72,
  "respiratory_rate": 16,
  "temperature": 98.6
}
```

---

### 6. Bulk Health Update
**Endpoint:** `POST /api/patients/health-update/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Description:** Update multiple health metrics at once

**Request Body:**
```json
{
  "weight": 76.0,
  "activity": "Very Active",
  "stress": "Moderate",
  "sleep_hours": 7.5,
  "diet": "Mixed",
  "blood_pressure": "120/80",
  "heart_rate": 72
}
```

**Response (200):**
```json
{
  "message": "Health metrics updated successfully",
  "updated_fields": ["weight", "activity", "blood_pressure"]
}
```

---

## 👨‍⚕️ DOCTOR PROFILE ENDPOINTS

---

## 👨‍⚕️ DOCTOR PROFILE ENDPOINTS

### 1. List All Doctors
**Endpoint:** `GET /api/doctors/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** List all doctors with their profiles and availability

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "email": "drsahir@example.com",
        "first_name": "Sahir",
        "last_name": "Khan",
        "phone": "1234567890"
      },
      "department": {
        "id": 1,
        "name": "Cardiology",
        "description": "Heart and cardiovascular diseases"
      },
      "specialization": "Interventional Cardiology",
      "experience_years": 10,
      "consultation_fee": 500,
      "bio": "Expert cardiologist with 10 years experience",
      "registration_number": "MC123456",
      "qualifications": "MBBS, MD Cardiology",
      "availability_status": "Available",
      "average_rating": 4.8,
      "total_ratings": 45,
      "is_verified": true,
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-03-23T10:00:00Z"
    }
  ]
}
```

---

### 2. Get Doctor Details
**Endpoint:** `GET /api/doctors/<int:pk>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get detailed profile of a specific doctor including availability and ratings

**Response (200):**
```json
{
  "id": 1,
  "user": {...},
  "department": {...},
  "specialization": "Interventional Cardiology",
  "experience_years": 10,
  "consultation_fee": 500,
  "bio": "Expert cardiologist with 10 years experience",
  "registration_number": "MC123456",
  "qualifications": "MBBS, MD Cardiology",
  "availability_status": "Available",
  "average_rating": 4.8,
  "total_ratings": 45,
  "is_verified": true,
  "next_available_slot": "2024-03-24T10:00:00Z"
}
```

---

### 3. Create Doctor Profile (Admin)
**Endpoint:** `POST /api/doctors/`

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 2,
  "department_id": 1,
  "specialization": "General Medicine",
  "experience_years": 5,
  "consultation_fee": 300,
  "bio": "Experienced general physician",
  "registration_number": "MC789012",
  "qualifications": "MBBS, General Medicine"
}
```

**Response (201):**
```json
{
  "message": "Doctor profile created successfully",
  "doctor": {...}
}
```

---

### 4. Update Doctor Profile
**Endpoint:** `PUT /api/doctors/<int:pk>/` or `PATCH /api/doctors/<int:pk>/`

**Headers:**
```
Authorization: Bearer <doctor_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "bio": "Updated bio",
  "availability_status": "On Leave",
  "consultation_fee": 600
}
```

**Response (200):**
```json
{
  "message": "Doctor profile updated successfully",
  "doctor": {...}
}
```

---

### 5. Delete Doctor Profile
**Endpoint:** `DELETE /api/doctors/<int:pk>/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Doctor profile Dr. Sahir Khan deleted successfully"
}
```

---

## 📅 APPOINTMENT & SLOT ENDPOINTS

### 1. List Available Slots
**Endpoint:** `GET /api/slots/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
?doctor_id=1&date=2024-03-24&status=available
```

**Description:** Get available appointment slots for doctors

**Response (200):**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "doctor": {
        "id": 1,
        "user": "Dr. Sahir Khan",
        "department": "Cardiology"
      },
      "start_time": "2024-03-24T09:00:00Z",
      "end_time": "2024-03-24T09:30:00Z",
      "status": "available",
      "max_patients": 1,
      "booked_count": 0,
      "created_at": "2024-03-20T10:00:00Z"
    }
  ]
}
```

---

### 2. Get Slot Details
**Endpoint:** `GET /api/slots/<int:pk>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "doctor": {...},
  "start_time": "2024-03-24T09:00:00Z",
  "end_time": "2024-03-24T09:30:00Z",
  "status": "available",
  "max_patients": 1,
  "booked_count": 0
}
```

---

### 3. Create Slot (Doctor)
**Endpoint:** `POST /api/slots/`

**Headers:**
```
Authorization: Bearer <doctor_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "start_time": "2024-03-24T09:00:00Z",
  "end_time": "2024-03-24T09:30:00Z",
  "max_patients": 1
}
```

**Response (201):**
```json
{
  "message": "Slot created successfully",
  "slot": {...}
}
```

---

### 4. Update Slot
**Endpoint:** `PUT /api/slots/<int:pk>/` or `PATCH /api/slots/<int:pk>/`

**Headers:**
```
Authorization: Bearer <doctor_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "unavailable",
  "max_patients": 2
}
```

**Response (200):**
```json
{
  "message": "Slot updated successfully",
  "slot": {...}
}
```

---

### 5. Delete Slot
**Endpoint:** `DELETE /api/slots/<int:pk>/`

**Headers:**
```
Authorization: Bearer <doctor_token>
```

**Response (200):**
```json
{
  "message": "Slot deleted successfully"
}
```

---

### 6. List Appointments
**Endpoint:** `GET /api/appointments/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
?doctor_id=1&patient_id=1&status=confirmed&date=2024-03-24
```

**Description:** Get list of appointments (filtered based on user role)

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "patient": {
        "id": 1,
        "user": "John Doe",
        "email": "john@example.com"
      },
      "doctor": {
        "id": 1,
        "user": "Dr. Sahir Khan",
        "department": "Cardiology"
      },
      "appointment_slot": "2024-03-24T10:00:00Z",
      "status": "confirmed",
      "reason_for_visit": "Regular checkup",
      "notes": "Patient has hypertension history",
      "appointment_type": "in-person",
      "created_at": "2024-03-20T10:00:00Z",
      "updated_at": "2024-03-23T10:00:00Z"
    }
  ]
}
```

---

### 7. Get Appointment Details
**Endpoint:** `GET /api/appointments/<int:pk>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "patient": {...},
  "doctor": {...},
  "appointment_slot": "2024-03-24T10:00:00Z",
  "status": "confirmed",
  "reason_for_visit": "Regular checkup",
  "notes": "Patient has hypertension history",
  "appointment_type": "in-person",
  "created_at": "2024-03-20T10:00:00Z",
  "updated_at": "2024-03-23T10:00:00Z"
}
```

---

### 8. Create Appointment (Book)
**Endpoint:** `POST /api/appointments/`

**Headers:**
```
Authorization: Bearer <patient_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "doctor_id": 1,
  "slot_id": 5,
  "reason_for_visit": "Regular checkup",
  "notes": "Family history of hypertension",
  "appointment_type": "in-person"
}
```

**Response (201):**
```json
{
  "message": "Appointment booked successfully",
  "appointment": {...}
}
```

---

### 9. Update Appointment
**Endpoint:** `PUT /api/appointments/<int:pk>/` or `PATCH /api/appointments/<int:pk>/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "completed",
  "notes": "Patient doing well, continue current medication"
}
```

**Response (200):**
```json
{
  "message": "Appointment updated successfully",
  "appointment": {...}
}
```

---

### 10. Cancel Appointment
**Endpoint:** `DELETE /api/appointments/<int:pk>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Appointment cancelled successfully"
}
```

---

### 11. Get Doctor Dashboard
**Endpoint:** `GET /api/doctor/dashboard/`

**Headers:**
```
Authorization: Bearer <doctor_token>
```

**Description:** Get dashboard statistics for a doctor (appointments, patients, ratings)

**Response (200):**
```json
{
  "total_appointments": 150,
  "appointments_today": 5,
  "appointments_pending": 2,
  "total_patients": 45,
  "average_rating": 4.8,
  "total_ratings": 45,
  "revenue_this_month": 25000,
  "upcoming_appointments": [
    {
      "id": 1,
      "patient": "John Doe",
      "time": "2024-03-24T10:00:00Z",
      "status": "confirmed"
    }
  ]
}
```

---

## 💬 MESSAGE & CHAT ENDPOINTS

### 1. Get Message History for Appointment
**Endpoint:** `GET /api/api/appointments/<int:appointment_id>/messages/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get all messages in an appointment conversation

**Response (200):**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "appointment": 1,
      "sender": {
        "id": 1,
        "name": "John Doe",
        "role": "patient"
      },
      "message": "Hi Doctor, I have been having headaches",
      "message_type": "text",
      "created_at": "2024-03-24T09:00:00Z",
      "updated_at": "2024-03-24T09:00:00Z"
    }
  ]
}
```

---

### 2. Send Message in Chat
**Endpoint:** `POST /api/chat/<int:appointment_id>/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Hi Doctor, I have been having headaches",
  "message_type": "text",
  "attachment": null
}
```

**Response (201):**
```json
{
  "message": "Message sent successfully",
  "data": {
    "id": 16,
    "appointment": 1,
    "sender": "John Doe",
    "message": "Hi Doctor, I have been having headaches",
    "created_at": "2024-03-24T10:30:00Z"
  }
}
```

---

### 3. Get Chat History
**Endpoint:** `GET /api/chat2/<int:appointment_id>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Get complete chat/message history for an appointment

**Response (200):**
```json
{
  "appointment_id": 1,
  "patient": "John Doe",
  "doctor": "Dr. Sahir Khan",
  "conversation_status": "active",
  "message_count": 15,
  "messages": [...]
}
```

---

### 4. Delete Message
**Endpoint:** `DELETE /api/messages/<int:message_id>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Message deleted successfully"
}
```

---

### 5. Video Call
**Endpoint:** `GET /api/video_call/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Description:** Initialize video call for an appointment

**Response (200):**
```json
{
  "room_id": "appointment_123_456",
  "video_url": "http://localhost:8000/video-room/appointment_123_456/",
  "status": "ready"
}
```

---

## 📄 REPORT ENDPOINTS

### 1. List Reports
**Endpoint:** `GET /api/reports/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
?doctor_id=1&patient_id=1&report_type=lab
```

**Description:** Get medical reports (filtered by role)

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "appointment": {
        "id": 1,
        "patient": "John Doe",
        "doctor": "Dr. Sahir Khan"
      },
      "report_type": "lab",
      "title": "Blood Test Report",
      "description": "Complete blood profile",
      "report_file": "/media/reports/blood_test_2024.pdf",
      "report_date": "2024-03-23",
      "created_at": "2024-03-23T10:00:00Z",
      "updated_at": "2024-03-23T10:00:00Z"
    }
  ]
}
```

---

### 2. Get Report Details
**Endpoint:** `GET /api/reports/<int:report_id>/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "appointment": {...},
  "report_type": "lab",
  "title": "Blood Test Report",
  "description": "Complete blood profile",
  "report_file": "/media/reports/blood_test_2024.pdf",
  "report_file_url": "http://localhost:8000/media/reports/blood_test_2024.pdf",
  "report_date": "2024-03-23",
  "created_at": "2024-03-23T10:00:00Z"
}
```

---

### 3. Create Report (Doctor)
**Endpoint:** `POST /api/reports/`

**Headers:**
```
Authorization: Bearer <doctor_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
appointment_id=1
report_type=lab
title=Blood Test Report
description=Complete blood profile
report_file=<file>
report_date=2024-03-23
```

**Response (201):**
```json
{
  "message": "Report created successfully",
  "report": {...}
}
```

---

### 4. Update Report
**Endpoint:** `PUT /api/reports/<int:report_id>/` or `PATCH /api/reports/<int:report_id>/`

**Headers:**
```
Authorization: Bearer <doctor_token>
Content-Type: multipart/form-data
```

**Response (200):**
```json
{
  "message": "Report updated successfully",
  "report": {...}
}
```

---

### 5. Delete Report
**Endpoint:** `DELETE /api/reports/<int:report_id>/`

**Headers:**
```
Authorization: Bearer <doctor_token>
```

**Response (200):**
```json
{
  "message": "Report deleted successfully"
}
```

---

## 🔐 SUPER ADMIN ENDPOINTS

### Admin Dashboard
**Endpoint:** `GET /api/admin/dashboard/`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Description:** Get comprehensive admin dashboard statistics

**Response (200):**
```json
{
  "total_users": 150,
  "total_patients": 120,
  "total_doctors": 30,
  "total_appointments": 500,
  "pending_appointments": 15,
  "completed_appointments": 485,
  "total_revenue": 250000,
  "new_users_this_month": 25,
  "platform_health": "Good"
}
```

---

### User Management
**Endpoint:** 
- `GET /api/admin/users/` - List all users
- `GET /api/admin/users/<int:user_id>/` - Get user details
- `PUT /api/admin/users/<int:user_id>/` - Update user
- `DELETE /api/admin/users/<int:user_id>/` - Delete user

---

### Doctor Management
**Endpoint:**
- `GET /api/admin/doctors/` - List all doctors
- `GET /api/admin/doctors/<int:doctor_id>/` - Get doctor details
- `PUT /api/admin/doctors/<int:doctor_id>/` - Update doctor
- `DELETE /api/admin/doctors/<int:doctor_id>/` - Delete doctor

---

### Patient Management
**Endpoint:**
- `GET /api/admin/patients/` - List all patients
- `GET /api/admin/patients/<int:patient_id>/` - Get patient details
- `PUT /api/admin/patients/<int:patient_id>/` - Update patient
- `DELETE /api/admin/patients/<int:patient_id>/` - Delete patient

---

### Appointment Management
**Endpoint:**
- `GET /api/admin/appointments/` - List all appointments
- `GET /api/admin/appointments/<int:appointment_id>/` - Get appointment details
- `PUT /api/admin/appointments/<int:appointment_id>/` - Update appointment
- `DELETE /api/admin/appointments/<int:appointment_id>/` - Delete appointment

---

## 🏠 GENERAL ENDPOINTS

### Home/API Root
**Endpoint:** `GET /api/index/`

**Description:** API root endpoint for navigation and available resources

**Response (200):**
```json
{
  "message": "Welcome to MedoAir API",
  "version": "1.0",
  "endpoints": {
    "auth": "/api/login/",
    "users": "/api/users/",
    "patients": "/api/patients/",
    "doctors": "/api/doctors/",
    "appointments": "/api/appointments/",
    "reports": "/api/reports/"
  }
}
```

---

## 📊 API RESPONSE CODES

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

---

## � AUTHENTICATION & AUTHORIZATION

### JWT Token Usage
All protected endpoints require JWT Bearer token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Obtaining Tokens

**Signup requests return tokens:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Refresh Token (when access expires):**
```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Role-Based Access Control
| Role | Access | Endpoints |
|------|--------|-----------|
| **patient** | Own profile, appointments, messages | /patients/me/, /appointments/ |
| **doctor** | Doctor profile, slots, appointments, reports | /doctor/dashboard/, /slots/, /reports/ |
| **admin** | All endpoints | /admin/* |

---

## 🖼️ FILE UPLOADS

### Supported File Types
- **Profile Image:** JPG, PNG, GIF
- **Report File:** PDF, DOC, DOCX, XLS, XLSX
- **Max Size:** 5MB (recommended)

### Upload Example
```bash
curl -X POST http://localhost:8000/api/reports/ \
  -H "Authorization: Bearer <access_token>" \
  -F "appointment_id=1" \
  -F "report_type=lab" \
  -F "title=Blood Test" \
  -F "report_file=@report.pdf"
```

---

## 📝 DATA VALIDATION RULES

### User Fields
| Field | Rules |
|-------|-------|
| **Email** | Must be unique, valid email format |
| **Password** | Min 6 chars, at least 1 number |
| **Name** | Min 3 chars, alphabetic + space |
| **Phone** | Optional, max 20 chars |
| **Date of Birth** | Valid date, age > 18 |

### Patient Fields
| Field | Rules |
|-------|-------|
| **Age** | 18-120 |
| **Height** | 100-250 cm |
| **Weight** | 20-300 kg |
| **Blood Group** | A+, A-, B+, B-, AB+, AB-, O+, O- |
| **BMI** | Auto-calculated (weight/height²) |

### Doctor Fields
| Field | Rules |
|-------|-------|
| **Experience Years** | 0-60 |
| **Consultation Fee** | > 0 |
| **Registration Number** | Unique, valid format |
| **Qualifications** | Min 5 chars |

---

## ⚠️ ERROR HANDLING

### Common Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**400 Bad Request:**
```json
{
  "email": ["Email field is required."],
  "password": ["Password must be at least 6 characters."]
}
```

---

## 🔍 FILTERING & PAGINATION

### List Endpoints Support:

**Pagination:**
```
GET /api/users/?page=1&page_size=20
```

**Filtering:**
```
GET /api/appointments/?doctor_id=1&status=confirmed
GET /api/patients/?blood_group=O+&activity=Active
```

**Ordering:**
```
GET /api/appointments/?ordering=-created_at
GET /api/doctors/?ordering=average_rating
```

**Search:**
```
GET /api/doctors/?search=cardiology
GET /api/users/?search=john
```

---

## 🚀 BEST PRACTICES

### 1. Rate Limiting
- API requests are rate-limited to prevent abuse
- Recommended: Space requests at least 100ms apart

### 2. Error Handling
- Always check response status codes
- Parse error messages for debugging
- Implement retry logic for 5xx errors

### 3. Authentication
- Never expose access tokens in client-side code
- Use httpOnly cookies in production
- Refresh tokens before expiration

### 4. Data Validation
- Validate input on client side before sending
- Handle validation errors gracefully
- Use provided error messages for user feedback

### 5. Performance
- Use pagination for large result sets
- Implement request caching where appropriate
- Use filtering to reduce response sizes

---

## 📞 SUPPORT & DOCUMENTATION

For API issues or clarifications:
1. Check the error message and HTTP status code
2. Review this documentation for the specific endpoint
3. Contact support with:
   - Endpoint name
   - HTTP method and URL
   - Request body (if applicable)
   - Error response
   - Timestamp

---

**API Version:** 1.0  
**Last Updated:** April 2026  
**Status:** Production Ready
- **Profile Image:** Optional, supports JPG/PNG/GIF

### Patient Profile Fields
- **Height:** In centimeters (cm)
- **Weight:** In kilograms (kg)
- **Blood Group:** O+, O-, A+, A-, B+, B-, AB+, AB-
- **Activity:** Sedentary, Lightly Active, Moderately Active, Very Active
- **Diet:** Vegetarian, Non-Vegetarian, Vegan, Mixes
- **Stress:** Low, Moderate, High

---

## 🔑 JWT TOKEN USAGE

### Access Token Lifetime
**Default:** 10 days

### Using Token in Requests
```bash
curl -X GET http://localhost:8000/accounts/api/users/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

---

## ✅ COMPLETE SETUP CHECKLIST

- [x] User authentication (signup, login, password reset)
- [x] User CRUD operations
- [x] Profile image upload and retrieval
- [x] Patient profile management
- [x] Health metrics tracking
- [x] JWT token authentication
- [x] Permission-based access control
- [x] Full API documentation

---

## 🚀 QUICK START

1. **Create User:**
   ```bash
   curl -X POST http://localhost:8000/accounts/user/signup/ \
     -H "Content-Type: application/json" \
     -d '{"name": "John", "email": "john@test.com", "password": "pass123", "confirm_password": "pass123"}'
   ```

2. **Login:**
   ```bash
   curl -X POST http://localhost:8000/accounts/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "john@test.com", "password": "pass123"}'
   ```

3. **Update Profile:**
   ```bash
   curl -X PATCH http://localhost:8000/accounts/api/users/1/ \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"phone": "1234567890", "address": "123 Main St"}'
   ```

4. **Create Patient Profile:**
   ```bash
   curl -X POST http://localhost:8000/patients/api/profiles/ \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"age": 30, "height": 180, "weight": 75, "blood_group": "O+"}'
   ```

---

Generated: 2024-03-23
API Version: 1.0



GET /doctor/completed-patients/
{
    "count": 0,
    "next": null,
    "previous": null,
    "results": []
}

GET /doctor/completed-patients/?search=rahul

GET /doctor/completed-patients/?page=2

GET /doctor/completed-patients/?page_size=20


{
  "count": 12,
  "next": "http://127.0.0.1:8000/api?page=2",
  "previous": null,
  "results": [
    {
      "id": 5,
      "username": "rahul",
      "email": "rahul@gmail.com",
      "last_visit": "2026-03-20T10:30:00Z",
      "total_visits": 3
    }
  ]
}
# MedoAir Complete API Documentation

**Last Updated:** April 2026  
**API Version:** 1.0 (Consolidated)  
**Status:** ✅ Production Ready - All 37 Endpoints Active

## Base URL
```
http://localhost:8001/api/
```

## Authentication
Most endpoints require JWT Bearer token authentication:
```
Authorization: Bearer <access_token>
```

---

## 📊 Quick Endpoint Summary

| Category | Count | Endpoints |
|----------|-------|-----------|
| Authentication | 6 | User signup, doctor signup, login, forgot-password, reset-password, resend-otp |
| Patient Profiles | 6 | List, detail, my-profile, health-summary, health-metrics, health-update |
| Doctor Profiles | 4 | List, detail, dashboard, completed-patients |
| Appointments & Slots | 4 | List, detail, create, update/delete |
| Messages & Chat | 5 | List messages, send, history, delete, video-call |
| Reports | 2 | List, detail/create/update/delete |
| Super Admin | 9 | Dashboard, users (CRUD), doctors (CRUD), patients (CRUD), appointments (CRUD) |
| Home | 1 | API index/root |
| **TOTAL** | **37** | Complete healthcare platform |

---

## 🔐 AUTHENTICATION ENDPOINTS (6)

### 1. Patient Signup
**Endpoint:** `POST /api/user/signup/`

**Headers:** Not required

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
    "role": "patient"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 2. Doctor Signup
**Endpoint:** `POST /api/doctor/signup/`

**Headers:** Not required

**Request Body:**
```json
{
  "name": "Dr. Sahir Khan",
  "email": "drsahir@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "department_id": 1,
  "specialization": "Cardiology",
  "experience_years": 10,
  "registration_number": "MC123456"
}
```

**Response (201):**
```json
{
  "msg": "Doctor created successfully",
  "user": {
    "id": 2,
    "name": "Dr. Sahir Khan",
    "email": "drsahir@example.com",
    "role": "doctor",
    "department": "Cardiology"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 3. Login
**Endpoint:** `POST /api/login/`

**Headers:** Not required

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
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "role": "patient"
  }
}
```

---

### 4. Forgot Password
**Endpoint:** `POST /api/forgot-password/`

**Headers:** Not required

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

**Headers:** Not required

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
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

**Headers:** Not required

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "msg": "New OTP sent to your email"
}
```

---

## 👤 PATIENT PROFILE ENDPOINTS (6)

### 1. List All Patients
**Endpoint:** `GET /api/patients/`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:** `?page=1&page_size=20&search=john`

**Response (200):**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "user": {"id": 1, "name": "John Doe", "email": "john@example.com"},
      "age": 34,
      "height": 180.0,
      "weight": 75.5,
      "blood_group": "O+",
      "activity": "Moderately Active",
      "bmi": 23.3,
      "medical_history": "No major illnesses",
      "created_at": "2024-03-20T10:30:00Z"
    }
  ]
}
```

---

### 2. Get Patient Details
**Endpoint:** `GET /api/patients/<int:patient_id>/`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "user": {"id": 1, "name": "John Doe", "email": "john@example.com"},
  "age": 34,
  "height": 180.0,
  "weight": 75.5,
  "blood_group": "O+",
  "bmi": 23.3,
  "medical_history": "No major illnesses"
}
```

---

### 3. Get Current Patient Profile
**Endpoint:** `GET /api/patients/me/`

**Headers:** `Authorization: Bearer <patient_token>`

**Response (200):**
```json
{
  "id": 1,
  "user": {"id": 1, "name": "John Doe"},
  "age": 34,
  "weight": 75.5,
  "blood_group": "O+",
  "bmi": 23.3
}
```

---

### 4. Get Health Summary
**Endpoint:** `GET /api/patients/health-summary/`

**Headers:** `Authorization: Bearer <patient_token>`

**Response (200):**
```json
{
  "patient_id": 1,
  "bmi": 23.3,
  "bmi_status": "Normal",
  "weight_status": "Healthy",
  "vital_score": 95,
  "health_recommendations": ["Continue current exercise", "Maintain balanced diet"]
}
```

---

### 5. Get Health Metrics
**Endpoint:** `GET /api/patients/<int:patient_id>/health-metrics/`

**Headers:** `Authorization: Bearer <token>`

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
  "heart_rate": 72
}
```

---

### 6. Update Health Metrics
**Endpoint:** `POST /api/patients/health-update/`

**Headers:** 
```
Authorization: Bearer <patient_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "weight": 76.0,
  "activity": "Very Active",
  "stress": "Moderate",
  "sleep_hours": 7.5,
  "blood_pressure": "120/80"
}
```

**Response (200):**
```json
{
  "message": "Health metrics updated successfully",
  "updated_fields": ["weight", "activity"]
}
```

---

## 👨‍⚕️ DOCTOR PROFILE ENDPOINTS (4)

### 1. List All Doctors
**Endpoint:** `GET /api/doctors/`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:** `?page=1&department=1&search=cardiology`

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "user": {"id": 2, "name": "Dr. Sahir Khan", "email": "drsahir@example.com"},
      "department": {"id": 1, "name": "Cardiology"},
      "specialization": "Interventional Cardiology",
      "experience_years": 10,
      "consultation_fee": 500,
      "qualification": "MBBS, MD Cardiology",
      "average_rating": 4.8,
      "is_verified": true
    }
  ]
}
```

---

### 2. Get Doctor Details
**Endpoint:** `GET /api/doctors/<int:pk>/`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "user": {"id": 2, "name": "Dr. Sahir Khan"},
  "department": "Cardiology",
  "specialization": "Interventional Cardiology",
  "experience_years": 10,
  "consultation_fee": 500,
  "average_rating": 4.8,
  "availability_status": "Available"
}
```

---

### 3. Doctor Dashboard
**Endpoint:** `GET /api/doctor/dashboard/`

**Headers:** `Authorization: Bearer <doctor_token>`

**Response (200):**
```json
{
  "total_appointments": 150,
  "appointments_today": 5,
  "appointments_pending": 2,
  "total_patients": 45,
  "average_rating": 4.8,
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

### 4. Get Completed Patients
**Endpoint:** `GET /api/doctor/completed-patients/`

**Headers:** `Authorization: Bearer <doctor_token>`

**Response (200):**
```json
{
  "count": 45,
  "patients": [
    {
      "patient_id": 1,
      "patient_name": "John Doe",
      "email": "john@example.com",
      "last_appointment": "2024-03-23T10:00:00Z",
      "total_appointments": 5
    }
  ]
}
```

---

## 📅 APPOINTMENT & SLOT ENDPOINTS (4)

### 1. List Appointments
**Endpoint:** `GET /api/appointments/`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:** `?doctor_id=1&status=confirmed&date=2024-03-24`

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "patient": {"id": 1, "name": "John Doe"},
      "doctor": {"id": 1, "name": "Dr. Sahir Khan"},
      "appointment_slot": "2024-03-24T10:00:00Z",
      "status": "confirmed",
      "reason_for_visit": "Regular checkup",
      "appointment_type": "in-person"
    }
  ]
}
```

---

### 2. Get Appointment Details
**Endpoint:** `GET /api/appointments/<int:pk>/`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "patient": {"id": 1, "name": "John Doe"},
  "doctor": {"id": 1, "name": "Dr. Sahir Khan"},
  "appointment_slot": "2024-03-24T10:00:00Z",
  "status": "confirmed",
  "reason_for_visit": "Regular checkup"
}
```

---

### 3. Book Appointment
**Endpoint:** `POST /api/appointments/`

**Headers:** `Authorization: Bearer <patient_token>`

**Request Body:**
```json
{
  "doctor_id": 1,
  "slot_id": 5,
  "reason_for_visit": "Regular checkup",
  "appointment_type": "in-person"
}
```

**Response (201):**
```json
{
  "message": "Appointment booked successfully",
  "appointment": {
    "id": 1,
    "doctor": "Dr. Sahir Khan",
    "appointment_slot": "2024-03-24T10:00:00Z",
    "status": "confirmed"
  }
}
```

---

### 4. List Available Slots
**Endpoint:** `GET /api/slots/`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:** `?doctor_id=1&date=2024-03-24`

**Response (200):**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "doctor": {"id": 1, "name": "Dr. Sahir Khan"},
      "start_time": "2024-03-24T09:00:00Z",
      "end_time": "2024-03-24T09:30:00Z",
      "status": "available",
      "booked_count": 0
    }
  ]
}
```

---

## 💬 MESSAGE & CHAT ENDPOINTS (5)

### 1. Get Messages for Appointment
**Endpoint:** `GET /api/api/appointments/<int:appointment_id>/messages/`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "appointment": 1,
      "sender": {"id": 1, "name": "John Doe", "role": "patient"},
      "message": "Hi Doctor, I have headaches",
      "created_at": "2024-03-24T09:00:00Z"
    }
  ]
}
```

---

### 2. Send Message in Chat
**Endpoint:** `POST /api/chat/<int:appointment_id>/`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "message": "Hi Doctor, I have headaches",
  "message_type": "text"
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
    "message": "Hi Doctor, I have headaches",
    "created_at": "2024-03-24T10:30:00Z"
  }
}
```

---

### 3. Get Chat History
**Endpoint:** `GET /api/chat2/<int:appointment_id>/`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "appointment_id": 1,
  "patient": "John Doe",
  "doctor": "Dr. Sahir Khan",
  "message_count": 15,
  "messages": [...]
}
```

---

### 4. Delete Message
**Endpoint:** `DELETE /api/messages/<int:message_id>/`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Message deleted successfully"
}
```

---

### 5. Video Call
**Endpoint:** `GET /api/video_call/`

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "room_id": "appointment_123_456",
  "video_url": "http://localhost:8001/video-room/",
  "status": "ready"
}
```

---

## 📄 REPORT ENDPOINTS (2)

### 1. List Reports
**Endpoint:** `GET /api/reports/`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:** `?doctor_id=1&report_type=lab`

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "appointment": {"id": 1, "patient": "John Doe", "doctor": "Dr. Sahir Khan"},
      "report_type": "lab",
      "title": "Blood Test Report",
      "report_date": "2024-03-23",
      "created_at": "2024-03-23T10:00:00Z"
    }
  ]
}
```

---

### 2. Report Detail/Create/Update/Delete
**Endpoints:**
- `GET /api/reports/<int:report_id>/` - Get report
- `POST /api/reports/` - Create report (doctor)
- `PUT /api/reports/<int:report_id>/` - Update report (doctor)
- `DELETE /api/reports/<int:report_id>/` - Delete report

**POST/PUT Headers:** `Authorization: Bearer <doctor_token>`

**Request Body (multipart/form-data):**
```
appointment_id=1
report_type=lab
title=Blood Test Report
report_file=<file>
```

**Response (201/200):**
```json
{
  "message": "Report created/updated successfully",
  "report": {
    "id": 1,
    "title": "Blood Test Report",
    "report_file_url": "http://localhost:8001/media/reports/..."
  }
}
```

---

## 🔐 SUPER ADMIN ENDPOINTS (9)

### Admin Dashboard
**Endpoint:** `GET /api/admin/dashboard/`

**Headers:** `Authorization: Bearer <admin_token>`

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
  "platform_health": "Good"
}
```

---

### Admin User Management (CRUD)
**Endpoints:**
- `GET /api/admin/users/` - List all users
- `GET /api/admin/users/<int:user_id>/` - Get user details
- `PUT /api/admin/users/<int:user_id>/` - Update user
- `DELETE /api/admin/users/<int:user_id>/` - Delete user

**Headers:** `Authorization: Bearer <admin_token>`

---

### Admin Doctor Management (CRUD)
**Endpoints:**
- `GET /api/admin/doctors/` - List all doctors
- `GET /api/admin/doctors/<int:doctor_id>/` - Get doctor details
- `PUT /api/admin/doctors/<int:doctor_id>/` - Update doctor
- `DELETE /api/admin/doctors/<int:doctor_id>/` - Delete doctor

---

### Admin Patient Management (CRUD)
**Endpoints:**
- `GET /api/admin/patients/` - List all patients
- `GET /api/admin/patients/<int:patient_id>/` - Get patient details
- `PUT /api/admin/patients/<int:patient_id>/` - Update patient
- `DELETE /api/admin/patients/<int:patient_id>/` - Delete patient

---

### Admin Appointment Management (CRUD)
**Endpoints:**
- `GET /api/admin/appointments/` - List all appointments
- `GET /api/admin/appointments/<int:appointment_id>/` - Get appointment details
- `PUT /api/admin/appointments/<int:appointment_id>/` - Update appointment
- `DELETE /api/admin/appointments/<int:appointment_id>/` - Delete appointment

---

## 🏠 HOME ENDPOINT (1)

### API Root
**Endpoint:** `GET /api/index/`

**Response (200):**
```json
{
  "message": "Welcome to MedoAir API v1.0",
  "status": "Active",
  "endpoints": {
    "auth": "/api/user/signup/",
    "patients": "/api/patients/",
    "doctors": "/api/doctors/",
    "appointments": "/api/appointments/",
    "chat": "/api/chat/",
    "reports": "/api/reports/",
    "admin": "/api/admin/dashboard/"
  }
}
```

---

## 📋 HTTP STATUS CODES

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Delete successful |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error |

---

## 🔑 JWT AUTHENTICATION

### Getting Tokens
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using in Requests
```
Authorization: Bearer <your_access_token>
```

---

## 👥 ROLE-BASED ACCESS

| Role | Access |
|------|--------|
| Patient | Own profile, appointments, chat, health metrics |
| Doctor | Doctor profile, slots, patients, dashboard, reports |
| Admin | All endpoints |

---

## 📝 VALIDATION RULES

- **Email:** Valid format, unique
- **Password:** Min 6 chars, at least 1 number
- **Name:** Min 3 characters
- **Age:** 18-120 years
- **Height:** 100-250 cm
- **Weight:** 20-300 kg

---

## 🚀 ENVIRONMENT SETUP

```bash
# Start server
python manage.py runserver 8001

# Migrate database
python manage.py migrate

# Create admin
python manage.py createsuperuser

# Access admin
http://localhost:8001/admin/
```

---

**API Version:** 1.0  
**Base URL:** http://localhost:8001/api/  
**Last Updated:** April 2026  
**Status:** ✅ Production Ready

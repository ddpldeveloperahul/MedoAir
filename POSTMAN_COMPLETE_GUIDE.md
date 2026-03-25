# 📮 Postman Complete Testing Guide

## Setup

### 1. Create a New Collection
- Open Postman
- Click **+ New Collection** → Name it "MedoAir API"
- Create folders: Auth, Users, Patients, Doctors, Appointments, Messages, Reports

### 2. Set Environment Variables
- Click **Environments** → **+ New**
- Name: "MedoAir Dev"
- Add variables:
  ```
  base_url: http://localhost:8000
  access_token: (leave empty, will be filled after login)
  refresh_token: (leave empty)
  admin_access_token: (for admin testing)
  ```

### 3. Make Requests
- In request header, add `Authorization: Bearer {{access_token}}`
- Use `{{base_url}}` in URL
- Save requests to collection

---

## 🔐 AUTHENTICATION ENDPOINTS

### 1. User Signup
```
Method: POST
URL: {{base_url}}/user/signup/
Headers: Content-Type: application/json

REQUEST:
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123"
}

RESPONSE (201 Created):
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

### 2. Doctor Signup
```
Method: POST
URL: {{base_url}}/doctor/signup/
Headers: Content-Type: application/json

REQUEST:
{
  "name": "Dr. Smith",
  "email": "doctor@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "department": 1,
  "experience": 5,
  "bio": "Experienced cardiologist"
}

RESPONSE (201 Created):
{
  "status": "success",
  "message": "Doctor registered successfully",
  "data": {
    "id": 2,
    "name": "Dr. Smith",
    "email": "doctor@example.com",
    "role": "doctor",
    "experience": 5,
    "bio": "Experienced cardiologist"
  }
}
```

### 3. Login (Common for both)
```
Method: POST
URL: {{base_url}}/login/
Headers: Content-Type: application/json

REQUEST:
{
  "email": "john@example.com",
  "password": "password123"
}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user"
    }
  }
}
```

**IMPORTANT**: Copy the `access` token and set it in your Postman environment:
- Click environment icon → Edit → Set `access_token` variable to the token

### 4. Forgot Password
```
Method: POST
URL: {{base_url}}/forgot-password/
Headers: Content-Type: application/json

REQUEST:
{
  "email": "john@example.com"
}

RESPONSE (200 OK):
{
  "status": "success",
  "message": "OTP sent to your email"
}
```

### 5. Verify OTP
```
Method: POST
URL: {{base_url}}/verify-otp/
Headers: Content-Type: application/json

REQUEST:
{
  "email": "john@example.com",
  "otp": "123456"
}

RESPONSE (200 OK):
{
  "status": "success",
  "message": "OTP verified",
  "data": {
    "temp_token": "temporary_token_for_reset"
  }
}
```

### 6. Reset Password
```
Method: POST
URL: {{base_url}}/reset-password/
Headers: Content-Type: application/json

REQUEST:
{
  "email": "john@example.com",
  "temp_token": "temporary_token_from_verify_otp",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}

RESPONSE (200 OK):
{
  "status": "success",
  "message": "Password reset successfully"
}
```

### 7. Resend OTP
```
Method: POST
URL: {{base_url}}/resend-otp/
Headers: Content-Type: application/json

REQUEST:
{
  "email": "john@example.com"
}

RESPONSE (200 OK):
{
  "status": "success",
  "message": "OTP resent to your email"
}
```

---

## 👥 USER MANAGEMENT ENDPOINTS

### 1. List All Users
```
Method: GET
URL: {{base_url}}/api/users/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "created_at": "2026-03-23T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Dr. Smith",
      "email": "doctor@example.com",
      "role": "doctor",
      "created_at": "2026-03-23T10:05:00Z"
    }
  ]
}
```

### 2. Get User Detail
```
Method: GET
URL: {{base_url}}/api/users/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "phone": "+1234567890",
    "created_at": "2026-03-23T10:00:00Z"
  }
}
```

### 3. Get Current User (Me)
```
Method: GET
URL: {{base_url}}/api/users/me/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "phone": "+1234567890",
    "created_at": "2026-03-23T10:00:00Z"
  }
}
```

### 4. Update User (PUT - Full Update)
```
Method: PUT
URL: {{base_url}}/api/users/1/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "name": "John Updated",
  "email": "john.updated@example.com",
  "phone": "+9876543210"
}

RESPONSE (200 OK):
{
  "status": "success",
  "message": "User updated successfully",
  "data": {
    "id": 1,
    "name": "John Updated",
    "email": "john.updated@example.com",
    "phone": "+9876543210"
  }
}
```

### 5. Partial Update (PATCH)
```
Method: PATCH
URL: {{base_url}}/api/users/1/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "name": "John New Name"
}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "John New Name",
    "email": "john.updated@example.com",
    "phone": "+9876543210"
  }
}
```

### 6. Change Password
```
Method: POST
URL: {{base_url}}/api/users/change-password/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "old_password": "password123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}

RESPONSE (200 OK):
{
  "status": "success",
  "message": "Password changed successfully"
}
```

### 7. Delete User
```
Method: DELETE
URL: {{base_url}}/api/users/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (204 No Content):
(Empty response)
```

### 8. Get User Profile Stats
```
Method: GET
URL: {{base_url}}/api/users/profile-stats/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "total_appointments": 5,
    "total_doctors": 3,
    "total_reports": 2,
    "pending_appointments": 1
  }
}
```

---

## 🏥 PATIENT ENDPOINTS

### 1. List All Patients
```
Method: GET
URL: {{base_url}}/api/patients/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      },
      "blood_type": "O+",
      "height": 180,
      "weight": 75,
      "allergies": "Penicillin"
    }
  ]
}
```

### 2. Get Patient Detail
```
Method: GET
URL: {{base_url}}/api/patients/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    "blood_type": "O+",
    "height": 180,
    "weight": 75,
    "allergies": "Penicillin",
    "medical_history": "Diabetes",
    "insurance_provider": "Aetna",
    "insurance_number": "123456789",
    "emergency_contact": "Jane Doe",
    "emergency_phone": "+0987654321"
  }
}
```

### 3. Get Current Patient (Me)
```
Method: GET
URL: {{base_url}}/api/patients/me/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "user": {...}
    "blood_type": "O+",
    ...
  }
}
```

### 4. Create Patient Profile
```
Method: POST
URL: {{base_url}}/api/patients/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "blood_type": "A+",
  "height": 175,
  "weight": 70,
  "allergies": "None",
  "medical_history": "Asthma",
  "insurance_provider": "BlueCross",
  "insurance_number": "987654321",
  "emergency_contact": "Jane Smith",
  "emergency_phone": "+1111111111"
}

RESPONSE (201 Created):
{
  "status": "success",
  "message": "Patient profile created",
  "data": {
    "id": 2,
    "user": {
      "id": 1,
      "name": "John Doe"
    },
    "blood_type": "A+",
    "height": 175,
    "weight": 70,
    ...
  }
}
```

### 5. Update Patient Profile (PUT)
```
Method: PUT
URL: {{base_url}}/api/patients/1/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "blood_type": "AB+",
  "height": 180,
  "weight": 72,
  "allergies": "Nuts"
}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {...}
}
```

### 6. Partial Patient Update (PATCH)
```
Method: PATCH
URL: {{base_url}}/api/patients/1/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "weight": 73
}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {...}
}
```

### 7. Get Health Summary
```
Method: GET
URL: {{base_url}}/api/patients/health-summary/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "bmi": 23.1,
    "bmi_status": "Normal",
    "blood_type": "O+",
    "allergies": "Penicillin",
    "medical_conditions": "Diabetes",
    "last_checkup": "2026-03-15T10:00:00Z"
  }
}
```

### 8. Get Health Metrics
```
Method: GET
URL: {{base_url}}/api/patients/1/health-metrics/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "height": 180,
    "weight": 75,
    "bmi": 23.1,
    "blood_type": "O+",
    "pulse_rate": 72,
    "blood_pressure": "120/80",
    "temperature": 98.6
  }
}
```

### 9. Update Health Metrics
```
Method: POST
URL: {{base_url}}/api/patients/health-update/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "height": 181,
  "weight": 76,
  "pulse_rate": 75,
  "blood_pressure": "118/78",
  "temperature": 98.4
}

RESPONSE (200 OK):
{
  "status": "success",
  "message": "Health metrics updated",
  "data": {...}
}
```

### 10. Delete Patient
```
Method: DELETE
URL: {{base_url}}/api/patients/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (204 No Content):
(Empty response)
```

---

## 👨‍⚕️ DOCTOR ENDPOINTS

### 1. Get All Doctors
```
Method: GET
URL: {{base_url}}/api/doctors/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "name": "Dr. Smith",
        "email": "doctor@example.com"
      },
      "specialization": "Cardiology",
      "experience": 5,
      "bio": "Experienced cardiologist",
      "is_online": true
    }
  ]
}
```

### 2. Get Doctor Detail
```
Method: GET
URL: {{base_url}}/api/doctors/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "user": {
      "id": 2,
      "name": "Dr. Smith",
      "email": "doctor@example.com",
      "phone": "+1234567890"
    },
    "department": {
      "id": 1,
      "name": "Cardiology"
    },
    "specialization": "Cardiology",
    "experience": 5,
    "bio": "Experienced cardiologist",
    "is_online": true,
    "rating": 4.8,
    "consultation_fee": 500
  }
}
```

### 3. Get Current Doctor (Me)
```
Method: GET
URL: {{base_url}}/api/doctors/me/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {...}
}
```

### 4. Update Doctor Profile
```
Method: PUT
URL: {{base_url}}/api/doctors/1/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "specialization": "Interventional Cardiology",
  "experience": 6,
  "bio": "Senior Interventional Cardiologist",
  "is_online": true
}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {...}
}
```

### 5. Get Departments
```
Method: GET
URL: {{base_url}}/api/departments/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Cardiology",
      "description": "Heart and cardiovascular care"
    },
    {
      "id": 2,
      "name": "Neurology",
      "description": "Brain and nervous system"
    }
  ]
}
```

---

## 📅 APPOINTMENT ENDPOINTS

### 1. List Appointments
```
Method: GET
URL: {{base_url}}/api/appointments/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "patient": {
        "id": 1,
        "user": {"name": "John Doe"}
      },
      "doctor": {
        "id": 1,
        "user": {"name": "Dr. Smith"}
      },
      "appointment_date": "2026-03-25T14:00:00Z",
      "reason": "Regular checkup",
      "status": "scheduled",
      "notes": "Patient has diabetes history"
    }
  ]
}
```

### 2. Get Appointment Detail
```
Method: GET
URL: {{base_url}}/api/appointments/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "patient": {...},
    "doctor": {...},
    "appointment_date": "2026-03-25T14:00:00Z",
    "reason": "Regular checkup",
    "status": "scheduled",
    "notes": "Patient has diabetes history",
    "created_at": "2026-03-23T10:00:00Z"
  }
}
```

### 3. Create Appointment
```
Method: POST
URL: {{base_url}}/api/appointments/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "patient_id": 1,
  "doctor_id": 1,
  "appointment_date": "2026-03-25T14:00:00Z",
  "reason": "Regular checkup",
  "notes": "Patient has diabetes history"
}

RESPONSE (201 Created):
{
  "status": "success",
  "message": "Appointment created",
  "data": {
    "id": 2,
    "patient": {...},
    ...
  }
}
```

### 4. Update Appointment
```
Method: PUT
URL: {{base_url}}/api/appointments/1/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "appointment_date": "2026-03-26T10:00:00Z",
  "reason": "Follow-up checkup",
  "status": "completed"
}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {...}
}
```

### 5. Cancel Appointment
```
Method: PATCH
URL: {{base_url}}/api/appointments/1/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "status": "cancelled"
}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {...}
}
```

### 6. Delete Appointment
```
Method: DELETE
URL: {{base_url}}/api/appointments/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (204 No Content):
(Empty response)
```

---

## 💬 MESSAGE/CHAT ENDPOINTS

### 1. Get Messages for Appointment
```
Method: GET
URL: {{base_url}}/api/appointments/1/messages/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "appointment": 1,
      "sender": {
        "id": 1,
        "name": "John Doe"
      },
      "content": "Hi Doctor, I have a question about my medication",
      "created_at": "2026-03-23T10:30:00Z"
    },
    {
      "id": 2,
      "appointment": 1,
      "sender": {
        "id": 2,
        "name": "Dr. Smith"
      },
      "content": "Sure, what's your question?",
      "created_at": "2026-03-23T10:35:00Z"
    }
  ]
}
```

### 2. Send Message
```
Method: POST
URL: {{base_url}}/api/appointments/1/messages/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: application/json

REQUEST:
{
  "content": "Hi Doctor, I wanted to follow up on my last visit"
}

RESPONSE (201 Created):
{
  "status": "success",
  "message": "Message sent",
  "data": {
    "id": 3,
    "appointment": 1,
    "sender": {
      "id": 1,
      "name": "John Doe"
    },
    "content": "Hi Doctor, I wanted to follow up on my last visit",
    "created_at": "2026-03-23T11:00:00Z"
  }
}
```

---

## 📋 REPORT ENDPOINTS

### 1. List Reports
```
Method: GET
URL: {{base_url}}/api/reports/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "patient": {
        "id": 1,
        "user": {"name": "John Doe"}
      },
      "doctor": {
        "id": 1,
        "user": {"name": "Dr. Smith"}
      },
      "title": "Blood Test Report",
      "report_type": "Lab",
      "uploaded_at": "2026-03-23T09:00:00Z"
    }
  ]
}
```

### 2. Get Report Detail
```
Method: GET
URL: {{base_url}}/api/reports/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (200 OK):
{
  "status": "success",
  "data": {
    "id": 1,
    "patient": {...},
    "doctor": {...},
    "title": "Blood Test Report",
    "report_type": "Lab",
    "description": "Blood work results",
    "file_url": "http://localhost:8000/media/reports/blood_test.pdf",
    "uploaded_at": "2026-03-23T09:00:00Z"
  }
}
```

### 3. Upload Report
```
Method: POST
URL: {{base_url}}/api/reports/
Headers: 
  - Authorization: Bearer {{access_token}}
  - Content-Type: multipart/form-data

REQUEST (Form Data):
- patient_id: 1
- doctor_id: 1
- title: "X-Ray Report"
- report_type: "Imaging"
- description: "Chest X-Ray results"
- file: [select file]

RESPONSE (201 Created):
{
  "status": "success",
  "message": "Report uploaded",
  "data": {
    "id": 2,
    "patient": {...},
    "doctor": {...},
    "title": "X-Ray Report",
    "file_url": "http://localhost:8000/media/reports/xray.pdf",
    "uploaded_at": "2026-03-23T11:00:00Z"
  }
}
```

### 4. Delete Report
```
Method: DELETE
URL: {{base_url}}/api/reports/1/
Headers: Authorization: Bearer {{access_token}}

RESPONSE (204 No Content):
(Empty response)
```

---

## 🧪 TESTING WORKFLOW

### Step 1: Setup Environment
1. Create new Postman environment: "MedoAir Dev"
2. Set `base_url = http://localhost:8000`

### Step 2: Test Authentication
1. **User Signup** - Create test user
2. **Login** - Get access token, copy to environment variable
3. **Get Me** - Verify token works

### Step 3: Test Patient Flow
1. **Create Patient Profile** - POST /api/patients/
2. **Get Patient** - GET /api/patients/me/
3. **Update Health Metrics** - POST /api/patients/health-update/
4. **Get Health Summary** - GET /api/patients/health-summary/

### Step 4: Test Doctor Flow
1. **List Doctors** - GET /api/doctors/
2. **Get Doctor** - GET /api/doctors/1/
3. **Get Departments** - GET /api/departments/

### Step 5: Test Appointments
1. **Create Appointment** - POST /api/appointments/
2. **Get Appointment** - GET /api/appointments/1/
3. **Send Message** - POST /api/appointments/1/messages/
4. **Get Messages** - GET /api/appointments/1/messages/

### Step 6: Test Reports
1. **Upload Report** - POST /api/reports/ (with file)
2. **Get Report** - GET /api/reports/1/
3. **List Reports** - GET /api/reports/

### Step 7: Test User Management
1. **List Users** - GET /api/users/
2. **Update User** - PUT /api/users/me/
3. **Change Password** - POST /api/users/change-password/

---

## ✅ Common Test Cases

### Test Case 1: Full Patient Registration
```
1. POST /user/signup/ → Create patient account
2. POST /api/patients/ → Create patient profile
3. POST /api/patients/health-update/ → Add health metrics
4. GET /api/patients/health-summary/ → Verify health data
```

### Test Case 2: Doctor Registration
```
1. POST /doctor/signup/ → Register doctor
2. GET /api/doctors/me/ → Verify profile
3. PUT /api/doctors/1/ → Update info
4. GET /api/departments/ → View departments
```

### Test Case 3: Full Appointment Flow
```
1. POST /api/appointments/ → Book appointment
2. POST /api/appointments/1/messages/ → Send message
3. GET /api/appointments/1/messages/ → View chat
4. PATCH /api/appointments/1/ → Mark completed
```

### Test Case 4: Password Reset
```
1. POST /forgot-password/ → Request OTP
2. POST /verify-otp/ → Verify OTP
3. POST /reset-password/ → Reset password
```

---

## 🔑 Authentication Notes

**Token Types:**
- `access_token`: Short-lived (10 days), use for API calls
- `refresh_token`: Long-lived, use to get new access token

**Using Token in Postman:**
```
Headers:
Authorization: Bearer eyJ0eXAi...
```

Or set environment variable:
```
Authorization: Bearer {{access_token}}
```

**Token Refresh (if expired):**
```
Method: POST
URL: {{base_url}}/token/refresh/
Body: {"refresh": "{{refresh_token}}"}
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Invalid input",
  "errors": {
    "email": ["Email already registered"]
  }
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Authentication required",
  "detail": "Invalid token or token expired"
}
```

### 403 Forbidden
```json
{
  "status": "error",
  "message": "Permission denied",
  "detail": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Resource not found"
}
```

### 500 Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

---

## 📝 Quick Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| /user/signup/ | POST | ❌ | Create user account |
| /doctor/signup/ | POST | ❌ | Register doctor |
| /login/ | POST | ❌ | Login user |
| /api/users/ | GET | ✅ | List users |
| /api/users/me/ | GET | ✅ | Get current user |
| /api/patients/ | GET/POST | ✅ | Patient management |
| /api/doctors/ | GET | ✅ | List doctors |
| /api/appointments/ | GET/POST | ✅ | Manage appointments |
| /api/appointments/1/messages/ | GET/POST | ✅ | Chat messages |
| /api/reports/ | GET/POST | ✅ | Medical reports |
| /api/patients/health-summary/ | GET | ✅ | Health overview |

---

**Happy Testing! 🎉**

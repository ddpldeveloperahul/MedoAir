# MedoAir Complete CRUD API Documentation

## Base URL
```
http://localhost:8000/
```

---

## 🔐 AUTHENTICATION ENDPOINTS

### 1. User Signup
**Endpoint:** `POST /accounts/user/signup/`

**Description:** Register a new user

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
**Endpoint:** `POST /accounts/doctor/signup/`

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
**Endpoint:** `POST /accounts/login/`

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
**Endpoint:** `POST /accounts/forgot-password/`

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

### 5. Verify OTP
**Endpoint:** `POST /accounts/verify-otp/`

**Description:** Verify OTP for password reset

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "msg": "OTP verified successfully",
  "email": "john@example.com"
}
```

---

### 6. Reset Password
**Endpoint:** `POST /accounts/reset-password/`

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

### 7. Resend OTP
**Endpoint:** `POST /accounts/resend-otp/`

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
**Endpoint:** `GET /accounts/api/users/`

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

### 2. Create New User (CRUD)
**Endpoint:** `POST /accounts/api/users/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 6,
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": null,
    "address": null,
    "profile_image_url": null,
    "date_of_birth": null,
    "gender": null,
    "role": "user",
    "is_verified": false,
    "date_joined": "2024-03-23T10:00:00Z"
  }
}
```

---

### 3. Get User Details
**Endpoint:** `GET /accounts/api/users/{id}/`

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

### 4. Update User Profile
**Endpoint:** `PUT /accounts/api/users/{id}/` or `PATCH /accounts/api/users/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
first_name=John
last_name=Doe
phone=9876543210
address=456 Elm St
date_of_birth=1990-01-15
gender=Male
profile_image=<image_file>
```

**Response (200):**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "9876543210",
    "address": "456 Elm St",
    "profile_image_url": "http://localhost:8000/media/profiles/john_updated.jpg",
    "date_of_birth": "1990-01-15",
    "gender": "Male",
    "role": "user",
    "is_verified": true,
    "date_joined": "2024-03-20T10:00:00Z"
  }
}
```

---

### 5. Delete User
**Endpoint:** `DELETE /accounts/api/users/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "User john@example.com deleted successfully"
}
```

---

### 6. Get Current User Profile
**Endpoint:** `GET /accounts/api/users/me/`

**Headers:**
```
Authorization: Bearer <access_token>
```

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
**Endpoint:** `GET /patients/api/profiles/`

**Headers:**
```
Authorization: Bearer <access_token>
```

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
      "diet": "Mixes",
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

### 2. Create Patient Profile
**Endpoint:** `POST /patients/api/profiles/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "age": 34,
  "height": 180.0,
  "weight": 75.5,
  "blood_group": "O+",
  "activity": "Moderately Active",
  "diet": "Mixes",
  "stress": "Low",
  "sleep_hours": 8,
  "medical_history": "No major illnesses",
  "allergies": "Peanuts",
  "current_medications": "None",
  "family_history": "Diabetes in family",
  "emergency_contact": "Jane Doe",
  "emergency_contact_phone": "9876543210",
  "insurance_provider": "Blue Cross",
  "insurance_number": "BC123456"
}
```

**Response (201):**
```json
{
  "message": "Patient profile created successfully",
  "profile": {
    "id": 1,
    "user": {...},
    "age": 34,
    "height": 180.0,
    "weight": 75.5,
    "blood_group": "O+",
    "activity": "Moderately Active",
    "diet": "Mixes",
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
    "created_at": "2024-03-23T10:00:00Z",
    "updated_at": "2024-03-23T10:00:00Z"
  }
}
```

---

### 3. Get Patient Profile Details
**Endpoint:** `GET /patients/api/profiles/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Patient profile retrieved successfully",
  "profile": {...}
}
```

---

### 4. Update Patient Profile
**Endpoint:** `PUT /patients/api/profiles/{id}/` or `PATCH /patients/api/profiles/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "weight": 78.0,
  "activity": "Very Active",
  "stress": "Moderate"
}
```

**Response (200):**
```json
{
  "message": "Patient profile updated successfully",
  "profile": {...}
}
```

---

### 5. Delete Patient Profile
**Endpoint:** `DELETE /patients/api/profiles/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Patient profile for john@example.com deleted successfully"
}
```

---

### 6. Get My Patient Profile
**Endpoint:** `GET /patients/api/profiles/my_profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Your patient profile",
  "profile": {...}
}
```

---

### 7. Get Health Summary
**Endpoint:** `GET /patients/api/profiles/health_summary/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Your health summary",
  "summary": {
    "id": 1,
    "user_email": "john@example.com",
    "user_name": "John Doe",
    "profile_image_url": "http://localhost:8000/media/profiles/john.jpg",
    "age": 34,
    "height": 180.0,
    "weight": 75.5,
    "blood_group": "O+",
    "bmi": 23.3,
    "activity": "Moderately Active",
    "diet": "Mixes",
    "stress": "Low",
    "updated_at": "2024-03-23T10:00:00Z"
  }
}
```

---

### 8. Get Health Metrics
**Endpoint:** `GET /patients/api/profiles/{id}/health_metrics/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Health metrics",
  "metrics": {
    "height_cm": 180.0,
    "weight_kg": 75.5,
    "bmi": 23.3,
    "bmi_category": "Normal",
    "blood_group": "O+",
    "activity_level": "Moderately Active",
    "sleep_hours": 8,
    "stress_level": "Low"
  }
}
```

---

### 9. Bulk Health Update
**Endpoint:** `POST /patients/api/profiles/bulk_health_update/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "weight": 76.0,
  "sleep_hours": 7,
  "stress": "High"
}
```

**Response (200):**
```json
{
  "message": "Health metrics updated successfully",
  "profile": {...}
}
```

---

## 📋 API RESPONSE CODES

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

## 🖼️ UPLOADING PROFILE IMAGES

### Upload Profile Image
**Supporting Image Types:** JPG, PNG, GIF

**Max File Size:** 5MB (recommended)

**Example using cURL:**
```bash
curl -X PATCH http://localhost:8000/accounts/api/users/1/ \
  -H "Authorization: Bearer <access_token>" \
  -F "profile_image=@/path/to/photo.jpg" \
  -F "first_name=John"
```

**Image URL in Response:**
```json
{
  "profile_image_url": "http://localhost:8000/media/profiles/john_123abc.jpg"
}
```

---

## 📊 DATA VALIDATION

### User Fields
- **Email:** Must be unique and valid format
- **Password:** Minimum 6 characters, must contain at least 1 number
- **Name:** Minimum 3 characters
- **Phone:** Optional, max 20 characters
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

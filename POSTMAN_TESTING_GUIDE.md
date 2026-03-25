# MedoAir API - Postman Testing Guide

Complete guide for testing all MedoAir API endpoints with every possible condition using Postman.

## Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Management Endpoints](#user-management-endpoints)
4. [Patient Profile Endpoints](#patient-profile-endpoints)
5. [Test Scenarios Summary](#test-scenarios-summary)
6. [Common Error Responses](#common-error-responses)

---

## Setup Instructions

### 1. Import Environment Variables in Postman

Create a Postman environment with these variables:

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "(auto-populated after login)",
  "refresh_token": "(auto-populated after login)",
  "user_id": "1",
  "patient_id": "1"
}
```

### 2. Create Pre-request Script for Token Management

Add this to the collection or specific requests:

```javascript
// Update tokens after login
if (pm.response.code === 200 || pm.response.code === 201) {
    if (pm.response.json().access) {
        pm.environment.set("access_token", pm.response.json().access);
        pm.environment.set("refresh_token", pm.response.json().refresh);
    }
}
```

### 3. Set Default Authorization Header

For all authenticated endpoints, add Authorization header:
```
Authorization: Bearer {{access_token}}
```

---

## Authentication Endpoints

### 1. User Signup

**Endpoint:** `POST /accounts/user/signup/`

#### Test Case 1.1: Success Case ✅
**Request:**
```json
{
  "email": "testuser@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Expected Response:** 
- Status: `201 Created`
- Response:
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John",
    "email": "testuser@example.com",
    "role": "patient"
  }
}
```

#### Test Case 1.2: Missing Required Field ❌
**Request:** (missing `password`)
```json
{
  "email": "testuser@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "message": "Registration failed",
  "errors": {
    "password": ["This field is required."]
  }
}
```

#### Test Case 1.3: Duplicate Email ❌
**Request:**
```json
{
  "email": "existing@example.com",
  "password": "securePassword123",
  "first_name": "Jane",
  "last_name": "Smith"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "message": "Registration failed",
  "errors": {
    "email": ["User with this email already exists."]
  }
}
```

#### Test Case 1.4: Invalid Email Format ❌
**Request:**
```json
{
  "email": "notanemail",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "message": "Registration failed",
  "errors": {
    "email": ["Enter a valid email address."]
  }
}
```

#### Test Case 1.5: Password Too Short ❌
**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "123",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "message": "Registration failed",
  "errors": {
    "password": ["Ensure this field has at least 6 characters."]
  }
}
```

#### Test Case 1.6: Empty Body ❌
**Request:** (empty JSON `{}`)
**Expected Response:**
- Status: `400 Bad Request`
- Response shows missing required fields

#### Test Case 1.7: Special Characters in Email ❌
**Request:**
```json
{
  "email": "user@!@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Expected Response:**
- Status: `400 Bad Request`

---

### 2. Doctor Signup

**Endpoint:** `POST /accounts/doctor/signup/`

#### Test Case 2.1: Success Case ✅
**Request:**
```json
{
  "email": "doctor@example.com",
  "password": "docPassword123",
  "first_name": "Dr.",
  "last_name": "Smith",
  "phone": "+1234567890",
  "address": "123 Medical St",
  "specialization": "Cardiology",
  "department_id": 1
}
```
**Expected Response:**
- Status: `201 Created`
- Response:
```json
{
  "message": "Doctor registered successfully",
  "user": {
    "id": 2,
    "name": "Dr.",
    "email": "doctor@example.com",
    "role": "doctor",
    "department": "Cardiology"
  }
}
```

#### Test Case 2.2: Missing Department ID ❌
**Request:** (without `department_id`)
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 2.3: Invalid Department ID ❌
**Request:**
```json
{
  "email": "doctor@example.com",
  "password": "docPassword123",
  "first_name": "Dr.",
  "last_name": "Smith",
  "phone": "+1234567890",
  "address": "123 Medical St",
  "specialization": "Cardiology",
  "department_id": 9999
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 2.4: Duplicate Email ❌
**Request:** (same email as existing doctor)
**Expected Response:**
- Status: `400 Bad Request`

---

### 3. Login

**Endpoint:** `POST /accounts/login/`

#### Test Case 3.1: Successful Login ✅
**Request:**
```json
{
  "email": "testuser@example.com",
  "password": "securePassword123"
}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "patient",
    "is_verified": false,
    "profile_image": null
  }
}
```

#### Test Case 3.2: Missing Email ❌
**Request:**
```json
{
  "password": "securePassword123"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Email and password are required"
}
```

#### Test Case 3.3: Missing Password ❌
**Request:**
```json
{
  "email": "testuser@example.com"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 3.4: Invalid Password ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "password": "wrongPassword"
}
```
**Expected Response:**
- Status: `401 Unauthorized`
- Response:
```json
{
  "error": "Invalid email or password"
}
```

#### Test Case 3.5: Non-existent Email ❌
**Request:**
```json
{
  "email": "nonexistent@example.com",
  "password": "anyPassword123"
}
```
**Expected Response:**
- Status: `401 Unauthorized`

#### Test Case 3.6: Empty Body ❌
**Request:** (empty JSON `{}`)
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 3.7: Case Sensitivity ✅
**Request:**
```json
{
  "email": "TestUser@Example.com",
  "password": "securePassword123"
}
```
**Expected Response:**
- Status: `200 OK` (emails are case-insensitive)

---

### 4. Forgot Password (OTP Generation)

**Endpoint:** `POST /accounts/forgot-password/`

#### Test Case 4.1: Success Case ✅
**Request:**
```json
{
  "email": "testuser@example.com"
}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "OTP sent to your email",
  "email": "testuser@example.com"
}
```

#### Test Case 4.2: Missing Email ❌
**Request:**
```json
{}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "message": "Validation failed",
  "errors": {
    "email": ["This field is required."]
  }
}
```

#### Test Case 4.3: Non-existent Email ❌
**Request:**
```json
{
  "email": "nonexistent@example.com"
}
```
**Expected Response:**
- Status: `500 Internal Server Error` or `404 Not Found`

#### Test Case 4.4: Multiple OTP Requests (Last OTP Valid) ✅
**Request 1:**
```json
{
  "email": "testuser@example.com"
}
```
**Request 2:** (immediately call again)
```json
{
  "email": "testuser@example.com"
}
```
**Expected Response:**
- Status: `200 OK` for both
- Only the latest OTP is valid, previous ones are invalidated

#### Test Case 4.5: Invalid Email Format ❌
**Request:**
```json
{
  "email": "notanemail"
}
```
**Expected Response:**
- Status: `400 Bad Request`

---

### 5. Verify OTP

**Endpoint:** `POST /accounts/verify-otp/`

#### Test Case 5.1: Success Case ✅
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "123456"
}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "OTP verified successfully",
  "email": "testuser@example.com"
}
```

#### Test Case 5.2: Missing Email ❌
**Request:**
```json
{
  "otp": "123456"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Email and OTP are required"
}
```

#### Test Case 5.3: Missing OTP ❌
**Request:**
```json
{
  "email": "testuser@example.com"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 5.4: Invalid OTP ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "000000"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Invalid OTP"
}
```

#### Test Case 5.5: Expired OTP ❌
Wait 15+ minutes after requesting OTP, then:
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "123456"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "OTP has expired"
}
```

#### Test Case 5.6: Wrong Format OTP ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "abc123"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 5.7: Already Used OTP ❌
**Request 1:** (verify with valid OTP)
**Request 2:** (verify with same OTP again)
**Expected Response for Request 2:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Invalid OTP"
}
```

---

### 6. Reset Password

**Endpoint:** `POST /accounts/reset-password/`

#### Test Case 6.1: Success Case ✅
**Prerequisites:** Must have verified OTP first
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "123456",
  "new_password": "newSecurePass123",
  "confirm_password": "newSecurePass123"
}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Password reset successfully"
}
```

#### Test Case 6.2: Password Mismatch ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "123456",
  "new_password": "newSecurePass123",
  "confirm_password": "differentPassword456"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "message": "Validation failed",
  "errors": {
    "non_field_errors": ["Passwords do not match."]
  }
}
```

#### Test Case 6.3: Invalid OTP ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "000000",
  "new_password": "newSecurePass123",
  "confirm_password": "newSecurePass123"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Invalid OTP"
}
```

#### Test Case 6.4: Expired OTP ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "123456",
  "new_password": "newSecurePass123",
  "confirm_password": "newSecurePass123"
}
```
(After 15+ minutes)
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "OTP has expired"
}
```

#### Test Case 6.5: Password Too Short ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "otp": "123456",
  "new_password": "123",
  "confirm_password": "123"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 6.6: Missing Required Fields ❌
**Request:** (missing `new_password`)
```json
{
  "email": "testuser@example.com",
  "otp": "123456",
  "confirm_password": "newSecurePass123"
}
```
**Expected Response:**
- Status: `400 Bad Request`

---

### 7. Resend OTP

**Endpoint:** `POST /accounts/resend-otp/`

#### Test Case 7.1: Success Case ✅
**Request:**
```json
{
  "email": "testuser@example.com"
}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "New OTP sent to your email",
  "email": "testuser@example.com"
}
```

#### Test Case 7.2: Multiple Resend Requests ✅
**Request 1:** (send OTP)
**Request 2:** (resend OTP - old one invalidated)
**Request 3:** (resend OTP again)
**Expected Response:** All return `200 OK`, only latest OTP valid

#### Test Case 7.3: Non-existent Email ❌
**Request:**
```json
{
  "email": "nonexistent@example.com"
}
```
**Expected Response:**
- Status: `500 Internal Server Error`

#### Test Case 7.4: Missing Email ❌
**Request:**
```json
{}
```
**Expected Response:**
- Status: `400 Bad Request`

---

## User Management Endpoints

### 8. Get Current User

**Endpoint:** `GET /accounts/api/users/me/`

#### Test Case 8.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Current user retrieved",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "patient",
    "is_verified": false,
    "profile_image": null,
    "phone": null,
    "address": null,
    "date_of_birth": null,
    "gender": null
  }
}
```

#### Test Case 8.2: No Token ❌
**Headers:** (no Authorization header)
**Expected Response:**
- Status: `401 Unauthorized`
- Response:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### Test Case 8.3: Invalid Token ❌
**Headers:**
```
Authorization: Bearer invalidtoken123
```
**Expected Response:**
- Status: `401 Unauthorized`
- Response:
```json
{
  "detail": "Given token is invalid for any token type"
}
```

#### Test Case 8.4: Expired Token ❌
(Wait for token to expire or use old token)
**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```
**Expected Response:**
- Status: `401 Unauthorized`
- Response:
```json
{
  "detail": "Token is invalid or expired"
}
```

#### Test Case 8.5: Wrong Token Prefix ❌
**Headers:**
```
Authorization: {{access_token}}
```
(Missing "Bearer " prefix)
**Expected Response:**
- Status: `401 Unauthorized`

#### Test Case 8.6: Case Sensitive Bearer ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
(Should work)

#### Test Case 8.7: Extra Whitespace ❌
**Headers:**
```
Authorization: Bearer  {{access_token}}
```
(Extra space)
**Expected Response:**
- Status: `401 Unauthorized`

---

### 9. List All Users

**Endpoint:** `GET /accounts/api/users/`

#### Test Case 9.1: Success Case (Admin) ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Users retrieved successfully",
  "count": 2,
  "results": [
    {
      "id": 1,
      "email": "testuser@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "patient",
      "is_verified": false,
      "profile_image": null,
      "phone": null,
      "address": null,
      "date_of_birth": null,
      "gender": null
    },
    {
      "id": 2,
      "email": "doctor@example.com",
      "first_name": "Dr.",
      "last_name": "Smith",
      "role": "doctor",
      "is_verified": true,
      "profile_image": null,
      "phone": "+1234567890",
      "address": "123 Medical St",
      "date_of_birth": null,
      "gender": "M"
    }
  ]
}
```

#### Test Case 9.2: No Authentication ❌
**Headers:** (no Authorization)
**Expected Response:**
- Status: `401 Unauthorized`

#### Test Case 9.3: Pagination (if implemented) ✅
**Request:**
```
GET /accounts/api/users/?page=1&limit=10
```
**Expected Response:**
- Status: `200 OK`
- Contains paginated results

---

### 10. Create New User (Admin)

**Endpoint:** `POST /accounts/api/users/`

#### Test Case 10.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "passwordUser123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "patient"
}
```
**Expected Response:**
- Status: `201 Created`

#### Test Case 10.2: Missing Required Field ❌
**Request:** (missing `email`)
```json
{
  "password": "passwordUser123",
  "first_name": "Jane",
  "last_name": "Smith"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 10.3: Duplicate Email ❌
**Request:**
```json
{
  "email": "testuser@example.com",
  "password": "passwordUser123",
  "first_name": "Duplicate",
  "last_name": "User"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 10.4: Invalid Email ❌
**Request:**
```json
{
  "email": "notanemail",
  "password": "passwordUser123",
  "first_name": "Invalid",
  "last_name": "Email"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 10.5: Without Admin Token ❌
**Headers:**
```
Authorization: Bearer {{regular_user_token}}
```
**Expected Response:**
- Status: `403 Forbidden`

---

### 11. Get User by ID

**Endpoint:** `GET /accounts/api/users/{user_id}/`

#### Test Case 11.1: Success - Own Profile ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/accounts/api/users/1/`
**Expected Response:**
- Status: `200 OK`
- Returns user profile

#### Test Case 11.2: Success - Admin Accessing Others ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**URL:** `/accounts/api/users/2/`
**Expected Response:**
- Status: `200 OK`

#### Test Case 11.3: User Accessing Other's Profile ❌
**Headers:**
```
Authorization: Bearer {{user_token_id_1}}
```
**URL:** `/accounts/api/users/2/`
**Expected Response:**
- Status: `403 Forbidden`
- Response:
```json
{
  "error": "Permission denied. You can only view your own profile."
}
```

#### Test Case 11.4: Non-existent User ❌
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/accounts/api/users/9999/`
**Expected Response:**
- Status: `404 Not Found`
- Response:
```json
{
  "error": "User not found"
}
```

#### Test Case 11.5: No Authentication ❌
**URL:** `/accounts/api/users/1/`
**Expected Response:**
- Status: `401 Unauthorized`

#### Test Case 11.6: Invalid User ID Format ❌
**URL:** `/accounts/api/users/abc/`
**Expected Response:**
- Status: `404 Not Found` or `400 Bad Request`

---

### 12. Update User Profile

**Endpoint:** `PUT /accounts/api/users/{user_id}/`

#### Test Case 12.1: Success - Own Profile ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/accounts/api/users/1/`
**Request:**
```json
{
  "first_name": "Jonathan",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St",
  "date_of_birth": "1990-01-01",
  "gender": "M"
}
```
**Expected Response:**
- Status: `200 OK`
- Response includes updated user

#### Test Case 12.2: Partial Update (PATCH) ✅
**Method:** `PATCH`
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/accounts/api/users/1/`
**Request:**
```json
{
  "phone": "+9876543210"
}
```
**Expected Response:**
- Status: `200 OK`
- Only phone updated, other fields unchanged

#### Test Case 12.3: Update With Invalid Email ❌
**Request:**
```json
{
  "email": "notanemail",
  "first_name": "John"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 12.4: Update With Duplicate Email ❌
**Request:**
```json
{
  "email": "doctor@example.com",
  "first_name": "John"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 12.5: User Updating Other's Profile ❌
**Headers:**
```
Authorization: Bearer {{user_token_id_1}}
```
**URL:** `/accounts/api/users/2/`
**Request:**
```json
{
  "first_name": "Hacked"
}
```
**Expected Response:**
- Status: `403 Forbidden`

#### Test Case 12.6: Admin Can Update Any Profile ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**URL:** `/accounts/api/users/2/`
**Request:**
```json
{
  "first_name": "Updated By Admin"
}
```
**Expected Response:**
- Status: `200 OK`

#### Test Case 12.7: Invalid Date Format ❌
**Request:**
```json
{
  "date_of_birth": "invalid-date"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 12.8: Invalid Gender Value ❌
**Request:**
```json
{
  "gender": "invalid"
}
```
**Expected Response:**
- Status: `400 Bad Request`

---

### 13. Delete User

**Endpoint:** `DELETE /accounts/api/users/{user_id}/`

#### Test Case 13.1: Success - Own Profile ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/accounts/api/users/1/`
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "User testuser@example.com deleted successfully"
}
```

#### Test Case 13.2: Admin Deleting Other User ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**URL:** `/accounts/api/users/2/`
**Expected Response:**
- Status: `200 OK`

#### Test Case 13.3: User Deleting Other's Account ❌
**Headers:**
```
Authorization: Bearer {{user_token_id_1}}
```
**URL:** `/accounts/api/users/2/`
**Expected Response:**
- Status: `403 Forbidden`

#### Test Case 13.4: Non-existent User ❌
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/accounts/api/users/9999/`
**Expected Response:**
- Status: `404 Not Found`

#### Test Case 13.5: No Authentication ❌
**URL:** `/accounts/api/users/1/`
**Expected Response:**
- Status: `401 Unauthorized`

#### Test Case 13.6: Verify User Actually Deleted ✅
After deletion, GET `/accounts/api/users/{user_id}/` should return:
- Status: `404 Not Found`

---

### 14. Change Password

**Endpoint:** `POST /accounts/api/users/change-password/`

#### Test Case 14.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Request:**
```json
{
  "old_password": "securePassword123",
  "new_password": "newSecurePass456",
  "confirm_password": "newSecurePass456"
}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Password changed successfully"
}
```

#### Test Case 14.2: Incorrect Old Password ❌
**Request:**
```json
{
  "old_password": "wrongPassword",
  "new_password": "newSecurePass456",
  "confirm_password": "newSecurePass456"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Old password is incorrect"
}
```

#### Test Case 14.3: Passwords Don't Match ❌
**Request:**
```json
{
  "old_password": "securePassword123",
  "new_password": "newSecurePass456",
  "confirm_password": "differentPassword789"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "New password and confirm password do not match"
}
```

#### Test Case 14.4: New Password Too Short ❌
**Request:**
```json
{
  "old_password": "securePassword123",
  "new_password": "123",
  "confirm_password": "123"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Password must be at least 6 characters long"
}
```

#### Test Case 14.5: Same as Old Password ❌
**Request:**
```json
{
  "old_password": "securePassword123",
  "new_password": "securePassword123",
  "confirm_password": "securePassword123"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "New password must be different from old password"
}
```

#### Test Case 14.6: Missing Required Field ❌
**Request:**
```json
{
  "old_password": "securePassword123",
  "new_password": "newSecurePass456"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "All fields (old_password, new_password, confirm_password) are required"
}
```

#### Test Case 14.7: No Authentication ❌
**Headers:** (no Authorization)
**Expected Response:**
- Status: `401 Unauthorized`

#### Test Case 14.8: Verify Can Login With New Password ✅
After successful password change, attempt login:
**Request:**
```json
{
  "email": "testuser@example.com",
  "password": "newSecurePass456"
}
```
**Expected Response:**
- Status: `200 OK`
- Login successful with new password

---

### 15. User Profile Stats

**Endpoint:** `GET /accounts/api/users/profile-stats/`

#### Test Case 15.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Profile statistics retrieved",
  "stats": {
    "user_id": 1,
    "email": "testuser@example.com",
    "full_name": "John Doe",
    "role": "patient",
    "is_verified": false,
    "profile_complete": false,
    "last_login": "2024-01-15T10:30:00Z",
    "account_age_days": 30
  }
}
```

#### Test Case 15.2: No Authentication ❌
**Headers:** (no Authorization)
**Expected Response:**
- Status: `401 Unauthorized`

#### Test Case 15.3: Profile Complete Indicator ✅
After filling all profile fields:
- `profile_complete` should be `true`

#### Test Case 15.4: Invalid Token ❌
**Headers:**
```
Authorization: Bearer invalidtoken
```
**Expected Response:**
- Status: `401 Unauthorized`

---

## Patient Profile Endpoints

### 16. List All Patient Profiles

**Endpoint:** `GET /api/patients/`

#### Test Case 16.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Patient profiles retrieved",
  "count": 2,
  "results": [
    {
      "id": 1,
      "user": 1,
      "email": "testuser@example.com",
      "height": 175,
      "weight": 75,
      "blood_group": "O+",
      "bmi": 24.5,
      "activity": "moderate",
      "sleep_hours": 8,
      "stress": "low",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Test Case 16.2: No Authentication ❌
**Expected Response:**
- Status: `401 Unauthorized`

---

### 17. Create Patient Profile

**Endpoint:** `POST /api/patients/`

#### Test Case 17.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Request:**
```json
{
  "height": 175,
  "weight": 75,
  "blood_group": "O+",
  "activity": "moderate",
  "sleep_hours": 8,
  "stress": "low"
}
```
**Expected Response:**
- Status: `201 Created`
- Response:
```json
{
  "message": "Patient profile created successfully",
  "profile": {
    "id": 1,
    "user": 1,
    "email": "testuser@example.com",
    "height": 175,
    "weight": 75,
    "blood_group": "O+",
    "bmi": 24.5,
    "activity": "moderate",
    "sleep_hours": 8,
    "stress": "low",
    "created_at": "2024-01-16T10:00:00Z",
    "updated_at": "2024-01-16T10:00:00Z"
  }
}
```

#### Test Case 17.2: Profile Already Exists ❌
**Request:** (second time for same user)
```json
{
  "height": 180,
  "weight": 80,
  "blood_group": "A+",
  "activity": "high",
  "sleep_hours": 7,
  "stress": "medium"
}
```
**Expected Response:**
- Status: `400 Bad Request`
- Response:
```json
{
  "error": "Patient profile already exists for this user"
}
```

#### Test Case 17.3: Missing Required Field ❌
**Request:** (missing `height`)
```json
{
  "weight": 75,
  "blood_group": "O+",
  "activity": "moderate",
  "sleep_hours": 8,
  "stress": "low"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 17.4: Invalid Blood Group ❌
**Request:**
```json
{
  "height": 175,
  "weight": 75,
  "blood_group": "XX",
  "activity": "moderate",
  "sleep_hours": 8,
  "stress": "low"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 17.5: Invalid Activity Level ❌
**Request:**
```json
{
  "height": 175,
  "weight": 75,
  "blood_group": "O+",
  "activity": "invalid",
  "sleep_hours": 8,
  "stress": "low"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 17.6: Invalid Stress Level ❌
**Request:**
```json
{
  "height": 175,
  "weight": 75,
  "blood_group": "O+",
  "activity": "moderate",
  "sleep_hours": 8,
  "stress": "invalid"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 17.7: Negative Height ❌
**Request:**
```json
{
  "height": -175,
  "weight": 75,
  "blood_group": "O+",
  "activity": "moderate",
  "sleep_hours": 8,
  "stress": "low"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 17.8: Zero Weight ❌
**Request:**
```json
{
  "height": 175,
  "weight": 0,
  "blood_group": "O+",
  "activity": "moderate",
  "sleep_hours": 8,
  "stress": "low"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 17.9: No Authentication ❌
**Expected Response:**
- Status: `401 Unauthorized`

---

### 18. Get Current User's Patient Profile

**Endpoint:** `GET /api/patients/me/`

#### Test Case 18.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Expected Response:**
- Status: `200 OK`
- Returns user's patient profile

#### Test Case 18.2: No Profile Exists ❌
**Headers:**
```
Authorization: Bearer {{access_token}}
```
(For user without patient profile)
**Expected Response:**
- Status: `404 Not Found`
- Response:
```json
{
  "error": "No patient profile found. Create one first."
}
```

#### Test Case 18.3: No Authentication ❌
**Expected Response:**
- Status: `401 Unauthorized`

---

### 19. Get Patient Profile by ID

**Endpoint:** `GET /api/patients/{patient_id}/`

#### Test Case 19.1: Success - Own Profile ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/api/patients/1/`
**Expected Response:**
- Status: `200 OK`

#### Test Case 19.2: User Accessing Other's Profile ❌
**Headers:**
```
Authorization: Bearer {{other_user_token}}
```
**URL:** `/api/patients/1/`
**Expected Response:**
- Status: `403 Forbidden`
- Response:
```json
{
  "error": "Permission denied"
}
```

#### Test Case 19.3: Admin Accessing Any Profile ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**URL:** `/api/patients/1/`
**Expected Response:**
- Status: `200 OK`

#### Test Case 19.4: Non-existent Profile ❌
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/api/patients/9999/`
**Expected Response:**
- Status: `404 Not Found`
- Response:
```json
{
  "error": "Patient profile not found"
}
```

---

### 20. Update Patient Profile

**Endpoint:** `PUT /api/patients/{patient_id}/`

#### Test Case 20.1: Full Update ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/api/patients/1/`
**Request:**
```json
{
  "height": 180,
  "weight": 80,
  "blood_group": "A+",
  "activity": "high",
  "sleep_hours": 7,
  "stress": "medium"
}
```
**Expected Response:**
- Status: `200 OK`

#### Test Case 20.2: Partial Update (PATCH) ✅
**Method:** `PATCH`
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/api/patients/1/`
**Request:**
```json
{
  "weight": 78
}
```
**Expected Response:**
- Status: `200 OK`
- Only weight updated

#### Test Case 20.3: User Updating Other's Profile ❌
**Headers:**
```
Authorization: Bearer {{other_user_token}}
```
**URL:** `/api/patients/1/`
**Request:**
```json
{
  "weight": 100
}
```
**Expected Response:**
- Status: `403 Forbidden`

#### Test Case 20.4: Admin Updating Any Profile ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**URL:** `/api/patients/1/`
**Request:**
```json
{
  "weight": 70
}
```
**Expected Response:**
- Status: `200 OK`

#### Test Case 20.5: Invalid Values ❌
**Request:**
```json
{
  "height": -175,
  "stress": "invalid"
}
```
**Expected Response:**
- Status: `400 Bad Request`

---

### 21. Delete Patient Profile

**Endpoint:** `DELETE /api/patients/{patient_id}/`

#### Test Case 21.1: Success - Own Profile ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/api/patients/1/`
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Patient profile for testuser@example.com deleted successfully"
}
```

#### Test Case 21.2: User Deleting Other's Profile ❌
**Headers:**
```
Authorization: Bearer {{other_user_token}}
```
**URL:** `/api/patients/1/`
**Expected Response:**
- Status: `403 Forbidden`

#### Test Case 21.3: Admin Deleting Any Profile ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**URL:** `/api/patients/1/`
**Expected Response:**
- Status: `200 OK`

#### Test Case 21.4: Non-existent Profile ❌
**URL:** `/api/patients/9999/`
**Expected Response:**
- Status: `404 Not Found`

#### Test Case 21.5: Verify Deletion ✅
After deletion, GET same profile returns `404 Not Found`

---

### 22. Get Health Summary

**Endpoint:** `GET /api/patients/health-summary/`

#### Test Case 22.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Your health summary",
  "summary": {
    "bmi": 24.5,
    "bmi_category": "Normal",
    "activity": "moderate",
    "sleep_hours": 8,
    "stress": "low"
  }
}
```

#### Test Case 22.2: No Profile ❌
**Headers:**
```
Authorization: Bearer {{no_profile_token}}
```
**Expected Response:**
- Status: `404 Not Found`
- Response:
```json
{
  "error": "No patient profile found"
}
```

#### Test Case 22.3: No Authentication ❌
**Expected Response:**
- Status: `401 Unauthorized`

---

### 23. Get Detailed Health Metrics

**Endpoint:** `GET /api/patients/{patient_id}/health-metrics/`

#### Test Case 23.1: Success - Own Metrics ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**URL:** `/api/patients/1/health-metrics/`
**Expected Response:**
- Status: `200 OK`
- Response:
```json
{
  "message": "Health metrics retrieved successfully",
  "metrics": {
    "height_cm": 175,
    "weight_kg": 75,
    "bmi": 24.5,
    "bmi_category": "Normal",
    "blood_group": "O+",
    "activity_level": "moderate",
    "sleep_hours": 8,
    "stress_level": "low"
  }
}
```

#### Test Case 23.2: Different BMI Categories ✅
- BMI < 18.5: **Underweight**
- BMI 18.5-24.9: **Normal**
- BMI 25-29.9: **Overweight**
- BMI >= 30: **Obese**

#### Test Case 23.3: User Accessing Other's Metrics ❌
**Headers:**
```
Authorization: Bearer {{other_user_token}}
```
**URL:** `/api/patients/1/health-metrics/`
**Expected Response:**
- Status: `403 Forbidden`

#### Test Case 23.4: Admin Accessing Metrics ✅
**Headers:**
```
Authorization: Bearer {{admin_token}}
```
**URL:** `/api/patients/1/health-metrics/`
**Expected Response:**
- Status: `200 OK`

#### Test Case 23.5: Non-existent Patient ❌
**URL:** `/api/patients/9999/health-metrics/`
**Expected Response:**
- Status: `404 Not Found`

---

### 24. Bulk Health Update

**Endpoint:** `POST /api/patients/health-update/`

#### Test Case 24.1: Success Case ✅
**Headers:**
```
Authorization: Bearer {{access_token}}
```
**Request:**
```json
{
  "weight": 76,
  "sleep_hours": 7,
  "stress": "medium"
}
```
**Expected Response:**
- Status: `200 OK`
- Response includes updated profile

#### Test Case 24.2: Update Single Field ✅
**Request:**
```json
{
  "weight": 77
}
```
**Expected Response:**
- Status: `200 OK`

#### Test Case 24.3: Invalid Values ❌
**Request:**
```json
{
  "weight": -75,
  "stress": "invalid"
}
```
**Expected Response:**
- Status: `400 Bad Request`

#### Test Case 24.4: No Profile Exists ❌
**Headers:**
```
Authorization: Bearer {{no_profile_token}}
```
**Expected Response:**
- Status: `404 Not Found`
- Response:
```json
{
  "error": "Patient profile not found"
}
```

#### Test Case 24.5: No Authentication ❌
**Expected Response:**
- Status: `401 Unauthorized`

---

## Test Scenarios Summary

### Quick Reference: All Test Scenarios by Type

#### Success Scenarios (Should Return 2xx)
- ✅ User signup with valid data
- ✅ Doctor signup with valid data
- ✅ Login with correct credentials
- ✅ Request OTP, verify OTP, reset password
- ✅ Get current user
- ✅ Get user list (admin)
- ✅ Create user (admin)
- ✅ Get/update/delete own profile
- ✅ Admin accessing/modifying any user
- ✅ Change password successfully
- ✅ Get profile stats
- ✅ Create/get/update/delete patient profile
- ✅ Get health summary and metrics

#### Validation Failures (Should Return 400)
- ❌ Missing required fields
- ❌ Invalid email format
- ❌ Password too short
- ❌ Passwords don't match
- ❌ Invalid blood group
- ❌ Negative height/weight
- ❌ Invalid activity/stress levels
- ❌ Duplicate email
- ❌ Special characters in restricted fields

#### Authentication Failures (Should Return 401)
- ❌ No authentication token
- ❌ Invalid token
- ❌ Expired token
- ❌ Malformed Authorization header
- ❌ Wrong credentials (login)
- ❌ Invalid password (password reset)

#### Authorization Failures (Should Return 403)
- ❌ Non-admin accessing admin endpoints
- ❌ User accessing other user's profile
- ❌ User modifying other user's data
- ❌ User deleting other user's account
- ❌ User accessing other patient's data

#### Not Found Errors (Should Return 404)
- ❌ Non-existent user
- ❌ Non-existent patient profile
- ❌ Invalid user ID format leading to 404
- ❌ Accessing deleted resources

#### Server Errors (Should Return 500)
- ❌ Non-existent email in password reset
- ❌ Email delivery failures
- ❌ Database connection issues

---

## Common Error Responses

### 400 Bad Request
```json
{
  "message": "Validation failed" | "Details about what went wrong",
  "errors": {
    "field_name": ["Error message for this field"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials" | "Permission denied",
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied. You can only ... "
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to process request: [error details]"
}
```

---

## Testing Checklist

### Before Running Tests
- [ ] Django server running on `http://localhost:8000`
- [ ] Database migrations applied
- [ ] Email settings configured (for OTP tests)
- [ ] Create test users if needed
- [ ] Set up Postman environment variables

### Testing Flow
1. **Authentication Tests (3-7)**
   - [ ] Test signup (user and doctor)
   - [ ] Test login
   - [ ] Test password reset flow

2. **User Management Tests (8-15)**
   - [ ] Test get current user
   - [ ] Test list/create/get/update/delete user
   - [ ] Test change password
   - [ ] Test profile stats

3. **Patient Profile Tests (16-24)**
   - [ ] Test create patient profile
   - [ ] Test get current patient profile
   - [ ] Test list/get/update/delete by ID
   - [ ] Test health summary and metrics
   - [ ] Test bulk health update

### Post-Testing
- [ ] Document failed tests and errors
- [ ] Note any inconsistencies in responses
- [ ] Verify edge cases (null values, empty strings, etc.)
- [ ] Check API rate limiting (if implemented)
- [ ] Verify CORS headers (if applicable)

---

## Postman Collection Export Template

To export your test collection:
1. Click **Collections** in Postman sidebar
2. Click the three dots menu next to your collection
3. Select **Export**
4. Save as `MedoAir_API_Tests.postman_collection.json`

This file can be shared and imported by other team members.

---

## Notes

- All timestamps use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
- All IDs are positive integers
- Email addresses are case-insensitive in most endpoints
- Tokens expire after 10 days (access token)
- OTPs expire after 15 minutes
- All numeric values must be valid numbers (no strings)
- Blood groups: O+, O-, A+, A-, B+, B-, AB+, AB-
- Activity levels: low, moderate, high
- Stress levels: low, medium, high
- Genders: M, F, O (Other)

---

## Troubleshooting

### Token Not Working After Update
- Clear Postman cache
- Delete and re-login to get new tokens
- Check token expiration time

### OTP Not Received
- Check email service configuration in settings
- Check spam folder
- Verify email is correct
- Try resending OTP

### 500 Errors
- Check Django server logs
- Verify database connection
- Check email configuration
- Ensure all dependencies installed

---

**Last Updated:** 2024
**API Version:** v1
**Status:** Complete

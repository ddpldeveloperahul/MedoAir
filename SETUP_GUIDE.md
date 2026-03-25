# MedoAir Complete API Setup & Implementation Guide

## 📋 Overview

This document provides a complete guide to the MedoAir health management system's REST API with full CRUD operations for users and patient profiles, including profile image handling.

---

## 🔧 Installation & Setup

### 1. Install Required Packages
```bash
pip install django djangorestframework django-rest-framework-simplejwt pillow
```

### 2. Run Migrations
```bash
python manage.py makemigrations accounts
python manage.py makemigrations patients
python manage.py migrate
```

### 3. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 4. Start Development Server
```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

---

## 🗂️ Project Structure

```
Myproject/
├── accounts/
│   ├── models.py          # User model with profile fields
│   ├── serializers.py     # All user serializers
│   ├── views.py           # UserViewSet + Auth endpoints
│   └── urls.py            # API routes for users
├── patients/
│   ├── models.py          # PatientProfile with health data
│   ├── serializers.py     # Patient serializers
│   ├── views.py           # PatientProfileViewSet
│   └── urls.py            # API routes for patient profiles
├── API_DOCUMENTATION.md   # Complete API documentation
├── api_examples.py        # Python script with all examples
└── SETUP_GUIDE.md         # This file
```

---

## 🔐 Authentication Flow

```
1. User Signs Up
   POST /accounts/user/signup/
   
2. User Logs In
   POST /accounts/login/
   ↓
   Returns: access_token + refresh_token
   
3. Use access_token in Headers
   Authorization: Bearer <access_token>
   
4. All API requests require this header
```

---

## 📊 Database Models

### User Model (Extended)
```
- id (Primary Key)
- email (Unique)
- first_name
- last_name
- phone
- address
- profile_image (ImageField)
- date_of_birth
- gender
- role (user, doctor, admin)
- is_verified
- date_joined
- last_login
```

### PatientProfile Model
```
- id (Primary Key)
- user (OneToOne with User)
- age
- height (cm)
- weight (kg)
- blood_group
- activity (Sedentary, Lightly Active, Moderately Active, Very Active)
- diet (Vegetarian, Non-Vegetarian, Vegan, Mixes)
- stress (Low, Moderate, High)
- sleep_hours
- medical_history (TextField)
- allergies (TextField)
- current_medications (TextField)
- family_history (TextField)
- emergency_contact
- emergency_contact_phone
- insurance_provider
- insurance_number
- created_at
- updated_at
```

---

## 🚀 API Endpoints Summary

### Authentication (No Auth Required)
```
POST   /accounts/user/signup/          Create new user
POST   /accounts/doctor/signup/        Create new doctor
POST   /accounts/login/                Login user
POST   /accounts/forgot-password/      Request OTP
POST   /accounts/verify-otp/           Verify OTP
POST   /accounts/reset-password/       Reset password
POST   /accounts/resend-otp/           Resend OTP
```

### User Management (CRUD - Auth Required)
```
GET    /accounts/api/users/            List all users
POST   /accounts/api/users/            Create new user
GET    /accounts/api/users/{id}/       Get user details
PUT    /accounts/api/users/{id}/       Update user fully
PATCH  /accounts/api/users/{id}/       Update user partially
DELETE /accounts/api/users/{id}/       Delete user
```

### User Custom Actions
```
GET    /accounts/api/users/me/                  Current user profile
POST   /accounts/api/users/change_password/    Change password
GET    /accounts/api/users/profile_stats/      Profile statistics
```

### Patient Profiles (CRUD - Auth Required)
```
GET    /patients/api/profiles/                   List all profiles
POST   /patients/api/profiles/                   Create profile
GET    /patients/api/profiles/{id}/              Get profile
PUT    /patients/api/profiles/{id}/              Update profile fully
PATCH  /patients/api/profiles/{id}/              Update profile partially
DELETE /patients/api/profiles/{id}/              Delete profile
```

### Patient Custom Actions
```
GET    /patients/api/profiles/my_profile/       Get my profile
GET    /patients/api/profiles/health_summary/   Health summary
GET    /patients/api/profiles/{id}/health_metrics/  Health metrics
POST   /patients/api/profiles/bulk_health_update/   Quick update
```

---

## 📸 Image Upload & Retrieval

### Upload Profile Image
```bash
curl -X PATCH http://localhost:8000/accounts/api/users/1/ \
  -H "Authorization: Bearer <token>" \
  -F "profile_image=@photo.jpg" \
  -F "first_name=John"
```

### Image Response
```json
{
  "profile_image": "/media/profiles/photo_abc123.jpg",
  "profile_image_url": "http://localhost:8000/media/profiles/photo_abc123.jpg"
}
```

### Display Image in Frontend
```html
<img src="http://localhost:8000/media/profiles/photo_abc123.jpg" alt="Profile">
```

---

## 🧪 Testing with Examples

### Method 1: Use Python Script
```bash
python api_examples.py
```

### Method 2: Use cURL
```bash
# Signup
curl -X POST http://localhost:8000/accounts/user/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "confirm_password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'

# Get current user
curl -X GET http://localhost:8000/accounts/api/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Method 3: Use Postman
1. Import the API endpoints
2. Set Authorization to "Bearer Token"
3. Add your access token
4. Test each endpoint

### Method 4: Use Django Shell
```bash
python manage.py shell

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Create user
user = User.objects.create_user(
    email='test@example.com',
    password='password123',
    role='user',
    first_name='Test'
)

# Generate token
refresh = RefreshToken.for_user(user)
print(f"Access: {refresh.access_token}")
print(f"Refresh: {refresh}")
```

---

## 📱 Frontend Integration Examples

### React/JavaScript Example
```javascript
// Login
const loginUser = async (email, password) => {
  const response = await fetch('http://localhost:8000/accounts/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return data;
};

// Get current user
const getCurrentUser = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/accounts/api/users/me/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
};

// Update profile
const updateProfile = async (formData) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/accounts/api/users/1/', {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData  // FormData for file upload
  });
  return await response.json();
};
```

### Python/Requests Example
```python
import requests

# Login
response = requests.post('http://localhost:8000/accounts/login/', json={
    'email': 'john@example.com',
    'password': 'password123'
})
token = response.json()['access']

# Get user
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/accounts/api/users/me/', 
                       headers=headers)
user = response.json()['user']

# Update profile with image
with open('photo.jpg', 'rb') as f:
    files = {'profile_image': f}
    data = {'first_name': 'John', 'phone': '1234567890'}
    response = requests.patch(
        'http://localhost:8000/accounts/api/users/1/',
        headers=headers,
        files=files,
        data=data
    )
```

---

## 🔍 Dashboard Views Explained

Based on the provided screenshots, here are the key dashboards:

### 1. Profile Management Screen
- View: Personal information display
- Endpoints: `GET /accounts/api/users/me/`
- Features: Name, email, phone, address, profile picture

### 2. Health Baseline Screen
- View: Health metrics overview
- Endpoints: `GET /patients/api/profiles/health_summary/`
- Displays: Age, weight, BMI category, health status

### 3. Account Security Screen
- View: Security settings
- Endpoints: `POST /accounts/api/users/change_password/`
- Features: Password management, 2FA settings

### 4. Health Tracking System
- View: Detailed health records
- Endpoints: `GET /patients/api/profiles/health_metrics/`
- Displays: Daily updates, medicines, disease history

### 5. Doctor Consultation
- View: Doctor profiles and bookings
- Endpoints: Related to appointments app (can be extended)
- Features: Filter by specialty, view availability

### 6. Health & Lifestyle Setup
- View: Initial health profile creation
- Endpoints: `POST /patients/api/profiles/`
- Collects: Age, weight, activity level, diet, stress, medical history

---

## 🛠️ Common Issues & Solutions

### Issue: 401 Unauthorized
**Solution:** 
- Make sure token is valid and not expired
- Check Authorization header format: `Bearer <token>`
- Refresh token if expired

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

### Issue: 403 Forbidden
**Solution:**
- User doesn't have permission
- Can only access own profile (except admin)
- Admin can access all profiles

### Issue: 400 Bad Request
**Solution:**
- Check required fields
- Validate data types (integer vs string)
- Check image file size and format

### Issue: Image not uploading
**Solution:**
- Use Form-Data, not JSON
- Check `MEDIA_ROOT` and `MEDIA_URL` in settings
- Ensure Pillow is installed: `pip install pillow`

---

## 📈 Performance Tips

1. **Use Pagination for Large Datasets**
   ```python
   # settings.py
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 10
   }
   ```

2. **Optimize Image Uploads**
   - Compress images before upload
   - Use thumbnails for display
   - Set file size limit

3. **Cache User Profiles**
   - Use Redis for caching
   - Cache frequently accessed profiles

4. **Database Optimization**
   - Add indexes to frequently queried fields
   - Use `select_related()` and `prefetch_related()`

---

## 🔒 Security Checklist

- [x] JWT token authentication
- [x] CSRF protection
- [x] Password hashing (bcrypt)
- [x] Permission-based access control
- [x] Email verification (OTP)
- [x] Rate limiting (can be added)
- [x] HTTPS in production (required)
- [ ] API versioning (can be added)
- [ ] Request validation
- [ ] SQL injection protection (Django ORM handles)

---

## 📞 Support & Further Development

### Ready to Extend
1. **Appointments App** - Doctor bookings and scheduling
2. **Chat App** - Real-time messaging
3. **Reports App** - Health report generation
4. **Notifications** - Email and push notifications

### Documentation Links
- Django REST Framework: https://www.django-rest-framework.org/
- Django: https://docs.djangoproject.com/
- JWT: https://django-rest-framework-simplejwt.readthedocs.io/

---

## 🎯 Next Steps

1. ✅ Complete API implementation (DONE)
2. ✅ Profile image upload (DONE)
3. ✅ User CRUD operations (DONE)
4. ✅ Patient profile management (DONE)
5. ⏳ Frontend integration
6. ⏳ Appointment system
7. ⏳ Chat functionality
8. ⏳ Reports generation
9. ⏳ Deployment (AWS/Heroku)

---

## 📝 Quick Reference

### Most Used Endpoints

| Task | Endpoint | Method |
|------|----------|--------|
| Create account | `/accounts/user/signup/` | POST |
| Login | `/accounts/login/` | POST |
| Get my profile | `/accounts/api/users/me/` | GET |
| Update profile | `/accounts/api/users/{id}/` | PATCH |
| Create health profile | `/patients/api/profiles/` | POST |
| Get health data | `/patients/api/profiles/my_profile/` | GET |
| Update health data | `/patients/api/profiles/{id}/` | PATCH |
| Get health summary | `/patients/api/profiles/health_summary/` | GET |

---

**Version:** 1.0  
**Last Updated:** March 23, 2024  
**Status:** Complete ✅

For questions or issues, refer to `API_DOCUMENTATION.md` or run `api_examples.py`

# Quick Start - Running the Consolidated App

## 🚀 Fastest Way to Run

### Step 1: Apply Migrations
```bash
cd c:\Users\Dell Pc\Desktop\medoair\Myproject

# Create fresh migrations for the api app
python manage.py migrate

# If you get "no changes detected", run:
python manage.py makemigrations api
python manage.py migrate api
```

### Step 2: Create Admin User
```bash
python manage.py createsuperuser
# Email: admin@example.com
# Password: admin123
```

### Step 3: Start Server
```bash
python manage.py runserver
```

### Step 4: Test It!

**Access Django Admin:**
```
http://localhost:8000/admin/
```

**Test API Endpoints:**

```bash
# User Signup
curl -X POST http://localhost:8000/user/signup/ \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"John Doe\",
    \"email\": \"john@example.com\",
    \"password\": \"password123\",
    \"confirm_password\": \"password123\"
  }"

# Login
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"john@example.com\",
    \"password\": \"password123\"
  }"

# Get Current User (replace TOKEN with access token from login)
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer TOKEN"

# List All Users
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer TOKEN"
```

---

## 📋 Application Structure

### New Single App: `api/`
- ✅ Models (8 total)
- ✅ Views (20+ APIView classes)
- ✅ Serializers (15+ serializers)
- ✅ URLs (25+ endpoints)
- ✅ Admin panels (all models)

### Settings Updated
- ✅ `INSTALLED_APPS` - Only 'api' app
- ✅ `AUTH_USER_MODEL` - Changed to 'api.User'
- ✅ URL routing - All under 'api/' or root

---

## ⚠️ Important Notes

1. **Old Apps are Still There** but not used. You can delete them:
   ```bash
   rm -r accounts doctors patients appointments chat reports
   ```

2. **Database is Intact** - All data in db.sqlite3 is preserved

3. **No Data Loss** - Same models, just in one app now

4. **All Endpoints Work** - Same functionality, cleaner structure

---

## 🔧 Common Issues & Fixes

### Issue: Migration Errors
```bash
# Solution: Reset migrations
python manage.py migrate api 0001
python manage.py migrate
```

### Issue: Import Errors
```bash
# Check if api app is in INSTALLED_APPS (it should be)
# In settings.py, should have:
# 'api',
```

### Issue: AUTH_USER_MODEL not found
```bash
# Make sure settings.py has:
# AUTH_USER_MODEL = 'api.User'
```

---

## 📊 All Available Endpoints (25+)

### Auth (7)
- POST `/user/signup/`
- POST `/doctor/signup/`
- POST `/login/`
- POST `/forgot-password/`
- POST `/verify-otp/`
- POST `/reset-password/`
- POST `/resend-otp/`

### Users (5)
- GET/POST `/api/users/`
- GET/PUT/PATCH/DELETE `/api/users/<id>/`
- GET `/api/users/me/`
- POST `/api/users/change-password/`
- GET `/api/users/profile-stats/`

### Patients (6)
- GET/POST `/api/patients/`
- GET/PUT/PATCH/DELETE `/api/patients/<id>/`
- GET `/api/patients/me/`
- GET `/api/patients/health-summary/`
- GET `/api/patients/<id>/health-metrics/`
- POST `/api/patients/health-update/`

### Appointments (1)
- GET/POST `/api/appointments/`

### Messages (1)
- GET/POST `/api/appointments/<id>/messages/`

### Reports (1)
- GET/POST `/api/reports/`

---

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test api

# Run specific test
python manage.py test api.tests.UserModelTest

# With verbose output
python manage.py test api -v 2
```

---

## 📱 Postman Testing

Import this collection into Postman (or manually create requests):

### 1. Signup
```
POST http://localhost:8000/user/signup/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

### 2. Login
```
POST http://localhost:8000/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi...",
  "user": {...}
}
```

### 3. Use Access Token
```
GET http://localhost:8000/api/users/me/
Authorization: Bearer eyJ0eXAi...
```

---

## 🎯 Next Steps

1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Create admin: `python manage.py createsuperuser`
3. ✅ Start server: `python manage.py runserver`
4. ✅ Test endpoints with curl or Postman
5. ✅ Build your frontend to consume the API

---

## 📚 Documentation Files

- `APP_CONSOLIDATION_GUIDE.md` - Full consolidation details
- `POSTMAN_TESTING_GUIDE.md` - Complete test scenarios
- `APIVIEW_CONVERSION_SUMMARY.md` - APIView pattern info

---

**Everything is ready!** 🎉

Start the server and enjoy your unified API! 🚀

#!/usr/bin/env python3
"""
MedoAir API Examples
Complete examples for all CRUD operations
Run this script with: python3 api_examples.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = None  # Will be set after login

# ------ COLORS FOR TERMINAL OUTPUT ------
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")

def print_json(data):
    print(json.dumps(data, indent=2))

def set_headers():
    """Get headers with authorization"""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers

# ============================================
# 1. AUTHENTICATION EXAMPLES
# ============================================

def example_signup():
    print_header("1. USER SIGNUP")
    
    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    
    print_info("Request payload:")
    print_json(payload)
    
    response = requests.post(f"{BASE_URL}/accounts/user/signup/", json=payload)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())
    
    return response.json()

def example_login():
    print_header("2. USER LOGIN")
    global API_KEY
    
    payload = {
        "email": "john@example.com",
        "password": "password123"
    }
    
    print_info("Request payload:")
    print_json(payload)
    
    response = requests.post(f"{BASE_URL}/accounts/login/", json=payload)
    print_info(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        API_KEY = data.get('access')
        print_success("Login successful! Token stored.")
        print_json(data)
        return data
    else:
        print_error("Login failed!")
        print_json(response.json())
        return None

def example_forgot_password():
    print_header("3. FORGOT PASSWORD - REQUEST OTP")
    
    payload = {"email": "john@example.com"}
    
    print_info("Request payload:")
    print_json(payload)
    
    response = requests.post(f"{BASE_URL}/accounts/forgot-password/", json=payload)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

# ============================================
# 2. USER MANAGEMENT EXAMPLES
# ============================================

def example_get_current_user():
    print_header("4. GET CURRENT USER PROFILE")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/accounts/api/users/me/", headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_list_users():
    print_header("5. LIST ALL USERS")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/accounts/api/users/", headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_get_user_by_id(user_id=1):
    print_header(f"6. GET USER BY ID (ID: {user_id})")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/accounts/api/users/{user_id}/", headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_update_user_profile(user_id=1):
    print_header(f"7. UPDATE USER PROFILE (ID: {user_id})")
    
    payload = {
        "first_name": "John",
        "last_name": "Updated",
        "phone": "9876543210",
        "address": "456 Updated St",
        "date_of_birth": "1990-01-15",
        "gender": "Male"
    }
    
    print_info("Request payload:")
    print_json(payload)
    
    headers = set_headers()
    response = requests.patch(f"{BASE_URL}/accounts/api/users/{user_id}/", 
                            headers=headers, json=payload)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_change_password():
    print_header("8. CHANGE PASSWORD")
    
    payload = {
        "old_password": "password123",
        "new_password": "newpassword456",
        "confirm_password": "newpassword456"
    }
    
    print_info("Request payload:")
    print_json(payload)
    
    headers = set_headers()
    response = requests.post(f"{BASE_URL}/accounts/api/users/change_password/", 
                            headers=headers, json=payload)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_user_profile_stats():
    print_header("9. GET USER PROFILE STATISTICS")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/accounts/api/users/profile_stats/", 
                           headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_delete_user(user_id=1):
    print_header(f"10. DELETE USER (ID: {user_id})")
    
    print_info(f"⚠️  This will delete user with ID {user_id}")
    headers = set_headers()
    response = requests.delete(f"{BASE_URL}/accounts/api/users/{user_id}/", 
                              headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

# ============================================
# 3. PATIENT PROFILE EXAMPLES
# ============================================

def example_create_patient_profile():
    print_header("11. CREATE PATIENT PROFILE")
    
    payload = {
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
    
    print_info("Request payload:")
    print_json(payload)
    
    headers = set_headers()
    response = requests.post(f"{BASE_URL}/patients/api/profiles/", 
                            headers=headers, json=payload)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_list_patient_profiles():
    print_header("12. LIST ALL PATIENT PROFILES")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/patients/api/profiles/", headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_get_my_patient_profile():
    print_header("13. GET MY PATIENT PROFILE")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/patients/api/profiles/my_profile/", 
                           headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_get_health_summary():
    print_header("14. GET HEALTH SUMMARY")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/patients/api/profiles/health_summary/", 
                           headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_get_health_metrics(profile_id=1):
    print_header(f"15. GET HEALTH METRICS (Profile ID: {profile_id})")
    
    headers = set_headers()
    response = requests.get(f"{BASE_URL}/patients/api/profiles/{profile_id}/health_metrics/", 
                           headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_update_patient_profile(profile_id=1):
    print_header(f"16. UPDATE PATIENT PROFILE (ID: {profile_id})")
    
    payload = {
        "weight": 78.0,
        "activity": "Very Active",
        "stress": "Moderate"
    }
    
    print_info("Request payload:")
    print_json(payload)
    
    headers = set_headers()
    response = requests.patch(f"{BASE_URL}/patients/api/profiles/{profile_id}/", 
                             headers=headers, json=payload)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_bulk_health_update():
    print_header("17. BULK HEALTH UPDATE")
    
    payload = {
        "weight": 76.0,
        "sleep_hours": 7,
        "stress": "High"
    }
    
    print_info("Request payload:")
    print_json(payload)
    
    headers = set_headers()
    response = requests.post(f"{BASE_URL}/patients/api/profiles/bulk_health_update/", 
                            headers=headers, json=payload)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

def example_delete_patient_profile(profile_id=1):
    print_header(f"18. DELETE PATIENT PROFILE (ID: {profile_id})")
    
    print_info(f"⚠️  This will delete patient profile with ID {profile_id}")
    headers = set_headers()
    response = requests.delete(f"{BASE_URL}/patients/api/profiles/{profile_id}/", 
                              headers=headers)
    print_info(f"Response Status: {response.status_code}")
    print_json(response.json())

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║        MedoAir API - Complete CRUD Examples            ║")
    print("║              Django REST Framework                     ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print_info("Make sure your Django server is running on http://localhost:8000")
    print_info("Press Enter to continue or Ctrl+C to stop...\n")
    
    try:
        # Authentication Examples
        example_signup()
        input(f"\n{Colors.BOLD}Press Enter to continue to login...{Colors.ENDC}")
        
        example_login()
        input(f"\n{Colors.BOLD}Press Enter to continue to user management...{Colors.ENDC}")
        
        # User Management Examples
        example_get_current_user()
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_list_users()
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_get_user_by_id(1)
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_update_user_profile(1)
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_user_profile_stats()
        input(f"\n{Colors.BOLD}Press Enter to continue to patient profiles...{Colors.ENDC}")
        
        # Patient Profile Examples
        example_create_patient_profile()
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_list_patient_profiles()
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_get_my_patient_profile()
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_get_health_summary()
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_get_health_metrics(1)
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_update_patient_profile(1)
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        
        example_bulk_health_update()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
        print("╔════════════════════════════════════════════════════════╗")
        print("║          All API Examples Completed Successfully!      ║")
        print("╚════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}{Colors.BOLD}Script interrupted by user{Colors.ENDC}\n")
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to the server. Make sure Django is running!")
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

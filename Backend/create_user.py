import requests
import json

# Use the registration endpoint
url = "http://localhost:8000/api/auth/register"
email = "test@test.com"
payload = {
    "full_name": "Test User",
    "email": email,
    "password": "test1234"
}

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"✅ User created successfully!")
        print(f"Email: {email}")
        print(f"Password: test1234")
    elif response.status_code == 400:
        print(f"User already exists: {email}")
        print(f"Password: test1234")
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
    print("Make sure the backend server is running on port 8000")

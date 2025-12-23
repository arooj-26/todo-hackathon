"""Test signup with the new email from the screenshot."""
import requests
import json

# Test data from the new screenshot
test_user = {
    "email": "jenharaj0126@gmail.com",
    "password": "Test@123"
}

try:
    print(f"Testing signup with NEW email: {test_user['email']}")
    response = requests.post(
        "http://localhost:8000/auth/signup",
        json=test_user,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
        
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")

import requests
import json

url = "http://localhost:8000/auth/signup"
data = {
    "email": "directtest@example.com",
    "password": "Test1234"
}

print(f"Sending request to {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")

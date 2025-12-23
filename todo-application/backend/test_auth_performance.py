"""Test authentication endpoint performance."""
import time
import requests
import random
import string

def generate_random_email():
    """Generate a random email for testing."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

def test_signup_performance():
    """Test signup endpoint response time."""
    url = "http://127.0.0.1:8000/auth/signup"
    email = generate_random_email()
    data = {
        "email": email,
        "password": "testpassword123"
    }

    print(f"Testing signup with email: {email}")
    start_time = time.time()

    try:
        response = requests.post(url, json=data, timeout=30)
        end_time = time.time()
        elapsed = end_time - start_time

        print(f"\n[OK] Signup Response Time: {elapsed:.3f} seconds")
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 201:
            print(f"  [OK] User created successfully")
            return response.json(), email
        else:
            print(f"  Error: {response.json()}")
            return None, None
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Request timed out after 30 seconds")
        return None, None
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return None, None

def test_signin_performance(email, password="testpassword123"):
    """Test signin endpoint response time."""
    url = "http://127.0.0.1:8000/auth/signin"
    data = {
        "email": email,
        "password": password
    }

    print(f"\nTesting signin with email: {email}")
    start_time = time.time()

    try:
        response = requests.post(url, json=data, timeout=30)
        end_time = time.time()
        elapsed = end_time - start_time

        print(f"\n[OK] Signin Response Time: {elapsed:.3f} seconds")
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"  [OK] Signin successful")
        else:
            print(f"  Error: {response.json()}")
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Request timed out after 30 seconds")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")

def main():
    print("=" * 60)
    print("Authentication Performance Test")
    print("=" * 60)
    print("\nTesting backend endpoints at http://127.0.0.1:8000")
    print("This will measure the actual response time from your backend.")
    print("-" * 60)

    # Test signup
    response_data, email = test_signup_performance()

    if email:
        # Test signin with the same credentials
        test_signin_performance(email)

    print("\n" + "=" * 60)
    print("Performance Analysis:")
    print("=" * 60)
    print("If response times are:")
    print("  • < 1 second: Normal (network latency to Neon DB)")
    print("  • 1-3 seconds: Acceptable for Neon free tier")
    print("  • > 3 seconds: Investigate Neon connection or frontend")
    print("  • > 10 seconds: Likely frontend issue, not backend")
    print("=" * 60)

if __name__ == "__main__":
    main()

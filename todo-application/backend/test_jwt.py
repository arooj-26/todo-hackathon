"""Test JWT token generation."""
import traceback
from app.auth.jwt import create_access_token

def test_jwt():
    """Test JWT token creation."""
    
    test_user_id = 5  # The ID from the created user
    
    print(f"Testing JWT token generation for user_id: {test_user_id}")
    
    try:
        access_token = create_access_token(user_id=test_user_id)
        print(f"[SUCCESS] Token generated: {access_token[:50]}...")
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_jwt()

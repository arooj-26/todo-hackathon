"""Direct test of signup logic to see the actual error."""
import sys
import traceback
from sqlmodel import Session

# Import app components
from app.database import engine
from app.models.user import User
from app.schemas.auth import UserCreate
from app.auth.password import hash_password

def test_signup_direct():
    """Test signup logic directly to see actual errors."""
    
    test_email = "aroojshaheer126@gmail.com"
    test_password = "Test@123"
    
    print(f"Testing signup for: {test_email}")
    
    try:
        with Session(engine) as session:
            # Create user data
            user_data = UserCreate(email=test_email, password=test_password)
            print(f"[OK] Created UserCreate object")
            
            # Hash password
            password_hash = hash_password(user_data.password)
            print(f"[OK] Hashed password")
            
            # Create user
            new_user = User(
                email=user_data.email,
                password_hash=password_hash
            )
            print(f"[OK] Created User object")
            
            # Add to session
            session.add(new_user)
            print(f"[OK] Added user to session")
            
            # Commit
            session.commit()
            print(f"[OK] Committed to database")
            
            # Refresh
            session.refresh(new_user)
            print(f"[OK] Refreshed user object")
            
            print(f"\n[SUCCESS] User created with ID: {new_user.id}")
            
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_signup_direct()


"""Test complete signup with detailed error reporting."""
import traceback
from sqlmodel import Session, select

from app.database import engine
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, TokenResponse
from app.auth.password import hash_password
from app.auth.jwt import create_access_token

def test_full_signup():
    """Test full signup flow."""
    
    test_email = "completelynew@example.com"
    test_password = "Test@123"
    
    print(f"Testing FULL signup for: {test_email}")
    
    try:
        with Session(engine) as session:
            # Check existing
            statement = select(User).where(User.email == test_email)
            existing = session.exec(statement).first()
            
            if existing:
                print(f"[INFO] User exists, deleting first...")
                session.delete(existing)
                session.commit()
            
            # Create user
            user_data = UserCreate(email=test_email, password=test_password)
            print(f"[1/6] UserCreate validated")
            
            password_hash = hash_password(user_data.password)
            print(f"[2/6] Password hashed: {password_hash[:30]}...")
            
            new_user = User(
                email=user_data.email,
                password_hash=password_hash
            )
            print(f"[3/6] User model created")
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            print(f"[4/6] User saved to DB, ID: {new_user.id}")
            
            # Generate token
            access_token = create_access_token(user_id=new_user.id)
            print(f"[5/6] Token generated: {access_token[:50]}...")
            
            # Create response
            user_response = UserResponse.model_validate(new_user)
            token_response = TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )
            print(f"[6/6] Response created")
            
            print(f"\n✅ SUCCESS! Full signup completed")
            print(f"   User ID: {new_user.id}")
            print(f"   Email: {new_user.email}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_full_signup()

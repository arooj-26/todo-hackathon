"""Test complete signup flow with response model."""
import traceback
from sqlmodel import Session, select

from app.database import engine
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, TokenResponse
from app.auth.password import hash_password
from app.auth.jwt import create_access_token

def test_complete_signup():
    """Test complete signup flow including response model."""
    
    test_email = "testuser999@example.com"
    test_password = "Test@123"
    
    print(f"Testing COMPLETE signup flow for: {test_email}")
    
    try:
        with Session(engine) as session:
            # Check if user exists
            statement = select(User).where(User.email == test_email)
            existing_user = session.exec(statement).first()
            
            if existing_user:
                print(f"[INFO] User already exists, using existing user ID: {existing_user.id}")
                user = existing_user
            else:
                # Create user
                user_data = UserCreate(email=test_email, password=test_password)
                password_hash = hash_password(user_data.password)
                
                user = User(
                    email=user_data.email,
                    password_hash=password_hash
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"[OK] User created with ID: {user.id}")
            
            # Generate token
            access_token = create_access_token(user_id=user.id)
            print(f"[OK] Token generated")
            
            # Create UserResponse
            user_response = UserResponse.model_validate(user)
            print(f"[OK] UserResponse created: {user_response}")
            
            # Create TokenResponse
            token_response = TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )
            print(f"[OK] TokenResponse created")
            
            # Convert to dict (simulating FastAPI response)
            response_dict = token_response.model_dump()
            print(f"\n[SUCCESS] Complete response:")
            print(f"  - access_token: {response_dict['access_token'][:50]}...")
            print(f"  - token_type: {response_dict['token_type']}")
            print(f"  - user.id: {response_dict['user']['id']}")
            print(f"  - user.email: {response_dict['user']['email']}")
            
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_signup()

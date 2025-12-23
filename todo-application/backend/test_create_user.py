from app.database import get_session
from app.models.user import User
from app.auth.password import hash_password
from sqlmodel import Session, select

# Get a session
session_gen = get_session()
session = next(session_gen)

try:
    # Test user data
    email = "test456@example.com"
    password = "Test1234"

    # Check if user exists
    statement = select(User).where(User.email == email)
    existing = session.exec(statement).first()

    if existing:
        print(f"User already exists: {existing.email}")
    else:
        # Hash password
        password_hash = hash_password(password)
        print(f"Password hashed: {password_hash[:50]}...")

        # Create user
        new_user = User(
            email=email,
            password_hash=password_hash
        )
        print(f"User object created: {new_user.email}")

        # Add to session
        session.add(new_user)
        print("Added to session")

        # Commit
        session.commit()
        print("Committed")

        # Refresh
        session.refresh(new_user)
        print(f"User created successfully with ID: {new_user.id}")

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    session.rollback()
    import traceback
    traceback.print_exc()
finally:
    session.close()

from sqlmodel import SQLModel, create_engine
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("Error: DATABASE_URL not found in environment variables")
    print("Please make sure you have a .env file with DATABASE_URL configured")
    exit(1)

print(f"Connecting to database: {database_url}")

# Create engine
engine = create_engine(database_url)

# Drop all existing tables (WARNING: This will delete all data!)
print("Dropping existing tables...")
SQLModel.metadata.drop_all(engine)

# Create all tables with new schema
print("Creating new tables with updated schema...")
SQLModel.metadata.create_all(engine)

print('Database schema updated successfully!')
print('Tables created:')
print('- tasks (with integer id, string user_id)')
print('- conversations (with integer id, string user_id)') 
print('- messages (with integer id, string user_id)')
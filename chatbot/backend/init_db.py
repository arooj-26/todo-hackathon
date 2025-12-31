from sqlmodel import SQLModel, create_engine
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
SQLModel.metadata.create_all(engine)
print('Database initialized!')
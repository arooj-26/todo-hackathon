"""
FastAPI application entry point.

Provides the main application instance with CORS middleware and error handling.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Todo AI Chatbot API",
    description="Conversational interface for managing todos through natural language",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:3001"],  # Allow frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Add production middleware
from .middleware import RequestLoggingMiddleware, RateLimitMiddleware

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)


# Error Handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    Handle Pydantic validation errors.

    Returns user-friendly error messages for invalid requests.
    """
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "conversation_id": None,
            "response": "",
            "tool_calls": [],
            "error": f"Validation error: {'; '.join(error_messages)}"
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
):
    """
    Handle database errors.

    Returns user-friendly error message for database failures.
    """
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "conversation_id": None,
            "response": "",
            "tool_calls": [],
            "error": "Database connection error. Please try again later."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    """
    Handle all other unhandled exceptions.

    Returns generic error message to avoid leaking implementation details.
    """
    # Log the error (in production, use proper logging)
    print(f"Unhandled error: {type(exc).__name__}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "conversation_id": None,
            "response": "",
            "tool_calls": [],
            "error": "An unexpected error occurred. Please try again."
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns server status and basic information.
    """
    return {
        "status": "healthy",
        "service": "Todo AI Chatbot API",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.

    Returns welcome message and link to API documentation.
    """
    return {
        "message": "Todo AI Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }


# Import dependencies for chat endpoint
from fastapi import Depends
from sqlmodel import Session, select
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

from .schemas import ChatRequest, ChatResponse
from ..database.connection import get_session
from ..models.conversation import Conversation
from ..models.message import Message
from ..models import RoleEnum
from ..agent.chat_agent import run_agent
from ..auth.middleware import get_current_user_id


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Chat endpoint for conversational task management.

    Handles natural language input, manages conversation state,
    and invokes the AI agent to process requests.

    The user_id is automatically extracted from the JWT token in the
    Authorization header, so users don't need to know their ID.

    Args:
        request: Chat request with message and optional conversation_id
        user_id: User ID extracted from JWT token (injected by dependency)
        session: Database session

    Returns:
        ChatResponse with conversation_id, response text, and tool_calls

    Headers:
        Authorization: Bearer <JWT_TOKEN>
    """
    try:
        # Get or create conversation
        conversation_id = request.conversation_id
        if conversation_id:
            # Fetch existing conversation
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = session.exec(stmt).first()

            if not conversation:
                # Conversation not found or doesn't belong to user
                # This typically happens when switching accounts and the old conversation_id is cached
                print(f"⚠️ Conversation {conversation_id} not found for user {user_id} - likely account switch with stale conversation_id")
                return ChatResponse(
                    conversation_id=None,
                    response="",
                    tool_calls=[],
                    error="Conversation not found. Starting a new conversation."
                )
        else:
            # Create new conversation - let database auto-generate the ID
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Store user message - let database auto-generate the ID
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content=request.message,
            created_at=datetime.utcnow()
        )
        session.add(user_message)
        session.commit()

        # Fetch conversation history (last 50 messages for context)
        stmt = select(Message).where(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).limit(50)
        messages = session.exec(stmt).all()

        # Build message history for agent
        message_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

        # Run agent
        agent_response = await run_agent(message_history, user_id)

        # Debug logging
        print(f"🤖 Agent response: {agent_response}")
        print(f"🔧 Tool calls: {agent_response.get('tool_calls', [])}")

        # Store assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.ASSISTANT,
            content=agent_response["response"],
            created_at=datetime.utcnow()
        )
        session.add(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        chat_response = ChatResponse(
            conversation_id=conversation.id,
            response=agent_response["response"],
            tool_calls=agent_response.get("tool_calls", []),
            error=agent_response.get("error")
        )
        print(f"📤 Returning chat response: {chat_response}")
        return chat_response

    except Exception as e:
        return ChatResponse(
            conversation_id=conversation_id if conversation_id else None,
            response="",
            tool_calls=[],
            error=f"Error processing request: {str(e)}"
        )


@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat_with_user_id(
    user_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Chat endpoint with user_id in path (for backward compatibility).

    This endpoint is similar to /api/chat but accepts user_id in the URL path
    instead of extracting it from a JWT token.

    Args:
        user_id: User ID from URL path
        request: Chat request with message and optional conversation_id
        session: Database session

    Returns:
        ChatResponse with conversation_id, response text, and tool_calls
    """
    try:
        # Get or create conversation
        conversation_id = request.conversation_id
        if conversation_id:
            # Fetch existing conversation
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = session.exec(stmt).first()

            if not conversation:
                # Conversation not found or doesn't belong to user
                # This typically happens when switching accounts and the old conversation_id is cached
                print(f"⚠️ Conversation {conversation_id} not found for user {user_id} - likely account switch with stale conversation_id")
                return ChatResponse(
                    conversation_id=None,
                    response="",
                    tool_calls=[],
                    error="Conversation not found. Starting a new conversation."
                )
        else:
            # Create new conversation - let database auto-generate the ID
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Store user message - let database auto-generate the ID
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content=request.message,
            created_at=datetime.utcnow()
        )
        session.add(user_message)
        session.commit()

        # Fetch conversation history (last 50 messages for context)
        stmt = select(Message).where(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).limit(50)
        messages = session.exec(stmt).all()

        # Build message history for agent
        message_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

        # Run agent
        agent_response = await run_agent(message_history, user_id)

        # Debug logging
        print(f"🤖 Agent response: {agent_response}")
        print(f"🔧 Tool calls: {agent_response.get('tool_calls', [])}")

        # Store assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.ASSISTANT,
            content=agent_response["response"],
            created_at=datetime.utcnow()
        )
        session.add(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        chat_response = ChatResponse(
            conversation_id=conversation.id,
            response=agent_response["response"],
            tool_calls=agent_response.get("tool_calls", []),
            error=agent_response.get("error")
        )
        print(f"📤 Returning chat response: {chat_response}")
        return chat_response

    except Exception as e:
        return ChatResponse(
            conversation_id=conversation_id if conversation_id else None,
            response="",
            tool_calls=[],
            error=f"Error processing request: {str(e)}"
        )


@app.post("/api/{user_id}/chatkit")
async def chatkit_endpoint(
    user_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    ChatKit-compatible chat endpoint.

    Accepts OpenAI ChatKit format requests and returns responses
    in the format ChatKit expects.

    Args:
        user_id: User ID from URL path
        request: Raw request object
        session: Database session

    Returns:
        ChatKit-compatible response with choices array
    """
    try:
        # Parse ChatKit request format
        body = await request.json()
        messages = body.get("messages", [])

        if not messages:
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "No message provided."
                    }
                }],
                "error": "No messages in request"
            }

        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "No user message found."
                    }
                }],
                "error": "No user message found"
            }

        # Get or create conversation for this user
        # For ChatKit, we'll use one ongoing conversation per user
        stmt = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).limit(1)
        conversation = session.exec(stmt).first()

        if not conversation:
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Store user message
        user_msg = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content=user_message,
            created_at=datetime.utcnow()
        )
        session.add(user_msg)
        session.commit()

        # Fetch conversation history (last 50 messages for context)
        stmt = select(Message).where(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).limit(50)
        history_messages = session.exec(stmt).all()

        # Build message history for agent
        message_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in history_messages
        ]

        # Run agent
        agent_response = await run_agent(message_history, user_id)

        # Store assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.ASSISTANT,
            content=agent_response["response"],
            created_at=datetime.utcnow()
        )
        session.add(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        # Return ChatKit-compatible response
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": agent_response["response"]
                }
            }],
            "conversation_id": conversation.id,
            "tool_calls": agent_response.get("tool_calls", [])
        }

    except Exception as e:
        print(f"ChatKit endpoint error: {str(e)}")
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"I encountered an error: {str(e)}"
                }
            }],
            "error": str(e)
        }


@app.get("/api/conversations")
async def list_conversations(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    List recent conversations for a user.

    The user_id is automatically extracted from the JWT token.

    Args:
        user_id: User ID extracted from JWT token (injected by dependency)
        session: Database session

    Returns:
        List of recent conversations

    Headers:
        Authorization: Bearer <JWT_TOKEN>
    """
    stmt = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).limit(10)

    conversations = session.exec(stmt).all()

    return {
        "conversations": [
            {
                "id": str(conv.id),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ],
        "count": len(conversations)
    }

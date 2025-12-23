"""
Pydantic schemas for API request and response models.

Defines the contract for the chat endpoint.
"""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Attributes:
        conversation_id: Existing conversation to continue (null for new conversation)
        message: User's natural language message (1-5000 chars)
    """
    conversation_id: Optional[UUID] = Field(
        None,
        description="Conversation to continue (null for new)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message"
    )


class ToolCall(BaseModel):
    """
    Schema for MCP tool invocation details.

    Attributes:
        tool: MCP tool name
        parameters: Tool parameters
        result: Tool execution result
    """
    tool: str = Field(..., description="MCP tool name")
    parameters: dict = Field(..., description="Tool parameters")
    result: dict = Field(..., description="Tool execution result")


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Attributes:
        conversation_id: The conversation ID (new or existing)
        response: AI assistant's natural language response
        tool_calls: List of MCP tools invoked during processing
        error: Error message if request failed (null on success)
    """
    conversation_id: Optional[UUID] = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant response")
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Tools invoked"
    )
    error: Optional[str] = Field(None, description="Error message if failed")

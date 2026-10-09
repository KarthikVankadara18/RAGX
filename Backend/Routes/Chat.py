from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from fastapi.responses import StreamingResponse
from uuid import UUID

from Backend.Services.ChatServices import ChatService
from Backend.Security.Auth import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message"
    )

    session_id: str | None = Field(
        default=None,
        description="Existing conversation session ID"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Message cannot be empty or whitespace."
            )

        return value

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                UUID(value)
            except ValueError:
                raise ValueError("Invalid session ID format.")

        return value

class ChatResponse(BaseModel):

    response: str
    user_id: str
    email: str
    session_id: str
    tools_used: list[str] = Field(
        default_factory=list
    )

@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    print(
        f"Received chat request from user_id: {user_id}, "
        f"session_id: {request.session_id}, "
        f"message: {request.message}"
    )

    service = ChatService(
        user_id=user_id,
        session_id=request.session_id
    )

    result = service.process_message(
        request.message
    )

    return {
        "response": result.get("response", ""),
        "user_id": user_id,
        "email": service.email,
        "session_id": service.session_id,
        "tools_used": result.get("tools_used", [])
    }

@router.post("/stream")
def chat_stream(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    service = ChatService(
        user_id=user_id,
        session_id=request.session_id
    )

    def generate():
        try:
            for chunk in service.agent.run_stream(request.message):
                yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"

        except Exception:
            yield "data: [ERROR] Unable to process the request.\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no-cache",
        }
    )
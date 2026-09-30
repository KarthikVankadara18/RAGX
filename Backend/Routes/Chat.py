from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from Backend.Services.Chat_Services import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        description="User message"
    )

    user_id: str = Field(
        ...,
        min_length=1,
        description="User identifier"
    )

    session_id: str | None = Field(
        default=None,
        description="Existing conversation session ID"
    )

class ChatResponse(BaseModel):

    response: str

    user_id: str

    session_id: str

    tools_used: list[str] = Field(
        default_factory=list
    )

@router.post(
    "",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    try:

        service = ChatService(
            user_id=request.user_id,
            session_id=request.session_id
        )

        result = service.process_message(
            request.message
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Internal server error."
        )
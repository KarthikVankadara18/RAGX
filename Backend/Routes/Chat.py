from fastapi import APIRouter
from pydantic import BaseModel
from Backend.Services.Chat_Services import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    user_id: str
    session_id: str | None = None

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    print(
        f"Received chat request: "
        f"message='{request.message}' "
        f"user_id='{request.user_id}' "
        f"session_id='{request.session_id}'"
    )

    service = ChatService(
        user_id=request.user_id,
        session_id=request.session_id
    )

    result = service.process_message(request.message)

    return result
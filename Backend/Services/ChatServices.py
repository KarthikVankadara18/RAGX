import uuid
from bson import ObjectId

from RAGChatBot.FunctionCalling.FunctionCallingManager import FunctionCallingManager
from RAGChatBot.Memory.PersistentMemory import PersistentMemory

from Backend.Exceptions.Exceptions import (
    BadRequestError,
    AuthorizationError,
    ResourceNotFoundError,
)

class ChatService:

    def __init__(
        self,
        user_id: str,
        session_id: str | None = None
    ):
        self.user_id = user_id
        self.persistent_memory = PersistentMemory()

        user = self.persistent_memory.users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )

        if not user:
            raise ResourceNotFoundError("User not found.")

        self.email = user["email"]
        if session_id:

            existing_session = (
                self.persistent_memory.get_chat_session(
                    user_id=user_id,
                    session_id=session_id
                )
            )

            if not existing_session:
                raise AuthorizationError(
                    "Invalid or unauthorized session."
                )

            self.session_id = session_id

        else:

            self.session_id = str(uuid.uuid4())
            self.persistent_memory.create_chat_session(
                user_id=user_id,
                email=self.email,
                session_id=self.session_id
            )

        self.agent = FunctionCallingManager(
            user_id=user_id,
            email=self.email,
            session_id=self.session_id
        )

    def process_message(self, message: str):

        if not message or not message.strip():
            raise BadRequestError(
                "Message cannot be empty."
            )

        result = self.agent.run(message)

        self.persistent_memory.update_chat_session(
            user_id=self.user_id,
            session_id=self.session_id
        )

        return {
            "response": result.get("answer", ""),
            "user_id": self.user_id,
            "email": self.email,
            "session_id": self.session_id,
            "tools_used": list(
                dict.fromkeys(
                    result.get("state").tools_used
                    if result.get("state")
                    else []
                )
            )
        }
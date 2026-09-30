from RAGChatBot.FunctionCalling.FunctionCallingManager import (
    FunctionCallingManager
)

class ChatService:

    def __init__(
        self,
        user_id: str,
        session_id: str | None = None
    ):

        self.user_id = user_id

        self.agent = FunctionCallingManager(
            user_id=user_id,
            session_id=session_id
        )

        self.session_id = (
            self.agent.session_id
        )

    def process_message(
        self,
        message: str
    ):

        if not message or not message.strip():

            raise ValueError(
                "Message cannot be empty."
            )

        result = self.agent.run(
            message
        )

        answer = ""

        tools_used = []

        if isinstance(result, dict):

            answer = (
                result.get("answer")
                or ""
            )

            state = result.get(
                "state"
            )

            if state is not None:

                tools_used = list(
                    dict.fromkeys(
                        state.tools_used
                    )
                )

        return {
            "response": answer,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tools_used": tools_used
        }
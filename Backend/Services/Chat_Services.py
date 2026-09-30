from RAGChatBot.FunctionCalling.FunctionCallingManager import FunctionCallingManager

class ChatService:

    def __init__(
        self,
        user_id: str,
        session_id: str | None = None
    ):
        self.user_id = user_id
        self.session_id = session_id

        self.agent = FunctionCallingManager(
            user_id=user_id,
            session_id=session_id
        )

    def process_message(self, message: str):

        result = self.agent.run(message)

        print("DEBUG AGENT RESULT TYPE:", type(result))
        print("DEBUG AGENT RESULT:", repr(result))

        answer = ""

        if isinstance(result, dict):
            answer = result.get("answer") or ""

        print("DEBUG FINAL ANSWER:", repr(answer))

        return {
            "response": answer,
            "user_id": self.user_id,
            "session_id": self.session_id
        }
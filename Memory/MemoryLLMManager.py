from groq import Groq

from config import Config

from Memory.ConversationMemory import (
    ConversationMemory
)

from Memory.ConversationSummarizer import (
    ConversationSummarizer
)

from Memory.ContextManager import (
    ContextManager
)

from Memory.PersistentMemory import (
    PersistentMemory
)


class MemoryLLMManager:

    def __init__(
        self,
        session_id
    ):

        print(
            "Memory LLM Manager Initialized"
        )

        if not Config.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=Config.GROQ_API_KEY
        )

        self.model = Config.GROQ_MODEL

        self.persistent_memory = (
            PersistentMemory()
        )

        self.memory = ConversationMemory(
            persistent_memory=(
                self.persistent_memory
            ),
            session_id=session_id,
            max_recent_messages=6
        )

        self.summarizer = (
            ConversationSummarizer()
        )

        self.context_manager = (
            ContextManager(
                max_context_tokens=4000
            )
        )

    def chat(
        self,
        user_message
    ):

        if not user_message.strip():

            raise ValueError(
                "Message cannot be empty."
            )

        self.memory.add_user_message(
            user_message
        )

        messages = (
            self.context_manager
            .build_context(
                self.memory.get_summary(),
                self.memory.get_recent_messages()
            )
        )

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        self.memory.add_assistant_message(
            answer
        )

        if (
            self.memory.message_count()
            > self.memory.max_recent_messages
        ):

            old_messages = (
                self.memory.messages[
                    :-
                    self.memory.max_recent_messages
                ]
            )

            summary = (
                self.summarizer.summarize(
                    self.memory.get_summary(),
                    old_messages
                )
            )

            self.memory.update_summary(
                summary
            )

        return answer
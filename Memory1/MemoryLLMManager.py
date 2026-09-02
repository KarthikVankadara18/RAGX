from groq import Groq
from config import Config

from Memory.ConversationMemory import ConversationMemory
from Memory.ConversationSummarizer import ConversationSummarizer
from Memory.ContextManager import ContextManager
from Memory.PersistentMemory import PersistentMemory
from Memory.LongTermMemoryManager import LongTermMemoryManager


class MemoryLLMManager:

    def __init__(self, user_id, session_id):
        print("Memory LLM Manager Initialized")

        self.user_id = user_id

        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured.")

        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL

        self.persistent_memory = PersistentMemory()

        self.memory = ConversationMemory(
            persistent_memory=self.persistent_memory,
            session_id=session_id,
            max_recent_messages=6,
        )

        self.summarizer = ConversationSummarizer()
        self.long_term_memory = LongTermMemoryManager(self.persistent_memory)
        self.context_manager = ContextManager(max_context_tokens=4000)

    def chat(self, user_message):
        if not user_message.strip():
            raise ValueError("Message cannot be empty.")

        self.memory.add_user_message(user_message)

        long_term_memories = self.long_term_memory.retrieve_memories(
            query=user_message,
            user_id=self.user_id,
            session_id=self.memory.session_id,
            top_k=5,
            scope="user",
            relevance_threshold=0.30,
        )

        if long_term_memories:
            print("\n" + "=" * 60)
            print("RANKED LONG-TERM MEMORIES")
            print("=" * 60)
            for memory in long_term_memories:
                print("Memory:", memory["content"])
                print("Type:", memory["type"])
                print("Importance:", memory["importance"])
                print("Semantic Score:", memory["semantic_score"])
                print("Recency Score:", memory["recency_score"])
                print("Final Score:", memory["final_score"])
                print("Distance:", memory["distance"])
                print()

        messages = self.context_manager.build_context(
            summary=self.memory.get_summary(),
            recent_messages=self.memory.get_recent_messages(),
            long_term_memories=long_term_memories,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        answer = response.choices[0].message.content

        self.memory.add_assistant_message(answer)

        decisions = self.long_term_memory.process_conversation(
            user_id=self.user_id,
            session_id=self.memory.session_id,
            user_message=user_message,
            assistant_message=answer,
        )

        if decisions:
            print("\n" + "=" * 60)
            print("MEMORY DECISIONS")
            print("=" * 60)
            for decision in decisions:
                print("Action:", decision["action"])
                print("Type:", decision["memory_type"])
                print("Memory:", decision["content"])
                print("Importance:", decision["importance"])
                print("ID:", decision["memory_id"])
                print("Reason:", decision["reason"])
                print()

        lifecycle = self.long_term_memory.run_lifecycle(self.user_id)
        if lifecycle["archived"] or lifecycle["forgotten"]:
            print("Lifecycle:", lifecycle)

        if self.memory.message_count() > self.memory.max_recent_messages:
            old_messages = self.memory.messages[:-self.memory.max_recent_messages]
            summary = self.summarizer.summarize(
                self.memory.get_summary(),
                old_messages,
            )
            self.memory.update_summary(summary)

        return answer

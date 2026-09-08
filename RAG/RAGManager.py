from ContextBuilder.ContextOptimizer import ContextOptimizer
from LLM.LLMManager import LLMManager
from Memory.ContextManager import ContextManager
from Memory.ConversationMemory import ConversationMemory
from Memory.ConversationSummarizer import ConversationSummarizer
from Memory.LongTermMemoryManager import LongTermMemoryManager
from Memory.PersistentMemory import PersistentMemory
from PromptBuilder.PromptBuilder import PromptBuilder
from Retrieval.Retrieval import Retriever


class RAGManager:

    def __init__(self, user_id, session_id):
        print("RAG Manager Initialized")

        self.user_id = user_id
        self.persistent_memory = PersistentMemory()
        self.conversation_memory = ConversationMemory(
            persistent_memory=self.persistent_memory,
            session_id=session_id,
            max_recent_messages=6,
        )
        self.summarizer = ConversationSummarizer()
        self.long_term_memory = LongTermMemoryManager(
            self.persistent_memory
        )
        self.context_manager = ContextManager(
            max_context_tokens=4000
        )
        self.retriever = Retriever()
        self.context_optimizer = ContextOptimizer()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMManager()

    def chat(self, user_message, top_k=None):
        if not user_message or not user_message.strip():
            raise ValueError("Message cannot be empty.")

        self.conversation_memory.add_user_message(user_message)

        memories = self.long_term_memory.retrieve_memories(
            query=user_message,
            user_id=self.user_id,
            session_id=self.conversation_memory.session_id,
            top_k=5,
            scope="user",
            relevance_threshold=0.30,
        )

        retrieval_results = self.retriever.retrieve(
            user_message,
            top_k=top_k
        )

        optimized_results = self.context_optimizer.optimize(
            retrieval_results
        )

        if not optimized_results:
            raise ValueError(
                "No usable document context was retrieved."
            )

        document_prompt = self.prompt_builder.build(
            query=user_message,
            context_results=optimized_results,
        )

        memory_messages = self.context_manager.build_context(
            summary=self.conversation_memory.get_summary(),
            recent_messages=[],
            long_term_memories=memories,
        )

        system_content = memory_messages[0]["content"]
        system_content += (
            "\n\nYou must answer the user's question using the "
            "retrieved document context below. User memory can "
            "personalize the response, but it must never override "
            "or invent document facts.\n\n"
            "DOCUMENT CONTEXT:\n"
            + document_prompt["prompt"]
        )

        messages = [
            {
                "role": "system",
                "content": system_content,
            }
        ]

        recent_messages = self.conversation_memory.get_recent_messages()
        if len(recent_messages) > 1:
            messages.extend(recent_messages[:-1])

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        answer = self.llm.generate_response_from_messages(
            messages
        )

        self.conversation_memory.add_assistant_message(answer)

        decisions = self.long_term_memory.process_conversation(
            user_id=self.user_id,
            session_id=self.conversation_memory.session_id,
            user_message=user_message,
            assistant_message=answer,
        )

        lifecycle = self.long_term_memory.run_lifecycle(
            self.user_id
        )

        if self.conversation_memory.message_count() > self.conversation_memory.max_recent_messages:
            old_messages = self.conversation_memory.messages[
                :-self.conversation_memory.max_recent_messages
            ]
            summary = self.summarizer.summarize(
                self.conversation_memory.get_summary(),
                old_messages,
            )
            self.conversation_memory.update_summary(summary)

        return {
            "answer": answer,
            "sources": document_prompt["sources"],
            "memories": memories,
            "memory_decisions": decisions,
            "lifecycle": lifecycle,
            "retrieved_count": len(retrieval_results),
            "optimized_count": len(optimized_results),
        }

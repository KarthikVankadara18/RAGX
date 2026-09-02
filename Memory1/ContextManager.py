class ContextManager:

    def __init__(
        self,
        max_context_tokens=4000
    ):

        print(
            "Context Manager Initialized"
        )

        self.max_context_tokens = (
            max_context_tokens
        )

    def build_context(
        self,
        summary,
        recent_messages,
        long_term_memories=None
    ):

        messages = []

        system_content = """
        You are a helpful AI assistant.

        Use the conversation context and long-term
        memory when relevant.

        Do not mention internal memory systems,
        FAISS, embeddings, or memory retrieval
        unless the user explicitly asks about them.

        Do not assume a memory is relevant simply
        because it exists. Use it only when it helps
        answer the user's current question.
        """
        if long_term_memories:

            system_content += (
                "\n\nRelevant long-term memories:\n"
            )

            for memory in long_term_memories:

                system_content += (
                    f"- {memory['content']}\n"
                )

        if summary:

            system_content += (
                "\n\nConversation summary:\n"
            )

            system_content += summary

        messages.append(
            {
                "role": "system",
                "content": system_content
            }
        )

        messages.extend(
            recent_messages
        )

        return messages

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
    def estimate_tokens(self, text):

        if not text:
            return 0

        return max(
            1,
            len(text) // 4
        )

    def estimate_message_tokens(
        self,
        message
    ):

        content = message.get(
            "content",
            ""
        )

        return self.estimate_tokens(
            content
        )

    def estimate_context_tokens(
        self,
        messages
    ):

        total = 0

        for message in messages:

            total += (
                self.estimate_message_tokens(
                    message
                )
            )

        return total

    def build_context(
        self,
        summary,
        recent_messages
    ):

        context_messages = []

        if summary:

            summary_message = {
                "role": "system",
                "content": (
                    "Conversation memory summary:\n\n"
                    + summary
                )
            }

            context_messages.append(
                summary_message
            )

        current_tokens = (
            self.estimate_context_tokens(
                context_messages
            )
        )

        selected_messages = []

        for message in reversed(
            recent_messages
        ):

            message_tokens = (
                self.estimate_message_tokens(
                    message
                )
            )

            if (
                current_tokens
                + message_tokens
                > self.max_context_tokens
            ):
                break

            selected_messages.insert(
                0,
                message
            )

            current_tokens += (
                message_tokens
            )

        context_messages.extend(
            selected_messages
        )

        return context_messages

    def get_context_stats(
        self,
        messages
    ):

        token_count = (
            self.estimate_context_tokens(
                messages
            )
        )

        return {
            "message_count": len(
                messages
            ),
            "estimated_tokens": token_count,
            "max_tokens": (
                self.max_context_tokens
            ),
            "remaining_tokens": max(
                0,
                self.max_context_tokens
                - token_count
            )
        }
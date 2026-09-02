from groq import Groq
from config import Config


class ConversationSummarizer:

    def __init__(self):

        print(
            "Conversation Summarizer Initialized"
        )

        if not Config.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=Config.GROQ_API_KEY
        )

        self.model = Config.GROQ_MODEL

    def summarize(
        self,
        previous_summary,
        messages
    ):

        if not messages:
            return previous_summary

        conversation_text = "\n".join(
            [
                (
                    f"{message['role']}: "
                    f"{message['content']}"
                )
                for message in messages
            ]
        )

        prompt = f"""
                You are a conversation memory summarizer.

                Your job is to create a concise factual summary
                of the conversation.

                Preserve important information such as:

                - User identity or name
                - User preferences
                - User goals
                - Important facts
                - Projects
                - Decisions
                - Important context
                - Questions already discussed

                Do not invent information.

                Previous summary:
                {previous_summary or "No previous summary."}

                New conversation:
                {conversation_text}

                Create an updated summary that combines the
                previous summary with the new conversation.
                """

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        summary = (
            response
            .choices[0]
            .message
            .content
        )

        return summary.strip()

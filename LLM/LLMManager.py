from groq import Groq
from config import Config

class LLMManager:
    
    def __init__(self):
        print("LLM Manager Initialized")

        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in the configuration.")

        self.client= Groq(
            api_key=Config.GROQ_API_KEY,
        )
        self.model= Config.GROQ_MODEL

    def generate_response(self, prompt):
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response= (self.client.chat.completions.create(
            model= self.model,
            messages= [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=(
                Config.GROQ_TEMPERATURE
                ),
            max_completion_tokens=(
                Config.GROQ_MAX_TOKENS
                )
            )
        )
        answer = (
            response.choices[0].message.content
        )

        if not answer:
            raise ValueError(
                "LLM returned an empty response."
            )

        return answer.strip()
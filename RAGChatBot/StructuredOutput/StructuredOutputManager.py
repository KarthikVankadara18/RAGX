import json

from groq import Groq
from config import Config
from StructuredOutput.Schemas import CandidateAnalysis


class StructuredOutputManager:
    def __init__(self):
        print("StructuredOutputManager initialized")

        if not Config.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=Config.GROQ_API_KEY
        )

        self.model = Config.GROQ_MODEL

    def analyze_candidate(self, candidate_text):

        if not candidate_text.strip():
            raise ValueError(
                "Candidate text cannot be empty."
            )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant "
                        "that analyzes candidate "
                        "profiles."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze the following "
                        "candidate profile and "
                        "extract the requested "
                        "information.\n\n"
                        f"{candidate_text}"
                    )
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "candidate_analysis",
                    "schema": CandidateAnalysis.model_json_schema()
                }
            },
            temperature=0
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Structured output response was empty."
            )

        try:
            result = CandidateAnalysis.model_validate(
                json.loads(content)
            )
        except Exception as exc:
            raise ValueError(
                "Structured output parsing failed."
            ) from exc

        return result

from groq import Groq
from pydantic import BaseModel, Field
from typing import List
from config import Config
import json


class MemoryItem(BaseModel):

    content: str = Field(
        description=(
            "A concise factual memory that "
            "may be useful in future conversations."
        )
    )

    memory_type: str = Field(
        description=(
            "Type of memory such as "
            "identity, preference, project, "
            "goal, skill, technology, "
            "personal_fact, constraint, or plan."
        )
    )

    importance: int = Field(
        ge=1,
        le=5,
        description=(
            "Importance of this memory for future "
            "conversations. 1 is trivial and "
            "5 is critical."
        )
    )


class MemoryExtraction(BaseModel):

    memories: List[MemoryItem] = Field(
        default_factory=list
    )


class MemoryExtractor:

    def __init__(self):

        print(
            "Memory Extractor Initialized"
        )

        if not Config.GROQ_API_KEY:

            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=Config.GROQ_API_KEY
        )

        self.model = Config.GROQ_MODEL

    def extract(
        self,
        user_message,
        assistant_message
    ):

        prompt = f"""
You are a long-term memory extraction system.

Analyze the conversation below and identify ONLY
information that would be useful to remember
in future conversations.

Store things such as:

- User identity
- User preferences
- User goals
- Projects
- Skills
- Important personal facts
- Technology choices
- Long-term plans
- Constraints that may affect future responses

Use these memory types when appropriate:

- identity
- preference
- goal
- project
- skill
- technology
- personal_fact
- constraint
- plan
- fact

Assign importance from 1 to 5:

1 = trivial or rarely useful
2 = mildly useful
3 = useful general fact
4 = highly useful long-term information
5 = critical identity, goal, project, preference, or constraint

Do NOT store:

- Temporary questions
- General explanations
- Facts that only describe the assistant
- Trivial conversational statements
- Information that is not useful later
- Information invented by the assistant

Only extract information explicitly supported
by the user's message.

Classify statements by what they actually express:
- A statement about building or using a named project is a project or technology memory.
- Do not classify project activity as a goal unless the user explicitly states an objective or desired outcome.
- A preference should describe how the user wants future responses or interactions handled.
- A goal should describe something the user explicitly wants to achieve.

Do not invent information.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "memories": [
        {{
            "content": "memory text",
            "memory_type": "identity",
            "importance": 5
        }}
    ]
}}

If there is nothing worth remembering, return:

{{
    "memories": []
}}

USER:
{user_message}

ASSISTANT:
{assistant_message}
"""

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    }
                ],
                temperature=0
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        try:

            data = json.loads(
                content
            )

            result = (
                MemoryExtraction
                .model_validate(
                    data
                )
            )

            return result.memories

        except Exception as e:

            print(
                "Memory extraction parsing failed:",
                e
            )

            print(
                "Raw model response:",
                content
            )

            return []

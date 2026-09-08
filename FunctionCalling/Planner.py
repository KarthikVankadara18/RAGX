import json

from groq import Groq
from config import Config


class Planner:

    VALID_ACTIONS = {
        "MEMORY_LOOKUP",
        "DOCUMENT_LOOKUP",
        "CALCULATION",
    }

    ACTION_ALIASES = {
        "calculator": "CALCULATION",
        "search_memory": "MEMORY_LOOKUP",
        "search_documents": "DOCUMENT_LOOKUP",
    }

    def __init__(self):
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured.")

        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL

    def create_plan(self, user_query: str, tool_definitions: list):

        if not user_query or not user_query.strip():
            raise ValueError("User query cannot be empty.")

        system_prompt = """
You are the planning component of an AI agent.

Your job is ONLY to create a plan.
You are NOT executing tools.

Return ONLY valid JSON.

The JSON must have this exact structure:

{
    "steps": [
        {
            "step": 1,
            "action": "MEMORY_LOOKUP",
            "query": "information to retrieve",
            "reason": "why this action is needed"
        }
    ]
}

Available actions:

1. MEMORY_LOOKUP

Use for information about the user:

- projects
- goals
- preferences
- skills
- personal facts
- previous conversations


2. DOCUMENT_LOOKUP

Use for information that must be retrieved from uploaded documents.


3. CALCULATION

Use for exact mathematical calculations.


IMPORTANT RULES:

- The field MUST be called "action".
- Never use the field "tool".
- MEMORY_LOOKUP is the only valid action for user-specific memory.
- DOCUMENT_LOOKUP is the only valid action for uploaded documents.
- CALCULATION is the only valid action for mathematics.
- Never output "calculator" as an action.
- Never output "search_memory" as an action.
- Never output "search_documents" as an action.
- Do not execute anything.
- Do not produce function calls.
- If multiple actions are required, create multiple ordered steps.
- Each step must have a step number, action, query, and reason.
- Keep the plan minimal.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            temperature=0,
            max_completion_tokens=Config.GROQ_MAX_TOKENS,
            response_format={
                "type": "json_object"
            }
        )

        content = response.choices[0].message.content

        if not content:
            return {"steps": []}

        try:
            plan = json.loads(content)
        except json.JSONDecodeError:
            return {"steps": []}

        if not isinstance(plan, dict):
            return {"steps": []}

        if not isinstance(plan.get("steps"), list):
            plan["steps"] = []

        normalized_steps = []

        for index, step in enumerate(plan["steps"], start=1):

            if not isinstance(step, dict):
                continue

            action = step.get("action")

            if action is None:
                action = step.get("tool")

            if isinstance(action, str):
                action = self.ACTION_ALIASES.get(
                    action,
                    action.upper()
                )

            if action not in self.VALID_ACTIONS:
                continue

            query = step.get("query")

            if not query:
                continue

            normalized_steps.append({
                "step": index,
                "action": action,
                "query": query,
                "reason": step.get(
                    "reason",
                    "Required to answer the user's query."
                )
            })

        plan["steps"] = normalized_steps

        return plan
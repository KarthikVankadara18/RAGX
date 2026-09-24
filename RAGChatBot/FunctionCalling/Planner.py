import json

from groq import Groq
from config import Config


class Planner:

    VALID_ACTIONS = {
        "MEMORY_LOOKUP",
        "MEMORY_SAVE",
        "MEMORY_UPDATE",
        "MEMORY_FORGET",
        "DOCUMENT_LOOKUP",
        "CALCULATION",
    }

    ACTION_ALIASES = {
        "calculator": "CALCULATION",
        "search_memory": "MEMORY_LOOKUP",
        "search_documents": "DOCUMENT_LOOKUP",
        "save_memory": "MEMORY_SAVE",
        "update_memory": "MEMORY_UPDATE",
        "forget_memory": "MEMORY_FORGET",
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

        Use when the user asks for information about themselves, their projects,
        goals, preferences, skills, technologies, personal facts, or previous
        conversations.

        2. MEMORY_SAVE

        Use when the user explicitly provides new durable information about
        themselves that should be remembered.

        Examples:

        "I am learning MCP."
        "My project is called RAGX-Enterprise."
        "I prefer Python."

        Do NOT save ordinary questions or temporary conversation content.

        3. MEMORY_UPDATE

        Use when the user explicitly changes previously stored information.

        Examples:

        "My project is now called RAGX-Next."
        "I no longer use React."
        "My preferred language has changed to Python."

        IMPORTANT:
        If the existing memory must be identified first, use MEMORY_LOOKUP before
        MEMORY_UPDATE.

        4. MEMORY_FORGET

        Use when the user explicitly asks to forget or remove previously stored
        information.

        IMPORTANT:
        If the memory_id is not already known, use MEMORY_LOOKUP first.

        5. DOCUMENT_LOOKUP

        Use for information that must be retrieved from uploaded documents
        or the RAGX knowledge base.

        6. CALCULATION

        Use for exact mathematical calculations.

        IMPORTANT RULES:

        - The field MUST be called "action".
        - Never use the field "tool".
        - Never output function calls.
        - Never output calculator, search_memory, search_documents,
        save_memory, update_memory, or forget_memory as actions.
        - Use only the six actions defined above.
        - Create multiple ordered steps when multiple actions are required.
        - Keep the plan minimal.
        - Each step must contain step, action, query, and reason.
        - Do not execute anything.
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
            response_format={"type": "json_object"}
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
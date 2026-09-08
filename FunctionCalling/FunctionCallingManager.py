import json

from groq import Groq
from config import Config

from FunctionCalling.AgentState import AgentState
from FunctionCalling.RuntimeContext import RuntimeContext
from FunctionCalling.ToolRegistry import ToolRegistry
from FunctionCalling.Planner import Planner

from FunctionCalling.Tools import (
    search_documents,
    calculator,
    search_memory,
)

from Memory.PersistentMemory import PersistentMemory
from Memory.LongTermMemoryManager import LongTermMemoryManager


class FunctionCallingManager:

    def __init__(
        self,
        user_id="default_user",
        session_id=None,
    ):
        print("Agent initialized")

        if not Config.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=Config.GROQ_API_KEY
        )

        self.model = Config.GROQ_MODEL
        self.max_iterations = 5

        self.runtime_context = RuntimeContext(
            user_id=user_id,
            session_id=session_id,
        )

        self.persistent_memory = PersistentMemory()

        self.long_term_memory = LongTermMemoryManager(
            self.persistent_memory
        )

        self.tool_registry = ToolRegistry()

        self._register_tools()

        self.tools = (
            self.tool_registry.get_definitions()
        )

        self.planner = Planner()

    # ==========================================================
    # TOOL REGISTRATION
    # ==========================================================

    def _register_tools(self):

        self.tool_registry.register(
            name="search_documents",
            function=search_documents,
            description=(
                "Search the uploaded RAGX documents "
                "for information relevant to the "
                "user's question."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The question or information "
                            "to search for in the documents."
                        ),
                    }
                },
                "required": ["query"],
            },
        )

        self.tool_registry.register(
            name="calculator",
            function=calculator,
            description=(
                "Perform mathematical calculations."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Mathematical expression "
                            "such as 25 * 18."
                        ),
                    }
                },
                "required": ["expression"],
            },
        )

        self.tool_registry.register(
            name="search_memory",
            function=self._search_memory,
            description=(
                "Search the user's long-term memory "
                "for personal information, projects, "
                "preferences, goals, skills, or facts "
                "previously stored about the user."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The information to search "
                            "for in the user's memory."
                        ),
                    }
                },
                "required": ["query"],
            },
        )

    # ==========================================================
    # MEMORY SEARCH
    # ==========================================================

    def _search_memory(self, query: str):

        result = search_memory(
            query=query,
            long_term_memory=self.long_term_memory,
            user_id=self.runtime_context.user_id,
            session_id=self.runtime_context.session_id,
        )

        print()
        print("=" * 60)
        print("MEMORY SEARCH RESULTS")
        print("=" * 60)

        for memory in result:

            print(
                "Memory:",
                memory.get("content")
            )

            print(
                "Type:",
                memory.get("type")
            )

            print(
                "Importance:",
                memory.get("importance")
            )

            print(
                "Semantic Score:",
                memory.get("semantic_score")
            )

            print(
                "Final Score:",
                memory.get("final_score")
            )

            print()

        return result

    # ==========================================================
    # PLANNING TOOL MAP
    # ==========================================================

    PLANNING_TOOL_MAP = {
        "MEMORY_LOOKUP": "search_memory",
        "DOCUMENT_LOOKUP": "search_documents",
        "CALCULATION": "calculator",
    }

    # ==========================================================
    # PLAN EXECUTION
    # ==========================================================

    def execute_plan(self, plan):

        if not plan or "steps" not in plan:
            raise ValueError("Invalid plan.")

        execution_results = []

        for step in plan["steps"]:

            action = step.get("action")

            if action not in self.PLANNING_TOOL_MAP:
                raise ValueError(
                    f"Unknown planning action: {action}"
                )

            tool_name = self.PLANNING_TOOL_MAP[action]

            tool = self.tool_registry.get_tool(
                tool_name
            )

            if tool is None:
                raise ValueError(
                    f"Tool not found: {tool_name}"
                )

            query = step.get("query")

            if not query:
                raise ValueError(
                    f"Missing query for action: {action}"
                )

            if action == "CALCULATION":

                arguments = {
                    "expression": query
                }

            else:

                arguments = {
                    "query": query
                }

            print()
            print("=" * 60)
            print("PLAN STEP EXECUTION")
            print("=" * 60)

            print("Action :", action)
            print("Tool   :", tool_name)
            print("Query  :", query)

            try:

                result = tool(**arguments)

                execution_results.append(
                    {
                        "step": step.get("step"),
                        "action": action,
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": result,
                    }
                )

                print("Result :", result)

            except Exception as exc:

                result = {
                    "error": str(exc)
                }

                execution_results.append(
                    {
                        "step": step.get("step"),
                        "action": action,
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": result,
                    }
                )

                print("Error  :", exc)

        return execution_results

    # ==========================================================
    # ANSWER SYNTHESIS
    # ==========================================================

    def synthesize_answer(
        self,
        user_query: str,
        plan: dict,
        execution_results: list,
    ):

        prompt = f"""
You are the final answer component of an AI agent.

Answer the user's question using ONLY the information
returned by the executed tools.

USER QUESTION:
{user_query}

PLAN:
{json.dumps(
    plan,
    indent=2,
    ensure_ascii=False
)}

TOOL RESULTS:
{json.dumps(
    execution_results,
    indent=2,
    ensure_ascii=False
)}

RULES:

- Give a direct and useful answer.
- Do not mention internal planning or execution unless necessary.
- Do not mention tool names.
- Do not invent information.
- If a tool result contains the answer, use it.
- If multiple tool results exist, combine them appropriately.
- For calculations, provide the exact result.
- If the available results are insufficient, clearly say so.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise answer "
                        "synthesis component."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_completion_tokens=Config.GROQ_MAX_TOKENS,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise ValueError(
                "LLM returned an empty synthesized answer."
            )

        return answer.strip()

    # ==========================================================
    # PLANNED AGENT
    # ==========================================================

    def run_planned(self, user_query: str):

        if not user_query or not user_query.strip():
            raise ValueError("Query cannot be empty.")

        state = AgentState(
            user_query=user_query
        )

        try:

            print()
            print("=" * 60)
            print("PLANNING")
            print("=" * 60)

            plan = self.planner.create_plan(
                user_query=user_query,
                tool_definitions=self.tools,
            )

            print("Plan:")

            print(
                json.dumps(
                    plan,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            if not plan.get("steps"):

                state.fail(
                    "Planner returned an empty plan."
                )

                return {
                    "answer": None,
                    "plan": plan,
                    "execution_results": [],
                    "state": state,
                }

            print()
            print("=" * 60)
            print("EXECUTING PLAN")
            print("=" * 60)

            execution_results = self.execute_plan(
                plan
            )

            for result in execution_results:

                state.add_tool_result(
                    tool_name=result["tool"],
                    arguments=result["arguments"],
                    result=result["result"],
                )

            state.increment_iteration()

            print()
            print("=" * 60)
            print("SYNTHESIZING ANSWER")
            print("=" * 60)

            answer = self.synthesize_answer(
                user_query=user_query,
                plan=plan,
                execution_results=execution_results,
            )

            state.finish()

            print()
            print("FINAL ANSWER")
            print("=" * 60)
            print(answer)

            return {
                "answer": answer,
                "plan": plan,
                "execution_results": execution_results,
                "state": state,
            }

        except Exception as exc:

            state.fail(str(exc))

            print()
            print("PLANNED AGENT FAILED")
            print(str(exc))

            return {
                "answer": None,
                "plan": None,
                "execution_results": [],
                "state": state,
            }

    # ==========================================================
    # REACTIVE AGENT
    # ==========================================================

    def run(self, user_query):

        if not user_query or not user_query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        state = AgentState(
            user_query=user_query
        )

        state.messages = [

            {
                "role": "system",
                "content": (
                    """
You are an intelligent AI agent.

Your job is to answer the user's request accurately
using the available tools when necessary.

AVAILABLE TOOLS:

1. search_memory

Use this FIRST when the user asks about themselves,
their projects, goals, preferences, skills,
personal facts, previous conversations,
or information previously remembered about them.

Examples:

- What project am I building?
- What are my goals?
- What technologies am I using?
- What do you remember about me?

2. search_documents

Use this when the user explicitly asks about information
contained in the uploaded documents or asks a knowledge
question that requires the document collection.

Examples:

- What does the uploaded document say about RAG?
- Explain hybrid search from the documents.
- According to the PDF, what are the challenges of RAG?

3. calculator

Use this when an exact mathematical calculation is required.

IMPORTANT TOOL RULES:

- Choose the tool based on the SOURCE of information required.
- Personal/user-specific information belongs to search_memory.
- Uploaded-document information belongs to search_documents.
- Mathematical calculations belong to calculator.
- Do not use search_documents to answer questions about the user.
- Do not use search_memory for general document knowledge.
- Do not call the same tool repeatedly for the same information
  unless the previous result was clearly insufficient.
- After receiving sufficient information from a tool,
  stop calling tools and provide the final answer.
- You may use multiple different tools when the user's question
  genuinely requires multiple sources.
- Do not use tools unnecessarily.
- Never invent personal information that was not returned
  by search_memory.
- Never invent document information that was not returned
  by search_documents.
"""
                ),
            },

            {
                "role": "user",
                "content": user_query,
            }

        ]

        try:

            for _ in range(
                self.max_iterations
            ):

                state.increment_iteration()

                print()
                print("=" * 60)
                print(
                    f"AGENT ITERATION "
                    f"{state.iteration}"
                )
                print("=" * 60)

                response = (
                    self.client
                    .chat
                    .completions
                    .create(
                        model=self.model,
                        messages=state.messages,
                        tools=self.tools,
                        tool_choice="auto",
                    )
                )

                message = (
                    response
                    .choices[0]
                    .message
                )

                if not message.tool_calls:

                    state.finish()

                    print()
                    print("AGENT FINISHED")

                    return {
                        "answer": message.content,
                        "state": state,
                    }

                state.messages.append(
                    message
                )

                for tool_call in (
                    message.tool_calls
                ):

                    function_name = (
                        tool_call
                        .function
                        .name
                    )

                    print()
                    print("=" * 60)
                    print("TOOL REQUESTED")
                    print("-" * 60)

                    print(
                        "Function :",
                        function_name
                    )

                    tool = (
                        self.tool_registry
                        .get_tool(
                            function_name
                        )
                    )

                    if tool is None:

                        error_message = (
                            f"Unknown tool: "
                            f"{function_name}"
                        )

                        print(
                            error_message
                        )

                        state.fail(
                            error_message
                        )

                        return {
                            "answer": None,
                            "state": state,
                        }

                    try:

                        arguments = json.loads(
                            tool_call
                            .function
                            .arguments
                        )

                    except json.JSONDecodeError as exc:

                        error_message = (
                            "Invalid tool arguments: "
                            f"{exc}"
                        )

                        print(
                            error_message
                        )

                        state.fail(
                            error_message
                        )

                        return {
                            "answer": None,
                            "state": state,
                        }

                    print(
                        "Arguments:",
                        arguments
                    )

                    try:

                        result = tool(
                            **arguments
                        )

                        state.add_tool_result(
                            tool_name=function_name,
                            arguments=arguments,
                            result=result,
                        )

                        print(
                            "\nTool executed successfully."
                        )

                    except Exception as exc:

                        result = {
                            "error": str(exc)
                        }

                        state.add_tool_result(
                            tool_name=function_name,
                            arguments=arguments,
                            result=result,
                        )

                        print(
                            "\nTool execution failed:"
                        )

                        print(
                            str(exc)
                        )

                    state.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": (
                                tool_call.id
                            ),
                            "content": json.dumps(
                                result,
                                ensure_ascii=False,
                            ),
                        }
                    )

            error_message = (
                "Agent exceeded maximum "
                f"iterations ({self.max_iterations})."
            )

            state.fail(
                error_message
            )

            return {
                "answer": None,
                "state": state,
            }

        except Exception as exc:

            state.fail(
                str(exc)
            )

            return {
                "answer": None,
                "state": state,
            }
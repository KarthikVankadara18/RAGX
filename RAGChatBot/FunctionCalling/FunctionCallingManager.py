import asyncio
import json

from groq import Groq
from config import Config

from FunctionCalling.AgentState import AgentState
from FunctionCalling.RuntimeContext import RuntimeContext
from FunctionCalling.ToolRegistry import ToolRegistry
from FunctionCalling.Planner import Planner
from FunctionCalling.RecoveryManager import RecoveryManager
from FunctionCalling.SecurityManager import SecurityManager

from FunctionCalling.Tools import (
    search_documents,
    calculator,
    search_memory,
)

from mcp import Client, StdioServerParameters

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

        self.tool_registry = ToolRegistry()

        self.security_manager = SecurityManager(
            self.runtime_context
        )

        self._register_tools()

        self.tools = (
            self.tool_registry.get_definitions()
        )

        self.planner = Planner()

        self.recovery_manager = RecoveryManager()

        self.mcp_server = StdioServerParameters(
            command="uv",
            args=["run", "MCP/Server.py"],
        )

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

    def _search_memory(self, query: str):

        result = search_memory(
            query=query,
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

    async def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):

        async with Client(self.mcp_server) as client:

            result = await client.call_tool(
                tool_name,
                arguments,
            )

            return self._parse_mcp_result(result)

    @staticmethod
    def _parse_mcp_result(result):

        if not result.content:
            return []

        parsed = []

        for item in result.content:

            text = getattr(
                item,
                "text",
                None,
            )

            if text is None:
                parsed.append(item)
                continue

            try:
                parsed.append(
                    json.loads(text)
                )

            except json.JSONDecodeError:
                parsed.append(text)

        return parsed

    def _mcp_memory_save(self, content):

        return asyncio.run(
            self._call_mcp_tool(
                "save_user_memory",
                {
                    "content": content,
                    "memory_type": "fact",
                    "user_id": self.runtime_context.user_id,
                    "session_id": self.runtime_context.session_id,
                    "importance": 3,
                },
            )
        )

    def _mcp_memory_update(
        self,
        memory_id,
        content,
    ):

        return asyncio.run(
            self._call_mcp_tool(
                "update_user_memory",
                {
                    "memory_id": memory_id,
                    "content": content,
                    "user_id": self.runtime_context.user_id,
                },
            )
        )

    def _mcp_memory_forget(
        self,
        memory_id,
    ):

        return asyncio.run(
            self._call_mcp_tool(
                "forget_user_memory",
                {
                    "memory_id": memory_id,
                    "user_id": self.runtime_context.user_id,
                },
            )
        )

    def _mcp_document_lookup(self, query):

        return asyncio.run(
            self._call_mcp_tool(
                "search_rag",
                {
                    "query": query,
                },
            )
        )

    def _mcp_calculation(self, expression):

        return asyncio.run(
            self._call_mcp_tool(
                "calculate",
                {
                    "expression": expression,
                },
            )
        )
    
    PLANNING_TOOL_MAP = {
        "MEMORY_LOOKUP": "search_memory",
        "DOCUMENT_LOOKUP": "search_documents",
        "CALCULATION": "calculator",
    }


    def execute_single_step(self, step, state):

        action = step.get("action")
        query = step.get("query")

        authorization = self.security_manager.authorize_action(action)

        if not authorization["allowed"]:
            raise PermissionError(authorization["reason"])

        if not action:
            raise ValueError("Planning step has no action.")

        if not query:
            raise ValueError(
                f"Missing query for action: {action}"
            )

        print()
        print("=" * 60)
        print("PLAN STEP EXECUTION")
        print("=" * 60)

        print("Action :", action)
        print("Query  :", query)

        tool_name = action

        try:

            if action == "MEMORY_LOOKUP":

                print("Tool   : search_user_memory")

                tool_name = "search_user_memory"

                result = asyncio.run(
                    self._call_mcp_tool(
                        tool_name,
                        {
                            "query": query,
                            "user_id": self.runtime_context.user_id,
                            "session_id": self.runtime_context.session_id,
                        },
                    )
                )

            elif action == "MEMORY_SAVE":

                print("Tool   : save_user_memory")

                tool_name = "save_user_memory"

                result = asyncio.run(
                    self._call_mcp_tool(
                        tool_name,
                        {
                            "content": query,
                            "memory_type": "fact",
                            "user_id": self.runtime_context.user_id,
                            "session_id": self.runtime_context.session_id,
                            "importance": 3,
                        },
                    )
                )

            elif action == "MEMORY_UPDATE":

                print("Tool   : update_user_memory")

                tool_name = "update_user_memory"

                memory_id = self._find_previous_memory_id(
                    state.tool_results
                )

                if not memory_id:
                    result = {
                        "error": "No memory ID found for update."
                    }
                else:
                    result = asyncio.run(
                        self._call_mcp_tool(
                            tool_name,
                            {
                                "memory_id": memory_id,
                                "content": query,
                                "user_id": self.runtime_context.user_id,
                            },
                        )
                    )

            elif action == "MEMORY_FORGET":

                print("Tool   : forget_user_memory")

                tool_name = "forget_user_memory"

                memory_id = self._find_previous_memory_id(
                    state.tool_results
                )

                if not memory_id:
                    result = {
                        "error": "No memory ID found for forget."
                    }
                else:
                    result = asyncio.run(
                        self._call_mcp_tool(
                            tool_name,
                            {
                                "memory_id": memory_id,
                                "user_id": self.runtime_context.user_id,
                            },
                        )
                    )

            elif action == "DOCUMENT_LOOKUP":

                print("Tool   : search_rag")

                tool_name = "search_rag"

                result = asyncio.run(
                    self._call_mcp_tool(
                        tool_name,
                        {
                            "query": query,
                        },
                    )
                )

            elif action == "CALCULATION":

                print("Tool   : calculate")

                tool_name = "calculate"

                result = asyncio.run(
                    self._call_mcp_tool(
                        tool_name,
                        {
                            "expression": query,
                        },
                    )
                )

            else:
                raise ValueError(
                    f"Unknown planning action: {action}"
                )

            execution_result = {
                "step": step.get("step"),
                "action": action,
                "tool": tool_name,
                "arguments": {
                    "query": query
                },
                "result": result,
            }

            state.add_tool_result(
                tool_name=tool_name,
                arguments={
                    "query": query
                },
                result=result,
            )

            print("Result :", result)

            return execution_result

        except Exception as exc:

            print("Error  :", exc)

            error_result = {
                "error": str(exc)
            }

            state.add_tool_result(
                tool_name=tool_name,
                arguments={
                    "query": query
                },
                result=error_result,
            )

            raise

    def execute_plan(self, plan, state):

        if not plan or "steps" not in plan:
            raise ValueError("Invalid plan.")
        state.set_plan(plan["steps"])
        execution_results = []

        while True:

            current_step = state.get_current_step()

            if current_step is None:
                break

            while state.step_attempts < state.max_step_retries + 1:

                state.start_step()
                state.increment_iteration()

                if state.status == "failed":
                    raise RuntimeError(state.error)

                try:

                    result = self.execute_single_step(
                        current_step,
                        state
                    )
                    execution_results.append(result)
                    state.move_to_next_step()

                    break

                except Exception as exc:

                    print()
                    print(
                        f"Step {state.current_step + 1} "
                        f"failed on attempt "
                        f"{state.step_attempts}: {exc}"
                    )

                    if state.step_attempts >= state.max_step_retries + 1:

                        state.fail(
                            f"Step failed after "
                            f"{state.step_attempts} attempts: "
                            f"{exc}"
                        )

                        raise
            else:

                state.fail(
                    "Maximum retries exceeded."
                )
                raise RuntimeError(state.error)

        return execution_results

    @staticmethod
    def _find_previous_memory_id(
        execution_results
    ):

        for execution in reversed(
            execution_results
        ):

            result = execution.get(
                "result"
            )

            if not result:
                continue

            if isinstance(result, list):

                for item in result:

                    if isinstance(item, dict):

                        if item.get("memory_id"):
                            return item["memory_id"]

            elif isinstance(result, dict):

                if result.get("memory_id"):
                    return result["memory_id"]

        return None

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

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        if not answer:
            raise ValueError(
                "LLM returned an empty synthesized answer."
            )

        return answer.strip()

    def run_planned(self, user_query):

        state = AgentState(
            user_query=user_query,
            max_iterations=self.max_iterations,
        )

        execution_results = []
        plan = None

        try:

            plan = self.planner.create_plan(
                user_query,
                self.tools
            )

            print()
            print("Plan:")
            print(
                json.dumps(
                    plan,
                    indent=2,
                    ensure_ascii=False
                )
            )

            execution_results = self.execute_plan(
                plan,
                state
            )

            state.finish()

            answer = self.synthesize_answer(
                user_query,
                plan,
                execution_results
            )

            return {
                "answer": answer,
                "plan": plan,
                "execution": execution_results,
                "state": state,
            }

        except Exception as exc:

            state.fail(str(exc))

            return {
                "answer": f"Agent failed: {exc}",
                "plan": plan,
                "execution": execution_results,
                "state": state,
            }
            
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

    def recover_from_failure(self, failed_step, state):

        error = state.error

        print()
        print("=" * 60)
        print("AGENT RECOVERY")
        print("=" * 60)

        print("Failed action :", failed_step.get("action"))
        print("Error         :", error)

        if not self.recovery_manager.can_recover(
            failed_step,
            error,
        ):
            print("Recovery      : Not available")
            return False

        recovery_step = (
            self.recovery_manager.create_recovery_step(
                failed_step
            )
        )

        if not recovery_step:
            return False

        print(
            "Recovery action :",
            recovery_step["action"]
        )

        print(
            "Recovery query  :",
            recovery_step["query"]
        )

        try:

            result = self.execute_single_step(
                recovery_step,
                state
            )

            print(
                "Recovery result :",
                result
            )

            return True

        except Exception as exc:

            print(
                "Recovery failed :",
                exc
            )

            return False
        
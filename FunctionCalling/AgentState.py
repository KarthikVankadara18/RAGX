from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentState:

    user_query: str
    messages: list = field(
        default_factory=list
    )
    iteration: int = 0
    tools_used: list = field(
        default_factory=list
    )
    tool_results: list = field(
        default_factory=list
    )
    status: str = "running"
    error: str | None = None

    def add_tool_result(
        self,
        tool_name: str,
        arguments: dict,
        result: Any
    ):

        self.tools_used.append(
            tool_name
        )

        self.tool_results.append(
            {
                "tool": tool_name,
                "arguments": arguments,
                "result": result
            }
        )

    def increment_iteration(self):

        self.iteration += 1

    def finish(self):

        self.status = "completed"

    def fail(self, error: str):

        self.status = "failed"

        self.error = error
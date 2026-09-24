from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentState:
    user_query: str

    plan: list = field(default_factory=list)
    current_step: int = 0

    messages: list = field(default_factory=list)

    iteration: int = 0
    max_iterations: int = 5

    step_attempts: int = 0
    max_step_retries: int = 2

    tools_used: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)

    status: str = "running"
    error: str | None = None
    last_error: str | None = None
    failed_step: dict | None = None

    def set_plan(self, plan):
        self.plan = plan
        self.current_step = 0
        self.step_attempts = 0

    def get_current_step(self):
        if self.current_step >= len(self.plan):
            return None

        return self.plan[self.current_step]

    def start_step(self):
        self.step_attempts += 1

    def move_to_next_step(self):
        self.current_step += 1
        self.step_attempts = 0

    def add_tool_result(
        self,
        tool_name: str,
        arguments: dict,
        result: Any,
    ):
        self.tools_used.append(tool_name)

        self.tool_results.append({
            "step": self.current_step + 1,
            "attempt": self.step_attempts,
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
        })

    def increment_iteration(self):
        self.iteration += 1

        if self.iteration >= self.max_iterations:
            self.status = "failed"
            self.error = "Maximum agent iterations exceeded."

    def finish(self):
        self.status = "completed"

    def fail(self, error: str, step=None):
        self.status = "failed"
        self.error = error
        self.last_error = error
        self.failed_step = step

    def recover(self):
        self.status = "running"
        self.error = None
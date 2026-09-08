from dataclasses import dataclass

@dataclass
class RuntimeContext:
    user_id: str
    session_id: str | None = None
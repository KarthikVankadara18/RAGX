from difflib import SequenceMatcher
import json

from groq import Groq
from pydantic import BaseModel

from config import Config


class MemoryDecisionResult(BaseModel):
    action: str = "IGNORE"
    memory_id: str | None = None
    content: str | None = None
    memory_type: str | None = None
    importance: int | None = None
    reason: str = ""


class MemoryDecision:

    def __init__(self):
        print("Memory Decision Initialized")
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured.")
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL

    @staticmethod
    def _normalize(text):
        return " ".join(str(text).lower().strip().split())

    @classmethod
    def is_near_duplicate(cls, candidate, existing, threshold=0.88):
        a = cls._normalize(candidate)
        b = cls._normalize(existing)
        if not a or not b:
            return False
        if a == b:
            return True
        return SequenceMatcher(None, a, b).ratio() >= threshold

    @staticmethod
    def _valid_importance(value, fallback):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return fallback
        return max(1, min(5, value))

    def _fallback(self, related_memories, reason):
        existing = related_memories[0]
        return MemoryDecisionResult(
            action="IGNORE",
            memory_id=existing["memory_id"],
            content=existing["content"],
            memory_type=existing["type"],
            importance=existing["importance"],
            reason=reason,
        )

    def decide(self, candidate, related_memories):
        if not related_memories:
            return MemoryDecisionResult(
                action="ADD",
                content=candidate.content,
                memory_type=candidate.memory_type,
                importance=candidate.importance,
                reason="No related active memory found.",
            )

        for existing in related_memories:
            if self.is_near_duplicate(candidate.content, existing["content"]):
                return MemoryDecisionResult(
                    action="IGNORE",
                    memory_id=existing["memory_id"],
                    content=existing["content"],
                    memory_type=existing["type"],
                    importance=existing["importance"],
                    reason="Duplicate or near-duplicate memory.",
                )

        memories_text = "\n".join(
            f"ID={m['memory_id']} | type={m['type']} | importance={m['importance']} | content={m['content']}"
            for m in related_memories
        )

        prompt = f"""
You are a memory conflict-resolution system.

Candidate memory:
CONTENT: {candidate.content}
TYPE: {candidate.memory_type}
IMPORTANCE: {candidate.importance}

Related active memories:
{memories_text}

Choose exactly one action:
ADD means the candidate is genuinely new information.
UPDATE means the candidate changes or supersedes one existing memory.
IGNORE means the candidate is redundant, weak, or should not change memory.

Rules:
1. Never invent facts.
2. Use UPDATE when the candidate clearly changes the same preference, goal, project, identity, constraint, plan, or fact.
3. For UPDATE, memory_id must be copied exactly from the existing memory being replaced.
4. For UPDATE, content must be a concise replacement supported by the candidate.
5. For IGNORE, memory_id must identify the redundant existing memory.
6. For ADD, memory_id must be null and content must equal the candidate meaning.
7. Keep the candidate memory type unless the existing type is clearly more appropriate.
8. importance must be an integer from 1 to 5.

Return only a JSON object with these fields:
action, memory_id, content, memory_type, importance, reason
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0,
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Decision response is not a JSON object.")

            action = str(data.get("action", "")).strip().upper()
            if action not in {"ADD", "UPDATE", "IGNORE"}:
                raise ValueError("Invalid memory action.")

            related_by_id = {m["memory_id"]: m for m in related_memories}
            memory_id = data.get("memory_id")
            if memory_id not in related_by_id:
                memory_id = None

            if action == "IGNORE":
                if not memory_id:
                    return self._fallback(related_memories, "Invalid IGNORE target; preserved the closest existing memory.")
                existing = related_by_id[memory_id]
                return MemoryDecisionResult(
                    action="IGNORE",
                    memory_id=memory_id,
                    content=existing["content"],
                    memory_type=existing["type"],
                    importance=existing["importance"],
                    reason=str(data.get("reason") or "Candidate should not change memory."),
                )

            if action == "UPDATE":
                if not memory_id:
                    return self._fallback(related_memories, "Invalid UPDATE target; preserved the closest existing memory.")
                existing = related_by_id[memory_id]
                content = str(data.get("content") or candidate.content).strip()
                memory_type = str(data.get("memory_type") or existing["type"]).strip()
                importance = self._valid_importance(data.get("importance"), candidate.importance)
                return MemoryDecisionResult(
                    action="UPDATE",
                    memory_id=memory_id,
                    content=content,
                    memory_type=memory_type,
                    importance=importance,
                    reason=str(data.get("reason") or "Candidate supersedes an existing memory."),
                )

            content = str(data.get("content") or candidate.content).strip()
            memory_type = str(data.get("memory_type") or candidate.memory_type).strip()
            importance = self._valid_importance(data.get("importance"), candidate.importance)
            return MemoryDecisionResult(
                action="ADD",
                memory_id=None,
                content=content,
                memory_type=memory_type,
                importance=importance,
                reason=str(data.get("reason") or "Candidate is new information."),
            )

        except Exception as e:
            print("Memory decision failed:", e)
            return self._fallback(related_memories, "Decision model unavailable; preserved existing memory.")

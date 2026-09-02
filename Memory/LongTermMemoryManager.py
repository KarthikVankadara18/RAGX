import math
from datetime import datetime, timezone

from Memory.MemoryDecision import MemoryDecision
from Memory.MemoryEmbeddingManager import MemoryEmbeddingManager
from Memory.MemoryExtractor import MemoryExtractor
from Memory.SemanticMemory import SemanticMemory


class LongTermMemoryManager:

    VALID_MEMORY_TYPES = {
        "identity",
        "preference",
        "goal",
        "project",
        "skill",
        "technology",
        "personal_fact",
        "constraint",
        "plan",
        "fact",
    }

    def __init__(self, persistent_memory):
        print("Long-Term Memory Manager Initialized")

        self.persistent_memory = persistent_memory
        self.embedding_manager = MemoryEmbeddingManager()
        self.semantic_memory = SemanticMemory(self.embedding_manager)
        self.extractor = MemoryExtractor()
        self.decision_engine = MemoryDecision()

        self.rebuild_index()

    def _ensure_index_consistent(self, user_id):
        memories = self.persistent_memory.get_all_memories(status="active")
        if self.semantic_memory.index.ntotal != len(self.semantic_memory.memory_ids):
            self.semantic_memory.rebuild(memories)
        return memories

    def rebuild_index(self, user_id=None):
        memories = self.persistent_memory.get_all_memories(status="active")
        self.semantic_memory.rebuild(memories)

    def store_memory(
        self,
        user_id,
        session_id,
        content,
        memory_type="fact",
        importance=3,
        rebuild=True,
    ):
        memory_type = memory_type if memory_type in self.VALID_MEMORY_TYPES else "fact"

        memory_id = self.persistent_memory.save_long_term_memory(
            user_id=user_id,
            session_id=session_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
        )

        if rebuild:
            self.rebuild_index(user_id)

        return memory_id

    def _related_memories(self, user_id, query, top_k=5):
        self._ensure_index_consistent(user_id)

        semantic_results = self.semantic_memory.search(query, max(top_k * 4, top_k))
        memories_by_id = {
            memory["memory_id"]: memory
            for memory in self.persistent_memory.get_user_memories(user_id, status="active")
        }

        related = []
        for result in semantic_results:
            memory = memories_by_id.get(result["memory_id"])
            if not memory:
                continue
            memory["distance"] = result["distance"]
            related.append(memory)
            if len(related) >= top_k:
                break

        return related

    def process_conversation(self, user_id, session_id, user_message, assistant_message):
        candidates = self.extractor.extract(user_message, assistant_message)
        decisions = []

        for candidate in candidates:
            if candidate.memory_type not in self.VALID_MEMORY_TYPES:
                candidate.memory_type = "fact"

            related = self._related_memories(user_id, candidate.content, top_k=5)
            decision = self.decision_engine.decide(candidate, related)

            if decision.action == "IGNORE":
                if decision.memory_id:
                    self.persistent_memory.touch_memory(decision.memory_id)
                decisions.append({
                    "action": "IGNORE",
                    "memory_id": decision.memory_id,
                    "content": decision.content,
                    "memory_type": decision.memory_type,
                    "importance": decision.importance,
                    "reason": decision.reason,
                })
                continue

            if decision.action == "UPDATE":
                existing = self.persistent_memory.get_memory_by_id(decision.memory_id)
                if existing and existing["user_id"] == user_id:
                    self.persistent_memory.update_long_term_memory(
                        memory_id=decision.memory_id,
                        content=decision.content,
                        memory_type=decision.memory_type,
                        importance=decision.importance,
                        status="active",
                    )
                    decisions.append({
                        "action": "UPDATE",
                        "memory_id": decision.memory_id,
                        "content": decision.content,
                        "memory_type": decision.memory_type,
                        "importance": decision.importance,
                        "reason": decision.reason,
                    })
                    continue

                decision.action = "ADD"

            memory_id = self.persistent_memory.save_long_term_memory(
                user_id=user_id,
                session_id=session_id,
                content=decision.content or candidate.content,
                memory_type=decision.memory_type or candidate.memory_type,
                importance=decision.importance or candidate.importance,
            )

            decisions.append({
                "action": "ADD",
                "memory_id": memory_id,
                "content": decision.content or candidate.content,
                "memory_type": decision.memory_type or candidate.memory_type,
                "importance": decision.importance or candidate.importance,
                "reason": decision.reason,
            })

        self.rebuild_index(user_id)
        return decisions

    @staticmethod
    def _recency_score(last_accessed):
        if not last_accessed:
            return 0.0
        if last_accessed.tzinfo is None:
            last_accessed = last_accessed.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (datetime.now(timezone.utc) - last_accessed).total_seconds() / 86400)
        return math.exp(-age_days / 30.0)

    @staticmethod
    def _semantic_score(distance):
        return 1.0 / (1.0 + max(0.0, distance))

    def retrieve_memories(
        self,
        query,
        user_id,
        session_id=None,
        top_k=3,
        scope="user",
        relevance_threshold=0.30,
    ):
        self._ensure_index_consistent(user_id)

        candidate_k = max(top_k * 5, 10)
        semantic_results = self.semantic_memory.search(query, candidate_k)

        active_memories = self.persistent_memory.get_user_memories(
            user_id=user_id,
            session_id=session_id,
            scope=scope,
            status="active",
        )
        memory_by_id = {memory["memory_id"]: memory for memory in active_memories}

        ranked = []
        for result in semantic_results:
            memory = memory_by_id.get(result["memory_id"])
            if not memory:
                continue

            semantic_score = self._semantic_score(result["distance"])
            if semantic_score < relevance_threshold:
                continue

            importance_score = memory["importance"] / 5.0
            recency_score = self._recency_score(memory["last_accessed"])

            final_score = (
                0.65 * semantic_score
                + 0.25 * importance_score
                + 0.10 * recency_score
            )

            memory["distance"] = result["distance"]
            memory["semantic_score"] = round(semantic_score, 4)
            memory["recency_score"] = round(recency_score, 4)
            memory["final_score"] = round(final_score, 4)
            ranked.append(memory)

        ranked.sort(key=lambda item: item["final_score"], reverse=True)

        selected = ranked[:top_k]
        for memory in selected:
            self.persistent_memory.touch_memory(memory["memory_id"])

        return selected

    def run_lifecycle(self, user_id):
        result = self.persistent_memory.apply_lifecycle(user_id)
        if result["archived"] or result["forgotten"]:
            self.rebuild_index(user_id)
        return result

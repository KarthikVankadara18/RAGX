from Retrieval.Retrieval import Retriever
from Memory.PersistentMemory import PersistentMemory
from Memory.LongTermMemoryManager import LongTermMemoryManager

_retriever = None
_memory_manager = None
_persistent_memory = None


def get_retriever():
    global _retriever

    if _retriever is None:
        _retriever = Retriever()

    return _retriever


def get_memory_manager():
    global _memory_manager, _persistent_memory

    if _memory_manager is None:
        _persistent_memory = PersistentMemory()
        _memory_manager = LongTermMemoryManager(_persistent_memory)

    return _memory_manager


def search_documents(query: str):
    results = get_retriever().retrieve(query)

    return [
        {
            "text": result.get("text", ""),
            "page": result.get("page"),
            "section": result.get("section"),
            "subsection": result.get("subsection"),
            "source": result.get("source"),
            "rerank_score": result.get("rerank_score"),
        }
        for result in results
    ]


def calculator(expression: str):
    allowed = "0123456789+-*/().% "

    if not expression or any(char not in allowed for char in expression):
        return {"error": "Invalid mathematical expression."}

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "expression": expression,
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}


def search_memory(
    query: str,
    user_id: str,
    session_id: str | None = None
):
    memories = get_memory_manager().retrieve_memories(
        query=query,
        user_id=user_id,
        session_id=session_id,
        top_k=5,
        scope="user",
        relevance_threshold=0.30
    )

    return [
        {
            "memory_id": memory.get("memory_id"),
            "content": memory.get("content"),
            "type": memory.get("type"),
            "importance": memory.get("importance"),
            "semantic_score": memory.get("semantic_score"),
            "final_score": memory.get("final_score"),
        }
        for memory in memories
    ]
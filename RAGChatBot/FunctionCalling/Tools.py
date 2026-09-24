from Retrieval.Retrieval import Retriever
from Memory.PersistentMemory import PersistentMemory
from Memory.LongTermMemoryManager import LongTermMemoryManager


retriever = Retriever()


def search_documents(query: str):
    results = retriever.retrieve(query)

    formatted_results = []

    for result in results:
        formatted_results.append({
            "text": result.get("text", ""),
            "page": result.get("page"),
            "section": result.get("section"),
            "subsection": result.get("subsection"),
            "source": result.get("source"),
            "rerank_score": result.get("rerank_score"),
        })

    return formatted_results


def calculator(expression: str):
    allowed = "0123456789+-*/().% "

    if not expression or any(char not in allowed for char in expression):
        return {
            "error": "Invalid mathematical expression."
        }

    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return {
            "expression": expression,
            "result": result
        }

    except Exception as e:
        return {
            "error": str(e)
        }


def search_memory(
    query: str,
    long_term_memory: LongTermMemoryManager,
    user_id: str,
    session_id: str | None = None,
):
    memories = long_term_memory.retrieve_memories(
        query=query,
        user_id=user_id,
        session_id=session_id,
        top_k=5,
        scope="user",
        relevance_threshold=0.30,
    )

    formatted_memories = []

    for memory in memories:
        formatted_memories.append({
            "memory_id": memory.get("memory_id"),
            "content": memory.get("content"),
            "type": memory.get("type"),
            "importance": memory.get("importance"),
            "semantic_score": memory.get("semantic_score"),
            "final_score": memory.get("final_score"),
        })

    return formatted_memories
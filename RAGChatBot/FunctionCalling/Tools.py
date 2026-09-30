from pathlib import Path

from RAGChatBot.Retrieval.Retrieval import Retriever
from RAGChatBot.Memory.LongTermMemoryManager import LongTermMemoryManager

retriever = Retriever()

def search_documents(query: str):

    results = retriever.retrieve(query)

    formatted_results = []

    for result in results:

        metadata = result.get("metadata") or {}

        source = metadata.get("source")

        if source:
            source = Path(str(source)).name

        formatted_results.append(
            {
                "chunk_id": result.get("chunk_id"),
                "text": result.get("text", ""),

                "source": source,
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "subsection": metadata.get("subsection"),

                "document_type": metadata.get(
                    "document_type"
                ),

                "rerank_score": result.get(
                    "rerank_score"
                ),

                "retrieval_method": result.get(
                    "retrieval_method"
                ),
            }
        )

    return formatted_results


def calculator(expression: str):

    allowed = "0123456789+-*/().% "

    if (
        not expression
        or any(
            char not in allowed
            for char in expression
        )
    ):
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

    memories = long_term_memory.get_user_memories(
        user_id=user_id,
        session_id=session_id,
        scope="user",
        status="active",
    )
    
    formatted_memories = []

    for memory in memories:

        formatted_memories.append(
            {
                "memory_id": memory.get(
                    "memory_id"
                ),
                "content": memory.get(
                    "content"
                ),
                "type": memory.get(
                    "type"
                ),
                "importance": memory.get(
                    "importance"
                ),
                "semantic_score": memory.get(
                    "semantic_score"
                ),
                "final_score": memory.get(
                    "final_score"
                ),
            }
        )

    return formatted_memories
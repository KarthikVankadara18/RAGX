import uuid

from RAG.RAGManager import RAGManager


def main():
    user_id = f"rag-memory-test-{uuid.uuid4().hex[:10]}"
    session_id = f"rag-session-{uuid.uuid4().hex[:10]}"

    manager = RAGManager(
        user_id=user_id,
        session_id=session_id,
    )

    question = input("Ask something about the document: ").strip()
    result = manager.chat(question)

    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("DOCUMENT SOURCES")
    print("=" * 60)
    for source in result["sources"]:
        print(source)

    print("\n" + "=" * 60)
    print("MEMORY CONTEXT")
    print("=" * 60)
    for memory in result["memories"]:
        print(memory["content"])


if __name__ == "__main__":
    main()

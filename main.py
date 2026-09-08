from RAG.RAGManager import RAGManager


def main():

    user_id = input("User ID: ").strip()
    session_id = input("Session ID: ").strip()
    query = input(
        "Ask something about the document: "
    ).strip()

    if not user_id:
        raise ValueError(
            "User ID cannot be empty."
        )

    if not session_id:
        raise ValueError(
            "Session ID cannot be empty."
        )

    if not query:
        raise ValueError(
            "Query cannot be empty."
        )

    manager = RAGManager(
        user_id=user_id,
        session_id=session_id,
    )

    result = manager.chat(query)

    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCES")
    print("=" * 60)

    for source in result["sources"]:
        print(source)

    print("\n" + "=" * 60)
    print("MEMORY USED")
    print("=" * 60)

    if result["memories"]:

        for memory in result["memories"]:
            print(
                f"- {memory['content']}"
            )

    else:
        print("No relevant memories used.")


if __name__ == "__main__":
    main()
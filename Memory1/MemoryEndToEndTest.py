from Memory.MemoryLLMManager import MemoryLLMManager


import uuid

USER_ID = f"memory-e2e-{uuid.uuid4().hex[:10]}"
SESSION_1 = f"ragx-memory-e2e-{uuid.uuid4().hex[:8]}-1"
SESSION_2 = f"ragx-memory-e2e-{uuid.uuid4().hex[:8]}-2"


def show_memories(manager, title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    memories = manager.persistent_memory.get_user_memories(USER_ID)
    for memory in memories:
        print(
            f"[{memory['type']}] {memory['content']} "
            f"| importance={memory['importance']} "
            f"| status={memory['status']}"
        )
    print("Total active:", len(memories))


def main():
    print("\n" + "#" * 70)
    print("RAGX FULL MEMORY END-TO-END TEST")
    print("#" * 70)
    print(f"Test user: {USER_ID}")

    manager = MemoryLLMManager(USER_ID, SESSION_1)

    print("\n[1] ADD identity/project/goal")
    print("Assistant:", manager.chat(
        "My name is Karthik Vankadara. I am building a project called RAGX using Python, FAISS and Groq. I want to become a Generative AI developer."
    ))

    show_memories(manager, "AFTER ADD")

    print("\n[2] SEND THE SAME FACT AGAIN -> expect IGNORE for duplicates")
    print("Assistant:", manager.chat(
        "My name is Karthik Vankadara and I am building RAGX using Python, FAISS and Groq."
    ))

    print("\n[3] CHANGE A PREFERENCE -> expect UPDATE if extractor identifies it")
    print("Assistant:", manager.chat(
        "I prefer concise interview explanations, but from now on I want the explanations to include practical code examples."
    ))

    show_memories(manager, "AFTER DEDUP + POSSIBLE UPDATE")

    print("\n[4] START A NEW SESSION -> ask for an old memory")
    manager2 = MemoryLLMManager(USER_ID, SESSION_2)
    print("Assistant:", manager2.chat("What is my name and what project am I building?"))

    print("\n[5] EXPLICIT MEMORY RETRIEVAL + RANKING")
    results = manager2.long_term_memory.retrieve_memories(
        query="What project and career goal am I working toward?",
        user_id=USER_ID,
        session_id=SESSION_2,
        top_k=5,
        scope="user",
        relevance_threshold=0.30,
    )
    for result in results:
        print(
            f"{result['content']}\n"
            f"  semantic={result['semantic_score']} "
            f"importance={result['importance']} "
            f"recency={result['recency_score']} "
            f"final={result['final_score']}"
        )

    print("\n[6] LIFECYCLE CHECK")
    print(manager2.long_term_memory.run_lifecycle(USER_ID))

    show_memories(manager2, "FINAL ACTIVE MEMORIES")
    print("\nEND-TO-END TEST COMPLETE")


if __name__ == "__main__":
    main()

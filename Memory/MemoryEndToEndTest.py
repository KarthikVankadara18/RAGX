from datetime import datetime, timedelta, timezone
from bson import ObjectId
import uuid

from Memory.MemoryLLMManager import MemoryLLMManager


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


def find_memory(manager, memory_type, text):
    for memory in manager.persistent_memory.get_user_memories(
        USER_ID,
        scope="all",
        status=None,
    ):
        if memory["type"] == memory_type and text.lower() in memory["content"].lower():
            return memory
    return None


def main():
    print("\n" + "#" * 70)
    print("RAGX FULL MEMORY END-TO-END TEST")
    print("#" * 70)
    print(f"Test user: {USER_ID}")

    manager = MemoryLLMManager(USER_ID, SESSION_1)

    print("\n[1] ADD identity/project/goal/technology/preference")
    print("Assistant:", manager.chat(
        "My name is Karthik Vankadara. I am building a project called RAGX using Python, FAISS and Groq. I want to become a Generative AI developer. I prefer concise interview explanations."
    ))

    show_memories(manager, "AFTER ADD")

    print("\n[2] SEND THE SAME FACT AGAIN -> expect IGNORE for duplicates")
    print("Assistant:", manager.chat(
        "My name is Karthik Vankadara and I am building RAGX using Python, FAISS and Groq. I prefer concise interview explanations."
    ))

    print("\n[3] CHANGE THE PREFERENCE -> expect UPDATE")
    print("Assistant:", manager.chat(
        "I now prefer detailed interview explanations with practical code examples instead of concise explanations."
    ))

    show_memories(manager, "AFTER UPDATE")

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

    print("\n[6] ARCHIVE CHECK")
    target = find_memory(manager2, "preference", "detailed interview")
    if not target:
        raise AssertionError("Preference memory not found for lifecycle test.")

    manager2.persistent_memory.long_term_collection.update_one(
        {"_id": ObjectId(target["memory_id"])},
        {
            "$set": {
                "importance": 1,
                "last_accessed": datetime.now(timezone.utc) - timedelta(days=200),
            }
        },
    )

    archive_result = manager2.long_term_memory.run_lifecycle(USER_ID)
    print(archive_result)
    archived = manager2.persistent_memory.get_memory_by_id(target["memory_id"])
    if not archived or archived["status"] != "archived":
        raise AssertionError("Lifecycle archive test failed.")

    print("\n[7] FORGET CHECK")
    manager2.persistent_memory.long_term_collection.update_one(
        {"_id": ObjectId(target["memory_id"])},
        {
            "$set": {
                "last_accessed": datetime.now(timezone.utc) - timedelta(days=400),
            }
        },
    )

    forget_result = manager2.long_term_memory.run_lifecycle(USER_ID)
    print(forget_result)
    forgotten = manager2.persistent_memory.get_memory_by_id(target["memory_id"])
    if not forgotten or forgotten["status"] != "forgotten":
        raise AssertionError("Lifecycle forget test failed.")

    print("\n[8] FAISS / MONGODB SYNC CHECK")
    active_memories = manager2.persistent_memory.get_all_memories(status="active")
    if manager2.long_term_memory.semantic_memory.index.ntotal != len(active_memories):
        raise AssertionError("FAISS index is out of sync with active MongoDB memories.")
    print("FAISS active vectors:", manager2.long_term_memory.semantic_memory.index.ntotal)
    print("MongoDB active memories:", len(active_memories))

    show_memories(manager2, "FINAL ACTIVE MEMORIES")
    print("\nEND-TO-END TEST COMPLETE")


if __name__ == "__main__":
    main()

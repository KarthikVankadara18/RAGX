import asyncio
from FunctionCalling.FunctionCallingManager import FunctionCallingManager

def main():

    print("=" * 70)
    print("CROSS-USER MEMORY SECURITY TEST")
    print("=" * 70)

    user_1 = FunctionCallingManager(
        user_id="security_user_001",
        session_id="security_session_001",
    )

    user_2 = FunctionCallingManager(
        user_id="security_user_002",
        session_id="security_session_002",
    )

    print("\nUSER 001 SAVING PRIVATE MEMORY")

    save_result = user_1._mcp_memory_save(
        "PRIVATE SECURITY TEST: User 001 secret project is RAGX-Enterprise."
    )

    print("Save result:")
    print(save_result)

    print("\nUSER 001 SEARCH")

    user_1_result = asyncio.run(
        user_1._call_mcp_tool(
            "search_user_memory",
            {
                "query": "secret project",
                "user_id": user_1.runtime_context.user_id,
                "session_id": user_1.runtime_context.session_id,
            }
        )
    )

    print("User 001 result:")
    print(user_1_result)

    print("\nUSER 002 SEARCH")

    user_2_result = asyncio.run(
        user_2._call_mcp_tool(
            "search_user_memory",
            {
                "query": "secret project",
                "user_id": user_2.runtime_context.user_id,
                "session_id": user_2.runtime_context.session_id,
            }
        )
    )

    print("User 002 result:")
    print(user_2_result)

    leaked = any(
        isinstance(memory, dict)
        and "User 001 secret project" in memory.get("content", "")
        for memory in user_2_result
    )

    print("\n" + "=" * 70)
    print("SECURITY RESULT")
    print("=" * 70)

    if leaked:
        print("❌ SECURITY FAILURE")
        print("User 002 accessed User 001's memory.")
    else:
        print("✅ SECURITY PASSED")
        print("User 002 could not access User 001's memory.")


if __name__ == "__main__":
    main()
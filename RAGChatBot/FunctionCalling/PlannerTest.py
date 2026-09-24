from FunctionCalling.FunctionCallingManager import FunctionCallingManager

def main():

    agent = FunctionCallingManager(
        user_id="user_001",
        session_id="planning_agent_test",
    )

    queries = [
        "What project am I building?",
        "I am learning MCP and Agentic AI.",
        "My RAGX project is now called RAGX-Enterprise v2.",
        "Forget that I am learning MCP.",
    ]

    for query in queries:

        print()
        print("=" * 70)
        print("USER QUERY")
        print("=" * 70)
        print(query)

        result = agent.run_planned(query)

        print()
        print("=" * 70)
        print("RETURNED ANSWER")
        print("=" * 70)
        print(result["answer"])


if __name__ == "__main__":
    main()
from FunctionCalling.FunctionCallingManager import FunctionCallingManager

def main():

    agent = FunctionCallingManager(
        user_id="karthik",
        session_id="planning_agent_test",
    )

    queries = [
        "What project am I building?",
        "What is RAG according to the uploaded document?",
        "What is 25 * 18?",
        "What project am I building and what is 25 * 18?",
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
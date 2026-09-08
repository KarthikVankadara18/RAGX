from FunctionCalling.FunctionCallingManager import (
    FunctionCallingManager
)

def main():

    print()
    print("=" * 60)
    print("RAGX AGENT TEST")
    print("=" * 60)

    agent = FunctionCallingManager(
        user_id="karthik",
        session_id="agent_test_session",
    )

    while True:

        print()

        user_query = input(
            "User: "
        ).strip()

        if user_query.lower() in {
            "exit",
            "quit"
        }:

            print(
                "Exiting agent."
            )

            break

        if not user_query:
            continue

        result = agent.run(
            user_query
        )

        state = result["state"]

        print()
        print("=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)

        if result["answer"]:

            print(
                result["answer"]
            )

        else:

            print(
                "Agent did not produce "
                "a final answer."
            )

        print()
        print("=" * 60)
        print("AGENT STATE")
        print("=" * 60)

        print(
            "Status:",
            state.status
        )

        print(
            "Iterations:",
            state.iteration
        )

        print(
            "Tools used:",
            state.tools_used
        )

        print(
            "Tool calls:",
            len(state.tool_results)
        )

        if state.error:

            print(
                "Error:",
                state.error
            )


if __name__ == "__main__":
    main()
from FunctionCalling.FunctionCallingManager import FunctionCallingManager
from FunctionCalling.AgentState import AgentState


def main():

    agent = FunctionCallingManager(
        user_id="user_001",
        session_id="retry_test",
    )

    state = AgentState(
        user_query="Retry test"
    )

    state.max_step_retries = 2

    original_execute = agent.execute_single_step

    attempts = {
        "count": 0
    }

    def flaky_execute(step, state):

        attempts["count"] += 1

        print(
            f"\nTEST EXECUTION ATTEMPT: "
            f"{attempts['count']}"
        )

        if attempts["count"] == 1:

            raise RuntimeError(
                "Simulated temporary failure"
            )

        return original_execute(
            step,
            state
        )

    agent.execute_single_step = flaky_execute

    plan = {
        "steps": [
            {
                "step": 1,
                "action": "CALCULATION",
                "query": "10 + 20",
            }
        ]
    }

    try:

        result = agent.execute_plan(
            plan,
            state
        )

        state.finish()

        print()
        print("=" * 70)
        print("RETRY TEST RESULT")
        print("=" * 70)

        print("Status        :", state.status)
        print("Step attempts :", state.step_attempts)
        print("Iterations    :", state.iteration)
        print("Tools used    :", state.tools_used)
        print("Results       :", result)

    except Exception as exc:

        state.fail(str(exc))

        print()
        print("=" * 70)
        print("RETRY TEST FAILED")
        print("=" * 70)

        print("Status        :", state.status)
        print("Step attempts :", state.step_attempts)
        print("Iterations    :", state.iteration)
        print("Error         :", state.error)


if __name__ == "__main__":
    main()
from FunctionCalling.FunctionCallingManager import FunctionCallingManager
from FunctionCalling.AgentState import AgentState

def main():

    agent = FunctionCallingManager(
        user_id="user_001",
        session_id="failure_test",
    )

    state = AgentState(
        user_query="Test failure"
    )

    plan = {
        "steps": [
            {
                "step": 1,
                "action": "INVALID_ACTION",
                "query": "test"
            }
        ]
    }

    try:

        agent.execute_plan(
            plan,
            state
        )

    except Exception as exc:

        print()
        print("=" * 70)
        print("FAILURE TEST")
        print("=" * 70)

        print("Exception    :", exc)
        print("Status       :", state.status)
        print("Current step :", state.current_step)
        print("Iteration    :", state.iteration)
        print("Error        :", state.error)
        print("Tools used   :", state.tools_used)
        print("Tool results :", state.tool_results)


if __name__ == "__main__":
    main()
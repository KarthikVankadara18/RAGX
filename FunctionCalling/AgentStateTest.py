from FunctionCalling.AgentState import AgentState

def main():
    state = AgentState(
        user_query="Update my project name"
    )

    plan = [
        {
            "step": 1,
            "action": "MEMORY_LOOKUP",
            "query": "project name",
        },
        {
            "step": 2,
            "action": "MEMORY_UPDATE",
            "query": "RAGX-Enterprise v2",
        },
    ]

    state.set_plan(plan)

    print("Initial state:")
    print("Current step:", state.current_step)
    print("Current action:", state.get_current_step()["action"])

    state.add_tool_result(
        tool_name="search_user_memory",
        arguments={"query": "project name"},
        result={"memory_id": "123"},
    )

    state.move_to_next_step()

    print()
    print("After Step 1:")
    print("Current step:", state.current_step)
    print("Current action:", state.get_current_step()["action"])

    state.add_tool_result(
        tool_name="update_user_memory",
        arguments={
            "memory_id": "123",
            "content": "RAGX-Enterprise v2",
        },
        result={"action": "UPDATE"},
    )

    state.move_to_next_step()

    print()
    print("After Step 2:")
    print("Current step:", state.current_step)
    print("Current step:", state.get_current_step())

    state.finish()

    print()
    print("Final state:")
    print("Status:", state.status)
    print("Tools used:", state.tools_used)
    print("Tool results:", state.tool_results)


if __name__ == "__main__":
    main()
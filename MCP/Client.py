import asyncio
import json

from mcp import Client, StdioServerParameters

server = StdioServerParameters(
    command="uv",
    args=["run", "MCP/Server.py"],
)

def extract_contents(result):
    if not result.content:
        return []

    values = []

    for item in result.content:
        text = getattr(item, "text", None)

        if text is None:
            values.append(item)
            continue

        try:
            values.append(json.loads(text))
        except json.JSONDecodeError:
            values.append(text)

    return values

async def main():

    async with Client(server) as client:

        tools_response = await client.list_tools()

        print("Available tools:\n")

        if isinstance(tools_response, tuple):
            for item in tools_response:
                if isinstance(item, list):
                    for tool in item:
                        print(f"- {tool.name}: {tool.description}")

                elif hasattr(item, "tools"):
                    for tool in item.tools:
                        print(f"- {tool.name}: {tool.description}")

        elif hasattr(tools_response, "tools"):
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description}")

        user_id = "user_001"
        session_id = "mcp-memory-test"

        print("\n" + "=" * 50)
        print("SAVE MEMORY")
        print("=" * 50)

        save_result = await client.call_tool(
            "save_user_memory",
            {
                "content": "I am learning MCP for my RAGX-Enterprise project.",
                "memory_type": "technology",
                "user_id": user_id,
                "session_id": session_id,
                "importance": 4
            }
        )

        save_data = extract_contents(save_result)

        print(json.dumps(save_data, indent=2))

        if not save_data:
            print("\nERROR: Save returned no result.")
            return

        save_data = save_data[0]

        if not isinstance(save_data, dict):
            print("\nERROR: Unexpected save response.")
            return

        if "memory_id" not in save_data:
            print("\nERROR: Memory ID was not returned.")
            return

        memory_id = save_data["memory_id"]

        print(f"\nCreated memory ID: {memory_id}")

        print("\n" + "=" * 50)
        print("SEARCH AFTER SAVE")
        print("=" * 50)

        search_result = await client.call_tool(
            "search_user_memory",
            {
                "query": "What am I learning for my RAGX project?",
                "user_id": user_id,
                "session_id": session_id
            }
        )

        search_data = extract_contents(search_result)

        print(json.dumps(search_data, indent=2))

        print("\n" + "=" * 50)
        print("UPDATE MEMORY")
        print("=" * 50)

        update_result = await client.call_tool(
            "update_user_memory",
            {
                "memory_id": memory_id,
                "content": "I am learning MCP and Agentic AI for my RAGX-Enterprise project.",
                "user_id": user_id,
                "memory_type": "technology",
                "importance": 5
            }
        )

        update_data = extract_contents(update_result)

        print(json.dumps(update_data, indent=2))

        print("\n" + "=" * 50)
        print("SEARCH AFTER UPDATE")
        print("=" * 50)

        search_update_result = await client.call_tool(
            "search_user_memory",
            {
                "query": "What am I learning for my RAGX project?",
                "user_id": user_id,
                "session_id": session_id
            }
        )

        search_update_data = extract_contents(search_update_result)

        print(json.dumps(search_update_data, indent=2))

        print("\n" + "=" * 50)
        print("FORGET MEMORY")
        print("=" * 50)

        forget_result = await client.call_tool(
            "forget_user_memory",
            {
                "memory_id": memory_id,
                "user_id": user_id
            }
        )

        forget_data = extract_contents(forget_result)

        print(json.dumps(forget_data, indent=2))

        print("\n" + "=" * 50)
        print("SEARCH AFTER FORGET")
        print("=" * 50)

        search_forget_result = await client.call_tool(
            "search_user_memory",
            {
                "query": "What am I learning for my RAGX project?",
                "user_id": user_id,
                "session_id": session_id
            }
        )

        search_forget_data = extract_contents(search_forget_result)

        print(json.dumps(search_forget_data, indent=2))

        print("\n" + "=" * 50)
        print("MCP MEMORY CRUD TEST COMPLETED")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
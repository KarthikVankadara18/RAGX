import asyncio
from mcp import Client, StdioServerParameters


server = StdioServerParameters(
    command="uv",
    args=["run", "MCP/Server.py"],
)


async def main():

    async with Client(server) as client:

        tools = await client.list_tools()

        print("Available tools:\n")

        for tool in tools.tools:
            print(f"- {tool.name}: {tool.description}")

        rag_result = await client.call_tool(
            "search_rag",
            {
                "query": "What is RAG?"
            }
        )

        calc_result = await client.call_tool(
            "calculate",
            {
                "expression": "25 * 18"
            }
        )

        memory_result = await client.call_tool(
            "search_user_memory",
            {
                "query": "What is my RAG project?",
                "user_id": "user_001"
            }
        )

        print("\nRAG result:")
        print(rag_result.content)

        print("\nCalculation result:")
        print(calc_result.content)

        print("\nMemory result:")
        print(memory_result.content)


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from mcp import Client, StdioServerParameters

class MCPClientManager:

    def __init__(self):

        self.server = StdioServerParameters(
            command="uv",
            args=["run", "MCP/Server.py"],
        )

    async def call_tool(self, tool_name: str, arguments: dict):

        async with Client(self.server) as client:

            result = await client.call_tool(
                tool_name,
                arguments
            )

            return result
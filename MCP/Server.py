import sys
import builtins
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_original_print = builtins.print


def mcp_print(*args, **kwargs):
    kwargs["file"] = sys.stderr
    _original_print(*args, **kwargs)


builtins.print = mcp_print

from mcp.server import MCPServer
from MCP.Tools import search_documents, calculator, search_memory

mcp = MCPServer("RAGX MCP Server")


@mcp.tool()
def search_rag(query: str):
    """Search the RAGX knowledge base."""
    return search_documents(query)


@mcp.tool()
def calculate(expression: str):
    """Calculate a mathematical expression."""
    return calculator(expression)


@mcp.tool()
def search_user_memory(query: str, user_id: str, session_id: str | None = None):
    try:
        return search_memory(query, user_id, session_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
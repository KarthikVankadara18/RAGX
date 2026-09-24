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

from MCP.Tools import (
    search_documents,
    calculator,
    search_memory,
    save_memory,
    update_memory,
    forget_memory
)


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
def search_user_memory(
    query: str,
    user_id: str,
    session_id: str | None = None
):
    """Search the user's long-term memory."""
    try:
        return search_memory(query, user_id, session_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@mcp.tool()
def save_user_memory(
    content: str,
    memory_type: str,
    user_id: str,
    session_id: str | None = None,
    importance: int = 3
):
    """Save a new user memory."""
    try:
        return save_memory(
            content=content,
            memory_type=memory_type,
            user_id=user_id,
            session_id=session_id,
            importance=importance
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@mcp.tool()
def update_user_memory(
    memory_id: str,
    content: str,
    user_id: str,
    memory_type: str | None = None,
    importance: int | None = None
):
    """Update an existing user memory."""
    try:
        return update_memory(
            memory_id=memory_id,
            content=content,
            user_id=user_id,
            memory_type=memory_type,
            importance=importance
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@mcp.tool()
def forget_user_memory(
    memory_id: str,
    user_id: str
):
    """Forget an existing user memory."""
    try:
        return forget_memory(
            memory_id=memory_id,
            user_id=user_id
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
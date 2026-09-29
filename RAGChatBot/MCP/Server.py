import builtins
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

_original_print = builtins.print


def mcp_print(*args, **kwargs):
    kwargs["file"] = sys.stderr
    _original_print(*args, **kwargs)


builtins.print = mcp_print

from mcp.server import MCPServer

from RAGChatBot.MCP.Tools import (
    search_documents,
    search_documents_by_source,
    get_knowledge_base_status,
    list_document_sources,
    calculator,
    search_memory,
    save_memory,
    update_memory,
    forget_memory,
    get_current_datetime,
    fetch_url,
    web_search,
)

mcp = MCPServer("RAGX MCP Server")


@mcp.tool()
def search_rag(query: str):
    """Search the RAGX hybrid knowledge base."""
    return search_documents(query)


@mcp.tool()
def search_rag_by_source(source: str, query: str, top_k: int = 5):
    """Search only within a selected knowledge-base source."""
    return search_documents_by_source(source, query, top_k)


@mcp.tool()
def get_knowledge_base_status_tool():
    """Return knowledge-base readiness, chunk count, sources, and retrieval pipeline."""
    return get_knowledge_base_status()


@mcp.tool()
def list_document_sources_tool():
    """List document sources currently indexed in the knowledge base."""
    return list_document_sources()


@mcp.tool()
def calculate(expression: str):
    """Calculate a mathematical expression."""
    return calculator(expression)


@mcp.tool()
def get_current_datetime_tool():
    """Return the current UTC date and time."""
    return get_current_datetime()


@mcp.tool()
def fetch_url_tool(url: str):
    """Fetch readable text from a public HTTP/HTTPS webpage."""
    return fetch_url(url)


@mcp.tool()
def web_search_tool(query: str, max_results: int = 5):
    """Search the public web for current external information."""
    return web_search(query, max_results)


@mcp.tool()
def search_user_memory(query: str, user_id: str, session_id: str | None = None):
    """Search the user's long-term memory."""
    try:
        return search_memory(query, user_id, session_id)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return {"error": str(exc)}


@mcp.tool()
def save_user_memory(content: str, memory_type: str, user_id: str,
                     session_id: str | None = None, importance: int = 3):
    """Save a new user memory."""
    try:
        return save_memory(content, memory_type, user_id, session_id, importance)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return {"error": str(exc)}


@mcp.tool()
def update_user_memory(memory_id: str, content: str, user_id: str,
                        memory_type: str | None = None, importance: int | None = None):
    """Update an existing user memory."""
    try:
        return update_memory(memory_id, content, user_id, memory_type, importance)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return {"error": str(exc)}


@mcp.tool()
def forget_user_memory(memory_id: str, user_id: str):
    """Forget an existing user memory."""
    try:
        return forget_memory(memory_id, user_id)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return {"error": str(exc)}


if __name__ == "__main__":
    mcp.run()

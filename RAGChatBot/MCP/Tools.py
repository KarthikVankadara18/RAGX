from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
import ipaddress
import re
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from RAGChatBot.config import Config
from RAGChatBot.Retrieval.Retrieval import Retriever
from RAGChatBot.Memory.PersistentMemory import PersistentMemory
from RAGChatBot.Memory.LongTermMemoryManager import LongTermMemoryManager

_retriever = None
_memory_manager = None
_persistent_memory = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def get_memory_manager():
    global _memory_manager, _persistent_memory
    if _memory_manager is None:
        _persistent_memory = PersistentMemory()
        _memory_manager = LongTermMemoryManager(_persistent_memory)
    return _memory_manager


def search_documents(query: str):
    results = get_retriever().retrieve(query)
    return [
        {
            "chunk_id": result.get("chunk_id"),
            "text": result.get("text", ""),
            "page": result.get("metadata", {}).get("page", result.get("page")),
            "section": result.get("metadata", {}).get("section", result.get("section")),
            "subsection": result.get("metadata", {}).get("subsection", result.get("subsection")),
            "source": result.get("metadata", {}).get("source", result.get("source")),
            "rerank_score": result.get("rerank_score"),
            "rrf_score": result.get("rrf_score"),
        }
        for result in results
    ]


def search_documents_by_source(source: str, query: str, top_k: int = 5):
    if not source or not source.strip():
        return {"error": "Source cannot be empty."}
    if not query or not query.strip():
        return {"error": "Query cannot be empty."}

    documents = get_retriever().documents
    source_key = source.strip().lower()
    matched = [
        doc for doc in documents
        if source_key in str(doc.get("metadata", {}).get("source", "")).lower()
    ]

    if not matched:
        return []

    # Reuse the existing reranker on the filtered source collection.
    candidates = [
        {
            "chunk_id": doc.get("chunk_id"),
            "text": doc.get("text", ""),
            "metadata": doc.get("metadata", {}),
            "score": 0.0,
        }
        for doc in matched
    ]
    results = get_retriever().reranker.rerank(query, candidates, top_k)
    return [
        {
            "chunk_id": item.get("chunk_id"),
            "text": item.get("text", ""),
            "source": item.get("metadata", {}).get("source"),
            "page": item.get("metadata", {}).get("page"),
            "section": item.get("metadata", {}).get("section"),
            "rerank_score": item.get("rerank_score"),
        }
        for item in results
    ]


def get_knowledge_base_status():
    retriever = get_retriever()
    documents = retriever.documents
    sources = sorted({
        str(doc.get("metadata", {}).get("source", "unknown"))
        for doc in documents
    })
    return {
        "status": "ready" if documents else "empty",
        "chunk_count": len(documents),
        "source_count": len(sources),
        "sources": sources,
        "retrieval_pipeline": ["FAISS", "BM25", "RRF", "CrossEncoder"],
    }


def list_document_sources():
    return get_knowledge_base_status()["sources"]


def calculator(expression: str):
    allowed = "0123456789+-*/().% "
    if not expression or any(char not in allowed for char in expression):
        return {"error": "Invalid mathematical expression."}
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": result}
    except Exception as exc:
        return {"error": str(exc)}


def search_memory(query: str, user_id: str, session_id: str | None = None):
    memories = get_memory_manager().retrieve_memories(
        query=query,
        user_id=user_id,
        session_id=session_id,
        top_k=5,
        scope="user",
        relevance_threshold=0.30,
    )
    return [
        {
            "memory_id": memory.get("memory_id"),
            "content": memory.get("content"),
            "type": memory.get("type"),
            "importance": memory.get("importance"),
            "semantic_score": memory.get("semantic_score"),
            "final_score": memory.get("final_score"),
        }
        for memory in memories
    ]


def save_memory(content: str, memory_type: str, user_id: str,
                session_id: str | None = None, importance: int = 3):
    memory_id = get_memory_manager().store_memory(
        user_id=user_id,
        session_id=session_id,
        content=content,
        memory_type=memory_type,
        importance=importance,
    )
    return {
        "action": "ADD",
        "memory_id": memory_id,
        "content": content,
        "type": memory_type,
        "importance": importance,
    }


def update_memory(memory_id: str, content: str, user_id: str,
                  memory_type: str | None = None, importance: int | None = None):
    manager = get_memory_manager()
    memory = manager.persistent_memory.get_memory_by_id(memory_id)
    if not memory:
        return {"error": "Memory not found."}
    if memory["user_id"] != user_id:
        return {"error": "Unauthorized memory access."}

    final_type = memory_type or memory["type"]
    final_importance = importance if importance is not None else memory["importance"]
    manager.persistent_memory.update_long_term_memory(
        memory_id=memory_id,
        content=content,
        memory_type=final_type,
        importance=final_importance,
        status="active",
    )
    manager.rebuild_index(user_id)
    return {
        "action": "UPDATE",
        "memory_id": memory_id,
        "content": content,
        "type": final_type,
        "importance": final_importance,
    }


def forget_memory(memory_id: str, user_id: str):
    manager = get_memory_manager()
    memory = manager.persistent_memory.get_memory_by_id(memory_id)
    if not memory:
        return {"error": "Memory not found."}
    if memory["user_id"] != user_id:
        return {"error": "Unauthorized memory access."}

    manager.persistent_memory.update_long_term_memory(
        memory_id=memory_id,
        content=memory["content"],
        memory_type=memory["type"],
        importance=memory["importance"],
        status="forgotten",
    )
    manager.rebuild_index(user_id)
    return {
        "action": "FORGET",
        "memory_id": memory_id,
        "content": memory["content"],
    }


def get_current_datetime():
    now = datetime.now(timezone.utc)
    return {
        "iso_utc": now.isoformat(),
        "date": now.date().isoformat(),
        "time": now.time().isoformat(timespec="seconds"),
        "timezone": "UTC",
    }


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def _validate_external_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only http and https URLs are supported.")

    hostname = parsed.hostname.lower()
    blocked = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
    if hostname in blocked or hostname.endswith(".local"):
        raise ValueError("Local network URLs are not allowed.")

    try:
        addresses = socket.getaddrinfo(hostname, None)
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise ValueError("Private or local network URLs are not allowed.")
    except socket.gaierror:
        raise ValueError("Unable to resolve the URL host.")


def fetch_url(url: str):
    try:
        _validate_external_url(url)
        request = Request(
            url,
            headers={
                "User-Agent": "RAGX-Enterprise/1.0",
                "Accept": "text/html,text/plain,application/xhtml+xml",
            },
        )
        with urlopen(request, timeout=Config.EXTERNAL_REQUEST_TIMEOUT) as response:
            raw = response.read(Config.MAX_EXTERNAL_CONTENT_CHARS * 4)
            content_type = response.headers.get("Content-Type", "")
            final_url = response.geturl()

        text = raw.decode("utf-8", errors="replace")
        if "html" in content_type.lower() or "xhtml" in content_type.lower():
            parser = _TextExtractor()
            parser.feed(text)
            text = "\n".join(parser.parts)

        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        text = text[:Config.MAX_EXTERNAL_CONTENT_CHARS]

        return {
            "url": final_url,
            "content_type": content_type,
            "content": text,
            "truncated": len(text) >= Config.MAX_EXTERNAL_CONTENT_CHARS,
        }
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeError) as exc:
        return {"error": str(exc), "url": url}


def web_search(query: str, max_results: int = 5):
    if not query or not query.strip():
        return {"error": "Search query cannot be empty."}
    max_results = max(1, min(int(max_results), 10))

    # DuckDuckGo's lightweight HTML endpoint avoids requiring another API key.
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query.strip())
    try:
        request = Request(
            url,
            headers={"User-Agent": "RAGX-Enterprise/1.0"},
        )
        with urlopen(request, timeout=Config.EXTERNAL_REQUEST_TIMEOUT) as response:
            html = response.read(2_000_000).decode("utf-8", errors="replace")

        class SearchParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results = []
                self.current = None
                self.capture_title = False
                self.capture_snippet = False

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                cls = attrs.get("class", "")
                href = attrs.get("href")
                if tag == "a" and "result__a" in cls and href:
                    self.current = {"title": "", "url": href, "snippet": ""}
                    self.capture_title = True
                elif tag in {"a", "div", "td"} and "result__snippet" in cls and self.current:
                    self.capture_snippet = True

            def handle_endtag(self, tag):
                if tag == "a" and self.capture_title:
                    self.capture_title = False
                if self.capture_snippet and tag in {"a", "div", "td"}:
                    self.capture_snippet = False
                    if self.current and self.current["title"]:
                        self.results.append(self.current)
                        self.current = None

            def handle_data(self, data):
                if not self.current:
                    return
                text = re.sub(r"\s+", " ", data).strip()
                if self.capture_title:
                    self.current["title"] += text
                elif self.capture_snippet:
                    self.current["snippet"] += text

        parser = SearchParser()
        parser.feed(html)
        results = []
        for item in parser.results:
            if item["title"] and item["url"]:
                results.append(item)
            if len(results) >= max_results:
                break
        return {"query": query, "results": results}
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return {"error": str(exc), "query": query}

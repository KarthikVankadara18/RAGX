import json
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path


_CURRENT_TRACE = ContextVar("ragx_current_trace", default=None)


class Trace:
    def __init__(self, query=None, trace_id=None):
        self.trace_id = trace_id or uuid.uuid4().hex
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.query = query
        self.events = []
        self.status = "running"
        self.error = None
        self._started = time.perf_counter()

    def event(self, name, **data):
        self.events.append({
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "elapsed_ms": round((time.perf_counter() - self._started) * 1000, 3),
            "data": data,
        })

    def finish(self, status="completed", error=None):
        self.status = status
        self.error = error
        self.finished_at = datetime.now(timezone.utc).isoformat()
        self.duration_ms = round((time.perf_counter() - self._started) * 1000, 3)

    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "started_at": self.started_at,
            "finished_at": getattr(self, "finished_at", None),
            "duration_ms": getattr(self, "duration_ms", None),
            "query": self.query,
            "status": self.status,
            "error": self.error,
            "events": self.events,
        }


class Observability:
    def __init__(self, log_path="Data/Observability/traces.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def start_trace(self, query=None):
        trace = Trace(query=query)
        _CURRENT_TRACE.set(trace)
        return trace

    def current_trace(self):
        return _CURRENT_TRACE.get()

    def record(self, name, **data):
        trace = self.current_trace()
        if trace:
            trace.event(name, **data)

    def finish_trace(self, trace, status="completed", error=None):
        trace.finish(status=status, error=error)
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(trace.to_dict(), ensure_ascii=False) + "\n")
        _CURRENT_TRACE.set(None)
        return trace.to_dict()

    @contextmanager
    def trace(self, query=None):
        trace = self.start_trace(query=query)
        try:
            yield trace
        except Exception as exc:
            self.finish_trace(trace, status="failed", error=str(exc))
            raise
        else:
            self.finish_trace(trace)


observability = Observability()


def current_trace():
    return observability.current_trace()


def record_event(name, **data):
    observability.record(name, **data)


def trace_request(query_param="query"):
    def decorator(function):
        def wrapper(*args, **kwargs):
            query = kwargs.get(query_param)
            if query is None and len(args) > 1:
                query = args[1]
            with observability.trace(query):
                return function(*args, **kwargs)
        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper
    return decorator

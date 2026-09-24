import json
import tempfile
from pathlib import Path

from Observability.Tracer import Observability, trace_request, record_event


def main():
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "traces.jsonl"
        obs = Observability(path)
        with obs.trace("test query"):
            obs.record("retrieval.start", method="dense", candidate_k=20)
            obs.record("retrieval.complete", result_count=5, chunk_ids=[1, 2, 3])
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        trace = json.loads(lines[0])
        assert trace["query"] == "test query"
        assert trace["status"] == "completed"
        assert trace["duration_ms"] >= 0
        assert len(trace["events"]) == 2
        print("OBSERVABILITY TEST PASSED")


if __name__ == "__main__":
    main()

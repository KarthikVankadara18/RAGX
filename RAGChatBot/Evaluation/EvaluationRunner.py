import json
import os
from datetime import datetime, timezone

from Retrieval.Retrieval import Retriever
from Retrieval.Hybrid_Search import HybridRetriever
from Evaluation.RetrievalEvaluator import RetrievalEvaluator
from Observability.Tracer import observability


class EvaluationRunner:
    def __init__(self, dataset_path, k_values=(1, 3, 5), report_path=None):
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Evaluation dataset not found: {dataset_path}")
        with open(dataset_path, "r", encoding="utf-8") as file:
            self.dataset = json.load(file)
        self.evaluator = RetrievalEvaluator(k_values)
        self.report_path = report_path or os.path.join(
            os.path.dirname(dataset_path), "reports", "latest_report.json"
        )

    def _evaluate(self, name, retriever):
        return self.evaluator.evaluate(self.dataset, retriever, name=name)

    @staticmethod
    def print_report(name, report):
        print()
        print("=" * 72)
        print(name)
        print("=" * 72)
        print(f"Queries: {report['queries']}")
        for metric, value in report["metrics"].items():
            print(f"{metric.upper():<15}: {value:.4f}")

    @staticmethod
    def _metric_delta(baseline, hybrid):
        metrics = sorted(set(baseline["metrics"]) | set(hybrid["metrics"]))
        return {
            metric: round(hybrid["metrics"].get(metric, 0.0) - baseline["metrics"].get(metric, 0.0), 4)
            for metric in metrics
        }

    def run_comparison(self):
        baseline = self._evaluate("baseline_dense", Retriever())
        hybrid = self._evaluate("hybrid_bm25_rrf", HybridRetriever())
        comparison = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dataset_queries": len(self.dataset),
            "baseline": baseline,
            "hybrid": hybrid,
            "hybrid_minus_baseline": self._metric_delta(baseline, hybrid),
        }
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as file:
            json.dump(comparison, file, indent=2, ensure_ascii=False)

        self.print_report("BASELINE: FAISS + CROSS-ENCODER", baseline)
        self.print_report("HYBRID: FAISS + BM25 + RRF + CROSS-ENCODER", hybrid)
        print()
        print("=" * 72)
        print("HYBRID - BASELINE DELTA")
        print("=" * 72)
        for metric, value in comparison["hybrid_minus_baseline"].items():
            print(f"{metric.upper():<15}: {value:+.4f}")
        print(f"Report saved: {self.report_path}")
        return comparison


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_root, "Evaluation", "evaluation_dataset.json")
    runner = EvaluationRunner(dataset_path=dataset_path)
    runner.run_comparison()

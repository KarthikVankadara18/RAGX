class RetrievalEvaluator:
    """Evaluate ranked retrieval against manually labelled relevant chunks."""

    def __init__(self, ks=(1, 3, 5)):
        self.ks = tuple(sorted(set(int(k) for k in ks if int(k) > 0)))
        if not self.ks:
            raise ValueError("At least one positive evaluation k is required.")

    @staticmethod
    def _chunk_id(result):
        return result.get("chunk_id") if isinstance(result, dict) else None

    def evaluate_query(self, results, relevant_chunk_ids):
        relevant = set(relevant_chunk_ids)
        if not relevant:
            raise ValueError("Each evaluation query needs at least one relevant chunk ID.")

        metrics = {}
        retrieved_ids = [self._chunk_id(result) for result in results]

        for k in self.ks:
            top_ids = retrieved_ids[:k]
            relevant_ids = {chunk_id for chunk_id in top_ids if chunk_id in relevant}
            hit = 1.0 if relevant_ids else 0.0
            recall = len(relevant_ids) / len(relevant)
            precision = len(relevant_ids) / k
            mrr = 0.0
            for rank, chunk_id in enumerate(top_ids, start=1):
                if chunk_id in relevant:
                    mrr = 1.0 / rank
                    break
            metrics.update({
                f"hit@{k}": hit,
                f"recall@{k}": recall,
                f"precision@{k}": precision,
                f"mrr@{k}": mrr,
            })

        return metrics

    def evaluate(self, dataset, retriever, name=None):
        if not dataset:
            raise ValueError("Evaluation dataset cannot be empty.")

        per_query = []
        totals = {}
        from Observability.Tracer import observability

        for item in dataset:
            query = item["query"]
            relevant_chunk_ids = item["relevant_chunk_ids"]
            with observability.trace(query):
                results = retriever.retrieve(query, top_k=max(self.ks))
            metrics = self.evaluate_query(results, relevant_chunk_ids)
            per_query.append({
                "query": query,
                "relevant_chunk_ids": relevant_chunk_ids,
                "metrics": metrics,
                "results": [
                    {
                        "chunk_id": result.get("chunk_id"),
                        "score": result.get("score"),
                        "dense_score": result.get("dense_score"),
                        "rrf_score": result.get("rrf_score"),
                        "rerank_score": result.get("rerank_score"),
                        "retrieval_method": result.get("retrieval_method"),
                    }
                    for result in results
                ],
            })
            for metric, value in metrics.items():
                totals[metric] = totals.get(metric, 0.0) + value

        count = len(dataset)
        averages = {metric: round(value / count, 4) for metric, value in sorted(totals.items())}
        return {
            "name": name,
            "queries": count,
            "metrics": averages,
            "per_query": per_query,
        }

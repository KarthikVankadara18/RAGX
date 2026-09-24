from sentence_transformers import CrossEncoder

from config import Config


class ReRanker:
    """
    Reranks a pool of FAISS candidates by actual query-passage relevance
    using a cross-encoder (the query and each candidate are scored
    jointly, not just compared as two separate embeddings).

    This is what fixes cases like reference/citation chunks outranking
    the real answer: a citation line repeats the query's own keywords
    (e.g. "Retrieval-Augmented Generation Research") so it looks close
    in bi-encoder vector space, but a cross-encoder can tell it doesn't
    actually answer "What is Retrieval Augmented Generation?".
    """

    def __init__(self, model_name: str = None):
        print("Re-Ranker Initialized")
        self.model = CrossEncoder(
            model_name or Config.RERANKER_MODEL
        )

    def rerank(self, query, candidates, top_k):
        """
        candidates: list of result dicts, each with a "text" key
                    (the same shape Retriever.retrieve() builds).
        Returns the top_k candidates sorted by cross-encoder score,
        each with an added "rerank_score" field.
        """

        if not candidates:
            return []

        pairs = [
            (query, candidate["text"])
            for candidate in candidates
        ]

        scores = self.model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        candidates.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return candidates[:top_k]
class ReciprocalRankFusion:
    """
    Combines ranked dense and sparse retrieval results using
    Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, k=60):
        if k <= 0:
            raise ValueError("RRF k must be greater than 0.")

        self.k = k

    def fuse(self, result_lists, top_k=None):
        if not result_lists:
            return []

        scores = {}
        candidates = {}

        for result_list in result_lists:
            for rank, result in enumerate(result_list, start=1):
                chunk_id = result.get("chunk_id")

                if chunk_id is None:
                    continue

                rrf_score = 1.0 / (self.k + rank)
                scores[chunk_id] = scores.get(chunk_id, 0.0) + rrf_score

                if chunk_id not in candidates:
                    candidates[chunk_id] = dict(result)

        fused = []

        for chunk_id, candidate in candidates.items():
            candidate["rrf_score"] = scores[chunk_id]
            fused.append(candidate)

        fused.sort(
            key=lambda item: item["rrf_score"],
            reverse=True
        )

        if top_k is not None:
            fused = fused[:top_k]

        return fused

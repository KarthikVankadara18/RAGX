from Embeddings.EmbeddingManager import EmbeddingManager
from Retrieval.BM25Retriever import BM25Retriever
from Retrieval.ReRanker import ReRanker
from Retrieval.RRF import ReciprocalRankFusion
from VectorDB.Faiss_Manager import FAISSManager
from VectorDB.MetaData_Store import MetadataStore
from config import Config
from Observability.Tracer import record_event


class HybridRetriever:
    """
    Hybrid retrieval using dense FAISS search and sparse BM25 search.

    Dense and sparse ranked lists are fused with Reciprocal Rank Fusion
    before the existing CrossEncoder reranker produces the final ranking.
    """

    def __init__(self, rrf_k=60):
        print("Hybrid Retriever Initialized")

        self.embedding_manager = EmbeddingManager()
        self.faiss = FAISSManager()
        self.metadata = MetadataStore()
        self.faiss.load_index()
        self.documents = self.metadata.load()

        self.bm25 = BM25Retriever(self.documents)
        self.rrf = ReciprocalRankFusion(k=rrf_k)
        self.reranker = ReRanker()

    def _dense_retrieve(self, query, candidate_k):
        query_embedding = self.embedding_manager.generate_query_embedding(query)
        scores, indices = self.faiss.search(query_embedding, candidate_k)

        results = []

        for position, index in enumerate(indices[0]):
            if index < 0 or index >= len(self.documents):
                continue

            document = self.documents[index]

            results.append(
                {
                    "chunk_id": document.get("chunk_id"),
                    "text": document.get("text", ""),
                    "metadata": document.get("metadata", {}),
                    "score": float(scores[0][position]),
                    "dense_score": float(scores[0][position]),
                    "retrieval_method": "dense"
                }
            )

        return results

    def retrieve(self, query, top_k=None):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k is None:
            top_k = Config.TOP_K

        candidate_k = max(top_k, Config.CANDIDATE_K)

        record_event("retrieval.start", method="hybrid", top_k=top_k, candidate_k=candidate_k)
        dense_results = self._dense_retrieve(query, candidate_k)
        sparse_results = self.bm25.retrieve(query, candidate_k)
        record_event(
            "retrieval.hybrid_candidates",
            dense_count=len(dense_results),
            sparse_count=len(sparse_results),
        )

        fused_candidates = self.rrf.fuse(
            [dense_results, sparse_results],
            top_k=candidate_k
        )

        results = self.reranker.rerank(
            query,
            fused_candidates,
            top_k
        )

        return results

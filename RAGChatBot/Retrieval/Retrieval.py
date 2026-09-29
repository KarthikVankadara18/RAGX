from RAGChatBot.Retrieval.Hybrid_Search import HybridRetriever


class Retriever(HybridRetriever):
    """Production RAG retriever: FAISS + BM25 + RRF + CrossEncoder."""

    def __init__(self, rrf_k=60):
        super().__init__(rrf_k=rrf_k)

from VectorDB.Faiss_Manager import FAISSManager
from VectorDB.MetaData_Store import MetadataStore
from Embeddings.EmbeddingManager import EmbeddingManager
from Retrieval.RetrievalDeBug import RetrievalDebugger
from Retrieval.ReRanker import ReRanker
from config import Config

class Retriever:

    def __init__(self):
        print("Retriever Initialized")

        self.embedding_manager = (
            EmbeddingManager()
        )

        self.faiss = FAISSManager()
        self.metadata = MetadataStore()
        self.faiss.load_index()
        self.documents = (
            self.metadata.load()
        )
        self.debug = RetrievalDebugger()
        self.reranker = ReRanker()

    def retrieve(
        self,
        query,
        top_k=None
    ):

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        print(
            f"\nQuery: {query}"
        )
        if top_k is None:
            top_k = Config.TOP_K

        # Pull a wider candidate pool from FAISS (cheap, bi-encoder
        # search) and let the cross-encoder reranker pick the real
        # top_k from it. This is what stops keyword-heavy but
        # irrelevant chunks (e.g. citation lists) from being the
        # final answer just because they scored well in vector space.
        candidate_k = max(top_k, Config.CANDIDATE_K)

        query_embedding = (
            self.embedding_manager
            .generate_query_embedding(query)
        )
        scores, indices = (
            self.faiss.search(
                query_embedding,
                candidate_k
            )
        )

        candidates = []

        for position, index in enumerate(indices[0]):

            if index < 0:
                continue

            if index >= len(self.documents):
                continue

            candidate = {
                "chunk_id": self.documents[index]["chunk_id"],
                "text": self.documents[index]["text"],
                "metadata": self.documents[index]["metadata"],
                "score": float(scores[0][position])
            }

            candidates.append(candidate)

        self.debug.print_results(
            scores,
            indices,
            self.documents
        )

        results = self.reranker.rerank(
            query,
            candidates,
            top_k
        )

        self.debug.print_reranked(results)

        return results
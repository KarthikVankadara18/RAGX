from VectorDB.Faiss_Manager import FAISSManager
from VectorDB.MetaData_Store import MetadataStore
from Embeddings.EmbeddingManager import EmbeddingManager
from Retrieval.RetrievalDeBug import RetrievalDebugger
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
        query_embedding = (
            self.embedding_manager
            .generate_query_embedding(query)
        )
        distances, indices = (
            self.faiss.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for position, index in enumerate(indices[0]):

            if index < 0:
                continue

            if index >= len(self.documents):
                continue

            result = {
                "chunk_id": self.documents[index]["chunk_id"],
                "text": self.documents[index]["text"],
                "metadata": self.documents[index]["metadata"],
                "distance": float(distances[0][position])
            }

            results.append(result)

        self.debug.print_results(
            distances,
            indices,
            self.documents
        )

        return results
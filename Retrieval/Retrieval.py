from VectorDB.Faiss_Manager import FAISSManager
from VectorDB.MetaData_Store import MetadataStore
from Embeddings.EmbeddingManager import EmbeddingManager
from Retrieval.RetrievalDeBug import RetrievalDebugger
from config import Config

class Retriever:

    def __init__(self):
        print("Retriever Initialized")

        self.embedding_manager = EmbeddingManager()
        self.faiss = FAISSManager()
        self.metadata = MetadataStore()

        self.faiss.load_index()
        self.documents = self.metadata.load()
        self.debug = RetrievalDebugger()

    def retrieve(self, query):
        print(f"\nQuery: {query}")

        query_embedding = self.embedding_manager.model.encode(query)

        distances, indices = self.faiss.search(
            query_embedding,
            Config.TOP_K
        )

        results = []

        for index in indices[0]:
            results.append(self.documents[index])

        self.debugger.print_results(
            distances,
            indices,
            self.documents
        )

        return results
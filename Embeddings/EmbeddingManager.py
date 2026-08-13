from sentence_transformers import SentenceTransformer
from config import Config
from Embeddings.EmbeddingStat import EmbeddingStatistics

class EmbeddingManager:

    def __init__(self):
        print("Embedding Manager Initialized")
        self.model = SentenceTransformer(
            Config.EMBEDDING_MODEL
        )
        self.embedding_stat = EmbeddingStatistics()

    def generate_embeddings(self, chunks):
        if not chunks:
            raise ValueError(
                "No chunks available for embedding."
            )
        texts = [
            chunk.text
            for chunk in chunks
        ]
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True
        )
        self.embedding_stat.generate_report(
            embeddings
        )
        return embeddings

    def generate_query_embedding(self, query):
        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )
        return self.model.encode(query)
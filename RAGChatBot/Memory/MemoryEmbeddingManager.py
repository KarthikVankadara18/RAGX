from sentence_transformers import SentenceTransformer
from config import Config

class MemoryEmbeddingManager:

    def __init__(self):
        print(
            "Memory Embedding Manager Initialized"
        )
        self.model = SentenceTransformer(
            Config.EMBEDDING_MODEL
        )

    def generate_embedding(
        self,
        text
    ):
        if not text or not text.strip():
            raise ValueError(
                "Memory text cannot be empty."
            )
        embedding = self.model.encode(
            text,
            convert_to_numpy=True
        )
        return embedding

    def generate_embeddings(
        self,
        texts
    ):
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )
        return embeddings

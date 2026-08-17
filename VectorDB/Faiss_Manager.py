import faiss
import numpy as np
from config import Config

class FAISSManager:

    def __init__(self):
        print("FAISS Manager Initialized")
        # Inner product on L2-normalized vectors == cosine similarity.
        # (Previously IndexFlatL2 on un-normalized embeddings, which lets
        # vector magnitude distort the ranking instead of pure direction/
        # semantic similarity.)
        self.index = faiss.IndexFlatIP(
            Config.VECTOR_DIMENSION
        )

    def add_embeddings(self, embeddings):
        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )
        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D array."
            )
        if embeddings.shape[1] != Config.VECTOR_DIMENSION:
            raise ValueError(
                f"Expected embedding dimension "
                f"{Config.VECTOR_DIMENSION}, "
                f"got {embeddings.shape[1]}"
            )
        self.index.add(embeddings)
        print(
            f"{self.index.ntotal} vectors stored."
        )

    def save_index(self):
        faiss.write_index(
            self.index,
            Config.FAISS_INDEX_PATH
        )
        print("FAISS Index Saved.")

    def load_index(self):
        self.index = faiss.read_index(
            Config.FAISS_INDEX_PATH
        )
        print("FAISS Index Loaded.")

    def search(
        self,
        query_embedding,
        top_k
    ):

        if self.index.ntotal == 0:
            raise ValueError(
                "FAISS index is empty."
            )

        top_k = min(
            top_k,
            self.index.ntotal
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32
        )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(
                1, -1
            )

        if query_embedding.shape[1] != Config.VECTOR_DIMENSION:
            raise ValueError(
                f"Expected query dimension "
                f"{Config.VECTOR_DIMENSION}, "
                f"got {query_embedding.shape[1]}"
            )

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )
        return distances, indices
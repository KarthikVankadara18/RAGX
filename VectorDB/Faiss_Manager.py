import faiss
from config import Config
import numpy as np

class FAISSManager:
    def __init__(self):
        print("FAISS Manager Initialized")

        self.index = faiss.IndexFlatL2(
            Config.VECTOR_DIMENSION
        )

    def add_embeddings(self, embeddings):
        embeddings = np.array(
            embeddings,
            dtype=np.float32
        )
        self.index.add(embeddings)
        print(f"{self.index.ntotal} vectors stored.")

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

    def search(self, query_embeddings, top_k):
        query_embeddings= np.array(
            [query_embeddings],
            dtype=np.float32
        )
        distance, indices= self.index.search(
            query_embeddings,
            top_k
        )

        return distance, indices
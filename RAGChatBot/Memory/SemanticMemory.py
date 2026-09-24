import json
import os

import faiss
import numpy as np

from config import Config


class SemanticMemory:

    def __init__(self, embedding_manager):
        print("Semantic Memory Initialized")

        self.embedding_manager = embedding_manager
        self.index = None
        self.memory_ids = []

        self.index_path = Config.MEMORY_FAISS_INDEX_PATH
        self.mapping_path = Config.MEMORY_FAISS_MAPPING_PATH

        for path in (self.index_path, self.mapping_path):
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)

        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            print("Memory FAISS Index Loaded.")
        else:
            self.index = faiss.IndexFlatL2(Config.VECTOR_DIMENSION)
            print("New Memory FAISS Index Created.")

        self._load_mapping()

        if self.index.ntotal != len(self.memory_ids):
            print("Memory FAISS/mapping mismatch detected. Index will require rebuild.")

    def _load_mapping(self):
        if os.path.exists(self.mapping_path):
            try:
                with open(self.mapping_path, "r", encoding="utf-8") as file:
                    self.memory_ids = json.load(file)
            except Exception:
                self.memory_ids = []
        else:
            self.memory_ids = []

    def _save_mapping(self):
        with open(self.mapping_path, "w", encoding="utf-8") as file:
            json.dump(self.memory_ids, file)

    def _persist(self):
        faiss.write_index(self.index, self.index_path)
        self._save_mapping()

    def add_memory(self, memory_id, text):
        embedding = self.embedding_manager.generate_embedding(text)
        vector = np.array([embedding], dtype=np.float32)
        self.index.add(vector)
        self.memory_ids.append(memory_id)
        self._persist()
        print("Memory added to semantic index.")

    def rebuild(self, memories):
        self.index = faiss.IndexFlatL2(Config.VECTOR_DIMENSION)
        self.memory_ids = []

        if memories:
            texts = [memory["content"] for memory in memories]
            embeddings = self.embedding_manager.generate_embeddings(texts)
            embeddings = np.asarray(embeddings, dtype=np.float32)
            self.index.add(embeddings)
            self.memory_ids = [memory["memory_id"] for memory in memories]

        self._persist()
        print(f"Semantic memory index rebuilt: {len(self.memory_ids)} active memories.")

    def search(self, query, top_k=5):
        if self.index.ntotal == 0:
            return []

        if self.index.ntotal != len(self.memory_ids):
            return []

        query_embedding = self.embedding_manager.generate_embedding(query)
        query_embedding = np.array([query_embedding], dtype=np.float32)

        top_k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for position, index in enumerate(indices[0]):
            if index < 0 or index >= len(self.memory_ids):
                continue
            results.append({
                "memory_id": self.memory_ids[index],
                "distance": float(distances[0][position]),
            })

        return results

    def save(self):
        self._persist()
        print("Semantic Memory Saved.")

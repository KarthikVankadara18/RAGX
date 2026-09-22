import re

from rank_bm25 import BM25Okapi

from config import Config


class BM25Retriever:
    """
    Sparse keyword retriever using BM25 over the indexed document chunks.

    Returns candidates in the same basic shape as the dense Retriever so
    the sparse results can later be fused with FAISS results.
    """

    def __init__(self, documents=None):
        print("BM25 Retriever Initialized")

        if documents is None:
            from VectorDB.MetaData_Store import MetadataStore
            documents = MetadataStore().load()

        if not documents:
            raise ValueError("No documents available for BM25 indexing.")

        self.documents = documents
        self.tokenized_documents = [
            self._tokenize(document.get("text", ""))
            for document in documents
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_documents
        )

    @staticmethod
    def _tokenize(text):
        if not text:
            return []

        return re.findall(
            r"(?u)\b\w+\b",
            text.lower()
        )

    def retrieve(self, query, top_k=None):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k is None:
            top_k = Config.TOP_K

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indices:
            score = float(scores[index])

            if score <= 0:
                continue

            document = self.documents[index]

            results.append(
                {
                    "chunk_id": document.get("chunk_id"),
                    "text": document.get("text", ""),
                    "metadata": document.get("metadata", {}),
                    "score": score,
                    "retrieval_method": "bm25"
                }
            )

            if len(results) >= top_k:
                break

        return results

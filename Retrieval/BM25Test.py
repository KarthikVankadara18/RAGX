from Retrieval.BM25Retriever import BM25Retriever


def main():
    documents = [
        {
            "chunk_id": 0,
            "text": "FAISS IndexFlatIP uses inner product search for vector retrieval.",
            "metadata": {"source": "test", "page": 1}
        },
        {
            "chunk_id": 1,
            "text": "Cross Encoder reranking scores query and document pairs jointly.",
            "metadata": {"source": "test", "page": 2}
        },
        {
            "chunk_id": 2,
            "text": "BM25 is a sparse retrieval algorithm based on term frequency and inverse document frequency.",
            "metadata": {"source": "test", "page": 3}
        },
        {
            "chunk_id": 3,
            "text": "Hybrid retrieval combines dense embeddings with sparse keyword retrieval.",
            "metadata": {"source": "test", "page": 4}
        }
    ]

    retriever = BM25Retriever(documents)

    queries = [
        "FAISS IndexFlatIP",
        "sparse retrieval BM25",
        "hybrid retrieval"
    ]

    for query in queries:
        print()
        print("=" * 70)
        print("QUERY:", query)
        print("=" * 70)

        results = retriever.retrieve(query, top_k=3)

        for rank, result in enumerate(results, start=1):
            print(
                f"{rank}. chunk_id={result['chunk_id']} "
                f"score={result['score']:.4f}"
            )
            print("   ", result["text"])

    print()
    print("=" * 70)
    print("BM25 TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()

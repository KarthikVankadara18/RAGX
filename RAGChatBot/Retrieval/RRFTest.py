from Retrieval.RRF import ReciprocalRankFusion

def main():
    dense_results = [
        {"chunk_id": 1, "text": "Dense result one."},
        {"chunk_id": 2, "text": "Dense result two."},
        {"chunk_id": 3, "text": "Dense result three."},
    ]

    sparse_results = [
        {"chunk_id": 3, "text": "Sparse result three."},
        {"chunk_id": 1, "text": "Sparse result one."},
        {"chunk_id": 4, "text": "Sparse result four."},
    ]

    fusion = ReciprocalRankFusion(k=60)
    results = fusion.fuse(
        [dense_results, sparse_results],
        top_k=4
    )

    print("=" * 70)
    print("RRF FUSION TEST")
    print("=" * 70)

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. chunk_id={result['chunk_id']} "
            f"rrf_score={result['rrf_score']:.6f}"
        )

    assert len(results) == 4
    assert len({result["chunk_id"] for result in results}) == 4
    assert results[0]["chunk_id"] == 1
    assert results[0]["rrf_score"] > results[-1]["rrf_score"]

    print("=" * 70)
    print("RRF TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()

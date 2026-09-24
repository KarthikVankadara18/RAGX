from Evaluation.RetrievalEvaluator import RetrievalEvaluator


def main():
    dataset = [
        {"query": "one", "relevant_chunk_ids": [10, 20]},
        {"query": "two", "relevant_chunk_ids": [30]},
    ]
    results = [
        {"chunk_id": 10},
        {"chunk_id": 99},
        {"chunk_id": 20},
    ]
    evaluator = RetrievalEvaluator((1, 3, 5))
    metrics = evaluator.evaluate_query(results, dataset[0]["relevant_chunk_ids"])
    assert metrics["hit@1"] == 1.0
    assert metrics["recall@3"] == 1.0
    assert metrics["precision@3"] == 2 / 3
    assert metrics["mrr@3"] == 1.0
    print("RETRIEVAL EVALUATION TEST PASSED")


if __name__ == "__main__":
    main()

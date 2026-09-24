# RAGX Retrieval Evaluation

This module evaluates the existing baseline retriever against the new
hybrid retriever.

## Metrics

- Hit@K
- Recall@K
- Precision@K
- MRR@K

## Evaluation dataset

Copy the example file:

```text
Evaluation/evaluation_dataset.example.json
```

to:

```text
Evaluation/evaluation_dataset.json
```

Then replace the example queries/relevant chunk IDs with queries and
ground-truth chunk IDs from your actual indexed document collection.

Each item has this structure:

```json
{
    "query": "What is ...?",
    "relevant_chunk_ids": [12, 18]
}
```

`relevant_chunk_ids` must be manually labelled. They represent the chunks
that actually contain the information needed to answer the query.

## First test the evaluator itself

```bash
uv run -m Evaluation.EvaluationTest
```

## Run the real baseline vs hybrid comparison

After creating `evaluation_dataset.json`:

```bash
uv run -m Evaluation.EvaluationRunner
```

The runner compares:

```text
Baseline:
FAISS → CrossEncoder

Hybrid:
FAISS + BM25 → RRF → CrossEncoder
```

Important: the evaluator does not decide what is relevant. Ground-truth
labels must come from the dataset creator. This keeps the evaluation
separate from the retrieval system being evaluated.


Active VENV: .venv\Scripts\activate
Activating MCP: uv run mcp dev MCP/Server.py
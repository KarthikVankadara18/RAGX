import json
import os
from VectorDB.MetaData_Store import MetadataStore


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_root, "Evaluation", "evaluation_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    documents = MetadataStore().load()
    valid_ids = {item["chunk_id"] for item in documents}

    for item in dataset:
        if not item.get("query"):
            raise AssertionError("Evaluation query cannot be empty.")
        if not item.get("relevant_chunk_ids"):
            raise AssertionError(f"No ground-truth chunks for: {item['query']}")
        missing = set(item["relevant_chunk_ids"]) - valid_ids
        if missing:
            raise AssertionError(
                f"Unknown ground-truth chunk IDs for '{item['query']}': {sorted(missing)}"
            )

    print(f"DATASET VALIDATION PASSED: {len(dataset)} queries, {len(valid_ids)} indexed chunks")


if __name__ == "__main__":
    main()

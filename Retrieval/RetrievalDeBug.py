class RetrievalDebugger:

    def print_results(self, distances, indices, metadata):
        print("\n" + "=" * 80)
        print("              Retrieval Debug Report")
        print("=" * 80)

        for rank, (distance, index) in enumerate(zip(distances[0], indices[0]), start=1):
            chunk = metadata[index]

            print(f"\nRank      : {rank}")
            print(f"Distance  : {distance:.4f}")
            print(f"Chunk ID  : {chunk['metadata'].get('chunk_id')}")
            print(f"Page      : {chunk['metadata'].get('page')}")
            print(f"Source    : {chunk['metadata'].get('source')}")

            preview = chunk["text"][:200].replace("\n", " ")
            print(f"Preview   : {preview}")
            print("-" * 80)
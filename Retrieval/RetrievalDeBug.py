class RetrievalDebugger:

    def print_results(self, scores, indices, metadata):
        print("\n" + "=" * 80)
        print("              FAISS Candidate Report (pre-rerank)")
        print("=" * 80)

        for rank, (score, index) in enumerate(zip(scores[0], indices[0]), start=1):
            if index < 0 or index >= len(metadata):
                continue

            chunk = metadata[index]

            print(f"\nRank      : {rank}")
            print(f"Score     : {score:.4f}")
            # chunk_id lives at the top level of the stored record
            # (see MetadataStore.save), not inside 'metadata'.
            print(f"Chunk ID  : {chunk.get('chunk_id')}")
            print(f"Page      : {chunk['metadata'].get('page')}")
            print(f"Section   : {chunk['metadata'].get('section')}")
            print(f"Source    : {chunk['metadata'].get('source')}")

            preview = chunk["text"][:200].replace("\n", " ")
            print(f"Preview   : {preview}")
            print("-" * 80)

    def print_reranked(self, results):
        print("\n" + "=" * 80)
        print("              Reranked Results (final)")
        print("=" * 80)

        for rank, result in enumerate(results, start=1):
            print(f"\nRank         : {rank}")
            print(f"Rerank Score : {result.get('rerank_score'):.4f}")
            print(f"Chunk ID     : {result['chunk_id']}")
            print(f"Page         : {result['metadata'].get('page')}")
            print(f"Section      : {result['metadata'].get('section')}")

            preview = result["text"][:200].replace("\n", " ")
            print(f"Preview      : {preview}")
            print("-" * 80)
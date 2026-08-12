import numpy as np

class EmbeddingStatistics:

    def generate_report(self, embeddings):
        print()

        print("=" * 50)
        print("Embedding Report")
        print("=" * 50)

        print(f"Total Embeddings : {len(embeddings)}")
        print(f"Dimension        : {embeddings.shape[1]}")
        print(f"Minimum Value    : {np.min(embeddings):.4f}")
        print(f"Maximum Value    : {np.max(embeddings):.4f}")

        print("=" * 50)
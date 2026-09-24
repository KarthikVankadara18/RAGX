from config import Config

class ChunkStatistics:

    def __init__(self):
        print("Chunk Statistics Initialized")

    def generate_report(self, chunks):
        if not chunks:
            print("No chunks available.")
            return

        lengths = [len(chunk.page_content) for chunk in chunks]
        total_chunks = len(chunks)
        average_length = sum(lengths) / total_chunks
        largest_chunk = max(lengths)
        smallest_chunk = min(lengths)

        print("\n" + "=" * 50)
        print("           Chunk Report")
        print("=" * 50)
        print(f"Total Chunks      : {total_chunks}")
        print(f"Average Length    : {average_length:.2f} characters")
        print(f"Largest Chunk     : {largest_chunk} characters")
        print(f"Smallest Chunk    : {smallest_chunk} characters")
        print(f"\nConfigured Chunk Size     : {Config.CHUNK_SIZE}")
        print(f"Configured Chunk Overlap  : {Config.CHUNK_OVERLAP}")
        print("=" * 50)
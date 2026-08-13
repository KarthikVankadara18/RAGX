import pickle
from config import Config

class MetadataStore:

    def __init__(self):
        print("Metadata Store Initialized")

    def save(self, chunks):
        metadata = []
        for chunk in chunks:
            metadata.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata
                }
            )
        with open(
            Config.METADATA_PATH,
            "wb"
        ) as file:
            pickle.dump(
                metadata,
                file
            )
        print("Metadata Saved.")

    def load(self):
        with open(
            Config.METADATA_PATH,
            "rb"
        ) as file:
            metadata = pickle.load(
                file
            )

        return metadata

    def get_by_ids(self, indices):
        metadata = self.load()
        results = []
        for index in indices:
            if index < 0:
                continue
            if index >= len(metadata):
                continue
            results.append(
                metadata[index]
            )
        return results
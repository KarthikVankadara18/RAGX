import pickle
from config import Config

class MetadataStore:

    def __init__(self):
        print("Metadata Store Initialized")

    def save(self, chunks):
        metadata = []
        for chunk in chunks:
            metadata.append({
                "text": chunk.page_content,
                "metadata": chunk.metadata
            })

        with open(
            Config.METADATA_PATH,
            "wb"
        ) as file:
            pickle.dump(metadata, file)
        print("Metadata Saved.")

    def load(self):
        with open(
            Config.METADATA_PATH,
            "rb"
        ) as file:
            metadata = pickle.load(file)
        return metadata
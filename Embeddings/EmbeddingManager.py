from sentence_transformers import SentenceTransformer
from config import Config
from Embeddings.EmbeddingStat import EmbeddingStatistics

class EmbeddingManager:
    def __init__(self):
        print("Here takes places the embedding layer")
        self.model = SentenceTransformer(
            Config.EMBEDDING_MODEL
        )
        self.embedding_stat= EmbeddingStatistics()

    def GenerateEmbeeding(self, chunks):
        text=[ 
            chunk.page_content
            for chunk in chunks
        ]
        embeddings= self.model.encode(
            text,
            show_progress_bar= True
        )
        self.embedding_stat.generate_report(embeddings)
        return embeddings
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # print(GROQ_API_KEY)

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    CHUNK_SIZE = 500

    CHUNK_OVERLAP = 100

    TOP_K = 5

    CANDIDATE_K = 20

    VECTOR_DIMENSION = 384

    FAISS_INDEX_PATH = "Data/VectorDB/faiss.index"

    METADATA_PATH = "Data/VectorDB/metadata.pkl"

    RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    EXCLUDE_UNNUMBERED_MAJOR_SECTIONS = True
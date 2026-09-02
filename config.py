from dotenv import load_dotenv
import os

load_dotenv()

class Config:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    GROQ_TEMPERATURE = float(
        os.getenv("GROQ_TEMPERATURE", "0.2")
    )

    MONGODB_URI = os.getenv(
        "MONGODB_URI"
    )

    MONGODB_DATABASE = os.getenv(
        "MONGODB_DATABASE",
        "ragx"
    )

    MONGODB_COLLECTION = os.getenv(
        "MONGODB_COLLECTION",
        "conversation_memory"
    )

    GROQ_MAX_TOKENS = int(
        os.getenv("GROQ_MAX_TOKENS", "1024")
    )

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    VECTOR_DIMENSION = 384

    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100
    MIN_CHUNK_CHARS = 40

    TOP_K = 5
    CANDIDATE_K = 20

    RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    MIN_RERANK_SCORE = 0.0

    CONTEXT_DEDUP_THRESHOLD = 0.85
    EXCLUDE_UNNUMBERED_MAJOR_SECTIONS = True

    FAISS_INDEX_PATH = "Data/VectorDB/faiss.index"
    METADATA_PATH = "Data/VectorDB/metadata.pkl"

    MEMORY_FAISS_INDEX_PATH = (
        "Data/Memory/memory.index"
    )
    MEMORY_FAISS_MAPPING_PATH = (
        "Data/Memory/memory_mapping.json"
    )
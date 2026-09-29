from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(BASE_DIR / ".env")


class Config:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))

    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "ragx")
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "conversation_memory")
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1024"))

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DIMENSION = 384
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100
    MIN_CHUNK_CHARS = 40
    TOP_K = 5
    CANDIDATE_K = 20
    RRF_K = 60
    RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    MIN_RERANK_SCORE = 0.0
    CONTEXT_DEDUP_THRESHOLD = 0.85
    EXCLUDE_UNNUMBERED_MAJOR_SECTIONS = True

    DATA_DIR = BASE_DIR / "Data"
    FAISS_INDEX_PATH = str(DATA_DIR / "VectorDB" / "faiss.index")
    METADATA_PATH = str(DATA_DIR / "VectorDB" / "metadata.pkl")
    MEMORY_FAISS_INDEX_PATH = str(DATA_DIR / "Memory" / "memory.index")
    MEMORY_FAISS_MAPPING_PATH = str(DATA_DIR / "Memory" / "memory_mapping.json")

    EXTERNAL_REQUEST_TIMEOUT = float(os.getenv("EXTERNAL_REQUEST_TIMEOUT", "10"))
    MAX_EXTERNAL_CONTENT_CHARS = int(os.getenv("MAX_EXTERNAL_CONTENT_CHARS", "20000"))

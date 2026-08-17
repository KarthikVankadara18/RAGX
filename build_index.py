"""
Ingestion entrypoint: loads PDFs, chunks them, embeds the chunks, and
writes the FAISS index + metadata store to disk.

This was missing from the project - main.py only does retrieval against
an already-built index. Run this first (or any time you add/change
source PDFs) before running main.py.

Usage:
    python build_index.py                      # ingest everything in Data/PDF
    python build_index.py path/to/one_file.pdf  # ingest a single file
"""

import sys
from pathlib import Path

from DocumentManger.DocumentManger import DocManger
from Embeddings.EmbeddingManager import EmbeddingManager
from VectorDB.Faiss_Manager import FAISSManager
from VectorDB.MetaData_Store import MetadataStore
from config import Config


def get_pdf_paths(cli_args):
    if cli_args:
        return [Path(p) for p in cli_args]

    pdf_dir = Path("Data/PDF")
    if not pdf_dir.exists():
        raise FileNotFoundError(
            f"No PDFs given and '{pdf_dir}' does not exist. "
            f"Put your PDFs in Data/PDF/ or pass a path as an argument."
        )

    pdf_paths = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No .pdf files found in '{pdf_dir}'.")

    return pdf_paths


def main():
    pdf_paths = get_pdf_paths(sys.argv[1:])

    Path(Config.FAISS_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)

    doc_manager = DocManger()
    embedding_manager = EmbeddingManager()
    faiss_manager = FAISSManager()
    metadata_store = MetadataStore()

    all_chunks = []

    for pdf_path in pdf_paths:
        print(f"\n{'=' * 60}\nIngesting: {pdf_path}\n{'=' * 60}")

        profile = doc_manager.load_documents(str(pdf_path))

        print(f"{len(profile.chunks)} chunks created from {pdf_path.name}")

        all_chunks.extend(profile.chunks)

    if not all_chunks:
        raise ValueError("No chunks were produced from any input PDF.")

    # Re-number chunk_ids sequentially across ALL ingested files so
    # chunk_id always matches this chunk's position in both the FAISS
    # index and metadata.pkl (they must stay in the same order).
    for new_id, chunk in enumerate(all_chunks):
        chunk.chunk_id = new_id
        chunk.metadata["chunk_id"] = new_id

    embeddings = embedding_manager.generate_embeddings(all_chunks)

    faiss_manager.add_embeddings(embeddings)
    faiss_manager.save_index()

    metadata_store.save(all_chunks)

    print(f"\nDone. Indexed {len(all_chunks)} chunks from {len(pdf_paths)} file(s).")


if __name__ == "__main__":
    main()
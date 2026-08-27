from Retrieval.Retrieval import Retriever

retriever = Retriever()

def search_documents(query: str):

    if not query or not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    results = retriever.retrieve(
        query,
        top_k=5
    )

    return [
        {
            "text": result["text"],
            "page": result["metadata"].get("page"),
            "section": result["metadata"].get("section"),
            "subsection": result["metadata"].get("subsection")
        }
        for result in results
    ]
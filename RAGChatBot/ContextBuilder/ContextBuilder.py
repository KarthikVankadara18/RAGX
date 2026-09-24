class ContextBuilder:
    
    def __init__(self):
        print("Context Builder Initialized")

    def build(self, results):

        if not results:
            raise ValueError(
                "No retrieval results available."
            )

        context_parts = []
        sources = []

        for position, result in enumerate(
            results,
            start=1
        ):

            chunk_id = result["chunk_id"]
            text = result["text"]
            metadata = result["metadata"]

            page = metadata.get("page")
            section = metadata.get("section")
            subsection = metadata.get(
                "subsection"
            )

            context_block = (
                f"[Source {position}]\n"
                f"Page: {page}\n"
                f"Section: {section}\n"
                f"Subsection: {subsection}\n"
                f"Chunk ID: {chunk_id}\n\n"
                f"{text}"
            )

            context_parts.append(
                context_block
            )

            sources.append(
                {
                    "source_number": position,
                    "chunk_id": chunk_id,
                    "page": page,
                    "section": section,
                    "subsection": subsection
                }
            )

        context = "\n\n".join(
            context_parts
        )

        return {
            "context": context,
            "sources": sources
        }
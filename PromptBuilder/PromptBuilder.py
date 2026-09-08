class PromptBuilder:

    def __init__(self):
        print("Prompt Builder Initialized")

    def build(
        self,
        query,
        context_results
    ):

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if not context_results:
            raise ValueError(
                "No context available."
            )

        context = self.build_context(
            context_results
        )

        return {
            "prompt": self._build_prompt(
                query=query,
                context=context,
            ),
            "sources": self.build_sources(
                context_results
            ),
        }

    def build_context(self, results):

        if not results:
            raise ValueError(
                "No context results available."
            )

        context_parts = []

        for position, result in enumerate(
            results,
            start=1
        ):

            metadata = result.get(
                "metadata",
                {}
            )

            page = metadata.get(
                "page"
            )

            section = metadata.get(
                "section"
            )

            subsection = metadata.get(
                "subsection"
            )

            chunk_id = result.get(
                "chunk_id"
            )

            text = result.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            context_parts.append(
                f"""
[Source {position}]
Chunk ID: {chunk_id}
Page: {page}
Section: {section}
Subsection: {subsection}

{text}
""".strip()
            )

        if not context_parts:
            raise ValueError(
                "No usable document text found."
            )

        return "\n\n".join(
            context_parts
        )

    def _build_prompt(
        self,
        query,
        context
    ):

        prompt = f"""
You are a document-grounded AI assistant.

Answer the user's question using only
the information provided in the document context.

Rules:

1. Do not invent or assume information.
2. If the document context does not contain
   enough information to answer the question,
   clearly say that the information is not
   available in the provided documents.
3. Prefer the most relevant and specific
   information from the context.
4. Keep the answer clear and concise.
5. Preserve important source information
   when appropriate.

---------------- DOCUMENT CONTEXT ----------------

{context}

-------------- END DOCUMENT CONTEXT --------------

USER QUESTION:

{query}

ANSWER:
""".strip()

        return prompt

    def build_sources(self, results):

        sources = []

        for position, result in enumerate(
            results,
            start=1
        ):

            metadata = result.get(
                "metadata",
                {}
            )

            sources.append(
                {
                    "source_number": position,
                    "chunk_id": result.get(
                        "chunk_id"
                    ),
                    "page": metadata.get(
                        "page"
                    ),
                    "section": metadata.get(
                        "section"
                    ),
                    "subsection": metadata.get(
                        "subsection"
                    ),
                    "source": metadata.get(
                        "source"
                    ),
                }
            )

        return sources
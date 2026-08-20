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

        context = self._build_context(
            context_results
        )

        prompt = self._build_prompt(
            query,
            context
        )

        return {
            "prompt": prompt,
            "sources": self._build_sources(
                context_results
            )
        }

    def _build_context(self, results):

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
        the information provided in the context.

        Rules:

        1. Do not invent or assume information.
        2. If the context does not contain enough
        information to answer the question,
        clearly say that the information is not
        available in the provided document.
        3. Prefer the most relevant and specific
        information from the context.
        4. Keep the answer clear and concise.
        5. Preserve important source information
        so the answer can be traced back to the
        document.

        ---------------- CONTEXT ----------------

        {context}

        -------------- END CONTEXT --------------

        USER QUESTION:

        {query}

        ANSWER:
        """.strip()

        return prompt

    def _build_sources(self, results):

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
                    )
                }
            )

        return sources
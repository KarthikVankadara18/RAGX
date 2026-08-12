class MetadataEnricher:

    def enrich(self, chunks, profile):
        for index, chunk in enumerate(chunks):

            chunk.metadata["chunk_id"] = index
            chunk.metadata["document_type"] = (
                profile.document_type
            )
            chunk.metadata["title"] = profile.title
            chunk.metadata["source"] = profile.file_path
            chunk.metadata["chunk_length"] = (
                len(chunk.page_content)
            )
        return chunks
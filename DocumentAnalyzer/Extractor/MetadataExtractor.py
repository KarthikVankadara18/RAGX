class MetadataExtractor:

    def extract(self, documents):

        metadata = {}
        metadata["title"] = self.title_extractor.extract(
            documents
        )
        metadata["authors"] = self.author_extractor.extract(
            documents
        )
        return metadata
from langchain_text_splitters import RecursiveCharacterTextSplitter

from Chunking.Chunk import Chunk


class ChunkManager:

    def __init__(
        self,
        chunk_size=800,
        chunk_overlap=120
    ):

        print("Chunk Manager Initialized")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=[
                    "\n\n",
                    "\n",
                    ". ",
                    " ",
                    ""
                ]
            )
        )

    def create_chunks(self, profile):

        if not profile.documents:
            raise ValueError(
                "No documents available for chunking."
            )

        chunks = []

        chunk_id = 0

        for page_number, document in enumerate(
            profile.documents,
            start=1
        ):

            text = document.page_content.strip()

            if not text:
                continue

            sections = self.build_page_sections(
                profile,
                page_number,
                text
            )

            for section_data in sections:

                section_text = section_data["text"]

                section = section_data["section"]

                subsection = section_data["subsection"]

                page_chunks = self.splitter.split_text(
                    section_text
                )

                for chunk_text in page_chunks:

                    chunk_text = chunk_text.strip()

                    if not chunk_text:
                        continue

                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            text=chunk_text,
                            metadata={
                                "source": profile.file_path,
                                "page": page_number,
                                "document_type": profile.document_type,
                                "section": section,
                                "subsection": subsection
                            }
                        )
                    )

                    chunk_id += 1

        profile.chunks = chunks

        return profile

    def build_page_sections(
        self,
        profile,
        page_number,
        text
    ):

        page_sections = []

        page_metadata = [
            section
            for section in profile.sections
            if section.page == page_number
        ]

        if not page_metadata:

            return [
                {
                    "text": text,
                    "section": None,
                    "subsection": None
                }
            ]

        boundaries = []

        for section in page_metadata:

            if not section.heading:
                continue

            position = text.lower().find(
                section.heading.lower()
            )

            if position == -1:
                continue

            boundaries.append(
                {
                    "position": position,
                    "section": section
                }
            )

        boundaries.sort(
            key=lambda item: item["position"]
        )

        if not boundaries:

            return [
                {
                    "text": text,
                    "section": None,
                    "subsection": None
                }
            ]

        for index, boundary in enumerate(
            boundaries
        ):

            section = boundary["section"]

            start = boundary["position"]

            if index + 1 < len(boundaries):

                end = boundaries[index + 1]["position"]

            else:

                end = len(text)

            section_text = text[start:end].strip()

            if not section_text:
                continue

            if section.section_type == "major":

                page_sections.append(
                    {
                        "text": section_text,
                        "section": section.name,
                        "subsection": None
                    }
                )

            else:

                page_sections.append(
                    {
                        "text": section_text,
                        "section": section.parent,
                        "subsection": section.name
                    }
                )

        return page_sections
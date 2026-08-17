from langchain_text_splitters import RecursiveCharacterTextSplitter

from Chunking.Chunk import Chunk
from config import Config


class ChunkManager:

    def __init__(
        self,
        chunk_size=None,
        chunk_overlap=None
    ):
        chunk_size = chunk_size or Config.CHUNK_SIZE
        chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP

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

        # Tracks whichever section/subsection was still "open" when we
        # finished the previous page, so a continuation page that has
        # no heading of its own doesn't lose its place in the
        # document's structure (previously it silently fell back to
        # section=None on every page without its own heading).
        running_state = {
            "section": None,
            "subsection": None,
            "is_unnumbered_major": False
        }

        for page_number, document in enumerate(
            profile.documents,
            start=1
        ):

            text = document.page_content.strip()

            if not text:
                continue

            sections, running_state = self.build_page_sections(
                profile,
                page_number,
                text,
                running_state
            )

            for section_data in sections:

                section_text = section_data["text"]

                section = section_data["section"]

                subsection = section_data["subsection"]

                is_unnumbered_major = section_data["is_unnumbered_major"]

                # Exclude sections that were detected as unnumbered
                # major headings (e.g. a References/Bibliography/
                # Appendix block, which - unlike "I. INTRODUCTION" or
                # "II. ARCHITECTURE" - has no roman numeral in front of
                # it). This is a structural fact already extracted by
                # DocumentAnalyzer.detect_sections() (SectionInfo.number
                # is None for these), not a hardcoded name lookup - so
                # it works regardless of what the section is literally
                # titled.
                if (
                    Config.EXCLUDE_UNNUMBERED_MAJOR_SECTIONS
                    and is_unnumbered_major
                ):
                    continue

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
                                "chunk_id": chunk_id,
                                "source": profile.file_path,
                                "page": page_number,
                                "document_type": profile.document_type,
                                "section": section,
                                "subsection": subsection,
                                "is_unnumbered_major": is_unnumbered_major
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
        text,
        running_state
    ):

        page_sections = []

        page_metadata = [
            section
            for section in profile.sections
            if section.page == page_number
        ]

        if not page_metadata:

            # No heading starts anywhere on this page - the entire
            # page is a continuation of whatever section was already
            # open coming in from the previous page.
            page_sections.append(
                {
                    "text": text,
                    "section": running_state["section"],
                    "subsection": running_state["subsection"],
                    "is_unnumbered_major": running_state["is_unnumbered_major"]
                }
            )

            return page_sections, running_state

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

            page_sections.append(
                {
                    "text": text,
                    "section": running_state["section"],
                    "subsection": running_state["subsection"],
                    "is_unnumbered_major": running_state["is_unnumbered_major"]
                }
            )

            return page_sections, running_state

        # Anything on this page BEFORE its first detected heading is
        # still part of whatever section was open coming into the
        # page (previously this leading text was silently dropped -
        # it fell outside every boundary's [start, end) range).
        leading_text = text[:boundaries[0]["position"]].strip()

        if leading_text:

            page_sections.append(
                {
                    "text": leading_text,
                    "section": running_state["section"],
                    "subsection": running_state["subsection"],
                    "is_unnumbered_major": running_state["is_unnumbered_major"]
                }
            )

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

            # A major section with no number (SectionInfo.number is
            # None) is the structural signature of an unnumbered
            # trailing section like References/Bibliography/Appendix -
            # extracted from the document itself, not matched against
            # a hardcoded name list.
            is_unnumbered_major = (
                section.section_type == "major"
                and section.number is None
            )

            if section.section_type == "major":

                page_sections.append(
                    {
                        "text": section_text,
                        "section": section.name,
                        "subsection": None,
                        "is_unnumbered_major": is_unnumbered_major
                    }
                )

                running_state = {
                    "section": section.name,
                    "subsection": None,
                    "is_unnumbered_major": is_unnumbered_major
                }

            else:

                page_sections.append(
                    {
                        "text": section_text,
                        "section": section.parent,
                        "subsection": section.name,
                        "is_unnumbered_major": is_unnumbered_major
                    }
                )

                running_state = {
                    "section": section.parent,
                    "subsection": section.name,
                    "is_unnumbered_major": is_unnumbered_major
                }

        return page_sections, running_state
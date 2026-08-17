import re

from Models.DocumentProfile import SectionInfo


class DocumentAnalyzer:

    def __init__(self):
        print("Document Analyzer Initialized")

    def analyze(self, profile):

        if not profile.documents:
            raise ValueError(
                "No documents available for analysis."
            )

        # Combine all pages into one text string
        full_text = "\n".join(
            document.page_content
            for document in profile.documents
        )

        # Debug document structure
        self.debug_lines(full_text)

        # Detect document type
        profile.document_type = (
            self.detect_document_type(full_text)
        )

        # Extract PDF metadata
        metadata = self.extract(profile)

        profile.title = metadata["title"]
        profile.authors = metadata["authors"]
        profile.creation_date = metadata["creation_date"]
        profile.subject = metadata["subject"]
        profile.keywords = metadata["keywords"]

        # Detect sections
        profile.sections = self.detect_sections(
            profile.documents
        )

        return profile

    # ---------------------------------------------------------
    # METADATA EXTRACTION
    # ---------------------------------------------------------

    def extract(self, profile):

        if not profile.documents:
            raise ValueError(
                "No documents available for metadata extraction."
            )

        metadata = profile.documents[0].metadata

        title = self._clean_value(
            metadata.get("title")
        )

        author = self._clean_value(
            metadata.get("author")
        )

        result = {
            "title": title,
            "authors": self._extract_authors(author),
            "creation_date": self._clean_value(
                metadata.get("creationdate")
            ),
            "subject": self._clean_value(
                metadata.get("subject")
            ),
            "keywords": self._extract_keywords(
                metadata.get("keywords")
            ),
            "sources": {}
        }

        if title:
            result["sources"]["title"] = "pdf_metadata"

        if author:
            result["sources"]["authors"] = "pdf_metadata"

        return result

    # ---------------------------------------------------------
    # DOCUMENT TYPE
    # ---------------------------------------------------------

    def detect_document_type(self, text):

        text_lower = text.lower()

        if (
            "abstract" in text_lower
            and "references" in text_lower
        ):
            return "research_paper"

        if (
            "api" in text_lower
            and (
                "endpoint" in text_lower
                or "request" in text_lower
                or "response" in text_lower
            )
        ):
            return "api_documentation"

        if (
            "employee" in text_lower
            and (
                "leave policy" in text_lower
                or "attendance" in text_lower
            )
        ):
            return "hr_policy"

        return "general_document"

    # ---------------------------------------------------------
    # SECTION DETECTION
    # ---------------------------------------------------------

    def detect_sections(self, documents):

        sections = []

        current_major_section = None

        # ---------------------------------------------------------
        # Major section
        #
        # Example:
        # I. INTRODUCTION
        # II. UNDERSTANDING RAG ARCHITECTURE
        # III. STEP-BY-STEP IMPLEMENTATION GUIDE
        # ---------------------------------------------------------

        major_pattern = re.compile(
            r"^\s*"
            r"(?P<number>"
            r"I|II|III|IV|V|VI|VII|VIII|IX|X|XI"
            r")"
            r"\.\s+"
            r"(?P<name>[A-Z][A-Z\s\-&]+)"
            r"\s*$",
            re.MULTILINE
        )

        # ---------------------------------------------------------
        # Subsection
        #
        # Example:
        # 2.1. Core Components
        # 2.2. Retrieval System Design
        # 3.1. Phase 1: Data Preparation and Knowledge Base Creation
        # ---------------------------------------------------------

        subsection_pattern = re.compile(
            r"^\s*"
            r"(?P<number>\d+\.\d+)"
            r"\.\s+"
            r"(?P<name>.+?)"
            r"\s*$",
            re.MULTILINE
        )

        # ---------------------------------------------------------
        # Standalone major sections that never carry a roman numeral,
        # e.g. REFERENCES / BIBLIOGRAPHY / APPENDIX. Previously these
        # were invisible to detect_sections(), so a References page
        # silently inherited whatever numbered section came before it
        # and could never be identified/filtered downstream.
        # ---------------------------------------------------------

        standalone_major_pattern = re.compile(
            r"^\s*"
            r"(?P<name>REFERENCES|BIBLIOGRAPHY|WORKS CITED|APPENDIX(?:\s+[A-Z0-9]+)?)"
            r"\s*$",
            re.MULTILINE
        )

        for page_number, document in enumerate(
            documents,
            start=1
        ):

            text = document.page_content

            # -----------------------------------------------------
            # Find ALL headings on this page
            # -----------------------------------------------------

            headings = []

            for match in major_pattern.finditer(text):

                headings.append(
                    (
                        match.start(),
                        "major",
                        match
                    )
                )

            for match in subsection_pattern.finditer(text):

                headings.append(
                    (
                        match.start(),
                        "subsection",
                        match
                    )
                )

            for match in standalone_major_pattern.finditer(text):

                headings.append(
                    (
                        match.start(),
                        "standalone_major",
                        match
                    )
                )

            # Important:
            # Process headings in the order they appear.
            headings.sort(
                key=lambda item: item[0]
            )

            # -----------------------------------------------------
            # Process headings
            # -----------------------------------------------------

            for _, heading_type, match in headings:

                section_number = (
                    match.group("number").strip()
                    if heading_type != "standalone_major"
                    else None
                )

                section_name = (
                    match.group("name").strip()
                )

                section_name = re.sub(
                    r"\s+",
                    " ",
                    section_name
                )

                if not section_name:
                    continue

                # =================================================
                # MAJOR SECTION
                # =================================================

                if heading_type == "major":

                    current_major_section = (
                        section_name
                    )

                    heading = (
                        f"{section_number}. "
                        f"{section_name}"
                    )

                    sections.append(
                        SectionInfo(
                            name=section_name,
                            page=page_number,
                            section_type="major",
                            parent=None,
                            number=section_number,
                            heading=heading
                        )
                    )

                # =================================================
                # STANDALONE MAJOR SECTION (no roman numeral)
                # =================================================

                elif heading_type == "standalone_major":

                    current_major_section = (
                        section_name
                    )

                    sections.append(
                        SectionInfo(
                            name=section_name,
                            page=page_number,
                            section_type="major",
                            parent=None,
                            number=None,
                            heading=section_name
                        )
                    )

                # =================================================
                # SUBSECTION
                # =================================================

                else:

                    heading = (
                        f"{section_number}. "
                        f"{section_name}"
                    )

                    sections.append(
                        SectionInfo(
                            name=section_name,
                            page=page_number,
                            section_type="subsection",
                            parent=current_major_section,
                            number=section_number,
                            heading=heading
                        )
                    )

        return sections
    #---------------------------------------------------------
    # CLEANING HELPERS
    # ---------------------------------------------------------

    def _clean_value(self, value):

        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        return value if value else None

    def _extract_authors(self, author):

        if not author:
            return []

        # Handle common PDF metadata formats
        authors = re.split(
            r"\s*;\s*|\s*,\s*|\s+and\s+",
            author
        )

        return [
            item.strip()
            for item in authors
            if item.strip()
        ]

    def _extract_keywords(self, keywords):

        if not keywords:
            return []

        if not isinstance(keywords, str):
            keywords = str(keywords)

        keywords = keywords.replace(
            ";",
            ","
        )

        return [
            keyword.strip()
            for keyword in keywords.split(",")
            if keyword.strip()
        ]

    # ---------------------------------------------------------
    # DEBUG
    # ---------------------------------------------------------

    def debug_lines(self, text):

        print("\n" + "=" * 60)
        print("DOCUMENT STRUCTURE DEBUG")
        print("=" * 60)

        for number, line in enumerate(
            text.splitlines(),
            start=1
        ):

            cleaned_line = line.strip()

            if cleaned_line:
                print(
                    f"{number:03d}: {cleaned_line}"
                )

        print("=" * 60)
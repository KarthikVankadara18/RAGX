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
        # Detect major and subsection headings
        # in the order they appear in the document
        # ---------------------------------------------------------

        heading_pattern = re.compile(
            r"""
            (?:
                # Major section
                (?P<major_number>
                    I|II|III|IV|V|VI|VII|VIII|IX|X|XI
                )
                \.\s+
                (?P<major_name>
                    [A-Z][A-Z\-&]*
                    (?:\s+[A-Z][A-Z\-&]*)*
                )

                |

                # Subsection
                (?P<sub_number>
                    \d+\.\d+
                )
                \.\s+
                (?P<sub_name>
                    [A-Z][A-Za-z0-9\-:&]*
                    (?:\s+[A-Za-z0-9][A-Za-z0-9\-:&]*){0,15}
                )
            )
            """,
            re.VERBOSE
        )

        for page_number, document in enumerate(
            documents,
            start=1
        ):

            text = document.page_content

            # -----------------------------------------------------
            # Find headings in document order
            # -----------------------------------------------------

            for match in heading_pattern.finditer(text):

                # =================================================
                # MAJOR SECTION
                # =================================================

                if match.group("major_number"):

                    section_number = (
                        match.group("major_number")
                    )

                    section_name = (
                        match.group("major_name")
                    )

                    section_name = re.sub(
                        r"\s+",
                        " ",
                        section_name.strip()
                    )

                    if not section_name:
                        continue

                    current_major_section = section_name

                    sections.append(
                        SectionInfo(
                            name=section_name,
                            page=page_number,
                            section_type="major",
                            parent=None,
                            number=section_number
                        )
                    )

                # =================================================
                # SUBSECTION
                # =================================================

                elif match.group("sub_number"):

                    subsection_number = (
                        match.group("sub_number")
                    )

                    subsection_name = (
                        match.group("sub_name")
                    )

                    subsection_name = re.sub(
                        r"\s+",
                        " ",
                        subsection_name.strip()
                    )

                    if not subsection_name:
                        continue

                    sections.append(
                        SectionInfo(
                            name=subsection_name,
                            page=page_number,
                            section_type="subsection",
                            parent=current_major_section,
                            number=subsection_number
                        )
                    )

        return sections
    # ---------------------------------------------------------
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

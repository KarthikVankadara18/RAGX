from dataclasses import dataclass, field
from typing import Any


@dataclass
class SectionInfo:

    name: str
    page: int | None = None
    section_type: str = "major"
    parent: str | None = None
    number: str | None = None
    heading: str | None = None

@dataclass
class DocumentProfile:

    file_path: str
    document_type: str | None = None
    title: str | None = None

    authors: list[str] = field(
        default_factory=list
    )

    creation_date: str | None = None
    subject: str | None = None

    keywords: list[str] = field(
        default_factory=list
    )
    sections: list[SectionInfo] = field(
        default_factory=list
    )
    documents: list[Any] = field(
        default_factory=list
    )
    chunks: list[Any] = field(
        default_factory=list
    )
    embeddings: Any = None
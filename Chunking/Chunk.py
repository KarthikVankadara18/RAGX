from dataclasses import dataclass, field

@dataclass
class Chunk:

    chunk_id: int
    text: str
    metadata: dict = field(
        default_factory=dict
    )
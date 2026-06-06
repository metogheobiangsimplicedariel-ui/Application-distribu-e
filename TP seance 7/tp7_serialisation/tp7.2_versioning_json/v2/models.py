from dataclasses import dataclass, field
from typing import List


@dataclass
class DocumentV2:
    id: int
    title: str
    author: str
    tags: List[str] = field(default_factory=list)
    classification: str = "internal"

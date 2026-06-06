from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Document:
    id: int
    title: str
    author: str
    tags: List[str] = field(default_factory=list)
    classification: str = "internal"
    created_at: Optional[str] = None


@dataclass
class UserPublic:
    username: str
    display_name: str
    role: str

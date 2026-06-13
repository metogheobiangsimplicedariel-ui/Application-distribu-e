from dataclasses import dataclass


@dataclass
class DocumentV1:
    id: int
    title: str
    author: str

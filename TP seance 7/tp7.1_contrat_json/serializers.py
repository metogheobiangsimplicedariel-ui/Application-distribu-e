import json
from dataclasses import asdict
from models import Document, UserPublic

EXCLUDED_FIELDS = set()


def serialize_document(doc: Document) -> str:
    data = {k: v for k, v in asdict(doc).items() if k not in EXCLUDED_FIELDS}
    return json.dumps(data, ensure_ascii=False)


def serialize_user(user: UserPublic) -> str:
    data = {k: v for k, v in asdict(user).items() if k not in EXCLUDED_FIELDS}
    return json.dumps(data, ensure_ascii=False)

import json
from .models import DocumentV2


def serialize_document_v2(doc: DocumentV2) -> str:
    return json.dumps({
        "id": doc.id,
        "title": doc.title,
        "author": doc.author,
        "tags": doc.tags,
        "classification": doc.classification,
    }, ensure_ascii=False)

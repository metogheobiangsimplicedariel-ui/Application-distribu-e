import json


def deserialize_document_v1(raw: str):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide : {e}")

    if "id" not in data:
        raise ValueError("Champ 'id' manquant")
    if "title" not in data:
        raise ValueError("Champ 'title' manquant")
    if "author" not in data:
        raise ValueError("Champ 'author' manquant")

    if not isinstance(data["id"], int):
        raise ValueError("'id' doit etre un entier")
    if not isinstance(data["title"], str):
        raise ValueError("'title' doit etre une chaine")
    if not isinstance(data["author"], str):
        raise ValueError("'author' doit etre une chaine")

    from .models import DocumentV1
    return DocumentV1(
        id=data["id"],
        title=data["title"],
        author=data["author"],
    )

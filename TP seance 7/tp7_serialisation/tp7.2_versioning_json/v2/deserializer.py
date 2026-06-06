import json
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "secret"}


def deserialize_document_v2(raw: str):
    errors = []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("JSON invalide : %s", e)
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    for field in ("id", "title", "author"):
        if field not in data:
            errors.append(f"Champ obligatoire manquant : {field}")

    if "id" in data and not isinstance(data["id"], int):
        errors.append("'id' doit etre un entier")

    if "title" in data and not isinstance(data["title"], str):
        errors.append("'title' doit etre une chaine")

    if "author" in data and not isinstance(data["author"], str):
        errors.append("'author' doit etre une chaine")

    tags = data.get("tags", [])
    if not isinstance(tags, list):
        errors.append("'tags' doit etre une liste")
    elif not all(isinstance(t, str) for t in tags):
        errors.append("Tous les tags doivent etre des chaines")

    classification = data.get("classification", "internal")
    if not isinstance(classification, str):
        errors.append("'classification' doit etre une chaine")
    elif classification not in ALLOWED_CLASSIFICATIONS:
        errors.append(f"'classification' invalide : {classification}")

    if errors:
        logger.warning("Validation echouee : %s", errors)
        raise ValueError("Payload invalide")

    from .models import DocumentV2
    return DocumentV2(
        id=data["id"],
        title=data["title"].strip(),
        author=data["author"].strip(),
        tags=tags,
        classification=classification,
    )

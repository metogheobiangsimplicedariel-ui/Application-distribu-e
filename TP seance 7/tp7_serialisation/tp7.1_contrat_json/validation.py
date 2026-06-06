import json
import re
import logging
from typing import List, Optional
from models import Document, UserPublic

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "secret"}
MAX_TITLE_LEN = 200
MAX_AUTHOR_LEN = 100
MAX_TAGS = 20
MAX_TAG_LEN = 50
MAX_USERNAME_LEN = 30
MIN_USERNAME_LEN = 3
MAX_DISPLAY_NAME_LEN = 100
ALLOWED_ROLES = {"viewer", "editor", "admin"}
ALLOWED_USERNAME_CHARS = r"^[a-zA-Z0-9_]+$"


def validate_document(data: dict) -> dict:
    errors = []

    for field in ("id", "title", "author"):
        if field not in data:
            errors.append(f"Champ obligatoire manquant : {field}")

    if "id" in data:
        if not isinstance(data["id"], int):
            errors.append("'id' doit etre un entier")
        elif data["id"] <= 0:
            errors.append("'id' doit etre > 0")

    if "title" in data:
        if not isinstance(data["title"], str):
            errors.append("'title' doit etre une chaine")
        else:
            stripped = data["title"].strip()
            if not stripped:
                errors.append("'title' ne peut pas etre vide")
            elif len(stripped) > MAX_TITLE_LEN:
                errors.append(f"'title' trop long (max {MAX_TITLE_LEN})")

    if "author" in data:
        if not isinstance(data["author"], str):
            errors.append("'author' doit etre une chaine")
        elif len(data["author"].strip()) > MAX_AUTHOR_LEN:
            errors.append(f"'author' trop long (max {MAX_AUTHOR_LEN})")
        elif len(data["author"].strip()) == 0:
            errors.append("'author' ne peut pas etre vide")

    tags = data.get("tags", [])
    if not isinstance(tags, list):
        errors.append("'tags' doit etre une liste")
    else:
        if len(tags) > MAX_TAGS:
            errors.append(f"Trop de tags (max {MAX_TAGS})")
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                errors.append(f"Le tag a l'index {i} doit etre une chaine")
            elif len(tag) > MAX_TAG_LEN:
                errors.append(f"Tag trop long (max {MAX_TAG_LEN})")

    classification = data.get("classification", "internal")
    if not isinstance(classification, str):
        errors.append("'classification' doit etre une chaine")
    elif classification not in ALLOWED_CLASSIFICATIONS:
        errors.append(f"'classification' invalide : {classification}")

    created_at = data.get("created_at")
    if created_at is not None:
        if not isinstance(created_at, str):
            errors.append("'created_at' doit etre une chaine")
        else:
            iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
            if not re.match(iso_pattern, created_at):
                errors.append("'created_at' doit etre au format ISO 8601")

    if errors:
        logger.warning("Validation Document echouee : %s", errors)
        raise ValueError("Payload invalide")

    return {
        "id": data["id"],
        "title": data["title"].strip(),
        "author": data["author"].strip(),
        "tags": tags,
        "classification": classification,
        "created_at": created_at,
    }


def deserialize_document(raw: str) -> Document:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("JSON invalide : %s", e)
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    validated = validate_document(data)

    return Document(
        id=validated["id"],
        title=validated["title"],
        author=validated["author"],
        tags=validated["tags"],
        classification=validated["classification"],
        created_at=validated["created_at"],
    )


def validate_user(data: dict) -> dict:
    errors = []

    for field in ("username", "display_name", "role"):
        if field not in data:
            errors.append(f"Champ obligatoire manquant : {field}")

    if "username" in data:
        if not isinstance(data["username"], str):
            errors.append("'username' doit etre une chaine")
        else:
            if not (MIN_USERNAME_LEN <= len(data["username"]) <= MAX_USERNAME_LEN):
                errors.append(f"'username' doit faire entre {MIN_USERNAME_LEN} et {MAX_USERNAME_LEN} caracteres")
            elif not re.match(ALLOWED_USERNAME_CHARS, data["username"]):
                errors.append("'username' doit contenir uniquement lettres, chiffres et underscore")

    if "display_name" in data:
        if not isinstance(data["display_name"], str):
            errors.append("'display_name' doit etre une chaine")
        elif len(data["display_name"].strip()) == 0:
            errors.append("'display_name' ne peut pas etre vide")
        elif len(data["display_name"]) > MAX_DISPLAY_NAME_LEN:
            errors.append(f"'display_name' trop long (max {MAX_DISPLAY_NAME_LEN})")

    if "role" in data:
        if not isinstance(data["role"], str):
            errors.append("'role' doit etre une chaine")
        elif data["role"] not in ALLOWED_ROLES:
            errors.append(f"'role' invalide : {data['role']}")

    if errors:
        logger.warning("Validation User echouee : %s", errors)
        raise ValueError("Payload invalide")

    return {
        "username": data["username"],
        "display_name": data["display_name"].strip(),
        "role": data["role"],
    }


def deserialize_user(raw: str) -> UserPublic:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("JSON invalide : %s", e)
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    validated = validate_user(data)

    return UserPublic(
        username=validated["username"],
        display_name=validated["display_name"],
        role=validated["role"],
    )

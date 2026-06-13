from models import Document, UserPublic
from serializers import serialize_document, serialize_user
from validation import deserialize_document, deserialize_user


def run():
    print("=" * 60)
    print("TP7.1 - Contrat JSON et validation stricte")
    print("=" * 60)

    doc = Document(
        id=42,
        title="Rapport de securite",
        author="Alice Martin",
        tags=["cybersec", "audit"],
        classification="confidential",
        created_at="2026-06-05T10:30:00Z",
    )
    json_doc = serialize_document(doc)
    print(f"Document serialise : {json_doc}")
    doc_deser = deserialize_document(json_doc)
    print(f"Document deserialise : {doc_deser}\n")

    user = UserPublic(username="alice_d", display_name="Alice Dupont", role="editor")
    json_user = serialize_user(user)
    print(f"User serialise : {json_user}")
    user_deser = deserialize_user(json_user)
    print(f"User deserialise : {user_deser}")


if __name__ == "__main__":
    run()

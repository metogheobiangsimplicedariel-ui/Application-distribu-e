from v1.deserializer import deserialize_document_v1
from v2.deserializer import deserialize_document_v2
from v2.serializer import serialize_document_v2
from v2.models import DocumentV2


def run():
    print("=" * 60)
    print("TP7.2 - Versioning JSON (compatibilite v1/v2)")
    print("=" * 60)

    payload_v1 = '{"id": 42, "title": "Rapport Q1", "author": "Alice"}'
    payload_v2 = '{"id": 42, "title": "Rapport Q1", "author": "Alice", "tags": ["finance"], "classification": "confidential"}'

    print("\nCas 1: Lecteur v2 <- Payload v1")
    doc = deserialize_document_v2(payload_v1)
    print(f"   Resultat: {doc}")

    print("\nCas 2: Lecteur v2 <- Payload v2")
    doc2 = deserialize_document_v2(payload_v2)
    print(f"   Resultat: {doc2}")

    print("\nCas 3: Lecteur v1 <- Payload v2")
    doc_v1 = deserialize_document_v1(payload_v2)
    print(f"   Resultat: {doc_v1}")

    print("\nCas 4: Rejet (classification hors allowlist)")
    try:
        deserialize_document_v2('{"id": 1, "title": "X", "author": "Y", "classification": "top_secret"}')
    except ValueError as e:
        print(f"   -> Rejete: {e}")


if __name__ == "__main__":
    run()

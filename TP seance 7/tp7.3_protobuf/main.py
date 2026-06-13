import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "generated"))

import json
import document_pb2


def run():
    print("=" * 60)
    print("TP7.3 - Protocol Buffers")
    print("=" * 60)

    doc = document_pb2.Document()
    doc.id = 42
    doc.title = "Rapport Q1"
    doc.author = "Alice"
    doc.tags.append("finance")
    doc.tags.append("interne")
    doc.classification = "confidential"

    binary_data = doc.SerializeToString()
    print(f"\nProtobuf taille: {len(binary_data)} octets")

    doc2 = document_pb2.Document()
    doc2.ParseFromString(binary_data)
    print(f"Decode: id={doc2.id}, title={doc2.title}")

    json_data = json.dumps({
        "id": 42,
        "title": "Rapport Q1",
        "author": "Alice",
        "tags": ["finance", "interne"],
        "classification": "confidential"
    }).encode("utf-8")
    print(f"JSON taille: {len(json_data)} octets")
    print(f"Ratio: Protobuf est {len(json_data) / len(binary_data):.1f}x plus petit")


if __name__ == "__main__":
    run()

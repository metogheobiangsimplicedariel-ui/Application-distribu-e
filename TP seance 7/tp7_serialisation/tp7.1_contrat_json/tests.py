import unittest
from models import Document, UserPublic
from serializers import serialize_document, serialize_user
from validation import deserialize_document, deserialize_user


class TestDocumentValidation(unittest.TestCase):

    def test_valid_document_full(self):
        raw = '{"id": 42, "title": "Rapport", "author": "Alice", "tags": ["sec"], "classification": "confidential", "created_at": "2026-06-05T10:30:00Z"}'
        doc = deserialize_document(raw)
        self.assertEqual(doc.id, 42)
        self.assertEqual(doc.title, "Rapport")
        self.assertEqual(doc.author, "Alice")

    def test_valid_document_minimal(self):
        raw = '{"id": 1, "title": "Note", "author": "Bob"}'
        doc = deserialize_document(raw)
        self.assertEqual(doc.tags, [])
        self.assertEqual(doc.classification, "internal")

    def test_invalid_id_negative(self):
        raw = '{"id": -1, "title": "X", "author": "Y"}'
        with self.assertRaises(ValueError):
            deserialize_document(raw)

    def test_invalid_title_type(self):
        raw = '{"id": 1, "title": 123, "author": "Y"}'
        with self.assertRaises(ValueError):
            deserialize_document(raw)

    def test_invalid_classification(self):
        raw = '{"id": 1, "title": "X", "author": "Y", "classification": "top_secret"}'
        with self.assertRaises(ValueError):
            deserialize_document(raw)


class TestUserValidation(unittest.TestCase):

    def test_valid_user(self):
        raw = '{"username": "alice_d", "display_name": "Alice", "role": "editor"}'
        user = deserialize_user(raw)
        self.assertEqual(user.username, "alice_d")

    def test_invalid_username_chars(self):
        raw = '{"username": "alice-d", "display_name": "Alice", "role": "viewer"}'
        with self.assertRaises(ValueError):
            deserialize_user(raw)

    def test_invalid_role(self):
        raw = '{"username": "alice", "display_name": "Alice", "role": "superadmin"}'
        with self.assertRaises(ValueError):
            deserialize_user(raw)


if __name__ == "__main__":
    unittest.main()

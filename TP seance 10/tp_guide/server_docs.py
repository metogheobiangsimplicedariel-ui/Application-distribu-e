import Pyro5.api
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentService:
    # Token partagé (en production : utiliser un mécanisme sécurisé)
    _VALID_TOKEN = "secret-tp10-2026"

    def __init__(self, storage_dir="documents"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        if not any(self.storage_dir.iterdir()):
            self._create_sample_documents()
    
    # METHODES INTERNES (non exposees)
    
    def _check_token(self, token):
        """Verifie le token d'acces — méthode interne, non exposée."""
        if token != self._VALID_TOKEN:
            logger.warning(f"Token invalide reçu: {token!r}")
            raise PermissionError("Accès refuse. Token invalide.")
        return True
    
    def _create_sample_documents(self):
        """Creation documents exemple - NON EXPOSEE"""
        sample_docs = {
            "doc1": "Contenu du document 1: Introduction à la cybersécurité",
            "doc2": "Contenu du document 2: Introduction à l'IA",
            "doc3": "Contenu du document 3: Introduction au Cloud computing"
        }
        for doc_id, content in sample_docs.items():
            self._save_document(doc_id, content)
    
    def _save_document(self, doc_id, content):
        """Ecriture fichier - NON EXPOSEE"""
        file_path = self.storage_dir / f"{doc_id}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _load_document(self, doc_id):
        """Lecture fichier - NON EXPOSEE"""
        # Validation anti-path traversal
        if not self._validate_doc_id(doc_id):
            raise ValueError("ID de document invalide")
        
        file_path = self.storage_dir / f"{doc_id}.txt"
        if not file_path.exists():
            raise KeyError(f"Document '{doc_id}' non trouve")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _validate_doc_id(self, doc_id):
        """Validation des IDs - NON EXPOSEE"""
        if not isinstance(doc_id, str):
            return False
        if not (3 <= len(doc_id) <= 32):
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, doc_id))
    
    # METHODES EXPOSEES
    
    @Pyro5.api.expose
    def list_documents(self):
        """Liste les documents - EXPOSEE (sans token necessaire)"""
        documents = []
        for file_path in self.storage_dir.glob("*.txt"):
            doc_id = file_path.stem
            documents.append(doc_id)
        return sorted(documents)
    
    @Pyro5.api.expose
    def get_document_content(self, doc_id, token=None):
        """
        Retourne le contenu - EXPOSEE avec token obligatoire
        Le client doit fournir un token valide
        """
        # Verifier le token en premier
        if token != self._VALID_TOKEN:
            logger.warning(f"Tentative d'acces sans token valide pour: {doc_id}")
            raise PermissionError("Accès refuse. Token requis ou invalide.")
        
        # Token valide, on peut acceder au document
        try:
            content = self._load_document(doc_id)
            return content
        except KeyError as e:
            raise KeyError(f"Document '{doc_id}' non trouve") from e

def main():
    print("=== Serveur DocumentService ===")
    print("\nPolitique d'exposition:")
    print("  - list_documents(): exposee (sans token)")
    print("  - get_document_content(): exposee (AVEC token requis)")
    print("  - Methodes internes: non exposees")
    print(f"  - Token valide: secret-tp10-2026\n")
    
    service = DocumentService()
    daemon = Pyro5.api.Daemon()
    
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(service)
    ns.register("document.service", uri)
    
    print(f"Service enregistre: {uri}")
    print("Documents disponibles:", service.list_documents())
    print("\nEn attente de requetes...")
    
    daemon.requestLoop()

if __name__ == "__main__":
    main()
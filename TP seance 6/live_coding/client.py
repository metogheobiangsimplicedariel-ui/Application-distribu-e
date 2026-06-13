import json
import uuid
import time
import random
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def api_request(method, url, data=None, token=None, timeout=30):
    body_bytes = json.dumps(data).encode("utf-8") if data else None
    req = Request(url, data=body_bytes, method=method)
    req.add_header("Content-Type", "application/json")
    
    # ── Identifiant unique (UUID) ──
    request_id = str(uuid.uuid4())
    req.add_header("X-Request-Id", request_id)
    
    # Affichage visuel (8 premiers caractères de l'ID)
    print(f"[{request_id[:8]}] {method} {url}")
    
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(f"  ✅ {resp.status}")
            return resp.status, body
    except HTTPError as e:
        error_body = {}
        try:
            error_body = json.loads(e.read().decode("utf-8"))
        except:
            pass
        print(f"  ❌ HTTP {e.code}: {error_body}")
        return e.code, error_body
    except URLError as e:
        print(f"  🔌 Erreur réseau: {e.reason}")
        return None, {"error": str(e.reason)}

def request_with_retry(func, max_retries=4):
    for attempt in range(max_retries + 1):
        status, body = func()
        
        # On s'arrête si succès ou erreur client définitive (4xx)
        if status is not None and (status < 500 and status != 429):
            return status, body
        
        # Si erreur 5xx ou réseau, on applique le Backoff + Jitter
        if attempt < max_retries:
            delay = min(1.0 * (2 ** attempt), 30.0)
            jitter = random.uniform(0, delay)
            print(f"     [RETRY] Tentative {attempt+1}/{max_retries} échouée. Nouvel essai dans {jitter:.1f}s...")
            time.sleep(jitter)
            
    return status, body

if __name__ == "__main__":
    BASE = "http://127.0.0.1:8080"
    TOKEN = "secret-token-abc123"

    print("--- Lancement du client résilient ---")

    # Test 1 : Santé du serveur
    request_with_retry(lambda: api_request("GET", f"{BASE}/health"))

    # Test 2 : Création de document
    def creer_doc():
        return api_request(
            "POST", 
            f"{BASE}/documents", 
            data={"title": "Rapport UEMF", "content": "Contenu du TP"}, 
            token=TOKEN
        )

    status, result = request_with_retry(creer_doc)
    
    print(f"\nStatut final : {status}")
    print(f"Dernière réponse : {result}")
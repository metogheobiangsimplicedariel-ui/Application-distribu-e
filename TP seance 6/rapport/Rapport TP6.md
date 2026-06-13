# Séance 6 — Communication, APIs et Fiabilité

## Livrables : Contrat d'API / Politiques de fiabilité / Matrice de sécurité

---

## TP6.1 — Contrat d'API

### Service Auth

| Endpoint | Méthode | Entrée (JSON) | Sortie (JSON) | Erreurs | Idempotent | Sécurité |
|----------|---------|---------------|---------------|---------|------------|----------|
| `/api/v1/auth/login` | POST | `username` (3-50), `password` (8-100) | `token`, `expires_at`, `user_id`, `roles` | 400, 401, 429 | Non | Rate limiting (5/min/IP), TLS, CAPTCHA |
| `/api/v1/auth/verify` | GET | Header: `Bearer token` | `valid`, `user_id`, `roles`, `expires_at` | 400, 401 | Oui | TLS, vérif signature locale |
| `/api/v1/auth/logout` | POST | Header: `Bearer token` | `message` | 400, 401 | Oui | TLS, blacklist Redis |

### Service Documents

| Endpoint | Méthode | Entrée (JSON) | Sortie (JSON) | Erreurs | Idempotent | Sécurité |
|----------|---------|---------------|---------------|---------|------------|----------|
| `/api/v1/documents` | POST | `title` (1-200), `content` (1-50000), `tags` (opt) | `id`, `title`, `created_at`, `tags` | 400, 401, 403, 413 | Non (Idempotency-Key) | AuthN, AuthZ (editor), validation stricte |
| `/api/v1/documents` | GET | Query: `page`, `per_page`, `sort`, `order`, `tag` | `data[]`, `total`, `page`, `per_page`, `total_pages` | 400, 401 | Oui | AuthN, pagination forcée (max 100) |
| `/api/v1/documents/{id}` | GET | Path: `id` (UUID) | `id`, `title`, `content`, `created_at`, `updated_at`, `tags`, `owner_id` | 401, 403, 404 | Oui | AuthN, AuthZ (owner ou reader) |
| `/api/v1/documents/{id}` | PUT | `title`, `content`, `tags` | `id`, `title`, `content`, `updated_at`, `tags` | 400, 401, 403, 404, 409 | Oui | AuthN, AuthZ (owner ou editor), ETag |
| `/api/v1/documents/{id}` | DELETE | Path: `id` (UUID) | `204 No Content` | 401, 403, 404 | Oui | AuthN, AuthZ (owner ou admin), audit log |

### Service Search

| Endpoint | Méthode | Entrée | Sortie (JSON) | Erreurs | Idempotent | Sécurité |
|----------|---------|--------|---------------|---------|------------|----------|
| `/api/v1/search` | GET | Query: `q` (≥2), `page`, `per_page`, `tag`, `date_from`, `date_to` | `results[]`, `total`, `page`, `per_page`, `query_time_ms` | 400, 401, 429 | Oui | AuthN, rate limiting (30/min), pagination (max 50) |
| `/api/v1/search/suggest` | GET | Query: `q` (≥1) | `suggestions[]` | 400, 401 | Oui | AuthN, rate limiting (60/min) |

---

## TP6.2 — Politiques de fiabilité

### Politiques par service

| Service | Opération | Timeout | Max retries | Base delay | Codes retryables | Idempotency key |
|---------|-----------|---------|-------------|------------|------------------|-----------------|
| Auth | POST /login | 5s | 1 | 1s | 502, 503, 504 | Non |
| Auth | GET /verify | 3s | 2 | 0.5s | 502, 503, 504 | Non |
| Documents | POST /documents | 10s | 0 | — | — | **Oui** (UUID client) |
| Documents | GET /documents | 8s | 2 | 1s | 502, 503, 504 | Non |
| Documents | GET /documents/{id} | 5s | 2 | 0.5s | 502, 503, 504 | Non |
| Documents | PUT /documents/{id} | 8s | 2 | 1s | 502, 503, 504 | Oui |
| Documents | DELETE /documents/{id} | 5s | 2 | 1s | 502, 503, 504 | Oui |
| Search | GET /search | 8s | 2 | 1s | 502, 503, 504 | Non |
| Search | GET /suggest | 3s | 1 | 0.5s | 502, 503, 504 | Non |

### Analyse des scénarios

| Scénario | Risque principal | Politique appliquée | Justification |
|----------|------------------|---------------------|---------------|
| **S1 — Latence élevée** | Blocage threads → cascade | Timeout 8s + backoff | Évite l'attente infinie ; le backoff évite la surcharge du service |
| **S2 — Serveur intermittent** | Erreurs 503 aléatoires | Retry (2x) + backoff + jitter | Les 503 sont transitoires (rolling update) ; jitter évite l'effet de foule |
| **S3 — Duplication requêtes** | Double création de document | Idempotency-Key (UUID client) | Le serveur stocke la clé et ignore les doublons |

### Situations de fallback

| Service | Situation | Fallback / Comportement dégradé |
|---------|-----------|--------------------------------|
| Search | Indisponible (timeout) | Retourner résultats en cache Redis |
| Search | Rate limiting atteint | 429 avec Retry-After |
| Documents | Indisponible pour lectures | Réplique PostgreSQL en lecture seule |
| Auth | Indisponible pour verify | Vérification locale du JWT (signature + expiration) |
| Documents | Échec indexation | File de messages avec retry (DLQ après 3 échecs) |

---

## TP6.3 — Matrice de sécurité

### Mécanisme de token

- **Génération :** JWT signé RS256, contenu : `sub`, `roles`, `exp`, `aud`
- **Durée de vie :** 24h pour tokens utilisateur, 7 jours pour tokens service
- **Transmission :** Header `Authorization: Bearer <token>` + mTLS inter-services
- **Vérification :** Signature locale + audience + expiration (pas d'appel Auth)
- **Invalidation :** Blacklist Redis au logout, expiration naturelle, révocation forcée

### Matrice Surface → Menace → Contrôle

| Surface d'attaque | Menace principale | Contrôle proposé | Priorité |
|------------------|-------------------|------------------|----------|
| API publique — /auth/login | Brute force | Rate limiting (5/min/IP), verrouillage progressif | **Critique** |
| API publique — /documents (POST) | Injection JSON | Validation stricte, taille max, Idempotency-Key | **Critique** |
| API publique — /search | DDoS applicatif | Rate limiting (30/min), pagination (max 50), timeout 8s | Élevée |
| API publique — tous endpoints | MITM | TLS 1.3, HSTS, certificats valides | **Critique** |
| API publique — /documents/{id} | Énumération d'IDs | UUID v4, réponses uniformes (404 = 403) | **Critique** |
| Inter-services (Auth→Document) | Mouvement latéral | mTLS, vérification audience JWT | **Critique** |
| Inter-services (Document→Search) | Replay attack | Timestamp + nonce, cache LRU des nonces | Élevée |
| Inter-services (tous) | Token theft | Tokens courte durée (24h), refresh token | Élevée |
| Admin — endpoints gestion | Accès non autorisé | VPN (WireGuard), MFA, RBAC admin | **Critique** |
| Admin — métriques et debug | Fuite d'informations | Endpoints non exposés en production | Élevée |
| Base de données PostgreSQL | SQL injection | Requêtes paramétrées, credentials en Vault, réseau privé | **Critique** |
| Stockage MinIO | Accès non autorisé | Clés scoped par service, chiffrement au repos | Élevée |
| Cache Redis | Exposition données sensibles | Authentification, réseau privé, chiffrement | Élevée |
| Logs applicatifs | Fuite de tokens | Masquage systématique, accès restreint | **Critique** |
| Secrets (clés JWT, credentials) | Fuite dans code source | Variables d'environnement, scan CI, Vault, rotation 30j | **Critique** |
| Dépendances Python | Supply chain attack | Lock files, pip-audit, SBOM | Moyenne |

---

## Récapitulatif des livrables

| Livrable | Contenu |
|----------|---------|
| **L1 — Contrat d'API** | 3 tableaux (Auth, Documents, Search) |
| **L2 — Politiques de fiabilité** | 1 tableau politique + 1 tableau scénarios + 1 tableau fallback |
| **L3 — Matrice de sécurité** | Description mécanisme token + 1 tableau complet (16 lignes) |
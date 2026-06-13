

<!-- PAGE DE GARDE -->

<div style="text-align: center; margin-top: 100px;">

# **RAPPORT TP — SÉANCE 5**

## Système de Gestion Documentaire Distribué (SGDD)

**Module** : Applications Réparties et Cybersécurité

**Auteur** :  METOGHE OBIANG Simplice Dariel

</div>

<div style="page-break-after: always;"></div>

<!-- TABLE DES MATIÈRES AUTO-GÉNÉRÉE -->

## Table des matières

1. [TP5.1 -- Schématisation d'architecture distribuée](#tp51-schematisation-darchitecture-distribuee)
   - 1.1 Composants identifiés
   - 1.2 Architecture logique
   - 1.3 Architecture physique
   - 1.4 Réponses aux cinq questions
   - 1.5 Justification des choix architecturaux
2. [TP5.2 -- Analyse des défis distribués](#tp52-analyse-des-defis-distribues)
   - 2.1 Service API Gateway
   - 2.2 Service Auth
   - 2.3 Service Stockage
   - 2.4 Service Recherche
   - 2.5 Application du théorème CAP
   - 2.6 Communications inter-services (patterns de résilience)
   - 2.7 Tableau récapitulatif des solutions
3. [TP5.3 -- Cartographie des surfaces d'attaque](#tp53-cartographie-des-surfaces-dattaque)
   - 3.1 Légende des priorités
   - 3.2 Matrice des surfaces d'attaque
   - 3.3 Récapitulatif des priorités
   - 3.4 Application des principes Zero Trust
4. [Conclusion générale](#conclusion-generale)

<div style="page-break-after: always;"></div>

---

## TP5.1 -- SCHÉMATISATION D'ARCHITECTURE DISTRIBUÉE

### 1.1 Composants identifiés

Quatre services sont retenus :

| Composant | Responsabilité | Technologie Python |
|-----------|----------------|---------------------|
| API Gateway | Point d'entrée unique, routage, validation JWT | FastAPI + httpx |
| Service Auth | Authentification, émission et vérification des JWT | FastAPI + python-jose + passlib |
| Service Stockage | Upload, download, liste, suppression des documents | FastAPI + aiofiles + MinIO |
| Service Recherche | Indexation et recherche plein texte | FastAPI + Elasticsearch (client Python) |

**Bases de données associées :**

| Service | Base de données |
|---------|------------------|
| Auth | PostgreSQL (utilisateurs, rôles, hash) |
| Stockage | MongoDB (métadonnées) + MinIO (fichiers) |
| Recherche | Elasticsearch (index plein texte) |
| Cache partagé | Redis (tokens JWT, résultats recherche) |

> **Note :** Chaque service possède sa propre base de données pour garantir un couplage faible.

---

### 1.2 Architecture logique

#### Diagramme ASCII

```
                    +-----------------+
                    |     CLIENT      |
                    +--------+--------+
                             | HTTPS / JSON
                             v
                    +-----------------+
                    |   API GATEWAY   |
                    |   (FastAPI)     |
                    +--------+--------+
                             |
            +----------------+----------------+----------------+
            |                |                |                |
            v                v                v                v
    +-----------+    +-----------+    +-----------+    +-----------+
    |   Auth    |    | Stockage  |    | Recherche |    |   Redis   |
    |  Service  |    |  Service  |    |  Service  |    |  (Cache)  |
    +-----+-----+    +-----+-----+    +-----+-----+    +-----------+
          |                |                |
          v                v                v
    +-----------+    +-----------+    +-----------+
    |PostgreSQL |    |  MongoDB  |    |Elasticsear|
    |           |    |  + MinIO  |    |    ch     |
    +-----------+    +-----------+    +-----------+

Legende :
-----> HTTP/REST (synchrone)
- - -> Communication asynchrone (file de messages Redis)
```



#### Flux d'authentification

```
Client -> API Gateway -> Service Auth -> PostgreSQL -> Service Auth -> API Gateway -> Client (JWT)
```

**Détail :**
1. Le client envoie ses identifiants (login, mot de passe) à l'API Gateway.
2. L'API Gateway transmet la requête au Service Auth.
3. Le Service Auth interroge PostgreSQL pour vérifier les identifiants.
4. En cas de succès, le Service Auth génère un JWT signé.
5. Le JWT est retourné au client via l'API Gateway.

#### Flux d'upload d'un document

```
Client -> API Gateway -> Service Auth -> API Gateway -> Service Stockage -> (MongoDB + MinIO) -> Client
```

**Détail :**
1. Le client envoie le fichier avec le JWT dans l'en-tête `Authorization`.
2. L'API Gateway valide le JWT auprès du Service Auth.
3. Le fichier est transmis au Service Stockage.
4. Le Service Stockage écrit le fichier sur MinIO.
5. Les métadonnées sont enregistrées dans MongoDB.
6. Une confirmation est retournée au client.

#### Flux d'indexation (asynchrone)

```
Service Stockage -> file Redis -> Service Recherche -> Elasticsearch
```

**Détail :**
1. Après l'upload, le Service Stockage publie un événement `document.uploaded` dans Redis.
2. Le Service Recherche consomme l'événement.
3. Le document est indexé dans Elasticsearch (plein texte).
4. L'indexation est asynchrone : l'utilisateur ne l'attend pas.

#### Flux de recherche

```
Client -> API Gateway -> Service Auth -> API Gateway -> Service Recherche -> Elasticsearch -> Client
```

**Détail :**
1. Le client envoie une requête de recherche avec le JWT.
2. L'API Gateway valide le JWT.
3. La requête est transmise au Service Recherche.
4. Le Service Recherche interroge Elasticsearch.
5. Les résultats (format JSON) sont retournés au client.

---

### 1.3 Architecture physique (sans Kubernetes)

Le déploiement est réalisé sur **trois machines virtuelles** distinctes :

| Machine | Services | Accès réseau |
|---------|----------|---------------|
| Machine 1 (DMZ) | API Gateway (2 instances), Service Auth (2 instances), Redis | Port 443 exposé, réseau interne |
| Machine 2 (Backend) | Service Stockage (2 instances), MongoDB, MinIO | Réseau privé uniquement |
| Machine 3 (Recherche) | Service Recherche (2 instances), Elasticsearch | Réseau privé uniquement |

> **Avertissement :** Les bases de données ne sont pas accessibles depuis l'extérieur. PostgreSQL est externalisé (service managé) ou déployé sur une machine dédiée.

---

### 1.4 Réponses aux cinq questions du TP5.1

**Question 1 : Combien de services identifiez-vous et quelles sont leurs frontières ?**

Quatre services sont identifiés : API Gateway, Service Auth, Service Stockage, Service Recherche. L'API Gateway ne contient aucune logique métier. Le Service Auth gère exclusivement les identités et les droits. Le Service Stockage gère uniquement les fichiers et leurs métadonnées. Le Service Recherche gère uniquement l'indexation et la recherche. Chaque service possède sa propre base de données.

**Question 2 : Quel protocole de communication entre chaque paire de services ?**

Toutes les communications inter-services sont en HTTP/REST avec des messages JSON, sauf entre le Service Stockage et le Service Recherche où la communication est asynchrone via une file de messages Redis. Cette asymétrie permet de découpler l'upload de l'indexation.

**Question 3 : Où placez-vous les bases de données ? Une par service ou mutualisées ?**

Les bases de données sont placées une par service : PostgreSQL pour le Service Auth, MongoDB pour le Service Stockage, Elasticsearch pour le Service Recherche. Aucune base n'est mutualisée. Redis est partagé pour le cache (tokens JWT, résultats de recherche fréquents).

**Question 4 : Y a-t-il des services qui peuvent être appelés en parallèle ?**

Pour un même flux utilisateur, les appels à Auth et Stockage sont séquentiels. En revanche, pour des requêtes indépendantes (exemple : deux recherches simultanées), le Service Recherche peut traiter plusieurs requêtes en parallèle grâce au modèle asynchrone de FastAPI. L'indexation est asynchrone et n'entre pas dans le chemin critique de l'upload.

**Question 5 : Quel est le chemin critique de latence pour chaque opération ?**

- **Authentification** : API Gateway -> Service Auth -> PostgreSQL (latence dominée par la base de données)
- **Upload** : API Gateway -> Service Auth -> Service Stockage -> écriture disque (étape la plus lente)
- **Recherche** : API Gateway -> Service Auth -> Service Recherche -> Elasticsearch (généralement < 100 ms)
- **Indexation** : asynchrone, hors chemin critique

---

### 1.5 Justification des choix architecturaux

Le choix d'une architecture à quatre services respecte le principe de **séparation des préoccupations** : l'authentification, le stockage et la recherche sont des responsabilités distinctes.

Chaque service possède sa propre base de données, ce qui garantit un **couplage faible** et permet des évolutions technologiques indépendantes.

L'API Gateway constitue un **point d'entrée unique** qui centralise la validation des jetons JWT, la limitation de débit et l'observabilité.

La communication asynchrone entre le stockage et la recherche via une file Redis **découple temporellement** l'upload de l'indexation : l'utilisateur n'attend pas que le document soit indexé.

Python et FastAPI sont choisis pour leur caractère asynchrone, leur riche écosystème (clients JWT, MongoDB, Elasticsearch) et leur productivité.

Le déploiement sur trois machines virtuelles (sans Kubernetes) offre un premier niveau de **tolérance aux pannes partielles** : la panne du service Recherche n'empêche ni l'authentification ni l'upload.

La **réplication** des services critiques (API Gateway, Auth, Stockage) limite les points uniques de défaillance.

Enfin, l'**isolation réseau** des bases de données réduit la surface d'attaque.

---

## TP5.2 -- ANALYSE DES DÉFIS DISTRIBUÉS

### 2.1 Service API Gateway

**Défi : point unique de défaillance (SPOF).** Si l'API Gateway tombe, aucune requête n'atteint les autres services. L'ensemble du système devient indisponible.

**Solution : réplication.** Deux instances de l'API Gateway sont déployées derrière un répartiteur de charge (HAProxy). Des sondes de santé détectent les instances défaillantes et redirigent le trafic.

**Défi : surcharge (DDoS ou pic de trafic).** Un afflux massif de requêtes peut saturer l'API Gateway.

**Solution : limitation de débit (rate limiting).** Chaque client est limité à 100 requêtes par seconde. Le passage à l'échelle horizontal est possible en ajoutant des instances.

---

### 2.2 Service Auth

**Défi : disponibilité.** Si le service Auth est indisponible, les utilisateurs ne peuvent plus se connecter. Les autres services ne peuvent plus vérifier les jetons JWT.

**Solution : réplication et cache.** Deux instances du service Auth sont déployées. L'API Gateway met en cache localement les jetons JWT valides pendant 5 minutes et vérifie leur signature sans appeler Auth.

**Défi : cohérence des données utilisateurs.** Deux administrateurs modifiant simultanément les droits d'un même utilisateur peuvent créer des incohérences.

**Solution : cohérence forte sur les écritures.** PostgreSQL est configuré en mode réplication synchrone pour les écritures critiques. Les lectures peuvent être éventuellement cohérentes.

---

### 2.3 Service Stockage

**Défi : cohérence des métadonnées.** Un document est uploadé. Ses métadonnées sont écrites dans MongoDB, mais le fichier n'est pas encore entièrement écrit sur MinIO.

**Solution : état intermédiaire.** Le service Stockage écrit d'abord le fichier, puis les métadonnées. Un champ `status` ("uploading" -> "available" -> "error") indique la disponibilité.

**Défi : latence d'écriture.** L'écriture d'un fichier volumineux peut prendre plusieurs secondes.

**Solution : accusé immédiat.** Le service retourne un identifiant immédiatement, puis termine l'écriture en arrière-plan. L'utilisateur interroge l'état via `GET /documents/{id}/status`.

---

### 2.4 Service Recherche

**Défi : latence d'indexation.** L'indexation d'un document PDF de 100 pages peut prendre 10 à 15 secondes.

**Solution : communication asynchrone.** Le service Stockage publie un événement `document.uploaded` dans une file Redis. Le service Recherche consomme et indexe en arrière-plan.

**Défi : cohérence entre l'index et les métadonnées.** Un document supprimé du stockage peut rester dans l'index.

**Solution : événements de suppression.** Le service Stockage publie `document.deleted`. Une tâche de nettoyage périodique supprime les orphelins.

**Défi : latence de recherche.** Une requête complexe peut prendre plusieurs secondes.

**Solution : cache et pagination.** Les résultats fréquents sont mis en cache Redis (TTL 60s). La pagination limite à 20 résultats par page.

---

### 2.5 Application du théorème CAP

Le théorème CAP (Brewer, 2000) stipule qu'en cas de partition réseau, il faut choisir entre **Cohérence (Consistency)** et **Disponibilité (Availability)**. Dans l'architecture proposée, le choix diffère selon le service :

| Service | Choix CAP | Justification |
|---------|-----------|----------------|
| Service Auth | **CP** (Cohérence forte) | Les données utilisateurs et les permissions ne peuvent pas tolérer d'incohérence. En cas de partition, la disponibilité est sacrifiée. |
| Service Stockage | **AP** (Disponibilité) | L'upload de documents privilégie la disponibilité. La cohérence éventuelle est acceptable car l'état intermédiaire (`status`) permet de détecter les incohérences. |
| Service Recherche | **AP** (Disponibilité) | Une recherche peut retourner des résultats légèrement obsolètes. La disponibilité prime sur la cohérence. |

> **Conclusion :** L'architecture respecte le théorème CAP en faisant des choix explicites et justifiés pour chaque service.

---

### 2.6 Communications inter-services (patterns de résilience)

**Défi : panne réseau ou timeout.** Un appel entre services peut échouer ou prendre trop de temps. Sans protection, les ressources s'épuisent et la cascade de pannes se produit.

**Solutions :**

- **Timeout court** : chaque appel inter-service a un timeout de 2 secondes maximum.
- **Retry avec backoff exponentiel** : après un échec, tentative à 0,5 s, puis 1 s, puis 2 s. L'ajout de jitter (variation aléatoire) évite l'effet de troupeau (thundering herd).
- **Circuit breaker** : après 5 échecs consécutifs, les appels sont bloqués pendant 10 secondes (état *open*). Un appel test (état *half-open*) décide de refermer le circuit.

---

### 2.7 Tableau récapitulatif des solutions

| Défi | Solution | Services concernés |
|------|----------|---------------------|
| SPOF | Réplication + load balancer | API Gateway, Auth |
| Surcharge | Rate limiting + scaling horizontal | API Gateway |
| Indisponibilité d'un service | Cache local (JWT), fallback | Auth, API Gateway |
| Cohérence des écritures | Réplication synchrone | Auth |
| Incohérence métadonnées/fichier | État intermédiaire (status) | Stockage |
| Latence d'écriture | Accusé immédiat + traitement async | Stockage |
| Latence d'indexation | File de messages (pub/sub) | Stockage, Recherche |
| Orphelins dans l'index | Événements de suppression + nettoyage périodique | Stockage, Recherche |
| Panne réseau / timeout | Timeout court (2s) | Tous |
| Cascade de pannes | Circuit breaker | Tous |
| Échec transitoire | Retry avec backoff exponentiel + jitter | Tous |

---

## TP5.3 -- CARTOGRAPHIE DES SURFACES D'ATTAQUE

### 3.1 Légende des priorités

| Priorité | Signification |
|----------|----------------|
| **CRITIQUE** | Menace pouvant rendre tout le système indisponible ou compromettre l'ensemble des données |
| **ÉLEVÉE** | Menace pouvant compromettre un sous-ensemble des données ou dégrader significativement le service |
| **MOYENNE** | Menace nécessitant une combinaison de vulnérabilités ou ayant un impact limité |

---

### 3.2 Matrice des surfaces d'attaque

| Surface d'attaque | Menace principale | Contrôle proposé | Priorité |
|-------------------|-------------------|------------------|----------|
| API Gateway (externe) | DDoS, injection SQL/NoSQL, force brute | Rate limiting (100 req/s par IP), validation stricte des entrées, lockout après 5 échecs (15 min), WAF | CRITIQUE |
| API Gateway -> Auth (interne) | MITM, usurpation d'identité du service Auth | mTLS, vérification de l'audience dans le JWT, rotation des certificats tous les 90 jours | CRITIQUE |
| API Gateway -> Stockage (interne) | MITM, usurpation d'identité du service Stockage | mTLS, JWT transmis dans chaque requête, vérification de la signature | CRITIQUE |
| API Gateway -> Recherche (interne) | MITM, usurpation d'identité | mTLS, JWT avec scope restreint (`scope: search`) | CRITIQUE |
| Service Auth -> PostgreSQL | Injection SQL, accès direct à la base | Requêtes paramétrées, credentials dans un coffre (Vault), base sur réseau privé | CRITIQUE |
| Service Stockage -> MongoDB | Injection NoSQL, accès non autorisé | Validation des entrées, ODM, réseau privé, authentification avec rôle dédié | CRITIQUE |
| Service Stockage -> MinIO | Accès direct aux fichiers, exfiltration | Permissions restreintes, chiffrement des fichiers sensibles au repos (AES-256) | ÉLEVÉE |
| Service Recherche -> Elasticsearch | Injection de requêtes malveillantes | Validation des requêtes, isolation des index par tenant, authentification avec rôle restreint | ÉLEVÉE |
| File de messages (Redis) | Interception des messages, injection de faux événements | Chiffrement TLS, authentification des producteurs/consommateurs, validation des schémas | ÉLEVÉE |
| Logs centralisés | Fuite de données sensibles (JWT, mots de passe) | Masquage automatique des tokens, exclusion des champs sensibles, accès restreint, rétention 30 jours | ÉLEVÉE |
| Secrets (clés JWT, mots de passe DB) | Fuite dans le code source ou les variables d'environnement | Stockage dans Vault, injection au démarrage, rotation automatique (JWT 24h, DB 30j), scan CI/CD | CRITIQUE |
| Dépendances Python (pip) | Attaque sur la chaîne d'approvisionnement (supply chain) | `requirements.lock`, audit régulier avec `pip-audit`, analyse des vulnérabilités dans le CI/CD | MOYENNE |
| Endpoint `POST /login` | Brute force, dictionnaire, épuisement des comptes | Délai progressif (1s, 2s, 4s), CAPTCHA après 5 échecs, journalisation des tentatives | CRITIQUE |
| Endpoint `POST /documents` | Upload de fichiers malveillants | Validation du type MIME, limitation de taille (10 Mo), analyse antivirus (ClamAV) | CRITIQUE |

---

### 3.3 Récapitulatif des priorités

| Priorité | Nombre de surfaces | Exemples |
|----------|-------------------|----------|
| **CRITIQUE** | 9 | API externe, inter-services, bases de données, secrets, login brute force, upload malveillant |
| **ÉLEVÉE** | 5 | Fichiers au repos, file de messages, logs, Elasticsearch |
| **MOYENNE** | 1 | Dépendances Python |

---

### 3.4 Application des principes Zero Trust

L'architecture respecte les principes **Zero Trust** suivants :

- **Authentification partout** : chaque service vérifie le JWT, pas seulement l'API Gateway.
- **Autorisation granulaire** : les permissions (lecture, écriture, suppression) sont vérifiées par le service Stockage et le service Recherche.
- **Moindre privilège** : le service Recherche a uniquement un accès en lecture à l'index. Le service Stockage a un accès limité à sa propre collection MongoDB.
- **Chiffrement en transit** : mTLS entre tous les services internes.
- **Segmentation réseau** : les bases de données sont sur un réseau privé, inaccessibles depuis l'extérieur.
- **Vérification continue** : les jetons JWT sont vérifiés à chaque requête (pas de session longue).
- **Hypothèse de compromission** : l'architecture est conçue en supposant qu'un service peut être compromis. La segmentation et le moindre privilège limitent la propagation latérale.

---

## CONCLUSION GÉNÉRALE

Ce travail a permis de concevoir l'architecture d'un **Système de Gestion Documentaire Distribué (SGDD)** en Python.

**Quatre services** ont été identifiés : API Gateway, Auth, Stockage et Recherche. Chaque service possède sa propre base de données, garantissant un **couplage faible**. Les communications sont en HTTP/REST avec JSON, sauf l'indexation qui est asynchrone via une file de messages Redis.

**Les défis distribués** (SPOF, cohérence, latence, pannes partielles) ont été analysés. Des solutions ont été proposées : réplication, cache, timeout court, retry avec backoff exponentiel, circuit breaker, file de messages et état intermédiaire pour les écritures longues. Le **théorème CAP** a été appliqué explicitement : le service Auth privilégie la cohérence (CP), tandis que les services Stockage et Recherche privilégient la disponibilité (AP).

**Les surfaces d'attaque** ont été cartographiées. Des contrôles de sécurité ont été proposés : mTLS, validation stricte des entrées, rate limiting, coffre à secrets (Vault), rotation des clés, isolation des bases de données sur réseau privé.

L'architecture respecte les principes **Zero Trust** : authentification partout, moindre privilège, chiffrement en transit, segmentation réseau et hypothèse de compromission.





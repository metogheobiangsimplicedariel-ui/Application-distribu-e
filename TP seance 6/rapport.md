# Rapport de Travaux Pratiques - Séance 6

**Matière :** Cloud Computing / Architecture Distribuée 

---

## 1. Introduction et Objectifs

Ce document présente les résultats des travaux pratiques de la séance 6. L'objectif principal de cette séance était d'appréhender les problématiques liées aux systèmes distribués, en se concentrant sur trois axes majeurs :
1. La définition stricte de contrats d'API HTTP.
2. L'implémentation de la fiabilité et de la tolérance aux pannes côté client.
3. La mise en place d'un modèle de sécurité minimal pour la protection des échanges.

## 2. Architecture du Projet

L'ensemble des fichiers a été organisé de manière modulaire afin de séparer l'implémentation technique de la conception théorique :

- **`live_coding/`** : Contient l'implémentation technique (Serveur API et clients).
- **`rapport/`** : Contient les livrables d'analyse (fichiers PDF et matrices de conception).

## 3. Travail Réalisé et Justifications Techniques

### 3.1. Spécification de l'API et Serveur HTTP (TP 6.1)
Un mini-serveur HTTP (`server.py`) a été développé pour simuler le service de gestion documentaire. 
- **Validation stricte** : Le serveur valide systématiquement la présence et la conformité des champs JSON (`title`, `content`).
- **Codes HTTP sémantiques** : Les réponses utilisent les codes standards (`201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`) afin de respecter les bonnes pratiques REST.

### 3.2. Fiabilité et Tolérance aux Pannes (TP 6.2)
Dans les environnements distribués, les pannes réseau sont inévitables. Pour y faire face, un client robuste a été implémenté (`client-v2.py` et `retry.py`).
- **Backoff Exponentiel et Jitter** : Un algorithme a été mis en place pour espacer les tentatives de reconnexion de manière aléatoire, évitant ainsi l'effet "troupeau tonitruant" (retry storm) sur le serveur.
- **Gestion du Rate Limiting** : Le code identifie spécifiquement le code `429 Too Many Requests` et applique une pause forcée avant de reprendre.
- **Timeouts** : L'utilisation de délais d'attente stricts prévient le blocage indéfini des threads clients.

### 3.3. Sécurité Minimaliste (TP 6.3)
La sécurité a été abordée tant au niveau architectural qu'au niveau applicatif :
- **Authentification** : Le serveur exige la présence d'un jeton d'authentification (`Bearer Token`) dans les en-têtes HTTP.
- **Traçabilité (Observabilité)** : Un identifiant unique (`X-Request-Id`) est généré par le client pour chaque requête, permettant d'assurer le suivi des requêtes (Correlation ID) dans les journaux du serveur en cas d'incident.
- **Défense en profondeur** : Le traitement des entrées rejette par défaut tout format non conforme (Fail-closed).

## 4. Exécution du Projet

Afin de vérifier le bon fonctionnement de l'architecture, il est possible de démarrer les modules localement :
1. Démarrer l'API en exécutant le script serveur : `python live_coding/server.py`
2. Simuler des requêtes résilientes via le client : `python live_coding/client-v2.py`

## 5. Conclusion

L'implémentation de ces mécanismes souligne l'importance d'une approche défensive en architecture distribuée. La combinaison d'un contrat d'API rigoureux et de politiques de reconnexion intelligentes permet de garantir la stabilité du système face aux aléas du réseau, tout en assurant un socle de sécurité fondamental.

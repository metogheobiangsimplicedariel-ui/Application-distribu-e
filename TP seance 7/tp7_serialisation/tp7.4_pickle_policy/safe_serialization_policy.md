# Politique de Sérialisation Sûre

## Tableau : Politique de sérialisation

| Source des donnees | Format autorise | Controles requis |
|--------------------|-----------------|------------------|
| API REST (client) | JSON uniquement | Validation stricte, limite taille, authentification, rate limiting |
| Inter-services (reseau interne) | JSON ou Protobuf | mTLS, HMAC, validation schema (zero trust) |
| Cache local (meme processus) | pickle autorise | Donnees generees localement UNIQUEMENT |
| Fichier uploadé utilisateur | JSON/CSV/XML (defused) | defusedxml, limite taille, validation, sandbox |
| File de messages (Kafka/RabbitMQ) | JSON ou Protobuf | Schema registry, signature, validation |
| Stockage persistant (DB/fichier) | JSON ou Protobuf | HMAC/chiffrement, migration schema |

## Checklist Secure Deserialization
- Interdire pickle/marshal/shelve pour toute entree non fiable
- Utiliser yaml.safe_load() au lieu de yaml.load()
- Limiter la taille des payloads avant parsing (ex: 1 Mo max)
- Valider chaque champ apres deserialisation (type, longueur, allowlist)
- Signer les donnees serialisees si elles transitent ou sont stockees (HMAC)
- Logger les echecs de deserialisation (sans donnees sensibles)
- Versionner les contrats de donnees (champs optionnels, pas de breaking change)
- Tester les cas limites : payload vide, geant, types incoherents, champs inconnus
- Reviewer tout usage de pickle en code review (flag automatique CI)
- Documenter le format accepte a chaque point d'entree (API doc, README)
- Appliquer un timeout au parsing pour prevenir les DoS
- Rejeter par defaut (fail closed) tout payload non conforme

# Matrice de compatibilite JSON v1/v2

| Version payload | Lecteur | Payload exemple | Accepte | Raison | Risque |
|----------------|---------|-----------------|---------|--------|--------|
| v1 | v2 | {"id":1,"title":"X","author":"A"} | Oui | Champs manquants -> valeurs par defaut | Aucun |
| v2 | v1 | {"id":1,"title":"X","author":"A","tags":[],"classification":"public"} | Oui | Lecteur v1 ignore champs inconnus | Perte d'info si reemission |
| v2 altere | v2 | {"id":1,"title":"X","author":"A","classification":"top_secret"} | Non | Valeur hors allowlist | Injection |
| v2 + champ inconnu | v2 | {"id":1,"title":"X","author":"A","priority":"high"} | Oui | Politique: ignorer | Risque faible |

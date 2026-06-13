<div style="text-align: center; margin-top: 100px;">

# **ARCHITECTURE DU DÉPÔT**

## Travaux Pratiques et Projet de Fin d'Année

**Module** : Applications Réparties

**Auteur** : METOGHE OBIANG Simplice Dariel

</div>

<div style="page-break-after: always;"></div>

Ce dépôt regroupe l'ensemble des travaux pratiques (TP) ainsi que le projet de fin d'année réalisés dans le cadre du cours d'Applications Distribuées. 

Ce fichier README a pour but d'aider à naviguer facilement à travers les différents répertoires et de comprendre leur contenu.

## Structure Générale

Le dépôt est organisé en plusieurs dossiers, chacun correspondant à une séance de TP spécifique ou au projet final :

```text
/
├── Projet/           # Projet de fin d'année - PhishShield
├── TP seance 5/      # Travaux pratiques de la séance 5
├── TP seance 6/      # Travaux pratiques de la séance 6
├── TP seance 7/      # Travaux pratiques de la séance 7 (Sérialisation & Sécurité)
└── TP seance 10/     # Travaux pratiques de la séance 10
```

---

## Détail des Répertoires

### 1. Projet/ (Projet de fin d'année : PhishShield)
Ce dossier contient l'implémentation complète du projet final, **PhishShield**, une plateforme distribuée de détection de phishing.
- Vous y trouverez l'architecture microservices (API Gateway, AuthService, AnalysisService, AuditService).
- Un README détaillé spécifique au projet est disponible à l'intérieur pour les instructions de lancement et d'architecture.
- Le dossier contient également le rapport final du projet dans le sous-dossier `rapport/`.

### 2. TP seance 5/
Ce dossier contient le travail réalisé lors de la séance 5.
- Il inclut principalement le rapport de la séance (`rapport.md`).

### 3. TP seance 6/
Ce dossier contient le travail de la séance 6.
- **live_coding/** : Contient les exercices de code réalisés pendant la séance.
- **rapport/** : Contient le compte-rendu (`rapport.md`) et d'éventuels schémas/annexes.

### 4. TP seance 7/ (Sérialisation, Marshalling et Sécurité)
Ce dossier regroupe les exercices de la séance 7, divisés en 4 sous-modules :
- `tp7.1_contrat_json` : Contrats JSON et validation stricte.
- `tp7.2_versioning_json` : Versioning et compatibilité.
- `tp7.3_protobuf` : Utilisation de Protocol Buffers.
- `tp7.4_pickle_policy` : Politique de sécurisation et signatures HMAC.
- Un README interne et un script `run_all_tests.py` sont fournis pour automatiser les tests de ces modules.

### 5. TP seance 10/
Ce dossier correspond à la séance 10.
- **live_coding/** : Scripts et exercices pratiques.
- **tp_guide/** : Guide utilisé pour le TP.
- Un rapport complet (`RAPPORT.md`) synthétisant le travail accompli.

---

## Navigation Rapide

Pour consulter les instructions détaillées ou les rapports, vous pouvez vous rendre directement dans les sous-dossiers correspondants. Le projet final et le TP 7 possèdent leur propre documentation détaillée.

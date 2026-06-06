# TP7 : Sérialisation, Marshalling et Sécurité

Ce projet contient l'ensemble des travaux pratiques du TP7 consacrés à la sérialisation des données, la gestion des versions (versioning), et la sécurité lors de la désérialisation.

## Structure du Projet

Le TP est divisé en 4 modules distincts :

### 1. `tp7.1_contrat_json` (Contrat JSON et Validation Stricte)
- Définition d'un contrat de données strict via les `dataclasses` Python.
- Implémentation d'un système de sérialisation excluant les champs sensibles (`EXCLUDED_FIELDS`).
- Désérialisation robuste (Fail-closed) vérifiant scrupuleusement les types, les longueurs minimales/maximales, et l'appartenance à des listes blanches (*allowlists*).

### 2. `tp7.2_versioning_json` (Versioning et Compatibilité)
- Démonstration de l'évolution d'une API de la version `v1` à `v2`.
- Gestion de la **rétrocompatibilité** (un lecteur `v2` peut lire un payload `v1` en attribuant des valeurs par défaut aux nouveaux champs).
- Mise en évidence de l'antérocompatibilité (tolérance aux champs inconnus).

### 3. `tp7.3_protobuf` (Protocol Buffers)
- Définition d'un schéma formel `.proto` (`document.proto`).
- Génération automatique de code Python via le compilateur `protoc` (intégré via `grpcio-tools`).
- Comparaison de l'efficacité de Protobuf par rapport à JSON (Protobuf est environ 2.2x plus compact).

### 4. `tp7.4_pickle_policy` (Politique de Sécurisation et HMAC)
- Explication des dangers liés à la désérialisation (exécution de code arbitraire via `pickle` ou `yaml.load()`).
- Définition d'une [Politique de sérialisation sûre](tp7.4_pickle_policy/safe_serialization_policy.md) (Checklist et tableau des formats autorisés).
- Implémentation d'un mécanisme de vérification d'intégrité par **signature HMAC** (SHA-256) pour garantir que les données n'ont pas été altérées lors du transit.

---

## Installation (Environnement Virtuel)

Il est **fortement recommandé** d'utiliser un environnement virtuel Python pour installer les dépendances du projet, notamment `grpcio-tools` qui nous permet de compiler le code Protobuf automatiquement sans avoir à installer manuellement de logiciels sur le système.

### Étape 1 : Créer l'environnement virtuel
À la racine du projet (le dossier parent de `tp7_serialisation`), exécutez :
```bash
python -m venv venv
```

### Étape 2 : Activer l'environnement
**Sous Windows (PowerShell) :**
```powershell
.\venv\Scripts\activate
```

**Sous Linux / macOS :**
```bash
source venv/bin/activate
```

### Étape 3 : Installer les dépendances
```bash
cd tp7_serialisation
pip install -r requirements.txt
```

---

## Exécution des Tests

Un script maître est fourni pour tester l'intégralité des TPs de manière automatisée. 

Ce script est "intelligent" :
1. Il détecte automatiquement votre environnement virtuel `venv`.
2. Il utilise l'outil `grpcio-tools` pour compiler à la volée le fichier `document.proto` en Python.
3. Il exécute de manière séquentielle l'ensemble des modules (TP 7.1 à 7.4).

Pour tout lancer, exécutez simplement (assurez-vous d'être dans le dossier `tp7_serialisation`) :
```bash
python run_all_tests.py
```

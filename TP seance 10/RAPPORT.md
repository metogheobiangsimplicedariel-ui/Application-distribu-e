# Rapport de TP - Séance 10 : Invocation d'Objets Distants en Python

## Introduction
Ce rapport présente les travaux réalisés lors de la séance 10, portant sur la création et la consommation d'objets distants en Python à l'aide de la bibliothèque **Pyro5**. L'objectif principal de cette séance était de comprendre la différence entre un appel RPC classique et l'invocation d'un objet distant (qui conserve un état et expose des méthodes), tout en appliquant des règles strictes de cybersécurité.

Le travail s'est divisé en deux parties : une session de Live Coding (Calculatrice) et un TP Guidé (Service de gestion de documents).

---

## 1. Live Coding : Service de Calculatrice Distante
Le premier exercice consistait à exposer un objet simple pour appréhender l'architecture RMI (Remote Method Invocation) sous Python.

### Architecture mise en place :
1. **Le Serveur (`server_calculator.py`)** :
   - Création d'une classe `CalculatorService`.
   - Utilisation du décorateur `@Pyro5.api.expose` comme **liste blanche** pour autoriser l'accès distant uniquement aux méthodes `add` et `subtract`.
   - La méthode `_internal_reset` n'a pas été décorée, la gardant ainsi inaccessible de l'extérieur.
   - Sécurité : Même pour un service basique, les types des arguments sont validés (`isinstance(a, (int, float))`) car on ne doit **jamais faire confiance au client**.
   - Enregistrement de l'objet dans le démon Pyro5 et publication sur le *Name Server* sous l'alias `example.calculator`.

2. **Le Client (`client_calculator.py`)** :
   - Localisation transparente du serveur via `Pyro5.api.locate_ns()`.
   - Création d'un **Proxy** local (`Pyro5.api.Proxy`) qui intercepte les appels de méthodes et les achemine à travers le réseau vers l'objet réel.

---

## 2. TP Guidé : Service Sécurisé de Gestion de Documents
Le TP visait à concevoir un système plus complexe (`DocumentService`) simulant une base de documents. L'accent a été mis sur le contrôle d'accès, la limitation de la surface d'attaque et la sécurité des requêtes.

### A. Politique d'Exposition
Conformément au principe du moindre privilège, seules deux méthodes sont exposées aux clients :
- `list_documents()` : Permet à tout client de voir la liste des identifiants des documents.
- `get_document_content(doc_id, token)` : Permet de lire un document précis, sous réserve d'authentification.

Toutes les méthodes d'accès au système de fichiers (`_save_document`, `_load_document`) ou de validation (`_validate_doc_id`, `_check_token`) sont restées des méthodes internes non exposées.

### B. Authentification
Pour empêcher les accès non autorisés, la lecture d'un document exige un **Token partagé** (`secret-tp10-2026`). Si le client (via `client_docs.py`) ne fournit pas ce jeton exact, le serveur rejette immédiatement la requête avec une exception de permission (`PermissionError`), empêchant toute exploitation.

### C. Validation Stricte des Entrées (TP 10.3)
Pour contrer les attaques de type injection ou Path Traversal (ex: `../../etc/passwd`), une validation drastique a été implémentée sur les identifiants de documents (`doc_id`) :
- **Validation du Type** : Rejet immédiat si `doc_id` n'est pas une chaîne de caractères (`str`).
- **Validation de la Longueur** : Le nom du document doit impérativement faire entre 3 et 32 caractères.
- **Validation du Format (Regex)** : L'identifiant est filtré par l'expression régulière `^[a-zA-Z0-9_]+$`. Les caractères spéciaux, les slashs (`/`) ou même les tirets classiques (`-`) sont proscrits.

### D. Gestion Discrète des Erreurs (Erreurs Sûres)
Une bonne pratique de sécurité appliquée dans ce TP est de ne pas être "bavard" avec le client. En cas d'erreur de formatage ou si un document est introuvable, le serveur soulève des exceptions standards et génériques (`ValueError("ID de document invalide")` ou `KeyError`). Les détails techniques (Stack Trace, chemins des fichiers locaux) ne sont jamais transmis au client, évitant ainsi la fuite d'informations système.

---

## 3. Guide d'Installation et d'Exécution

Pour exécuter correctement ce projet et tester les objets distants, il est impératif d'utiliser trois terminaux séparés (pour le Name Server, le Serveur d'objets, et le Client).

### Étape 1 : Préparation de l'environnement
Ouvrez un terminal à la racine du projet et installez les dépendances nécessaires. Il est fortement recommandé d'utiliser un environnement virtuel :

```bash
# Activation de l'environnement virtuel (sur Windows)
.\env\Scripts\activate

# Installation de Pyro5 et de son sérialiseur sécurisé Serpent
pip install Pyro5 serpent
```

### Étape 2 : Démarrage du Name Server (Terminal 1)
Le Name Server agit comme un annuaire permettant aux clients de découvrir les serveurs. Il doit toujours être lancé en premier.
```bash
# Toujours dans l'environnement virtuel
python -m Pyro5.nameserver
```
*Laissez ce terminal ouvert en arrière-plan.*

### Étape 3 : Lancement du TP Guidé (Gestion de documents)

**A. Démarrage du Serveur (Terminal 2)**
Ouvrez un nouveau terminal, activez l'environnement virtuel, et lancez le service de documents :
```bash
.\env\Scripts\activate
python tp_guide/server_docs.py
```
*Le serveur va démarrer, créer un dossier `documents` si nécessaire, s'enregistrer auprès du Name Server et se mettre en attente.*

**B. Exécution du Client (Terminal 3)**
Ouvrez un troisième terminal, activez l'environnement virtuel, et lancez le client interactif :
```bash
.\env\Scripts\activate
python tp_guide/client_docs.py
```
Vous pouvez désormais interagir avec le menu, demander la liste des documents (choix 1) ou afficher le contenu d'un document spécifique de manière sécurisée (choix 2).

> **Note :** Pour tester le "Live Coding" (Calculatrice), vous pouvez appliquer exactement le même processus que l'étape 3, en exécutant `python live_coding/server_calculator.py` dans le Terminal 2, puis `python live_coding/client_calculator.py` dans le Terminal 3.

---

## Conclusion
Ce TP a permis d'implémenter de bout en bout des objets distants fonctionnels en Python. Au-delà de l'aspect réseau et architecture (Proxy, Name Server, Daemon), il a surtout souligné que l'illusion de la localité offerte par des bibliothèques comme Pyro5 ne doit pas faire oublier les risques : authentification, validation stricte et exposition minimale sont indispensables pour sécuriser de tels services.

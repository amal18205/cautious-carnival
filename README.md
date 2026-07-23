# Cautious Carnival

Application web **Flask** + **PostgreSQL**, conteneurisée avec **Docker**, avec un pipeline d'intégration continue (**CI**) automatisé via **GitHub Actions**, incluant tests automatisés (**Pytest**) et analyse de vulnérabilités (**Trivy**). Le déploiement se fait manuellement sur le serveur **WEB01** (machine virtuelle Proxmox, laboratoire local non accessible depuis Internet).

---

## Sommaire

- [Architecture](#architecture)
- [Technologies utilisées](#technologies-utilisées)
- [Structure du projet](#structure-du-projet)
- [Installation et lancement en local](#installation-et-lancement-en-local)
- [Variables d'environnement](#variables-denvironnement)
- [Tests](#tests)
- [Pipeline CI (GitHub Actions)](#pipeline-ci-github-actions)
- [Déploiement sur WEB01](#déploiement-sur-web01)
- [Sécurité](#sécurité)

---

## Architecture

```text
                GitHub
                   │
                   ▼
          GitHub Actions
                   │
   ┌───────────────┼──────────────────┐
   │               │                  │
Pytest      Build Docker         Scan Trivy
(service Postgres     │                │
 éphémère)             │                │
   └───────────────┴──────────────────┘
                   │
                   ▼
                WEB01 (Proxmox, hors ligne)
                   │
          Docker Compose
          ┌───────────────┐
          │               │
      Flask App      PostgreSQL
          │
     Volume Docker (persistance)
```

**Pipeline CI** : à chaque `push` sur `main`, GitHub Actions télécharge le code, installe Python et les dépendances, initialise une base PostgreSQL éphémère, exécute les tests avec Pytest, construit l'image Docker, puis l'analyse avec Trivy.

**Déploiement** : WEB01 étant une VM Proxmox non accessible depuis Internet, GitHub Actions ne peut pas déployer directement dessus. Le déploiement reste donc **manuel**, effectué après validation du pipeline.

---

## Technologies utilisées

- Python / Flask
- PostgreSQL
- Docker / Docker Compose
- Git / GitHub
- GitHub Actions (CI)
- Pytest (tests automatisés)
- Trivy (scan de vulnérabilités des images Docker)

---

## Structure du projet

```
cautious-carnival/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env                          # non versionné (voir .gitignore)
├── .gitignore
├── templates/
│   └── index.html
├── tests/
│   └── test_app.py
└── .github/
    └── workflows/
        └── docker.yml
```

---

## Installation et lancement en local

### Prérequis

- Docker et Docker Compose installés

### Lancement avec Docker Compose

```bash
git clone https://github.com/amal18205/cautious-carnival.git
cd cautious-carnival
sudo docker compose up -d --build
sudo docker compose ps
```

L'application est ensuite accessible sur `http://<adresse-du-serveur>:5000`.

### Lancement sans Docker (environnement virtuel Python)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## Variables d'environnement

Les paramètres de connexion à la base de données sont configurables via des variables d'environnement (valeurs par défaut utilisées si absentes) :

| Variable      | Valeur par défaut | Description                    |
|---------------|--------------------|---------------------------------|
| `DB_HOST`     | `database`         | Hôte PostgreSQL                |
| `DB_NAME`     | `tasksdb`           | Nom de la base de données      |
| `DB_USER`     | `devops`            | Utilisateur PostgreSQL         |
| `DB_PASSWORD` | `password`          | Mot de passe PostgreSQL        |

En local avec Docker Compose, ces valeurs sont définies dans le fichier `.env` (non versionné, exclu via `.gitignore`).

---

## Tests

Les tests automatisés sont écrits avec **Pytest** dans `tests/test_app.py`.

### En local (dans le conteneur applicatif)

```bash
sudo docker exec -it cautious-carnival-app-1 bash
pip install pytest
python -m pytest
```

### Sur GitHub Actions

Les tests s'exécutent automatiquement à chaque push, contre une base PostgreSQL éphémère créée pour le job (`DB_HOST=localhost`), après initialisation du schéma (table `tasks`).

---

## Pipeline CI (GitHub Actions)

Fichier : `.github/workflows/docker.yml`

Étapes exécutées à chaque `push` sur `main` :

1. **Checkout** du code
2. **Installation de Python** (3.12)
3. **Installation des dépendances** (`requirements.txt`, incluant `pytest`)
4. **Initialisation de la base** (création de la table `tasks`) et **exécution des tests** Pytest, contre un service PostgreSQL éphémère fourni par le job
5. **Construction de l'image Docker**
6. **Scan de sécurité de l'image** avec Trivy (sévérités `HIGH` et `CRITICAL`)

Le service PostgreSQL utilisé pendant le job GitHub Actions est **temporaire** : il est créé au début du job, isolé sur l'infrastructure GitHub, sans donnée réelle, et détruit à la fin — il est indépendant de la base de production sur WEB01.

---

## Déploiement sur WEB01

WEB01 est une machine virtuelle Proxmox du laboratoire, non accessible depuis Internet. Le déploiement reste donc manuel, effectué après validation du pipeline CI sur GitHub :

```bash
git pull
sudo docker compose up -d --build
```

---

## Sécurité

- Les identifiants et paramètres sensibles de l'environnement de production (WEB01) sont stockés dans un fichier `.env`, exclu du dépôt via `.gitignore` — ils ne sont jamais versionnés sur GitHub.
- Les images Docker sont construites à partir d'une image officielle légère (`python:3.12-slim`).
- Chaque image Docker est analysée automatiquement avec **Trivy** dans le pipeline CI, afin de détecter les vulnérabilités connues avant tout déploiement.
- Les identifiants PostgreSQL utilisés dans le job GitHub Actions concernent une base **éphémère et isolée**, propre à l'exécution du pipeline, sans lien avec les données de production.

# Backend Application (FastAPI)

Ce dossier contient tout le code du backend de l'application basé sur FastAPI.

## Structure

- **`main.py`** : Point d'entrée de l'application FastAPI
- **`api/`** : Endpoints API, schémas et dépendances
  - **`endpoints/`** : Routes API organisées par domaine
  - **`schemas/`** : Schémas Pydantic pour validation
  - **`dependencies.py`** : Dépendances communes
- **`core/`** : Configuration, sécurité et dépendances centrales
  - **`config/`** : Paramètres de configuration
  - **`deps.py`** : Dépendances centrales
  - **`security.py`** : Sécurité et authentification
- **`db/`** : Configuration de base de données et modèles
  - **`models/`** : Modèles SQLAlchemy
  - **`repositories/`** : Repositories pour l'accès aux données
  - **`session.py`** : Configuration de session DB
- **`services/`** : Logique métier et services
- **`crud/`** : Opérations CRUD (Create, Read, Update, Delete)
- **`utils/`** : Utilitaires et helpers

## Architecture

Le backend suit une architecture en couches :
1. **API Layer** (`api/`) : Gestion des requêtes HTTP et validation
2. **Service Layer** (`services/`) : Logique métier
3. **Data Access Layer** (`crud/`, `db/`) : Accès aux données
4. **Model Layer** (`db/models/`) : Définition des entités

## Conventions

- Chaque endpoint est organisé par domaine métier
- Les schémas Pydantic sont séparés des modèles SQLAlchemy
- Les repositories encapsulent l'accès aux données
- Les services contiennent la logique métier complexe 
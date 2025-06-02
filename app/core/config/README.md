# Configuration

Ce dossier contient tous les fichiers de configuration de l'application.

## Contenu

- **`settings.py`** : Configuration principale de l'application
- **`database.py`** : Configuration de la base de données
- **`logging.py`** : Configuration du système de logs

## Configuration principale (settings.py)

Gère les paramètres suivants :
- **Informations de l'API** : nom, version, description
- **Configuration de base de données** : URL, credentials
- **Paramètres de sécurité** : clés secrètes, CORS
- **Features flags** : activation/désactivation de fonctionnalités
- **Configuration par environnement** : dev, test, prod

## Variables d'environnement

Les paramètres sont configurables via des variables d'environnement :

```env
# Base de données
DATABASE_URL=mysql://user:password@localhost:3306/analyseit
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=analyseit

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key

# Features
ENABLE_API_TECHNIQUE=false
ENABLE_DATAVIZ=false
```

## Utilisation

```python
from app.core.config.settings import settings

# Accès aux paramètres
database_url = settings.DATABASE_URL
api_port = settings.API_PORT
```

## Conventions

- Utilisation de Pydantic BaseSettings pour la validation
- Variables d'environnement en MAJUSCULES
- Valeurs par défaut appropriées pour le développement
- Documentation des paramètres obligatoires 
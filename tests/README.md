# Tests

Ce dossier contient tous les tests du projet AnalyseIt Backend.

## Structure

- **`test_api.py`** : Tests des endpoints API
- **`test_auth.py`** : Tests du système d'authentification
- **`test_models.py`** : Tests des modèles de données
- **`test_services.py`** : Tests des services métier
- **`conftest.py`** : Configuration des fixtures pytest

## Lancement des tests

### Tous les tests
```bash
pytest
```

### Tests avec couverture
```bash
pytest --cov=app tests/
```

### Tests spécifiques
```bash
# Tests API uniquement
pytest tests/test_api.py -v

# Tests d'authentification
pytest tests/test_auth.py -v

# Tests avec pattern
pytest -k "test_auth" -v
```

### Tests en mode verbose
```bash
pytest -v
```

## Configuration

Les tests utilisent une base de données SQLite en mémoire pour l'isolation.
La configuration se trouve dans `conftest.py`.

## Fixtures disponibles

- `client` : Client de test FastAPI
- `db_session` : Session de base de données de test
- `test_user` : Utilisateur de test
- `auth_headers` : Headers d'authentification

## Conventions

- Chaque module de test correspond à un module de l'application
- Les tests sont organisés par classe pour chaque endpoint/service
- Utilisation de fixtures pour éviter la duplication de code
- Tests d'intégration pour les endpoints complets 
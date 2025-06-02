# Services

Ce dossier contient la couche de services (logique métier) de l'application.

## Contenu

- **`stats_service.py`** : Service de calcul et agrégation des statistiques
- **`data_extraction.py`** : Service d'extraction et traitement des données Kaggle
- **`etl.py`** : Service ETL (Extract, Transform, Load)
- **`auth_service.py`** : Service d'authentification et gestion des utilisateurs

## Architecture

Les services implémentent la logique métier et orchestrent les interactions entre :
- Les repositories (accès aux données)
- Les utilitaires (traitement des données)
- Les APIs externes (Kaggle, etc.)

## Responsabilités

### StatsService
- Calcul des statistiques globales
- Agrégation des données par type/géographie
- Génération des données pour le dashboard

### DataExtractionService
- Téléchargement des datasets Kaggle
- Nettoyage et transformation des données
- Insertion en base de données

### ETLService
- Orchestration des processus ETL
- Gestion des erreurs et retry
- Logging des opérations

## Conventions

- Chaque service est une classe avec des méthodes spécialisées
- Injection de dépendances via le constructeur
- Gestion d'erreurs avec logging approprié
- Tests unitaires pour chaque méthode publique 
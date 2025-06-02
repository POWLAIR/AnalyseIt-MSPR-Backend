# SQL Scripts

Ce dossier contient tous les scripts SQL du projet, organisés comme suit :

## Structure

- **`schemas/`** : Scripts de création de tables et définition du schéma de base de données
- **`migrations/`** : Scripts de migration de base de données (ALTER TABLE, etc.)
- **`seeds/`** : Scripts d'insertion de données de test ou données initiales

## Utilisation

1. Exécuter d'abord les scripts dans `schemas/` pour créer la structure
2. Appliquer les migrations dans `migrations/` si nécessaire
3. Insérer les données initiales avec les scripts dans `seeds/` 
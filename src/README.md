# Frontend Source Code

Ce dossier contient le code source du frontend de l'application (TypeScript/JavaScript).

## Structure

- **`config/`** : Configuration du frontend (base de données, API, etc.)
- **`controllers/`** : Contrôleurs pour gérer la logique de présentation
- **`routes/`** : Définition des routes du frontend
- **`services/`** : Services pour communiquer avec l'API backend
- **`types/`** : Définitions des types TypeScript

## Architecture

Le frontend suit une architecture MVC (Model-View-Controller) :
- **Models** : Définis dans `types/`
- **Views** : Gérées par les routes dans `routes/`
- **Controllers** : Logique métier dans `controllers/`
- **Services** : Communication avec l'API dans `services/` 
# AnalyseIt Backend

Backend en **FastAPI** pour la gestion, l'analyse et la visualisation de données liées aux pandémies.  
Il expose une API RESTful connectée à une base de données **MySQL** avec support ETL, statistiques, géolocalisation et dashboard.

---

## �� Fonctionnalités

- **API RESTful** documentée (Swagger / ReDoc)
- **Authentification JWT** complète avec gestion des rôles
- **Gestion des épidémies** et statistiques associées
- **Intégration de datasets Kaggle** via pipeline ETL
- **Système de visualisation analytique**
- **Support des localisations** et sources de données
- **Architecture en couches** (API, Service, Data Access)

---

## 🛠️ Technologies

- **FastAPI** (0.109.0) - Framework web moderne
- **SQLAlchemy** (2.0.25) - ORM Python
- **PyMySQL** - Connecteur MySQL
- **Pydantic** - Validation de données
- **Pandas**, **NumPy** - Traitement de données
- **Alembic** - Migrations de base de données
- **Kaggle Hub** - Import de données
- **Pytest** - Tests unitaires
- **JWT** - Authentification sécurisée
- **bcrypt** - Hachage de mots de passe

---

## 📁 Structure du projet

~~~bash
AnalyseIt-MSPR-Backend/
├── app/                       # Backend FastAPI
│   ├── api/                   # API Layer
│   │   ├── endpoints/         # Routes API (auth, epidemics, stats, etc.)
│   │   ├── schemas/           # Schémas Pydantic
│   │   └── dependencies.py    # Dépendances API
│   ├── core/                  # Configuration et sécurité
│   │   ├── config/            # Paramètres de configuration
│   │   ├── deps.py            # Dépendances centrales (auth, admin)
│   │   └── security.py        # Sécurité JWT et authentification
│   ├── db/                    # Data Access Layer
│   │   ├── models/            # Modèles SQLAlchemy
│   │   ├── repositories/      # Repositories pour l'accès aux données
│   │   └── session.py         # Configuration de session DB
│   ├── services/              # Service Layer (logique métier)
│   ├── utils/                 # Utilitaires et helpers
│   └── main.py                # Point d'entrée FastAPI
├── core/                      # Configuration globale du projet
│   ├── Dockerfile             # Configuration Docker
│   ├── docker-compose.yml     # Orchestration des services
│   ├── requirements.txt       # Dépendances Python
│   └── .flake8               # Configuration linter
├── sql/                       # Scripts SQL
│   ├── schemas/               # Scripts de création de tables
│   ├── migrations/            # Scripts de migration
│   └── seeds/                 # Données initiales
├── src/                       # Frontend TypeScript/JavaScript
│   ├── config/                # Configuration frontend
│   ├── controllers/           # Contrôleurs MVC
│   ├── routes/                # Routes frontend
│   ├── services/              # Services API
│   └── types/                 # Types TypeScript
└── tests/                     # Tests unitaires et d'intégration
~~~

---

## 🚀 Démarrage rapide avec Docker

### Prérequis
- Docker et Docker Compose installés
- Port 8000 et 3306 disponibles

### Lancement
~~~bash
git clone <URL_DU_REPO_BACKEND>
cd AnalyseIt-MSPR-Backend/core
docker-compose up --build -d
~~~

### Accès à l'API
- **Documentation Swagger** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentation ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Santé de l'API** : [http://localhost:8000/health](http://localhost:8000/health)

---

## ⚙️ Installation locale

### Méthode manuelle
~~~bash
git clone <URL_DU_REPO_BACKEND>
cd AnalyseIt-MSPR-Backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r core/requirements.txt
cp .env.example .env  # Configurer selon vos besoins
~~~

---

## 🔧 Configuration (.env)

~~~env
# Configuration de base de données
DATABASE_URL=mysql://user:password@localhost:3306/analyseit
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=analyseit

# Configuration API
API_HOST=0.0.0.0
API_PORT=8000

# Sécurité JWT
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration optionnelle
ENABLE_API_TECHNIQUE=false
ENABLE_DATAVIZ=false
~~~

---

## 🔐 Authentification

Le système d'authentification JWT est complet avec :

### Endpoints disponibles
- **POST** `/api/v1/auth/register` - Créer un compte
- **POST** `/api/v1/auth/login` - Se connecter
- **GET** `/api/v1/auth/me` - Profil utilisateur
- **POST** `/api/v1/auth/logout` - Se déconnecter

### Exemple d'utilisation
~~~bash
# Créer un utilisateur admin
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123", "is_admin": true}'

# Se connecter
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123"}'
~~~

### Protection des routes
- Routes publiques : `/health`, `/docs`, `/auth/*`
- Routes protégées : Nécessitent un token JWT valide
- Routes admin : Nécessitent le rôle administrateur

---

## 📊 Endpoints principaux

### Épidémies
- **GET** `/api/v1/epidemics/` - Liste des épidémies
- **POST** `/api/v1/epidemics/` - Créer une épidémie
- **GET** `/api/v1/epidemics/{id}` - Détails d'une épidémie
- **PUT** `/api/v1/epidemics/{id}` - Modifier une épidémie
- **DELETE** `/api/v1/epidemics/{id}` - Supprimer une épidémie

### Statistiques
- **GET** `/api/v1/stats/dashboard` - Statistiques du tableau de bord
- **GET** `/api/v1/epidemics/stats/dashboard` - Stats détaillées des épidémies

### Administration
- **POST** `/api/v1/admin/init-db` - Initialiser la base de données
- **POST** `/api/v1/admin/run-etl` - Lancer le processus ETL
- **GET** `/api/v1/admin/extract-data` - Extraire les données Kaggle

---

## 🏃‍♂️ Lancement

### Avec Docker (recommandé)
~~~bash
cd core
docker-compose up --build -d
~~~

### Développement local
~~~bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
~~~

---

## 🧪 Tests

~~~bash
pytest                   # tests unitaires
pytest --cov=app tests/  # couverture
pytest tests/test_api.py -v
~~~

---

## 🐳 Docker

### Commandes utiles
~~~bash
# Voir les logs
cd core && docker-compose logs -f backend

# Arrêter les services
cd core && docker-compose down

# Reconstruire les images
cd core && docker-compose build --no-cache

# Voir l'état des conteneurs
cd core && docker-compose ps
~~~

### Services Docker
- **backend** : API FastAPI (port 8000)
- **mysql_db** : Base de données MySQL (port 3306)

---

## 📝 Conventions de commit

Le projet suit les conventions de commit standardisées pour maintenir un historique Git propre et cohérent.

### Format des commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types de commits

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation uniquement
- `style`: Changements qui n'affectent pas le sens du code (formatage, etc.)
- `refactor`: Refactorisation du code qui ne corrige pas de bug et n'ajoute pas de fonctionnalité
- `perf`: Amélioration des performances
- `test`: Ajout ou modification de tests
- `chore`: Mise à jour des dépendances, tâches de build, etc.
- `ci`: Configuration CI
- `build`: Changements qui affectent le système de build
- `revert`: Revert d'un commit précédent

### Exemples

```bash
# Ajout d'une nouvelle fonctionnalité
git commit -m "feat(auth): ajout de l'authentification JWT"

# Correction d'un bug
git commit -m "fix(api): correction du timeout sur l'endpoint /users"

# Mise à jour de la documentation
git commit -m "docs(readme): mise à jour de la documentation"
```

---

## 🔐 Sécurité

- **Protection CORS** configurée
- **Validation stricte** via Pydantic
- **Variables d'environnement** pour les secrets
- **Authentification JWT** avec tokens sécurisés
- **Hachage bcrypt** pour les mots de passe
- **Protection des routes** par rôles

---

## 🏗️ Architecture

### Couches de l'application
1. **API Layer** (`app/api/`) : Gestion des requêtes HTTP et validation
2. **Service Layer** (`app/services/`) : Logique métier
3. **Data Access Layer** (`app/db/`) : Accès aux données
4. **Model Layer** (`app/db/models/`) : Définition des entités

### Modèles de données
- **User** : Utilisateurs avec authentification
- **Epidemic** : Épidémies et leurs métadonnées
- **DailyStats** : Statistiques quotidiennes
- **Localisation** : Données géographiques
- **DataSource** : Sources de données
- **OverallStats** : Statistiques globales

---

## 🤝 Contribution

~~~bash
git checkout -b feature/ma-feature
git commit -m "feat: ajout d'une fonctionnalité"
git push origin feature/ma-feature
~~~
Ouvre une Pull Request !

---

## 📝 Licence

Ce projet est sous licence MIT.

---

## 🆘 Support

En cas de problème :
1. Vérifiez que Docker est démarré
2. Consultez les logs : `cd core && docker-compose logs -f`
3. Testez la santé de l'API : `curl http://localhost:8000/health`
4. Consultez la documentation Swagger : `http://localhost:8000/docs`

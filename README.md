# AnalyseIt Backend

Backend en **FastAPI** pour la gestion, l'analyse et la visualisation de données liées aux pandémies.  
Il expose une API RESTful connectée à une base de données **MySQL** avec support ETL, statistiques, géolocalisation et dashboard.

---

## 🌟 Fonctionnalités

- API RESTful documentée (Swagger / ReDoc)
- Gestion des épidémies et statistiques associées
- Intégration de datasets Kaggle via pipeline ETL
- Système de visualisation analytique
- Support des localisations et sources de données

---

## 🛠️ Technologies

- **FastAPI** (0.109.0)
- **SQLAlchemy** (2.0.25)
- **PyMySQL**, **Pydantic**, **Pandas**, **NumPy**
- **Alembic** (migrations)
- **Kaggle Hub** (import de données)
- **Pytest** (tests)

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
│   │   ├── deps.py            # Dépendances centrales
│   │   └── security.py        # Sécurité et authentification
│   ├── db/                    # Data Access Layer
│   │   ├── models/            # Modèles SQLAlchemy
│   │   ├── repositories/      # Repositories pour l'accès aux données
│   │   └── session.py         # Configuration de session DB
│   ├── services/              # Service Layer (logique métier)
│   ├── crud/                  # Opérations CRUD
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

## ⚙️ Installation locale

### Méthode rapide (recommandée)
~~~bash
git clone <URL_DU_REPO_BACKEND>
cd AnalyseIt-MSPR-Backend
./start.sh
~~~

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

## 🔧 Exemple de `.env`

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
SECRET_KEY=your-secret-key-change-this-in-production

# Configuration optionnelle
ENABLE_API_TECHNIQUE=false
ENABLE_DATAVIZ=false
~~~

---

## 🏃‍♂️ Lancement

### Développement local
~~~bash
./start.sh
~~~

### Avec Docker
~~~bash
./start-docker.sh
~~~

### Manuel
~~~bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
~~~

- Swagger : [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc : [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Tests

~~~bash
pytest                   # tests unitaires
pytest --cov=app tests/  # couverture
pytest tests/test_api.py -v
~~~

---

## 🐳 Docker

### Démarrage rapide
~~~bash
./start-docker.sh
~~~

### Manuel
~~~bash
cd core
docker-compose up --build -d
~~~

### Commandes utiles
~~~bash
# Voir les logs
cd core && docker-compose logs -f

# Arrêter les services
cd core && docker-compose down

# Reconstruire les images
cd core && docker-compose build --no-cache
~~~

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

### Règles

1. Le type et le sujet sont obligatoires
2. Le scope est optionnel
3. Le sujet doit être en minuscules
4. Le sujet ne doit pas dépasser 72 caractères
5. Le sujet ne doit pas se terminer par un point
6. Le corps et le pied de page sont optionnels
7. Le corps et le pied de page doivent être séparés par une ligne vide
8. Chaque ligne du corps et du pied de page ne doit pas dépasser 72 caractères

Pour plus de détails, consultez le fichier [commit-msg](commit-msg).

---

## 🔐 Sécurité

- Protection CORS
- Validation stricte via Pydantic
- Variables d'environnement pour les secrets
- Authentification JWT (projetée)

---

## 🤝 Contribution

~~~bash
git checkout -b feature/ma-feature
git commit -m "Ajout d'une fonctionnalité"
git push origin feature/ma-feature
~~~
Ouvre une Pull Request !

---

## 📝 Licence

Ce projet est sous licence MIT.

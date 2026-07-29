# Architecture Technique - Prédiction Oiseaux Migrateurs NPDC

## 🏗️ Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Utilisateur)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼──────┐
    │ Dashboard │          │    API     │
    │ Streamlit │          │ FastAPI    │
    └────┬─────┘          └─────┬──────┘
         │                       │
         └───────────┬───────────┘
                     │
        ┌────────────▼───────────┐
        │  Couche Prédiction     │
        │   - XGBoost (prod)     │
        │   - LSTM (expérimental)│
        │   - Feature Pipeline   │
        └────┬────────┬──────────┘
             │        │
    ┌────────▼─┐  ┌────▼───────────┐
    │ Modèles  │  │  Données Tests  │
    │ Sérialisés│  │  (parquet)      │
    └─────┬────┘  └────┬───────────┘
          │            │
    ┌─────▼────────────▼─────┐
    │   Data Lake (local)     │
    │  - donnees/brutes/      │
    │  - donnees/traitees/    │
    │  - donnees/features/    │
    └─────────────────────────┘
```

---

## 🔄 Flux données

### 1️⃣ **Acquisition** (BC01)
```
GBIF API                 Open-Meteo API
   │                           │
   └──────────────┬────────────┘
                  │
         scripts/acquisition.py
                  │
    ┌─────────────▼─────────────┐
    │  donnees/brutes/           │
    │  - observations_gbif.csv   │
    │  - meteo_npdc.csv          │
    └─────────────┬─────────────┘
```

### 2️⃣ **Nettoyage** (BC01)
```
donnees/brutes/
      │
scripts/nettoyage.py
      │
  ┌───┴────────────────────┐
  │                        │
  ▼                        ▼
observations_         grille_presence_
nettoyees.            hebdo.parquet
parquet
```

### 3️⃣ **Features Engineering** (BC03)
```
Grille hebdomadaire + Météo traitée
           │
  scripts/entrainer_modele.py
           │
  ┌────────▼─────────┐
  │ Features finales │
  │ - annee          │
  │ - semaine        │
  │ - lat/lon        │
  │ - variables météo│
  └────────┬─────────┘
           │
Données en mémoire pour entraînement
```

### 4️⃣ **Apprentissage** (BC03)
```
Features
   │
   ├─► Random Forest ──┐
   ├─► XGBoost ────────┼──► Évaluation
   └─► Log Regression ─┘
           │
       modeles/
   ├─ pipeline_ml.pkl
   ├─ random_forest.pkl
   ├─ logistic_regression.pkl
   └─ evaluations.csv
```

### 5️⃣ **Prédiction en production** (BC05)
```
Frontend (Streamlit / API)
           │
    ┌──────▼──────────┐
    │  API FastAPI    │
    │                 │
    │ Charge modèle   │
    │ XGBoost (prod)  │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │ Prédiction      │
    │ (< 100ms)       │
    └──────┬──────────┘
           │
      JSON Response
```

---

## 📊 Schéma base données

### Observations nettoyées
```sql
CREATE TABLE observations (
    ID_OBSERVATION INT PRIMARY KEY,
    ESPECE VARCHAR(50),
    DATE_OBSERVATION DATETIME,
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    LATITUDE_DISCRETE FLOAT,  -- Grille 0.1°
    LONGITUDE_DISCRETE FLOAT,
    PRECISION_M INT,
    PAYS VARCHAR(10),
    SOURCE VARCHAR(20),  -- "GBIF"
);
```

### Grille hebdomadaire
```sql
CREATE TABLE presence_hebdo (
    ANNEE INT,
    SEMAINE INT,
    ESPECE VARCHAR(50),
    LAT_DISCRETE FLOAT,
    LON_DISCRETE FLOAT,
    NOMBRE_OBSERVATIONS INT,
    PRESENCE BOOLEAN,  -- 1 si observée, 0 sinon
    
    PRIMARY KEY (ANNEE, SEMAINE, ESPECE, LAT_DISCRETE, LON_DISCRETE)
);
```

### Météorologiques
```sql
CREATE TABLE meteo (
    DATE DATE,
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    TEMPERATURE_MAX FLOAT,
    TEMPERATURE_MIN FLOAT,
    PRECIPITATION_SUM FLOAT,
    VENT_MAX FLOAT,
    HUMIDITE_MOYENNE FLOAT,
    PRESSION_MOYENNE FLOAT,
    
    PRIMARY KEY (DATE, LATITUDE, LONGITUDE)
);
```

### Features ML
```sql
CREATE TABLE features_ml (
    ID_SAMPLE INT PRIMARY KEY,
    ESPECE VARCHAR(50),
    ANNEE INT,
    SEMAINE INT,
    LAT_GROUPED FLOAT,
    LON_GROUPED FLOAT,
    
    -- Features météo (7j avant)
    TEMP_MAX_MEAN FLOAT,
    TEMP_MIN_MEAN FLOAT,
    PRECIP_SUM FLOAT,
    VENT_MAX MEAN FLOAT,
    
    -- Features temporelles
    DAY_OF_YEAR INT,
    WEEK_OF_YEAR INT,
    MONTH INT,
    
    -- Target
    PRESENCE BOOLEAN,
    
    -- Split
    SPLIT VARCHAR(10)  -- "train" / "test"
);
```

---

## 🔐 Organisation fichiers

```
oiseaux_migrateurs_npdc/
│
├── donnees/
│   ├── brutes/
│   │   ├── observations_gbif.csv      # Source GBIF brute
│   │   └── meteo_npdc.csv             # Source météo brute
│   │
│   ├── traitees/
│   │   ├── observations_nettoyees.parquet
│   │   ├── grille_presence_hebdo.parquet
│   │   └── meteo_processed.parquet
│   │
│   └── caracteristiques/
│       ├── features_train.parquet
│       ├── features_test.parquet
│       └── features_validation.parquet
│
├── scripts/
│   ├── __init__.py
│   ├── config.py                      # Configuration centralisée
│   ├── acquisition.py                 # BC01 - Téléchargement
│   ├── nettoyage.py                   # BC01 - ETL
│   ├── eda.py                         # BC02 - Analyses
│   ├── entrainer_modele.py            # BC03 - Entraînement ML
│   └── modeles.py                     # BC03 - Utilitaires modèles
│
├── notebooks/
│   ├── 01_exploration.ipynb           # BC02 - EDA notebook
│   └── 02_machine_learning.ipynb      # BC03 - ML models
│
├── modeles/
│   ├── pipeline_ml.pkl                # Sklearn Pipeline sérialisé
│   ├── random_forest.pkl              # Modèle de comparaison
│   ├── logistic_regression.pkl        # Baseline
│   └── evaluations.csv                # Résultats comparatifs
│
├── api/
│   ├── main.py                        # API FastAPI
│   └── (schémas Pydantic intégrés dans main.py)

├── dashboard.py                       # Dashboard Streamlit
│
├── tests/
│   ├── test_acquisition.py
│   ├── test_nettoyage.py
│   └── test_modeles.py
│
├── docs/
│   ├── ARCHITECTURE.md                # Ce fichier
│   ├── PLAN_OPERATIONNEL.md
│   ├── RAPPORT_EDA.md
│   ├── RESULTATS_MODELES.md
│   └── DEPLOIEMENT.md
│
├── requirements.txt
├── Dockerfile
├── .gitignore
├── README.md
└── .env                               # Variables environnement (git-ignored)
```

---

## 🛠️ Stack technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Acquisition** | GBIF API, Requests | 2.31 |
| **Data Processing** | Pandas, NumPy | 2.0+, 1.24+ |
| **Visualisation** | Matplotlib, Seaborn, Plotly, Folium | 3.7+, 0.12+, 5.15+, 0.14+ |
| **ML classique** | Scikit-learn, XGBoost | 1.3+, 2.0+ |
| **Deep Learning** | TensorFlow, Keras | 2.13+, 2.13+ |
| **API** | FastAPI, Uvicorn, Pydantic | 0.103+, 0.23+, 2.3+ |
| **Dashboard** | Streamlit | 1.27+ |
| **Containerisation** | Docker | Latest |
| **Env Gestion** | python-dotenv | 1.0+ |
| **Logging** | Loguru | 0.7+ |
| **Tests** | Pytest | 7.4+ |
| **Dev Tools** | Jupyter, Black, Pylint | Latest |

---

## 🚀 Déploiement

### Local
```bash
# API
python -m uvicorn api.main:app --reload

# Dashboard
streamlit run dashboard.py
```

### Docker
```bash
# Build
docker build -t oiseaux-migrateurs:latest .

# Run
docker run -p 8000:8000 \
  -v $(pwd)/donnees:/app/donnees \
  -v $(pwd)/modeles:/app/modeles \
  oiseaux-migrateurs:latest
```

### Cloud (exemple GCP)
```bash
# Créer image
gcloud builds submit --tag gcr.io/PROJECT_ID/oiseaux:latest

# Déployer Cloud Run
gcloud run deploy oiseaux \
  --image gcr.io/PROJECT_ID/oiseaux:latest \
  --platform managed \
  --port 8000
```

---

## 📈 Monitoring

### Logs
- **Répertoire** : `logs/` (créé au runtime)
- **Format** : Loguru avec timestamps
- **Niveau** : DEBUG, INFO, WARNING, ERROR

### Métriques (à tracker)
```
- Latence prédiction (ms)
- Accuracy modèle (%)
- Nombre prédictions/jour
- Erreurs API (count)
- Disponibilité (uptime %)
```

---

## 🔄 CI/CD (optionnel pour soutenance)

```yaml
# .gitlab-ci.yml (exemple)
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pytest tests/ --cov

build:
  stage: build
  script:
    - docker build -t oiseaux:latest .

deploy:
  stage: deploy
  script:
    - docker run oiseaux:latest
```

---

**Version** : 1.0  
**Dernière mise à jour** : Mars 2026  
**Auteur** : Projet RNCP

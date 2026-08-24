# Prédiction des Oiseaux Migrateurs - Nord-Pas-de-Calais

## Objectif
Prédire la probabilité de présence d'oiseaux migrateurs dans la région Nord-Pas-de-Calais selon les conditions météorologiques et la saison.

**Problématique scientifique :** Peut-on modéliser l'arrivée des migrations à partir de variables climatiques ?

---

## Données utilisées

### Observations d'oiseaux
- **Source** : Global Biodiversity Information Facility (GBIF)
- **Variables** : Date, latitude, longitude, espèce
- **Période** : 2015-2024
- **Région** : Nord-Pas-de-Calais (bounding box : 49.5°N-51.5°N, 1.5°E-4°E)

### Données météorologiques
- **Source** : Open-Meteo API
- **Variables** : Température (min/max), précipitations, vent, humidité, pression
- **Résolution** : Quotidienne

### Espèces étudiées
1. **Hirondelle rustique** (*Hirundo rustica*)
2. **Cigogne blanche** (*Ciconia ciconia*)
3. **Martinet noir** (*Apus apus*)
4. **Bergeronnette printanière** (*Motacilla alba*)

---

## Structure du projet

```
oiseaux_migrateurs_npdc/
├── donnees/
│   ├── brutes/              # Données téléchargées brutes (GBIF, Open-Meteo)
│   ├── traitees/            # Données nettoyées (Parquet)
│   └── caracteristiques/    # Features engineered (Parquet)
├── scripts/
│   ├── acquisition.py       # BC01 - Téléchargement GBIF + météo
│   ├── nettoyage.py        # BC01 - ETL et validation
│   ├── eda.py              # BC02 - Analyse exploratoire
│   ├── entrainer_modele.py  # BC03 - Entraînement et comparaison ML
│   └── modeles.py           # Utilitaires modèles et métriques
├── notebooks/
│   ├── 01_exploration.ipynb      # BC02 - Analyse & visualisations
│   └── 02_machine_learning.ipynb  # BC03 - Modèles classiques
├── modeles/
│   ├── pipeline_ml.pkl     # Pipeline preprocessing + modèle principal
│   ├── random_forest.pkl   # Modèle de comparaison
│   ├── logistic_regression.pkl  # Baseline
│   └── evaluations.csv     # Métriques de performance
├── api/
│   ├── main.py            # BC05 - API FastAPI
│   └── (schémas intégrés dans main.py)
├── tests/
│   ├── test_acquisition.py
│   ├── test_nettoyage.py
│   └── test_modeles.py
├── docs/
│   ├── PLAN_OPERATIONNEL.md
│   ├── ARCHITECTURE.md
│   └── README_COMPLET.md  # Détails complets du projet
└── requirements.txt        # Dépendances globales
```

---

## Blocs de compétences RNCP

### BC01 - Infrastructure de données
- Téléchargement GBIF API + Open-Meteo
- Pipeline ETL (nettoyage, validation, agrégation)
- Stockage Parquet (data lake)
- Schema technique documenté

### BC02 - Analyse exploratoire
- Corrélations météo ↔ présence
- Analyse saisonnière par espèce
- Cartes densité observations
- Tests statistiques (seuils de température)

### BC03 - Machine Learning
- Classification binaire (présence/absence)
- Features engineered (température, pluie, jour année, région)
- Modèles : Logistic Regression, Random Forest, XGBoost
- Comparaison : Accuracy, F1-score, AUC-ROC

### BC04 - Deep Learning
- Optionnel (piste d'extension notebook)

### BC05 - Industrialisation
- API FastAPI (`/predict`, `/species`, `/health`)
- Dashboard Streamlit interactif
- Docker Dockerfile
- Logging & monitoring

### BC06 - Gestion de projet
- Planning agile (4 semaines)
- Documentation technique
- Présentation soutenance
- Analyse ROI écologique

---

## Démarrage rapide

### Installation

```bash
# Cloner le projet
cd oiseaux_migrateurs_npdc

# Créer environnement
python -m venv venv
source venv/bin/activate  # ou: venv\Scripts\activate (Windows)

# Installer dépendances
pip install -r requirements.txt
```

### Étapes d'exécution

```bash
# 1. Acquisition données
python scripts/acquisition.py

# 2. Nettoyage ETL
python scripts/nettoyage.py

# 3. Exploration
python scripts/eda.py

# 4. Entraînement modèles
python scripts/entrainer_modele.py

# 5. Lancer API
uvicorn api.main:app --reload

# 6. Lancer Dashboard
streamlit run dashboard.py
```

---

## Calendrier

| Phase | Durée | Livrables |
|-------|-------|-----------|
| **BC01** - Infrastructure | Semaine 1 | Scripts acquisition + nettoyage |
| **BC02** - EDA | Semaine 1-2 | Notebook exploration + rapports |
| **BC03** - ML | Semaine 2-3 | Modèles entraînés + comparaison |
| **BC04** - DL | Semaine 3 | Optionnel (piste d'extension) |
| **BC05** - Industrialisation | Semaine 4 | API + Dashboard + Docker |
| **BC06** - Présentation | Semaine 4 | Docs + slides soutenance |

---

## Indicateurs de succès

- Données > 10,000 observations GBIF
- Couverture météo > 95% (Open-Meteo)
- Accuracy modèle > 75% (baseline XGBoost)
- Comparaison de modèles classiques documentée
- API en production (réponse < 500ms)
- Dashboard interactif fonctionnel

---

**Auteur :** Projet RNCP - Concepteur Développeur en Science des Données  
**Région :** Nord-Pas-de-Calais  
**Année :** 2026

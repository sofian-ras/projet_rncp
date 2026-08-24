# Plan Opérationnel Détaillé - Oiseaux Migrateurs NPDC

## Planification Agile (4 semaines)

### **SEMAINE 1 - BC01 : Infrastructure de Données**

#### Jour 1-2 : Acquisition données
- [ ] Télécharger observations GBIF pour 4 espèces (2015-2024)
  - Hirondelle rustique : ~5000 obs
  - Cigogne blanche : ~2000 obs  
  - Martinet noir : ~3000 obs
  - Bergeronnette : ~4000 obs
- [ ] Validation : `Total > 10,000 observations `

**Commandes:**
```bash
python scripts/acquisition.py
```

**Livrables :**
- `donnees/brutes/observations_gbif.csv`

---

#### Jour 3-4 : Nettoyage ETL
- [ ] Valider coordonnées GPS (supprimer outliers)
- [ ] Filtrer région NPDC (bounding box)
- [ ] Supprimer doublons
- [ ] Formater dates (ISO 8601)
- [ ] Agrégation hebdomadaire

**Commandes:**
```bash
python scripts/nettoyage.py
```

**Livrables :**
- `donnees/traitees/observations_nettoyees.parquet`
- `donnees/traitees/grille_presence_hebdo.parquet`

---

#### Jour 5 : Téléchargement météo + Documentation
- [ ] Télécharger météo Open-Meteo pour centre NPDC (2015-2024)
- [ ] Joindre observations + météo par date
- [ ] Documenter schema technique
- [ ] Créer diagramme architecture (PNG)

**Livrables :**
- `donnees/traitees/meteo_npdc.parquet`
- `docs/ARCHITECTURE.md`
- `docs/schema_base_donnees.png`

---

### **SEMAINE 2 - BC02 : Analyse Exploratoire**

#### Jour 1-2 : Analyse exploratoire basique
- [ ] Distributions par espèce
- [ ] Saisonnalité (calendrier heatmap)
- [ ] Corrélations météo ↔ présence

**Notebook :** `notebooks/01_exploration.ipynb`
- Cellule 1 : Chargement données
- Cellule 2 : Statistiques descriptives
- Cellule 3 : Visualisations saisonnières

**Livrables :**
- Heatmap saisonnière 4 espèces
- Rapport corrélations (Pearson)

---

#### Jour 3-4 : Tests statistiques + Cartes
- [ ] Tests d'indépendance : température ↔ présence
- [ ] Cartes densité dynamiques (Folium)
- [ ] Statistique par région (Nord vs Pas-de-Calais)

**Livrables :**
- Cartes interactives HTML
- Résultats tests statistiques (p-values)

---

#### Jour 5 : Rapport EDA
- [ ] Synthèse insights clés
- [ ] Identification biais données
- [ ] Recommandations pour ML

**Livrable :**
- `docs/RAPPORT_EDA.md` (2-3 pages)

---

### **SEMAINE 3 - BC03/BC04 : Modélisation**

#### Jour 1-2 : Machine Learning (BC03)
- [ ] Feature engineering complet
  - Fenêtre météo (7j avant observation)
  - Variables temporelles (jour année, mois)
  - Normalization (StandardScaler)
- [ ] Entraîner 3 modèles :
  - Logistic Regression (baseline)
  - Random Forest
  - XGBoost
- [ ] Cross-validation (5-folds)
- [ ] Évaluation : Accuracy, F1, AUC-ROC

**Notebook :** `notebooks/02_machine_learning.ipynb`

**Livrables :**
- Modèles sérialisés (`modeles/pipeline_ml.pkl`)
- Matrice confusion (images)
- Courbes ROC (4 espèces x 3 modèles)

---

#### Jour 3-4 : Consolidation ML (BC03/BC04)
- [ ] Réentraîner les modèles sur données nettoyées
- [ ] Comparer XGBoost, Random Forest, Logistic Regression
- [ ] Vérifier robustesse des métriques

**Script :** `scripts/entrainer_modele.py`

**Livrables :**
- Modèle principal (`modeles/pipeline_ml.pkl`)
- Modèles de comparaison (`modeles/random_forest.pkl`, `modeles/logistic_regression.pkl`)
- Tableau récapitulatif performances (`modeles/evaluations.csv`)

---

#### Jour 5 : Sélection modèle final
- [ ] Comparer ALL modèles sur test set
- [ ] Choisir meilleur : XGBoost probable
- [ ] Documenter rationale choix

**Livrable :**
- `docs/RESULTATS_MODELES.md`

---

### **SEMAINE 4 - BC05/BC06 : Production + Présentation**

#### Jour 1 : API FastAPI (BC05)
- [ ] Coder endpoints :
  - `POST /predict` (prédire présence)
  - `GET /species` (liste espèces)
  - `GET /health` (status API)
- [ ] Validation Pydantic
- [ ] Error handling

**Fichier :** `api/main.py`

**Livrables :**
- API fonctionnelle sur `localhost:8000`
- Documentation Swagger auto (FastAPI)

---

#### Jour 2 : Dashboard Streamlit
- [ ] Interface sélection espèce + date
- [ ] Affichage prédiction
- [ ] Graphiques contexte saisonnier
- [ ] Carte densité observations

**Fichier :** `dashboard.py`

**Livrable :**
- Dashboard interactif (`streamlit run dashboard.py`)

---

#### Jour 3 : Docker + Déploiement
- [ ] Dockerfile complet
- [ ] Requirements Python gelés
- [ ] Test conteneur local
- [ ] Documentation déploiement

**Livrables :**
- `Dockerfile`
- `docs/DEPLOIEMENT.md`

---

#### Jour 4-5 : Documentation + Soutenance (BC06)
- [ ] Synthèse technique complète
- [ ] Slides powerpoint (15 min)
- [ ] Vidéo démo (optionnel)

**Livrables :**
- `docs/RAPPORT_TECHNIQUE.md`
- `slides.pptx`
- Licence CC-BY

---

## Ressources par bloc

### BC01 - Infrastructure
```
scripts/acquisition.py       → GBIF API
scripts/nettoyage.py         → ETL validation
config.py                    → Configuration centralisée
```

### BC02 - EDA
```
notebooks/01_exploration.ipynb   → Visualisations
scripts/eda.py                   → Analyses stats
```

### BC03 - ML
```
notebooks/02_machine_learning.ipynb
scripts/entrainer_modele.py
scripts/modeles.py
modeles/pipeline_ml.pkl
```

### BC04 - DL
```
Optionnel (piste d'extension future)
```

### BC05 - API
```
api/main.py
dashboard.py
Dockerfile
```

### BC06 - Docs
```
docs/ARCHITECTURE.md
docs/RAPPORT_TECHNIQUE.md
slides.pptx
```

---

## Critères de réussite

| Critère | Cible | Validation |
|---------|-------|----------|
| **Données acquises** | > 10,000 obs | CSV + Parquet |
| **Couverture météo** | > 95% | Pas de nulls |
| **Accuracy ML** | > 75% | CV sur test set |
| **LSTM entraîné** | Convergence | Loss < 0.5 |
| **API en ligne** | 200 OK | Swagger test |
| **Dashboard** | Intéractif | Screenshots |
| **Docker** | Build OK | Image runnable |
| **Documentation** | Complète | README complet |

---

## Commandes clés

```bash
# Installation
pip install -r requirements.txt

# Acquisition (J1-2 Semaine 1)
python scripts/acquisition.py

# Nettoyage (J3-4 Semaine 1)
python scripts/nettoyage.py

# EDA (Semaine 2)
jupyter notebook notebooks/01_exploration.ipynb

# ML (Semaine 3 J1-2)
jupyter notebook notebooks/02_machine_learning.ipynb

# Consolidation modèles (Semaine 3 J3-4)
python scripts/entrainer_modele.py

# API (Semaine 4 J1)
uvicorn api.main:app --reload

# Dashboard (Semaine 4 J2)
streamlit run dashboard.py

# Docker (Semaine 4 J3)
docker build -t oiseaux:latest .
docker run -p 8000:8000 oiseaux:latest
```

---

**Statut :** PRET A DEMARRER  
**Région :** Nord-Pas-de-Calais  
**Année universitaire :** 2025-2026

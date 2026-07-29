# Guide de Démarrage - Projet Oiseaux Migrateurs

## 🚀 Initialisation rapide (5 minutes)

### 1. Clone et setup environnement
```bash
cd c:\Users\Administrateur\Documents\Projet_RNCP\oiseaux_migrateurs_npdc

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt
```

### 2. Vérifier structure
```bash
# Lancer tests config
python scripts/config.py
```

Expected output:
```
✓ Configuration chargée
✓ Répertoires créés
ZONE: Nord-Pas-de-Calais (49.5-51.5°N, 1.5-4.0°E)
ESPECES: 4 (hirondelle, cigogne, martinet, bergeronnette)
```

---

## 📅 Roadmap par jour

### **Jour 1-2 : Acquisition de données (BC01)**

```bash
# Télécharger observations GBIF + météo
python scripts/acquisition.py

# Résultat attendu:
# ✓ donnees/brutes/observations_gbif.csv (10,000+ lignes)
# ✓ donnees/brutes/meteo_npdc.csv (3,650 jours)
```

**Checkpoint :** Vérifier fichiers existent
```bash
ls -lh donnees/brutes/
```

---

### **Jour 3-5 : Nettoyage & EDA (BC01/BC02)**

```bash
# Nettoyage ETL
python scripts/nettoyage.py

# Résultat:
# ✓ donnees/traitees/observations_nettoyees.parquet
# ✓ donnees/traitees/grille_presence_hebdo.parquet
```

```bash
# Exploration
python scripts/eda.py

# Résultat:
# ✓ outputs/eda/saisonnalite.png
# ✓ outputs/eda/correlations_meteo.png
# ✓ outputs/eda/carte_densite.html
```

**Visualiser résultats :**
```bash
# Ouvrir dans navigateur
start outputs/eda/carte_densite.html
```

---

### **Semaine 2 : Notebooks exploration (BC02)**

```bash
# Lancer Jupyter
jupyter notebook

# Ouvrir: notebooks/01_exploration.ipynb
# Et exécuter toutes cellules (Ctrl+A puis Ctrl+Enter)
```

**Checkpoint :** Tous graphiques visualisés ✓

---

### **Semaine 2-3 : Machine Learning (BC03)**

```bash
# Ouvrir notebook
jupyter notebook notebooks/02_machine_learning.ipynb

# Exécuter et admirer résultats:
# - Cross-validation 5-folds
# - Courbes ROC
# - Confusion matrices
# - Feature importance
```

**Résultats attendus :**
- ✓ Accuracy > 75%
- ✓ Modèles sauvegardés : modeles/pipeline_ml.pkl

---

### **Semaine 3 : Consolidation Modèles (BC03/BC04)**

```bash
# Entraîner et comparer les modèles
python scripts/entrainer_modele.py
```

**Résultats attendus :**
- ✓ Modèle principal sauvegardé : modeles/pipeline_ml.pkl
- ✓ Modèles de comparaison sauvegardés
- ✓ Évaluations disponibles : modeles/evaluations.csv

---

### **Semaine 4 : Production (BC05)**

#### API FastAPI
```bash
# Lancer API
python -m uvicorn api.main:app --reload

# Vérifier dans navigateur:
# http://localhost:8000/docs

# Tester endpoint:
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "espece": "hirondelle_rustique",
    "latitude": 50.5,
    "longitude": 2.75,
    "meteo": {
      "temperature_max": 18.5,
      "temperature_min": 12.3,
      "precipitation_sum": 2.1,
      "vent_max": 15.0,
      "humidite_moyenne": 65.0,
      "jour_annee": 120
    }
  }'
```

#### Dashboard Streamlit
```bash
# Lancer dashboard
streamlit run dashboard.py

# Ouvre automatiquement: http://localhost:8501
# Tester sélection espèce + visualisations
```

#### Docker
```bash
# Build image
docker build -t oiseaux:latest .

# Test conteneur
docker run -p 8000:8000 oiseaux:latest

# Vérifier API
curl http://localhost:8000/health
```

---

## 📊 Commandes d'analyse utiles

### Vérifier données
```python
import pandas as pd

df = pd.read_parquet("donnees/traitees/observations_nettoyees.parquet")
print(df.info())
print(df.head())
print(df['espece'].value_counts())
```

### Lister modèles
```bash
ls -lh modeles/
```

### Tests
```bash
pytest tests/ -v
pytest tests/test_acquisition.py -v --cov
```

---

## 🐛 Troubleshooting

### Erreur : "Modèle non trouvé"
```bash
# Vérifier fichiers existent
ls donnees/traitees/

# Si manquant, réexécuter:
python scripts/nettoyage.py
```

### Erreur : "GBIF API timeout"
```bash
# Normal, réessayer (rate-limiting GBIF)
# Attendre 5 min et relancer
python scripts/acquisition.py
```

### Erreur : "Port 8000 déjà utilisé"
```bash
# Utiliser autre port
uvicorn api.main:app --port 8001 --reload
```

### Erreur : "DataFrame vide"
```bash
# Vérifier zone géographique filtre
python -c "from scripts.config import ZONE_GEOGRAPHIQUE; print(ZONE_GEOGRAPHIQUE)"

# Vérifier coordonnées dans données brutes
python -c "
import pandas as pd
df = pd.read_csv('donnees/brutes/observations_gbif.csv')
print(f'Lat range: {df.latitude.min()} - {df.latitude.max()}')
print(f'Lon range: {df.longitude.min()} - {df.longitude.max()}')
"
```

---

## 📈 Métriques clés à tracker

```bash
# Après acquisition
grep -c "," donnees/brutes/observations_gbif.csv  # Nombre lignes

# Après nettoyage
python -c "
import pandas as pd
df = pd.read_parquet('donnees/traitees/observations_nettoyees.parquet')
print(f'Observations nettoyées: {len(df)}')
print(f'Espèces: {df.species.nunique()}')
print(f'Plage: {df.date_observation.min()} à {df.date_observation.max()}')
"

# Après ML
python -c "
import pandas as pd
df = pd.read_csv('modeles/evaluations.csv')
print(df)
"
```

---

## 🎤 Avant soutenance

### Checklist finale
- [ ] Tous scripts exécutés sans erreur
- [ ] Données téléchargées (> 10,000 observations) ✓
- [ ] Nettoyage complet (0 nulls) ✓
- [ ] EDA avec visualisations ✓
- [ ] ML avec 3+ modèles comparés ✓
- [ ] Deep Learning (LSTM) entraîné ✓
- [ ] API localhost fonctionne ✓
- [ ] Dashboard Streamlit marche ✓
- [ ] Docker buildable ✓
- [ ] Documentation complète ✓
- [ ] Slides powerpoint prêtes ✓

### Démo soutenance
```bash
# Terminal 1: Lancer API
uvicorn api.main:app --reload

# Terminal 2: Lancer Dashboard
streamlit run dashboard.py

# Montrer:
# 1. Données brutes téléchargées
# 2. Graphiques saisonnalité
# 3. API Swagger
# 4. Dashboard interactif
# 5. Docker build réussi
```

---

## 📞 Aide

**Ressources :**
- Documentation : [docs/PLAN_OPERATIONNEL.md](docs/PLAN_OPERATIONNEL.md)
- Architecture : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Code : Chaque script a docstrings français

**Contacter :**
- Voir README.md pour contact auteur
- Issues : Documenter dans `docs/ISSUES.md`

---

**Bon courage ! 🚀**  
Commence par Jour 1-2 (acquisition), puis suis le calendrier.

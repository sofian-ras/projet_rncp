# Prédiction des Oiseaux Migrateurs — Nord-Pas-de-Calais

Projet RNCP — Concepteur Développeur en Science des Données.

## Objectif

Prédire la probabilité de présence de 4 espèces d'oiseaux migrateurs dans le Nord-Pas-de-Calais à
partir de la saison, de la météo et de la position géographique.

**Problématique scientifique :** peut-on modéliser l'arrivée des migrations à partir de variables
climatiques ?

Pour une explication complète, pédagogique et déjà exécutée (données réelles, graphiques, résultats de
modèles), voir le notebook :
[`notebooks/Notebook_Soutenance_Oiseaux_Migrateurs.ipynb`](notebooks/Notebook_Soutenance_Oiseaux_Migrateurs.ipynb).
Ce notebook est un **document narratif figé** (résultats déjà exécutés et mis en cache) ; la version
à jour et exécutable du code est celle des `run.py` de chaque dossier `blocs/bc0X_.../`.

---

## Le projet est organisé en 6 blocs

Le référentiel RNCP est découpé en 6 blocs de compétences (BC01 à BC06), un dossier par bloc dans
`blocs/`. Le code commun (config, chemins, logging, chargement des données) vit dans **un seul
package `commun/`** à la racine ; les données et artefacts sont dans **un seul jeu de dossiers
racine** (`donnees/`, `modeles/`, `outputs/`). Chaque bloc a **un script exécutable** (`run.py`, plus
`api.py` / `dashboard.py` pour BC05) et un `README.md` décrivant objectif, code, commande de
démonstration et livrables.

Les blocs partagent donc leurs entrées/sorties : **BC01 doit être exécuté en premier** (il produit
`donnees/traitees/`), ensuite BC02, BC03 et BC04 dans n'importe quel ordre, puis BC05. Les parquets
de `donnees/traitees/` et le modèle `modeles/pipeline_ml.pkl` sont **versionnés** dans le dépôt :
après un simple clone, BC02 à BC05 tournent sans avoir à relancer BC01.

| Bloc | Dossier | Ce qu'il démontre |
|---|---|---|
| BC01 | [`blocs/bc01_infrastructure_donnees/`](blocs/bc01_infrastructure_donnees/README.md) | Acquisition (GBIF + Open-Meteo), nettoyage (ETL), [schéma d'architecture + RGPD](blocs/bc01_infrastructure_donnees/docs/architecture.md) |
| BC02 | [`blocs/bc02_analyse_exploratoire/`](blocs/bc02_analyse_exploratoire/README.md) | Analyse univariée, corrélations, tests statistiques, visualisations |
| BC03 | [`blocs/bc03_machine_learning/`](blocs/bc03_machine_learning/README.md) | Supervisé (3 modèles + MLflow + validation croisée + importance des variables) et non supervisé (K-Means) |
| BC04 | [`blocs/bc04_deep_learning/`](blocs/bc04_deep_learning/README.md) | Prédiction sur données non structurées (réseau de neurones sur texte) |
| BC05 | [`blocs/bc05_industrialisation/`](blocs/bc05_industrialisation/README.md) | API FastAPI + Dashboard Streamlit + Docker + [procédure de déploiement](blocs/bc05_industrialisation/docs/deploiement.md) |
| BC06 | [`blocs/bc06_gestion_projet/`](blocs/bc06_gestion_projet/README.md) | Tests automatisés, [rétroplanning + risques + ROI](blocs/bc06_gestion_projet/docs/gestion_projet.md), limites assumées |

### Stack technique par bloc

| Bloc | Technologies clés |
|---|---|
| BC01 | `requests` (API GBIF + Open-Meteo), `pandas` (ETL), `loguru` |
| BC02 | `pandas`, `matplotlib`/`seaborn`, `folium` (carte), `scipy` (tests statistiques) |
| BC03 | `scikit-learn` (régression logistique, forêt aléatoire, K-Means), `xgboost`, `mlflow` |
| BC04 | `TensorFlow`/`Keras` (Embedding + LSTM) |
| BC05 | `FastAPI`, `Pydantic`, `Streamlit`, `Docker` |
| BC06 | `pytest` |

Stockage : fichiers locaux (CSV, Parquet, pickle, `.keras`) dans `donnees/`, `modeles/`, `outputs/`
à la racine du projet.

```
oiseaux_migrateurs_npdc/
├── commun/                          # package partage : config, journalisation, chargement
├── donnees/
│   ├── brutes/                      # dumps GBIF + Open-Meteo (non versionne, produit par BC01)
│   └── traitees/                    # parquets nettoyes (VERSIONNES : fixtures d'entree BC02..BC05)
├── modeles/                         # pipeline_ml.pkl + evaluations.csv versionnes, reste ignore
├── outputs/                         # graphiques et cartes (non versionne, regenerable)
├── mlruns/                          # suivi MLflow de BC03 (non versionne)
├── blocs/
│   ├── bc01_infrastructure_donnees/ # acquisition.py + nettoyage.py + run.py + docs/architecture.md
│   ├── bc02_analyse_exploratoire/   # run.py : EDA, distributions, cartes, tests statistiques
│   ├── bc03_machine_learning/       # run.py + gestion_modeles.py + segmentation.py
│   ├── bc04_deep_learning/          # modele.py (Embedding+LSTM) + run.py
│   ├── bc05_industrialisation/      # api.py, dashboard.py, prediction.py, run.py, Dockerfile, docs/
│   └── bc06_gestion_projet/         # run.py + tests/ (testent le vrai acquisition.py de BC01) + docs/
├── notebooks/                       # Notebook de soutenance, narratif et deja execute
├── pyproject.toml                   # config pytest / black / isort
├── requirements.txt                 # dependances du projet complet
└── SUJETS_RNCP35288.md
```

### Feuille de route infrastructure

Le stockage est aujourd'hui local (fichiers CSV/Parquet/pickle). Le schéma d'infrastructure actuel,
les choix techniques, les coûts et la cible d'industrialisation (**MinIO** data lake, **PostgreSQL**
métadonnées, **Spark** si le volume le justifie) sont détaillés dans
[`blocs/bc01_infrastructure_donnees/docs/architecture.md`](blocs/bc01_infrastructure_donnees/docs/architecture.md).
Le volume actuel (~5 Mo) est traité instantanément par pandas et ne nécessite pas de calcul distribué
en l'état.

---

## Démarrage rapide

Installation unique, depuis la racine `oiseaux_migrateurs_npdc/`.

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File setup_venv.ps1
& "$env:USERPROFILE\venv_rncp\Scripts\Activate.ps1"
```

`setup_venv.ps1` crée le venv **à un chemin court** (`%USERPROFILE%\venv_rncp`) — indispensable pour
que TensorFlow (BC04) s'installe : dans un dossier profondément imbriqué, Windows dépasse la limite
de 260 caractères et l'installation échoue. Le script installe aussi `requirements.txt` et enregistre
le kernel Jupyter.

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Tout se fait dans ce venv activé.** Chaque commande de ce README (blocs, notebooks, `pytest`,
> API/dashboard) suppose le venv **activé** — sinon `python` pointe sur l'interpréteur système, où
> TensorFlow n'est pas installé. Les notebooks utilisent le kernel Jupyter `python3` créé par le
> script (ou `python -m ipykernel install --user --name python3` depuis le venv).

### Exécuter les blocs

Chaque `run.py` se lance depuis son propre dossier, **venv activé**. **BC01 en premier** (il produit
`donnees/traitees/`) ; ensuite les autres dans n'importe quel ordre.

```bash
cd blocs/bc01_infrastructure_donnees && python run.py   # BC01 - acquisition + nettoyage (ETL)
cd blocs/bc02_analyse_exploratoire   && python run.py   # BC02 - analyse exploratoire
cd blocs/bc03_machine_learning       && python run.py   # BC03 - 3 modèles ML + K-Means + MLflow
cd blocs/bc04_deep_learning          && python run.py   # BC04 - réseau de neurones (texte)
cd blocs/bc05_industrialisation      && python run.py   # BC05 - démonstration de prédiction sans serveur
cd blocs/bc06_gestion_projet         && python run.py   # BC06 - tests automatisés
```

> Après un simple `git clone`, `donnees/traitees/` et `modeles/pipeline_ml.pkl` sont déjà présents
> (versionnés) : BC02 à BC05 tournent sans relancer BC01.

### Lancer les services de BC05 (API + Dashboard)

Depuis `blocs/bc05_industrialisation/` :

```bash
# Terminal 1
python -m uvicorn api:app --reload
# -> documentation interactive : http://127.0.0.1:8000/docs

# Terminal 2
python -m streamlit run dashboard.py
# -> http://localhost:8501
```

### Dépannage : TensorFlow ne s'importe pas (BC04)

Symptôme : `python blocs/bc04_deep_learning/run.py` lève
`ModuleNotFoundError: No module named 'tensorflow...'`.

- **Cause la plus fréquente : le venv n'est pas activé.** `python` pointe alors sur l'interpréteur
  système, sans TensorFlow. Activer le venv (`& "$env:USERPROFILE\venv_rncp\Scripts\Activate.ps1"`).
- **Si l'installation elle-même a échoué sous Windows** (chemins internes de TensorFlow trop longs) :
  utiliser `setup_venv.ps1` (voir *Démarrage rapide*), qui place le venv à un chemin court. En dernier
  recours, activer les chemins longs Windows (droits administrateur), puis réinstaller :
  ```powershell
  reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1
  # redémarrer, puis : pip install --force-reinstall -r requirements.txt
  ```

### Docker (API uniquement)

Le contexte de build est la **racine du projet** (l'image a besoin de `commun/`, `modeles/` et
`donnees/traitees/`) :

```bash
docker build -f blocs/bc05_industrialisation/Dockerfile -t oiseaux-migrateurs-api .
docker run -p 8000:8000 oiseaux-migrateurs-api
```

Déploiement public (Render + Streamlit Cloud) : voir
[`blocs/bc05_industrialisation/docs/deploiement.md`](blocs/bc05_industrialisation/docs/deploiement.md).

### Tests

```bash
python -m pytest        # depuis la racine (config dans pyproject.toml)
```

Les tests portent sur le module d'acquisition de BC01 ; BC06 les rejoue via son `run.py`.

---

## Données utilisées

- **Observations d'oiseaux** — source : GBIF (Global Biodiversity Information Facility), 40 000
  observations, 4 espèces, période 2019-2024, région Nord-Pas-de-Calais (49.5°N-51.5°N, 1.5°E-4°E).
  GBIF ne recense quasiment aucune observation de ces espèces dans la zone avant 2019.
- **Météo** — source : Open-Meteo, 6 ans de données journalières (2 192 jours : température,
  précipitations, vent, humidité, pression).
- **Espèces étudiées :** Hirondelle rustique (*Hirundo rustica*), Cigogne blanche (*Ciconia ciconia*),
  Martinet noir (*Apus apus*), Bergeronnette printanière (*Motacilla alba*).

## Résultats clés

- 3 modèles de Machine Learning comparés (BC03) : Régression logistique, Forêt aléatoire, XGBoost —
  XGBoost retenu en production (AUC-ROC ≈ 0.91).
- Un réseau Embedding + LSTM (BC04) sur données textuelles (analyse de sentiment), démontrant la
  compétence Deep Learning sur données non structurées, distincte de BC03.
- Une API et un tableau de bord interactif (BC05) exposant le modèle à un utilisateur non technique.

Pour l'analyse détaillée (déséquilibre des classes, limites, interprétation des résultats), voir le
notebook et les `README.md` de chaque bloc.

---

**Auteur :** Projet RNCP — Concepteur Développeur en Science des Données
**Région :** Nord-Pas-de-Calais

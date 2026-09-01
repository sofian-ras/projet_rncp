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
Ce notebook est un **document narratif figé** (résultats déjà exécutés et mis en cache) : ses cellules
de code référencent l'ancienne organisation du projet (module `commun/` partagé, chemins d'import
`blocs.bc0X_....run`) et ne sont plus destinées à être ré-exécutées telles quelles depuis que chaque
bloc a été rendu autonome — seuls les `run.py` de chaque dossier `blocs/bc0X_.../` sont la version à
jour et exécutable du code.

---

## Le projet est organisé en 6 blocs, chacun 100% autonome

Le référentiel RNCP est découpé en 6 blocs de compétences (BC01 à BC06). Chaque bloc vit dans son
propre dossier et est **réellement exécutable seul** : si vous copiez/envoyez uniquement
`blocs/bc0X_.../` (sans le reste du projet), il fonctionne quand même. Concrètement, chaque dossier
de bloc embarque :
- son propre sous-package `commun/` (config, chemins, logging — une copie réduite à ses besoins,
  pas un import d'un dossier partagé situé ailleurs) ;
- son propre `requirements.txt` (installable indépendamment) ;
- pour les blocs qui ont besoin de données produites par un bloc précédent (BC02, BC03, BC05) : une
  **copie figée** de ces données directement dans son dossier (`donnees/`, `modeles/`, `outputs/`) —
  duplication assumée, au bénéfice de l'autonomie totale de chaque dossier ;
- **un seul script exécutable** (`run.py`, ou `api.py`/`dashboard.py` pour BC05) et **un
  `README.md`** décrivant l'objectif, le code, la commande de démonstration et les livrables produits.

Chaque bloc a été testé en le copiant seul, hors de ce projet, dans un dossier vide.

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

Stockage actuel : fichiers locaux (CSV, Parquet, pickle, `.keras`), embarqués dans chaque dossier de
bloc qui en a besoin.

```
oiseaux_migrateurs_npdc/
├── blocs/
│   ├── bc01_infrastructure_donnees/ # acquisition.py + nettoyage.py + run.py (orchestrateur)
│   │   ├── commun/                  # config locale (chemins, especes, zone geo, logging)
│   │   ├── donnees/                 # brutes/ + traitees/ -- generees par ce bloc
│   │   └── requirements.txt
│   ├── bc02_analyse_exploratoire/   # run.py autonome : EDA, cartes, tests statistiques
│   │   ├── commun/
│   │   ├── donnees/traitees/        # copie figee des parquets de BC01 (fixture d'entree)
│   │   └── requirements.txt
│   ├── bc03_machine_learning/       # run.py + gestion_modeles.py : entrainement + comparaison ML
│   │   ├── commun/
│   │   ├── donnees/traitees/        # copie figee (grille + meteo) -- fixture d'entree
│   │   └── requirements.txt
│   ├── bc04_deep_learning/          # modele.py (Embedding+LSTM) + run.py (orchestration)
│   │   ├── commun/
│   │   └── requirements.txt
│   ├── bc05_industrialisation/      # api.py, dashboard.py, prediction.py, run.py, Dockerfile
│   │   ├── commun/
│   │   ├── donnees/, modeles/, outputs/  # copies figees (BC01/BC02/BC03) -- fixtures d'entree
│   │   └── requirements.txt
│   └── bc06_gestion_projet/         # run.py + tests/ (copie locale, teste acquisition.py de BC01)
│       ├── commun/, acquisition.py, tests/
│       └── requirements.txt
├── notebooks/                       # Notebook de soutenance, narratif et déjà exécuté
└── SUJETS_RNCP35288.md              # Sujets de soutenance (document de référence)
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

Chaque bloc s'installe et se lance **depuis son propre dossier**, indépendamment des autres :

```bash
cd blocs/bc0X_.../
python -m venv .venv
.venv\Scripts\activate      # Windows -- ou: source .venv/bin/activate sur Linux/Mac
pip install -r requirements.txt
python run.py
```

### Exécuter un bloc, indépendamment des autres

```bash
cd blocs/bc01_infrastructure_donnees && python run.py   # BC01 - acquisition + nettoyage
cd blocs/bc02_analyse_exploratoire   && python run.py   # BC02 - analyse exploratoire
cd blocs/bc03_machine_learning       && python run.py   # BC03 - entraîne 3 modèles ML
cd blocs/bc04_deep_learning          && python run.py   # BC04 - entraîne un réseau de neurones (texte)
cd blocs/bc05_industrialisation      && python run.py   # BC05 - démonstration de prédiction sans serveur
cd blocs/bc06_gestion_projet         && python run.py   # BC06 - tests automatisés
```

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

> Chaque dossier `blocs/bc0X_.../` peut être copié/envoyé **seul** (sans le reste du projet) : il
> embarque son propre `commun/`, son propre `requirements.txt`, et — pour BC02/BC03/BC05 — une copie
> figée des données dont il a besoin. Vérifié en copiant chaque dossier isolément hors de ce projet.

### Dépannage : TensorFlow ne s'importe pas (BC04)

Sous Windows, si l'installation de TensorFlow échoue ou que `python blocs/bc04_deep_learning/run.py`
lève `ModuleNotFoundError: No module named 'tensorflow.python'` ou
`ImportError: cannot import name 'keras' from 'tensorflow'`, c'est généralement dû à la limite Windows
sur la longueur des chemins de fichiers (TensorFlow contient des chemins internes très longs).

Deux solutions :
1. **Activer les chemins longs Windows** (nécessite les droits administrateur), puis réinstaller :
   ```powershell
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1
   ```
   Redémarrer la machine, puis `pip install --force-reinstall -r requirements.txt`.
2. **Créer le venv à un chemin court** (ex: `C:\venv_rncp` plutôt qu'un chemin profondément imbriqué),
   qui laisse assez de marge à TensorFlow pour ses chemins internes sans toucher au registre :
   ```powershell
   python -m venv C:\venv_rncp
   C:\venv_rncp\Scripts\pip install -r requirements.txt
   C:\venv_rncp\Scripts\python blocs/bc04_deep_learning/run.py
   ```

### Docker (API uniquement)

Depuis `blocs/bc05_industrialisation/` :

```bash
docker build -t oiseaux-migrateurs-api .
docker run -p 8000:8000 oiseaux-migrateurs-api
```

### Tests

Chaque bloc gère ses propres tests. BC06 embarque une copie du code de BC01 et de ses tests :

```bash
cd blocs/bc06_gestion_projet
python -m pytest tests/ -v
```

---

## Données utilisées

- **Observations d'oiseaux** — source : GBIF (Global Biodiversity Information Facility), 40 000
  observations, 4 espèces, période 2015-2024, région Nord-Pas-de-Calais (49.5°N-51.5°N, 1.5°E-4°E).
- **Météo** — source : Open-Meteo, 10 ans de données journalières (température, précipitations, vent,
  humidité, pression).
- **Espèces étudiées :** Hirondelle rustique (*Hirundo rustica*), Cigogne blanche (*Ciconia ciconia*),
  Martinet noir (*Apus apus*), Bergeronnette printanière (*Motacilla alba*).

## Résultats clés

- 3 modèles de Machine Learning comparés (BC03) : Régression logistique, Forêt aléatoire, XGBoost —
  XGBoost retenu en production (AUC-ROC ≈ 0.94).
- Un réseau Embedding + LSTM (BC04) sur données textuelles (analyse de sentiment), démontrant la
  compétence Deep Learning sur données non structurées, distincte de BC03.
- Une API et un tableau de bord interactif (BC05) exposant le modèle à un utilisateur non technique.

Pour l'analyse détaillée (déséquilibre des classes, limites, interprétation des résultats), voir le
notebook et les `README.md` de chaque bloc.

---

**Auteur :** Projet RNCP — Concepteur Développeur en Science des Données
**Région :** Nord-Pas-de-Calais

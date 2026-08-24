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

---

## Le projet est organisé en 6 blocs, chacun autonome

Le référentiel RNCP est découpé en 6 blocs de compétences (BC01 à BC06). Chaque bloc vit dans son
propre dossier, avec **un seul script exécutable seul** (`run.py`) et **un `README.md`** décrivant
l'objectif, le code, la commande de démonstration et les livrables produits. Aucun bloc n'a besoin des
autres pour être présenté — chacun lit les fichiers déjà produits par les blocs précédents (s'il en a
besoin) directement sur disque, sans jamais ré-exécuter leur code.

| Bloc | Dossier | Ce qu'il démontre |
|---|---|---|
| BC01 | [`blocs/bc01_infrastructure_donnees/`](blocs/bc01_infrastructure_donnees/README.md) | Acquisition (GBIF + Open-Meteo) et nettoyage (ETL) |
| BC02 | [`blocs/bc02_analyse_exploratoire/`](blocs/bc02_analyse_exploratoire/README.md) | Visualisations et tests statistiques |
| BC03 | [`blocs/bc03_machine_learning/`](blocs/bc03_machine_learning/README.md) | Prédiction sur données structurées (3 modèles ML comparés) |
| BC04 | [`blocs/bc04_deep_learning/`](blocs/bc04_deep_learning/README.md) | Prédiction sur données non structurées (réseau de neurones sur texte) |
| BC05 | [`blocs/bc05_industrialisation/`](blocs/bc05_industrialisation/README.md) | API FastAPI + Dashboard Streamlit + Docker |
| BC06 | [`blocs/bc06_gestion_projet/`](blocs/bc06_gestion_projet/README.md) | Tests automatisés, planning, limites assumées |

```
oiseaux_migrateurs_npdc/
├── commun/                          # Configuration partagée par tous les blocs (une seule source de vérité)
│   └── config.py
├── blocs/
│   ├── bc01_infrastructure_donnees/ # run.py autonome : acquisition + nettoyage
│   ├── bc02_analyse_exploratoire/   # run.py autonome : EDA, cartes, tests statistiques
│   ├── bc03_machine_learning/       # run.py autonome : entraînement + comparaison ML
│   ├── bc04_deep_learning/          # run.py autonome : réseau Embedding+LSTM (texte)
│   ├── bc05_industrialisation/      # api.py, dashboard.py, run.py (démo sans serveur)
│   └── bc06_gestion_projet/         # run.py autonome : tests + état des lieux du projet
├── donnees/
│   ├── brutes/                      # CSV bruts (GBIF, Open-Meteo)
│   ├── traitees/                    # Parquets nettoyés (produits par BC01)
│   └── caracteristiques/
├── modeles/                         # Modèles sérialisés (.pkl, .keras) + métriques
├── outputs/                         # Graphiques et cartes générés (eda/, dl/)
├── notebooks/                       # Notebook de soutenance, narratif et déjà exécuté
├── tests/                           # Tests automatisés (pytest)
├── Dockerfile                       # Empaquette l'API (BC05)
├── requirements.txt
└── SUJETS_RNCP35288.md              # Sujets de soutenance (document de référence)
```

---

## Démarrage rapide

```bash
cd oiseaux_migrateurs_npdc
python -m venv .venv
.venv\Scripts\activate      # Windows -- ou: source .venv/bin/activate sur Linux/Mac
pip install -r requirements.txt
```

### Exécuter un bloc, indépendamment des autres

```bash
python blocs/bc01_infrastructure_donnees/run.py   # BC01 - acquisition + nettoyage
python blocs/bc02_analyse_exploratoire/run.py     # BC02 - analyse exploratoire
python blocs/bc03_machine_learning/run.py         # BC03 - entraîne 3 modèles ML
python blocs/bc04_deep_learning/run.py            # BC04 - entraîne un réseau de neurones (texte)
python blocs/bc05_industrialisation/run.py        # BC05 - démonstration de prédiction sans serveur
python blocs/bc06_gestion_projet/run.py           # BC06 - tests automatisés + état des lieux
```

### Lancer les services de BC05 (API + Dashboard)

```bash
# Terminal 1
python -m uvicorn blocs.bc05_industrialisation.api:app --reload
# -> documentation interactive : http://127.0.0.1:8000/docs

# Terminal 2
python -m streamlit run blocs/bc05_industrialisation/dashboard.py
# -> http://localhost:8501
```

### Docker (API uniquement)

```bash
docker build -t oiseaux-migrateurs-api .
docker run -p 8000:8000 oiseaux-migrateurs-api
```

### Tests

```bash
python -m pytest -v
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

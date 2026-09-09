# BC05 — Industrialisation d'un algorithme et automatisation

**Objectif RNCP :** rendre un modèle utilisable par un non-technicien, via une API et une application
web, packagées de façon portable (Docker).

`run.py` fait la démonstration de la logique de prédiction sans lancer de serveur, ce qui rend le bloc
présentable même sans les deux terminaux de l'API et du dashboard ouverts. Le lancement réel de l'API
et du dashboard reste disponible pour la démo live. Le modèle servi (`modeles/pipeline_ml.pkl`) est
produit par BC03.

---

## Ce qui est implémenté

- Une **API FastAPI** (`api.py`) avec 3 points d'entrée : `/health`, `/species`, `/predict`, avec
  validation automatique des données reçues (Pydantic).
- Un **tableau de bord Streamlit** (`dashboard.py`, 4 onglets) qui appelle cette API, sans nécessiter de
  savoir coder pour l'utiliser.
- Un **Dockerfile** qui empaquette l'API pour qu'elle fonctionne à l'identique sur n'importe quelle
  machine compatible Docker.
- Un **`docker-compose.yml`** (à la racine du projet) qui lève toute la chaîne d'un coup : data lake
  **MinIO**, entrepôt **MongoDB**, serveur **MLflow** (artefacts sur MinIO), API et dashboard. En
  mode `STORAGE_BACKEND=objet`, l'API récupère `pipeline_ml.pkl` depuis MinIO et le dashboard lit
  MongoDB — l'image n'embarque plus de copie figée comme source unique.

## Où le voir dans le code

- `notebook_bc05.ipynb` : déroulé **de haut en bas, façon cours** (charger le modèle de BC03 →
  reproduire `/predict` sans serveur → faire varier la saison → interroger l'API pour de vrai via un
  client de test, validation Pydantic comprise → présentation du dashboard et de Docker). Chaque
  section explique *pourquoi* / *ce qu'on veut* avant le code, *ce que le résultat veut dire* après,
  avec des liens vers `prediction.py` / `api.py`. Version pour l'explication orale.
- `api.py` : schémas Pydantic (`ObservationMeteo`, `DemandePredicton`), les 3 endpoints.
- `dashboard.py` : formulaire de prédiction, appel HTTP à l'API, affichage des statistiques.
- `Dockerfile` (dans ce dossier) : image de base, dépendances, commande de démarrage.
- `prediction.py` : logique de prédiction (construction des features, alignement des colonnes, calcul
  de la confiance) — partagée entre `api.py::predire_presence` et `run.py::demo_prediction`, pour
  qu'un changement de logique de prédiction ne puisse pas être fait dans l'un et oublié dans l'autre.
- `run.py` : reproduit exactement la logique de `/predict`, sans serveur, à partir du vrai modèle de
  production (`modeles/pipeline_ml.pkl`, produit par BC03).

## Démonstration

```bash
# venv activé (cf. README racine) ; ou notebook_bc05.ipynb pour la version expliquée
cd blocs/bc05_industrialisation

# Démonstration sans serveur (rapide, toujours disponible)
python run.py

# Lancement réel de l'API (terminal 1)
python -m uvicorn api:app --reload
# -> documentation interactive : http://127.0.0.1:8000/docs

# Lancement réel du dashboard (terminal 2)
python -m streamlit run dashboard.py
# -> http://localhost:8501

# Construire et lancer le conteneur Docker (API seule)
docker build -f blocs/bc05_industrialisation/Dockerfile -t oiseaux-migrateurs-api .
docker run -p 8000:8000 oiseaux-migrateurs-api

# OU toute la chaine en une commande, depuis la racine :
# infra (MinIO + MongoDB + MLflow) + BC01 (données) + BC03 (entraînement) + API + dashboard
docker compose up -d --build
```

## Livrables produits

- `blocs/bc05_industrialisation/api.py`, `dashboard.py`
- `Dockerfile` fonctionnel (image basée sur `commun/` + l'API seule, sans le dashboard)
- Documentation interactive générée automatiquement par FastAPI (`/docs`)
- Fichiers de déploiement prêts à l'emploi : `render.yaml` (Blueprint Docker), `Procfile`
- [`docs/deploiement.md`](docs/deploiement.md) : procédure pas à pas pour obtenir une URL publique
  (API sur Render, dashboard sur Streamlit Cloud) et traçabilité MLflow du modèle servi

## Traçabilité du modèle

Le modèle servi (`modeles/pipeline_ml.pkl`) provient de BC03, où chaque entraînement est enregistré
dans **MLflow** (paramètres, métriques, comparaison des 3 modèles). L'industrialisation part donc
d'un modèle tracé et reproductible.

## Statut

**Fonctionnel en local, prêt à déployer.** L'API et le dashboard fonctionnent et ont été testés
(démarrage vérifié, `/health` et `/species` répondent correctement). Le déploiement public n'est
pas encore effectué (comptes cloud à créer) mais tout est en place : `render.yaml`, `Procfile`,
`Dockerfile` et procédure détaillée dans `docs/deploiement.md`. Le dashboard lit déjà l'adresse de
l'API dans la variable d'environnement `API_URL`.

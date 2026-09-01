# BC05 — Industrialisation d'un algorithme et automatisation

**Objectif RNCP :** rendre un modèle utilisable par un non-technicien, via une API et une application
web, packagées de façon portable (Docker).

Ce bloc est **autonome** : `run.py` fait la démonstration de la logique de prédiction sans avoir besoin
de lancer un serveur, ce qui en fait un bloc présentable même sans les deux terminaux de l'API et du
dashboard ouverts. Le lancement réel de l'API et du dashboard reste disponible pour la démo live.

---

## Ce qui est implémenté

- Une **API FastAPI** (`api.py`) avec 3 points d'entrée : `/health`, `/species`, `/predict`, avec
  validation automatique des données reçues (Pydantic).
- Un **tableau de bord Streamlit** (`dashboard.py`, 4 onglets) qui appelle cette API, sans nécessiter de
  savoir coder pour l'utiliser.
- Un **Dockerfile** qui empaquette l'API pour qu'elle fonctionne à l'identique sur n'importe quelle
  machine compatible Docker.

## Où le voir dans le code

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
cd blocs/bc05_industrialisation
pip install -r requirements.txt

# Démonstration sans serveur (rapide, toujours disponible)
python run.py

# Lancement réel de l'API (terminal 1)
python -m uvicorn api:app --reload
# -> documentation interactive : http://127.0.0.1:8000/docs

# Lancement réel du dashboard (terminal 2)
python -m streamlit run dashboard.py
# -> http://localhost:8501

# Construire et lancer le conteneur Docker
docker build -t oiseaux-migrateurs-api .
docker run -p 8000:8000 oiseaux-migrateurs-api
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

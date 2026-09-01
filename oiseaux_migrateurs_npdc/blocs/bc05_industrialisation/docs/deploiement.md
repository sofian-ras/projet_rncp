# BC05 — Déploiement (obtenir une URL publique)

Le bloc fonctionne en local (`python run.py`, `uvicorn api:app`, `streamlit run dashboard.py`).
Cette page décrit comment le rendre accessible publiquement. Tous les fichiers nécessaires sont
dans ce dossier ; il ne reste qu'à créer les comptes (gratuits) et à connecter le dépôt.

## Vue d'ensemble

```
  Navigateur ---> Dashboard Streamlit  ---HTTP--->  API FastAPI  ---> pipeline_ml.pkl
                  (Streamlit Cloud)                 (Render, Docker)
```

Deux services séparés : l'**API** (conteneur Docker) et le **dashboard** (app Streamlit qui appelle
l'API). Le dashboard lit l'adresse de l'API dans la variable d'environnement `API_URL`
(`dashboard.py` : `API_URL = os.getenv("API_URL", "http://localhost:8000")`).

Le build Docker se fait **depuis la racine du projet** (`oiseaux_migrateurs_npdc/`), car l'image a
besoin du package `commun/`, du modèle `modeles/pipeline_ml.pkl` et de `donnees/traitees/` :

```bash
cd oiseaux_migrateurs_npdc
docker build -f blocs/bc05_industrialisation/Dockerfile -t oiseaux-migrateurs-api .
docker run -p 8000:8000 oiseaux-migrateurs-api
```

## 1. Déployer l'API sur Render (Docker)

1. Créer un compte sur https://dashboard.render.com (offre *free*).
2. **New → Blueprint**, connecter ce dépôt GitHub.
3. **Apply** : Render lit [`render.yaml`](../render.yaml) (`rootDir: oiseaux_migrateurs_npdc`,
   `dockerfilePath: ./blocs/bc05_industrialisation/Dockerfile`), construit l'image et lance
   `uvicorn api:app`.
4. À la fin, Render affiche l'URL publique, par ex. `https://oiseaux-migrateurs-api.onrender.com`.
   Vérifier : `…/health` renvoie `{"statut":"OK","modele_charge":true,…}` et `…/docs` affiche la
   documentation interactive.

> Alternatives équivalentes : **Railway** (`Procfile` déjà présent), **Fly.io** (`fly launch`),
> **Hugging Face Spaces** (type *Docker*). Le `Procfile` (`web: uvicorn api:app --host 0.0.0.0
> --port $PORT`) couvre les plateformes qui n'utilisent pas Docker.

## 2. Déployer le dashboard sur Streamlit Community Cloud

1. Créer un compte sur https://share.streamlit.io (gratuit).
2. **New app** → ce dépôt → fichier principal :
   `oiseaux_migrateurs_npdc/blocs/bc05_industrialisation/dashboard.py`.
3. **Advanced settings → Secrets / Variables** : ajouter
   `API_URL = "https://oiseaux-migrateurs-api.onrender.com"` (l'URL obtenue à l'étape 1).
4. **Deploy** : Streamlit installe `requirements.txt` et publie l'app à une URL
   `https://<nom>.streamlit.app`.

## 3. Livrable pour le jury

- **URL de l'API** : `https://…onrender.com/docs`
- **URL du dashboard** : `https://….streamlit.app`

À coller dans le support de soutenance et le README racine une fois le déploiement effectué.

## Traçabilité du modèle (MLflow)

Le modèle servi (`modeles/pipeline_ml.pkl`) est produit par BC03, où chaque entraînement est
enregistré dans MLflow (dossier `mlruns/` à la racine du projet : paramètres, métriques,
comparaison des 3 modèles). L'industrialisation part donc d'un modèle **tracé et reproductible**,
pas d'un artefact opaque. Consultable avec `mlflow ui --backend-store-uri mlruns`.

## Note

Sur l'offre gratuite de Render, le conteneur se met en veille après ~15 min d'inactivité ; la
première requête suivante prend ~30 s (démarrage à froid). Suffisant pour une démonstration ;
une offre payante (~7 $/mois) supprime la mise en veille.

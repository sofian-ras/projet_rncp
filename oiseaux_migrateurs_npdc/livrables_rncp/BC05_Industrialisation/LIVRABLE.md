# BC05 — Industrialisation d’un algorithme et automatisation des décisions

## Objectif RNCP
Exposer le modèle via API et application web utilisable par des non-techniques.

## Ce livrable contient
- API FastAPI avec endpoints métier
- Validation des entrées (Pydantic)
- Dashboard Streamlit connecté à l’API

## Fichier Python du livrable
- `bc05_industrialisation.py` (vérifie API et dashboard)

## Preuves dans le code
- `api/main.py` : `ObservationMeteo`, `DemandePredicton`, `/health`, `/species`, `/predict`
- `dashboard.py` : check santé API, formulaire utilisateur, appel `/predict`

## Démonstration
```bash
# terminal 1
python -m uvicorn oiseaux_migrateurs_npdc.api.main:app --host 127.0.0.1 --port 8000

# terminal 2
python -m streamlit run oiseaux_migrateurs_npdc/dashboard.py --server.port=8501

# terminal 3
python livrables_rncp/BC05_Industrialisation/bc05_industrialisation.py
```

## Livrables produits
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`
- Dashboard: `http://localhost:8501`

## Statut
- C5.2 API: OK
- C5.3 application web: OK (local)
- C5.1 standardisation MLflow/Docker: partiel (Docker présent, MLflow à compléter)

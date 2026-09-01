# Image de l'API BC05.
# Contexte de build = la racine du projet (oiseaux_migrateurs_npdc/) :
#   docker build -f blocs/bc05_industrialisation/Dockerfile -t oiseaux-migrateurs-api .
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

# requirements dedie (API + dashboard, sans tensorflow/jupyter) plutot que le requirements.txt racine
COPY blocs/bc05_industrialisation/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Code : package partage + l'API et sa logique de prediction
COPY commun/ ./commun/
COPY blocs/bc05_industrialisation/api.py blocs/bc05_industrialisation/prediction.py ./

# Artefacts necessaires a l'API : modele de production + donnees traitees
COPY modeles/pipeline_ml.pkl ./modeles/
COPY donnees/traitees/ ./donnees/traitees/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

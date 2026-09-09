# Conteneur d'entrainement de BC03 (service "bc03" de docker-compose.yml).
# Lit la grille depuis MongoDB, entraine 3 modeles, journalise dans MLflow,
# pousse pipeline_ml.pkl dans MinIO. Contexte de build = la racine du projet.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

COPY infra/requirements-ml.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY commun/ ./commun/
COPY blocs/bc03_machine_learning/ ./blocs/bc03_machine_learning/

CMD ["python", "blocs/bc03_machine_learning/run.py"]

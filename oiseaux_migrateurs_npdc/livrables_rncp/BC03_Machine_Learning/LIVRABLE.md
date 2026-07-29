# BC03 — Analyse prédictive de données structurées (Machine Learning)

## Objectif RNCP
Construire un pipeline ML supervisé, évaluer et sélectionner un modèle performant.

## Ce livrable contient
- Préparation des features (spatiales, temporelles, météo)
- Entraînement de 3 modèles (XGBoost, RF, LR)
- Évaluation multi-métriques
- Sauvegarde des modèles et métadonnées

## Fichier Python du livrable
- `bc03_machine_learning.py` (orchestrateur BC03)

## Preuves dans le code
- `scripts/entrainer_modele.py` : `preparer_features`, `entrainer_modeles`, `executer_entrainement`
- `scripts/modeles.py` : `evaluator_modele`, `sauvegarder_modele`, `comparer_modeles`

## Démonstration
```bash
cd oiseaux_migrateurs_npdc
python livrables_rncp/BC03_Machine_Learning/bc03_machine_learning.py
```

## Livrables produits
- `modeles/pipeline_ml.pkl`
- `modeles/random_forest.pkl`
- `modeles/logistic_regression.pkl`
- `modeles/evaluations.csv`
- `modeles/*_metadata.json`

## Statut
- C3.1 pipeline de traitement: OK
- C3.2 supervisé: OK
- C3.4 évaluation performance: OK
- C3.3 non-supervisé (segmentation/réduction): à compléter

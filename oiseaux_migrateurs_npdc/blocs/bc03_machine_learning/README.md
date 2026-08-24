# BC03 — Machine Learning (prédiction sur données structurées)

**Objectif RNCP :** entraîner, évaluer et comparer plusieurs modèles de Machine Learning sur un
problème de classification, et savoir interpréter correctement leurs résultats — y compris leurs
limites.

Ce bloc est **autonome** : il lit la grille produite par BC01 (`donnees/traitees/*.parquet`) sans
jamais ré-exécuter son code. Si ces fichiers n'existent pas, le script s'arrête avec un message clair.

---

## Ce qui est implémenté

- Préparation des features (position, période, météo) et de la cible (`presence`) à partir de la
  grille de BC01.
- Découpage entraînement/test stratifié (80/20), pour évaluer honnêtement les modèles.
- Entraînement et comparaison de **3 modèles** de complexité croissante : Régression logistique
  (référence), Forêt aléatoire, XGBoost.
- Évaluation avec 3 indicateurs : Accuracy, F1-score, AUC-ROC — et une lecture critique de ces
  indicateurs face au fort déséquilibre des classes (~98,6% d'absences).

## Où le voir dans le code

- `run.py`, fonction `preparer_features`.
- `run.py`, fonction `entrainer_modeles` (les 3 pipelines scikit-learn).
- `gestion_modeles.py`, classe `GestionnaireModeles` (sauvegarde, évaluation, métadonnées).
- Hyperparamètres définis dans `commun/config.py`, classe `ParametresML` — pas de valeurs magiques
  dans le code d'entraînement.

## Démonstration

```bash
cd oiseaux_migrateurs_npdc
python blocs/bc03_machine_learning/run.py
```

Durée : environ 1 minute (l'essentiel du temps est pris par la forêt aléatoire sur ~900 000 lignes).

## Livrables produits (vérifiables sur disque)

- `modeles/pipeline_ml.pkl` (XGBoost, modèle retenu en production)
- `modeles/random_forest.pkl`, `modeles/logistic_regression.pkl`
- `modeles/evaluations.csv` (tableau comparatif)
- `modeles/*_metadata.json` (métriques et features utilisées par modèle)

## Statut

**Complet.** Les 3 modèles sont réellement entraînés à chaque exécution (pas de résultats en dur), et
comparés avec des métriques adaptées au déséquilibre des classes.

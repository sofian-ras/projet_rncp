# BC03 — Machine Learning (prédiction sur données structurées)

**Objectif RNCP :** construire un pipeline de préparation, entraîner et comparer plusieurs modèles
supervisés, mesurer l'influence des variables, contrôler le sur-apprentissage, et démontrer une
approche non supervisée — en interprétant correctement les résultats, y compris leurs limites.

Ce bloc lit la grille produite par BC01 (`donnees/traitees/*.parquet`, versionnée dans le dépôt) sans
jamais ré-exécuter son code. Si ces fichiers n'existent pas, lancer BC01 d'abord.

---

## Ce qui est implémenté

### Supervisé
- Préparation des features (position, période, météo) et de la cible (`presence`) à partir de la
  grille de BC01.
- Découpage entraînement/test stratifié (80/20).
- Entraînement et comparaison de **3 modèles** de complexité croissante : régression logistique
  (référence), forêt aléatoire, XGBoost. Chaque entraînement est enregistré dans **MLflow**
  (paramètres + métriques).
- Évaluation avec Accuracy, F1-score, AUC-ROC — lecture critique face au fort déséquilibre des
  classes (~98,6 % d'absences).
- **Validation croisée stratifiée 5-fold** sur le modèle retenu + contrôle de l'**écart train/test**
  (détection du sur-apprentissage).
- **Influence des variables** (`feature_importances_` du modèle retenu) → CSV + graphique.

### Non supervisé
- **Segmentation K-Means** des zones de densité d'observations. Le nombre de zones K n'est pas fixé
  d'avance : on teste K de 2 à 8 et on retient celui qui maximise le **score de silhouette**.

## Où le voir dans le code

- `run.py`, `preparer_features` : construction de X / y.
- `run.py`, `construire_modeles` / `entrainer_modeles` : les 3 pipelines scikit-learn + suivi MLflow.
- `run.py`, `valider_modele_retenu` : validation croisée + écart train/test.
- `run.py`, `analyser_influence_variables` : importance des variables.
- `segmentation.py`, `segmenter_zones_densite` / `choisir_nombre_zones` : K-Means + silhouette.
- `gestion_modeles.py` : sauvegarde, évaluation, métadonnées, helpers MLflow.
- Hyperparamètres dans `commun/config.py` (`ParametresML`, `ParametresSegmentation`) — pas de
  valeurs magiques dans le code.

## Démonstration

```bash
pip install -r requirements.txt   # depuis la racine du projet, une seule fois
cd blocs/bc03_machine_learning
python run.py
```

Durée : ~1 minute. Le suivi MLflow est optionnel : sans le paquet `mlflow`, le bloc tourne quand
même (le suivi est simplement ignoré).

## Livrables produits (vérifiables sur disque)

- `modeles/pipeline_ml.pkl` (XGBoost, modèle retenu en production)
- `modeles/foret_aleatoire.pkl`, `modeles/regression_logistique.pkl`
- `modeles/evaluations.csv` (tableau comparatif) + `modeles/*_metadata.json` (métriques par modèle)
- `modeles/influence_variables.csv` + `modeles/influence_variables.png`
- `modeles/zones_densite.csv` (centres et volumes des zones K-Means)
- `mlruns/` a la racine (suivi MLflow ; `mlflow ui --backend-store-uri mlruns` pour l'explorer)

## Statut

**Complet.** Supervisé (3 modèles, MLflow, validation croisée, importance des variables) et non
supervisé (K-Means + silhouette) sont réellement exécutés à chaque lancement, sans résultats en dur.

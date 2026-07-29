# BC04 — Analyse prédictive de données non-structurées (Deep Learning)

## Objectif RNCP
Traiter des données non-structurées (texte/image/audio) avec un réseau de neurones et métriques de validation.

## Ce livrable contient (plan séparé)
- Périmètre proposé: NLP sentiment analysis (texte)
- Données: corpus texte étiqueté
- Modèle: réseau dense/LSTM simple avec TensorFlow
- Évaluation: métriques train/validation/test

## Fichier Python du livrable
- `bc04_deep_learning.py` (génère le plan d’exécution BC04)

## Implémentation actuelle dans le projet
- Paramètres DL présents: `scripts/config.py` (`ParametresDL`)
- Pas encore de pipeline DL complet en production

## Livrable à produire pour conformité complète
- `notebooks/03_deep_learning.ipynb` ou `scripts/deep_learning.py`
- `modeles/deep_learning_model.keras`
- `modeles/deep_learning_metrics.json`
- `outputs/dl/confusion_matrix.png`

## Démonstration cible
```bash
cd oiseaux_migrateurs_npdc
python livrables_rncp/BC04_Deep_Learning/bc04_deep_learning.py
```

## Livrables produits par ce script
- `livrables_rncp/BC04_Deep_Learning/bc04_plan_execution.json`

## Statut
- BC04: à compléter (livrable séparé, clairement isolé)

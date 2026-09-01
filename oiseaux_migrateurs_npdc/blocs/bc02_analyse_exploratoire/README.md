# BC02 — Analyse exploratoire

**Objectif RNCP :** savoir résumer, visualiser et interroger statistiquement des données avant de se
précipiter sur un modèle d'intelligence artificielle.

Ce bloc lit les fichiers produits par BC01 (`donnees/traitees/*.parquet`, versionnés dans le dépôt)
sans jamais ré-exécuter son code. Si ces fichiers n'existent pas, lancer BC01 d'abord.

---

## Ce qui est implémenté

- Analyse de **saisonnalité** : distribution mensuelle des observations par espèce, comparée au
  calendrier de migration attendu.
- **Analyse univariée** des variables météo : moyennes, écarts-types, valeurs extrêmes détectées par
  la règle de l'écart interquartile (IQR), grille d'histogrammes de distribution.
- **Carte de densité** interactive (heatmap Folium) des observations dans la région.
- **Corrélations** de Pearson entre chaque variable météo et la présence, par espèce (analyse
  multivariée).
- **Test statistique du χ² d'indépendance** entre le mois et l'espèce observée, pour valider
  objectivement que la saisonnalité n'est pas due au hasard (analyse inférentielle).

## Où le voir dans le code

- `run.py`, classe `AnalyseurExploratoire.analyser_saisonnalite`.
- `run.py`, classe `AnalyseurExploratoire.analyser_distributions` (univarié : moyennes/variances/IQR).
- `run.py`, classe `AnalyseurExploratoire.creer_carte_densite`.
- `run.py`, classe `AnalyseurExploratoire.analyser_correlations` (multivarié : matrice de Pearson).
- `run.py`, fonction `test_independance_chi2` (utilise `scipy.stats.chi2_contingency`).

## Démonstration

```bash
pip install -r requirements.txt   # depuis la racine du projet, une seule fois
cd blocs/bc02_analyse_exploratoire
python run.py
```

Puis ouvrir `outputs/eda/carte_densite.html` dans un navigateur pour la carte interactive.

## Livrables produits (vérifiables sur disque)

- `outputs/eda/saisonnalite.png`
- `outputs/eda/distributions_meteo.png`
- `outputs/eda/carte_densite.html`
- `outputs/eda/correlations_meteo.png`
- Tableau des statistiques univariées (moyenne / écart-type / min / max / valeurs extrêmes) et
  résultat du test χ² affichés dans la console (χ² ≈ 11 477, p-value < 0.05)

## Note sur le périmètre

Le référentiel prévoit une seconde étude de cas sur une **base massive et déstructurée traitée avec
Spark**. Le jeu de données de ce projet (~1 million de lignes, ~5 Mo) est traité instantanément par
pandas ; un volet Spark n'apporterait rien à ce volume. Le passage à un traitement distribué
(MinIO + Spark + PostgreSQL) est décrit comme cible d'industrialisation dans le document
d'architecture de BC01.

## Statut

**Complet** pour l'analyse non massive (descriptive, univariée, multivariée, inférentielle) sur les
vraies données de BC01, avec des résultats reproductibles.

# BC02 — Analyse exploratoire

**Objectif RNCP :** savoir résumer, visualiser et interroger statistiquement des données avant de se
précipiter sur un modèle d'intelligence artificielle.

Ce bloc est **autonome** : il lit les fichiers déjà produits par BC01 (`donnees/traitees/*.parquet`)
sans jamais ré-exécuter son code. Si ces fichiers n'existent pas, le script s'arrête avec un message
clair.

---

## Ce qui est implémenté

- Analyse de **saisonnalité** : distribution mensuelle des observations par espèce, comparée au
  calendrier de migration attendu.
- **Carte de densité** interactive (heatmap Folium) des observations dans la région.
- **Corrélations** de Pearson entre chaque variable météo et la présence, par espèce.
- **Test statistique du χ² d'indépendance** entre le mois et l'espèce observée, pour valider
  objectivement que la saisonnalité n'est pas due au hasard.

## Où le voir dans le code

- `run.py`, classe `AnalyseurExploratoire.analyser_saisonnalite`.
- `run.py`, classe `AnalyseurExploratoire.creer_carte_densite`.
- `run.py`, classe `AnalyseurExploratoire.analyser_correlations`.
- `run.py`, fonction `test_independance_chi2` (utilise `scipy.stats.chi2_contingency`).

## Démonstration

```bash
cd blocs/bc02_analyse_exploratoire
pip install -r requirements.txt
python run.py
```

Puis ouvrir `outputs/eda/carte_densite.html` dans un navigateur pour la carte interactive.

## Livrables produits (vérifiables sur disque)

- `outputs/eda/saisonnalite.png`
- `outputs/eda/carte_densite.html`
- `outputs/eda/correlations_meteo.png`
- Résultat du test χ² affiché dans la console (χ² ≈ 11 477, p-value < 0.05)

## Statut

**Complet.** Les 3 analyses tournent sur les vraies données de BC01 et produisent des résultats
reproductibles.

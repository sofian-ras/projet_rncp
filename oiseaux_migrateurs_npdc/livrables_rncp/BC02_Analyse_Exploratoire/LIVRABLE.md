# BC02 — Analyse exploratoire, descriptive et inférentielle

## Objectif RNCP
Nettoyer, analyser et présenter les données de manière statistique et visuelle.

## Ce livrable contient
- Nettoyage structuré des observations
- Construction de la grille hebdomadaire présence/absence
- Analyse saisonnalité, densité, corrélations
- Test statistique chi2

## Fichier Python du livrable
- `bc02_analyse.py` (orchestrateur BC02)

## Preuves dans le code
- `scripts/nettoyage.py` : `NettoyeurObservations`, `creer_grille_hebdomadaire`, `traiter_meteo`, `executer_nettoyage`
- `scripts/eda.py` : `analyser_saisonnalite`, `creer_carte_densite`, `analyser_correlations`, `test_independance_chi2`

## Démonstration
```bash
cd oiseaux_migrateurs_npdc
python livrables_rncp/BC02_Analyse_Exploratoire/bc02_analyse.py
```

## Livrables produits
- `donnees/traitees/observations_nettoyees.parquet`
- `donnees/traitees/grille_presence_hebdo.parquet`
- `donnees/traitees/meteo_processed.parquet`
- `outputs/eda/saisonnalite.png`
- `outputs/eda/carte_densite.html`
- `outputs/eda/correlations_meteo.png`

## Statut
- C2.1 descriptif + inférentiel: OK
- C2.2 univarié/multivarié: OK
- C2.4 visualisation: OK
- C2.3 parallélisé Spark: à compléter

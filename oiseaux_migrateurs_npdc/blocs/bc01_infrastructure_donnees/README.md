# BC01 — Infrastructure de données

**Objectif RNCP :** construire une chaîne technique capable d'aller chercher des données réelles dans
le monde extérieur, de les stocker, de les nettoyer et de les transformer en un format exploitable
par la suite du projet.

Ce bloc est **autonome** : il peut être présenté et exécuté seul, sans avoir besoin des autres blocs.

---

## Ce qui est implémenté

- Téléchargement automatisé de **40 000 observations** d'oiseaux (4 espèces) depuis l'API publique
  **GBIF**, filtrées sur la région Nord-Pas-de-Calais et la période 2015-2024.
- Téléchargement de **10 ans de météo journalière** (température, pluie, vent, humidité, pression)
  depuis l'API publique **Open-Meteo**.
- Un pipeline **ETL** (Extract-Transform-Load) en 5 étapes : suppression des lignes incomplètes,
  validation des coordonnées GPS, filtrage géographique, uniformisation des dates, suppression des
  doublons.
- La transformation clé du projet : construction d'une **grille hebdomadaire présence/absence**
  (1 135 680 lignes), qui transforme des observations éparses en un jeu de données exploitable par un
  algorithme de classification.

## Où le voir dans le code

- `run.py`, classe `AcquisiteurGBIF` : pagination de l'API GBIF, filtre géographique WKT.
- `run.py`, classe `AcquisiteurMeteo` : appel à l'API Open-Meteo.
- `run.py`, classe `NettoyeurObservations` : les 5 étapes de nettoyage, dans l'ordre.
- `run.py`, classe `AggregeurTemporel.creer_grille_hebdomadaire` : le cœur de la transformation
  (discrétisation spatiale à 0.1°, grille complète par produit cartésien, marquage présence/absence).
- Configuration centrale utilisée : `commun/config.py` (zone géographique, espèces, paramètres).

## Démonstration

```bash
cd oiseaux_migrateurs_npdc
python blocs/bc01_infrastructure_donnees/run.py
```

Par défaut, si les fichiers bruts sont déjà présents (`donnees/brutes/*.csv`), le téléchargement est
sauté et seul le nettoyage est rejoué (rapide, ne dépend pas d'internet). Pour tout re-télécharger :

```bash
python blocs/bc01_infrastructure_donnees/run.py --forcer-telechargement
```

## Livrables produits (vérifiables sur disque)

- `donnees/brutes/observations_gbif.csv` (40 000 lignes)
- `donnees/brutes/meteo_npdc.csv` (3 653 jours)
- `donnees/traitees/observations_nettoyees.parquet` (39 986 lignes)
- `donnees/traitees/grille_presence_hebdo.parquet` (1 135 680 lignes)
- `donnees/traitees/meteo_processed.parquet`

## Statut

**Complet.** Les deux sources sont interrogées automatiquement, le nettoyage est testé
(`tests/test_acquisition.py`), et les fichiers de sortie sont ceux réellement utilisés par BC02 et BC03.

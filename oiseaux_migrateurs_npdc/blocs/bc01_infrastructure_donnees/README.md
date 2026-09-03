# BC01 — Infrastructure de données

**Objectif RNCP :** construire une chaîne technique capable d'aller chercher des données réelles dans
le monde extérieur, de les stocker, de les nettoyer et de les transformer en un format exploitable
par la suite du projet.

BC01 est le **premier maillon** de la chaîne : il ne dépend d'aucun autre bloc et produit les
fichiers `donnees/traitees/*.parquet` consommés par BC02 à BC05.

**Schéma d'infrastructure, choix techniques, coûts et conformité RGPD :**
[`docs/architecture.md`](docs/architecture.md) (1 page).

---

## Ce qui est implémenté

- Téléchargement automatisé de **40 000 observations** d'oiseaux (4 espèces) depuis l'API publique
  **GBIF**, filtrées sur la région Nord-Pas-de-Calais et la période 2019-2024 (GBIF ne recense
  quasiment aucune observation de ces espèces dans la zone avant 2019).
- Téléchargement de **6 ans de météo journalière** (2 192 jours : température, pluie, vent, humidité,
  pression) depuis l'API publique **Open-Meteo**.
- Un pipeline **ETL** (Extract-Transform-Load) en 5 étapes : suppression des lignes incomplètes,
  validation des coordonnées GPS, filtrage géographique, uniformisation des dates, suppression des
  doublons.
- La transformation clé du projet : construction d'une **grille hebdomadaire présence/absence**
  (681 408 lignes = 6 ans × 52 semaines × 4 espèces × 546 mailles), qui transforme des observations
  éparses en un jeu de données exploitable par un algorithme de classification.

## Où le voir dans le code

- `acquisition.py`, classe `AcquisiteurGBIF` : pagination de l'API GBIF, filtre géographique WKT.
- `acquisition.py`, classe `AcquisiteurMeteo` : appel à l'API Open-Meteo.
- `nettoyage.py`, classe `NettoyeurObservations` : les 5 étapes de nettoyage, dans l'ordre.
- `nettoyage.py`, classe `AggregeurTemporel.creer_grille_hebdomadaire` : le cœur de la transformation
  (discrétisation spatiale à 0.1°, grille complète par produit cartésien, marquage présence/absence).
- `run.py` : orchestrateur mince (argparse + appel de `acquisition.executer_acquisition` puis
  `nettoyage.executer_nettoyage`) — acquisition et nettoyage sont deux métiers séparés en deux fichiers.
- Configuration centrale utilisée : `commun/config.py` (zone géographique, espèces, paramètres).

## Démonstration

```bash
pip install -r requirements.txt   # depuis la racine du projet, une seule fois
cd blocs/bc01_infrastructure_donnees
python run.py
```

Par défaut, si les fichiers bruts sont déjà présents (`donnees/brutes/*.csv`), le téléchargement est
sauté et seul le nettoyage est rejoué (rapide, ne dépend pas d'internet). Pour tout re-télécharger :

```bash
python run.py --forcer-telechargement
```

## Livrables produits (vérifiables sur disque)

- `donnees/brutes/observations_gbif.csv` (40 000 lignes)
- `donnees/brutes/meteo_npdc.csv` (2 192 jours, 2019-2024)
- `donnees/traitees/observations_nettoyees.parquet` (39 986 lignes)
- `donnees/traitees/grille_presence_hebdo.parquet` (681 408 lignes)
- `donnees/traitees/meteo_processed.parquet`

## Statut

**Complet.** Les deux sources sont interrogées automatiquement, le nettoyage est testé
(`tests/test_acquisition.py`), et les fichiers de sortie sont ceux réellement utilisés par BC02 et BC03.

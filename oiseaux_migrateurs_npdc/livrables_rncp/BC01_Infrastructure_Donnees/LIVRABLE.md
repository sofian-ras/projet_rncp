# BC01 — Construction et alimentation d'une infrastructure de gestion de données

## Objectif RNCP
Construire l’infrastructure de collecte/stockage et le pipeline ETL de base.

## Ce livrable contient
- Configuration centrale (espèces, zone, paramètres)
- Acquisition GBIF + Open-Meteo
- Données brutes persistées
- Journalisation d’exécution

## Fichier Python du livrable
- `bc01_infrastructure.py` (orchestrateur BC01)

## Preuves dans le code
- `scripts/config.py` : `BoundingBoxNPdC`, `ESPECES`, `ParametresAcquisition`
- `scripts/acquisition.py` : `AcquisiteurGBIF`, `telecharger_observations_espece`, `AcquisiteurMeteo`, `executer_acquisition`

## Démonstration
```bash
cd oiseaux_migrateurs_npdc
python livrables_rncp/BC01_Infrastructure_Donnees/bc01_infrastructure.py
```

## Livrables produits
- `donnees/brutes/observations_gbif.csv`
- `donnees/brutes/meteo_npdc.csv`
- logs dans `logs/`

## Statut
- C1.3 (collecte multi-sources): OK
- C1.4 (ETL préparatoire): OK (complété dans BC02)
- C1.1 Data Lake/Warehouse formel: partiel
- C1.2 Spark/Redshift: à compléter

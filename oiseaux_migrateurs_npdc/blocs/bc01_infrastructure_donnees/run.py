"""
BC01 - Infrastructure de donnees
=================================

Ce script est AUTONOME : il peut etre lance seul, sans avoir besoin
qu'un autre bloc ait ete execute avant lui.

Il orchestre deux etapes, portees chacune par un fichier dedie du meme
dossier (separation des responsabilites, cf. bc03_machine_learning qui
suit le meme patron avec gestion_modeles.py) :
  1. ACQUISITION (acquisition.py) : telecharge les observations d'oiseaux
     (GBIF) et la meteo historique (Open-Meteo) -> donnees/brutes/*.csv
  2. NETTOYAGE / ETL (nettoyage.py) : valide, deduplique, et transforme
     ces donnees brutes en une grille hebdomadaire presence/absence
     exploitable par le Machine Learning -> donnees/traitees/*.parquet

Utilisation :
    python blocs/bc01_infrastructure_donnees/run.py
    python blocs/bc01_infrastructure_donnees/run.py --forcer-telechargement

Par defaut, si les fichiers bruts existent deja sur disque, l'etape de
telechargement est sautee (pour une demonstration rapide et qui ne
depend pas d'internet) ; utiliser --forcer-telechargement pour tout
re-telecharger depuis les API.
"""

import argparse
import sys
from pathlib import Path

_racine = next(p for p in Path(__file__).resolve().parents if (p / "commun").is_dir())
sys.path.insert(0, str(_racine))  # racine du projet -> package commun/

from commun.config import REPERTOIRE_DONNEES_BRUTES, REPERTOIRE_DONNEES_TRAITEES, REPERTOIRE_RACINE
from commun.journalisation import configurer_logger
from acquisition import executer_acquisition
from nettoyage import executer_nettoyage

RACINE_PROJET = REPERTOIRE_RACINE
logger = configurer_logger()


def main() -> None:
    parser = argparse.ArgumentParser(description="BC01 - Infrastructure de donnees (acquisition + nettoyage)")
    parser.add_argument(
        "--forcer-telechargement", action="store_true",
        help="Re-telecharge les donnees depuis GBIF/Open-Meteo meme si des fichiers bruts existent deja.",
    )
    args = parser.parse_args()

    print("\n" + "#" * 70)
    print("# BC01 - INFRASTRUCTURE DE DONNEES")
    print("#" * 70 + "\n")

    executer_acquisition(forcer=args.forcer_telechargement)
    executer_nettoyage()

    print("\nPreuves produites (fichiers verifiables sur disque) :")
    for chemin in [
        REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv",
        REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv",
        REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet",
        REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet",
        REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet",
    ]:
        marque = "OK" if chemin.exists() else "MANQUANT"
        print(f"  [{marque}] {chemin.relative_to(RACINE_PROJET)}")

    print("\nBC01 termine.\n")


if __name__ == "__main__":
    main()

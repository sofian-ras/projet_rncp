"""
BC06 - Gestion et pilotage du projet
=======================================

Bloc de pilotage : il demontre la competence "piloter et fiabiliser un
projet de bout en bout".

  1. Il execute la suite de tests automatises (tests/, qui portent sur le
     module d'acquisition de BC01) et affiche le resultat en direct.
  2. Il rappelle le planning du projet et les limites assumees, et renvoie
     vers docs/gestion_projet.md (retroplanning, risques, ROI).

Utilisation :
    python run.py
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # racine du projet -> package commun/

from commun.journalisation import configurer_logger

RACINE_PROJET = Path(__file__).resolve().parent
logger = configurer_logger()

PLANNING = [
    ("Semaine 1", "BC01", "Acquisition des donnees (GBIF, Open-Meteo) et pipeline de nettoyage"),
    ("Semaine 2", "BC02", "Analyse exploratoire, visualisations, tests statistiques"),
    ("Semaine 3", "BC03 / BC04", "Machine Learning (donnees structurees) et Deep Learning (texte)"),
    ("Semaine 4", "BC05 / BC06", "API, dashboard, Docker, documentation et soutenance"),
]


def executer_tests() -> bool:
    logger.info("Execution de la suite de tests automatises (pytest)...")
    resultat = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--no-header"],
        cwd=str(RACINE_PROJET), capture_output=True, text=True,
    )
    print(resultat.stdout[-3000:])
    if resultat.returncode == 0:
        logger.info("Tous les tests automatises passent.")
    else:
        logger.warning("Certains tests ont echoue -- voir le detail ci-dessus.")
    return resultat.returncode == 0


def afficher_planning() -> None:
    print("\n--- Planning agile (4 semaines) ---\n")
    for semaine, blocs, objectif in PLANNING:
        print(f"  {semaine:<10} {blocs:<14} {objectif}")
    print("\n  Retroplanning date, jalons, analyse des risques et ROI : docs/gestion_projet.md")


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC06 - GESTION ET PILOTAGE DU PROJET")
    print("#" * 70 + "\n")

    executer_tests()
    afficher_planning()

    print("\nLimites assumees et pistes d'amelioration (voir le README de ce bloc) :")
    print("  - Fort desequilibre des classes en BC03 (rappel des presences reelles perfectible)")
    print("  - Meteo seule faiblement correlee a la presence (voir BC02)")
    print("  - BC04 utilise un jeu de donnees texte generique (IMDB), distinct du theme")
    print("    ornithologique, pour demontrer specifiquement la competence donnees non structurees")
    print("  - Deploiement cloud (URL publique de l'API/dashboard) documente mais non realise")

    print("\nBC06 termine.\n")


if __name__ == "__main__":
    main()

"""
BC06 - Gestion et pilotage du projet
=======================================

Ce script est AUTONOME : il ne depend d'aucun autre bloc pour s'executer
(il fonctionne meme si aucune donnee n'a encore ete telechargee). Il
demontre la competence "piloter et fiabiliser un projet de bout en bout" :

  1. Il execute la suite de tests automatises (tests/) et affiche le
     resultat, en direct.
  2. Il dresse un etat des lieux du projet : quels blocs ont deja
     produit leurs preuves sur disque (fichiers de donnees, modeles,
     graphiques), et lesquels restent a lancer.

Utilisation :
    python blocs/bc06_gestion_projet/run.py
"""

import subprocess
import sys
from pathlib import Path

RACINE_PROJET = Path(__file__).resolve().parents[2]
if str(RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(RACINE_PROJET))

from commun.config import REPERTOIRE_DONNEES_BRUTES, REPERTOIRE_DONNEES_TRAITEES, REPERTOIRE_MODELES  # noqa: E402

PLANNING = [
    ("Semaine 1", "BC01", "Acquisition des donnees (GBIF, Open-Meteo) et pipeline de nettoyage"),
    ("Semaine 2", "BC02", "Analyse exploratoire, visualisations, tests statistiques"),
    ("Semaine 3", "BC03 / BC04", "Machine Learning (donnees structurees) et Deep Learning (texte)"),
    ("Semaine 4", "BC05 / BC06", "API, dashboard, Docker, documentation et soutenance"),
]

PREUVES_PAR_BLOC = {
    "BC01 - Infrastructure de donnees": [
        REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv",
        REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet",
    ],
    "BC02 - Analyse exploratoire": [
        RACINE_PROJET / "outputs" / "eda" / "saisonnalite.png",
        RACINE_PROJET / "outputs" / "eda" / "correlations_meteo.png",
    ],
    "BC03 - Machine Learning": [
        REPERTOIRE_MODELES / "pipeline_ml.pkl",
        REPERTOIRE_MODELES / "evaluations.csv",
    ],
    "BC04 - Deep Learning": [
        REPERTOIRE_MODELES / "deep_learning_sentiment.keras",
        RACINE_PROJET / "outputs" / "dl" / "entrainement_et_confusion.png",
    ],
    "BC05 - Industrialisation": [
        RACINE_PROJET / "blocs" / "bc05_industrialisation" / "api.py",
        RACINE_PROJET / "blocs" / "bc05_industrialisation" / "dashboard.py",
        RACINE_PROJET / "Dockerfile",
    ],
}


def executer_tests() -> bool:
    print("--- Execution de la suite de tests automatises (pytest) ---\n")
    resultat = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--no-header"],
        cwd=str(RACINE_PROJET), capture_output=True, text=True,
    )
    print(resultat.stdout[-3000:])
    if resultat.returncode == 0:
        print("Tous les tests automatises passent.")
    else:
        print("Certains tests ont echoue -- voir le detail ci-dessus.")
    return resultat.returncode == 0


def etat_des_lieux() -> None:
    print("\n--- Etat des lieux : preuves produites par bloc ---\n")
    for bloc, fichiers in PREUVES_PAR_BLOC.items():
        statuts = [f.exists() for f in fichiers]
        global_ok = all(statuts)
        etat = "PRET" if global_ok else "A LANCER"
        print(f"[{etat}] {bloc}")
        for fichier, ok in zip(fichiers, statuts):
            marque = "OK" if ok else "manquant"
            try:
                chemin_affiche = fichier.relative_to(RACINE_PROJET)
            except ValueError:
                chemin_affiche = fichier
            print(f"    [{marque}] {chemin_affiche}")


def afficher_planning() -> None:
    print("\n--- Planning agile (4 semaines) ---\n")
    for semaine, blocs, objectif in PLANNING:
        print(f"  {semaine:<10} {blocs:<14} {objectif}")


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC06 - GESTION ET PILOTAGE DU PROJET")
    print("#" * 70 + "\n")

    executer_tests()
    etat_des_lieux()
    afficher_planning()

    print("\nLimites assumees et pistes d'amelioration (voir le README de ce bloc) :")
    print("  - Fort desequilibre des classes en BC03 (rappel des presences reelles perfectible)")
    print("  - Meteo seule faiblement correlee a la presence (voir BC02)")
    print("  - BC04 utilise un jeu de donnees texte generique (IMDB), distinct du theme")
    print("    ornithologique, pour demontrer specifiquement la competence donnees non structurees")

    print("\nBC06 termine. C'est le dernier bloc : voir notebooks/ pour la synthese complete.\n")


if __name__ == "__main__":
    main()

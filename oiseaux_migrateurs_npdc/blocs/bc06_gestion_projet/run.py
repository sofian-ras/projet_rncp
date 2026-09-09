"""
BC06 - Direction de projet
=============================

Bloc de pilotage : il demontre la competence "cadrer, dimensionner et
fiabiliser un projet de bout en bout".

  1. Il execute la suite de tests automatises (tests/, qui portent sur le
     module d'acquisition de BC01) et affiche le resultat en direct.
  2. Il rappelle le planning, l'equipe et le budget (hypothese de
     dimensionnement), et renvoie vers docs/gestion_projet.md
     (parties prenantes, RACI, retroplanning, risques, ROI).

Note : l'equipe, les couts et le ROI sont une HYPOTHESE de dimensionnement
(chiffres estimes, assumes comme tels). Le projet reel a ete mene seul, en
formation.

Utilisation :
    python run.py
"""

import subprocess
import sys
from pathlib import Path

_racine = next(p for p in Path(__file__).resolve().parents if (p / "commun").is_dir())
sys.path.insert(0, str(_racine))  # racine du projet -> package commun/

from commun.journalisation import configurer_logger

RACINE_PROJET = Path(__file__).resolve().parent
logger = configurer_logger()

PLANNING = [
    ("Semaine 1", "BC01", "Acquisition des donnees (GBIF, Open-Meteo) et pipeline de nettoyage"),
    ("Semaine 2", "BC02", "Analyse exploratoire, visualisations, tests statistiques"),
    ("Semaine 3", "BC03 / BC04", "Machine Learning (donnees structurees) et Deep Learning (images)"),
    ("Semaine 4", "BC05 / BC06", "API, dashboard, Docker, documentation et soutenance"),
]

# --- Hypothese de dimensionnement (voir docs/gestion_projet.md) ---
DUREE_JOURS = 30  # ~6 semaines calendaires

EQUIPE = [
    # role,              ETP,   TJM (EUR), blocs portes
    ("Chef de projet / PO", 0.25, 650, "BC06"),
    ("Data Engineer",       1.0,  550, "BC01, BC05"),
    ("Data Scientist",      1.0,  600, "BC02, BC03, BC04"),
    ("Dev / MLOps",         0.5,  500, "BC05, BC06"),
]

INFRA_PROJET_EUR = 100          # GPU cloud ponctuel (CNN) + hebergement de test
TAUX_CONTINGENCE = 0.10
COUT_RECURRENT_AN_EUR = 7_100   # infra ~480 EUR/an + maintenance ~1 j-h/mois
BENEFICE_AN_EUR = 21_700        # temps benevole redeploye + coordination automatisee


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
    print("\n--- Planning agile (4 iterations) ---\n")
    for semaine, blocs, objectif in PLANNING:
        print(f"  {semaine:<10} {blocs:<14} {objectif}")
    print("\n  Jalons : J1 grille presence/absence -> J2 modele fige -> J3 API+dashboard en local")


def afficher_equipe_et_budget() -> None:
    print("\n--- Equipe et budget (HYPOTHESE de dimensionnement) ---\n")
    print(f"  {'Role':<20}{'ETP':>5}{'j-h':>7}{'TJM':>7}{'Cout (EUR)':>13}   Blocs")
    print("  " + "-" * 74)
    charge_totale = cout_rh = 0.0
    for role, etp, tjm, blocs in EQUIPE:
        jh = etp * DUREE_JOURS
        cout = jh * tjm
        charge_totale += jh
        cout_rh += cout
        print(f"  {role:<20}{etp:>5.2f}{jh:>7.1f}{tjm:>7}{cout:>13,.0f}   {blocs}")

    contingence = TAUX_CONTINGENCE * cout_rh
    budget = cout_rh + INFRA_PROJET_EUR + contingence
    print("  " + "-" * 74)
    print(f"  {'Total':<20}{'':>5}{charge_totale:>7.1f}{'':>7}{cout_rh:>13,.0f}   (RH)")
    print(f"  + infra phase projet {INFRA_PROJET_EUR:>7,.0f} EUR   + contingence 10% "
          f"{contingence:>8,.0f} EUR")
    print(f"  = BUDGET PROJET      {budget:>7,.0f} EUR (~52 k EUR)")

    gain_net = BENEFICE_AN_EUR - COUT_RECURRENT_AN_EUR
    print(f"\n  ROI : benefice ~{BENEFICE_AN_EUR:,.0f} EUR/an - cout recurrent "
          f"~{COUT_RECURRENT_AN_EUR:,.0f} EUR/an = gain net ~{gain_net:,.0f} EUR/an")
    print(f"        retour sur investissement ~{budget / gain_net:.1f} ans "
          f"(+ benefices qualitatifs, cf. docs/gestion_projet.md)")


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC06 - DIRECTION DE PROJET")
    print("#" * 70 + "\n")

    executer_tests()
    afficher_planning()
    afficher_equipe_et_budget()

    print("\nLimites assumees et pistes d'amelioration (voir le README de ce bloc) :")
    print("  - Fort desequilibre des classes en BC03 (rappel des presences reelles perfectible)")
    print("  - Meteo seule faiblement correlee a la presence (voir BC02)")
    print("  - BC04 (CNN images) : dataset volontairement petit (~120 photos/espece) et")
    print("    photos de science citoyenne bruitees -> accuracy ~0,75 sur 4 classes")
    print("  - Deploiement cloud (URL publique de l'API/dashboard) documente mais non realise")

    print("\n  Cadrage complet (parties prenantes, RACI, retroplanning date, risques, ROI) :")
    print("  docs/gestion_projet.md")

    print("\nBC06 termine.\n")


if __name__ == "__main__":
    main()

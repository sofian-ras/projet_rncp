from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.nettoyage import executer_nettoyage
from scripts.eda import executer_eda


def verifier_sorties() -> dict:
    fichiers = {
        "observations_nettoyees": ROOT / "donnees" / "traitees" / "observations_nettoyees.parquet",
        "grille_presence_hebdo": ROOT / "donnees" / "traitees" / "grille_presence_hebdo.parquet",
        "meteo_processed": ROOT / "donnees" / "traitees" / "meteo_processed.parquet",
        "saisonnalite_png": ROOT / "outputs" / "eda" / "saisonnalite.png",
        "carte_densite_html": ROOT / "outputs" / "eda" / "carte_densite.html",
        "correlations_png": ROOT / "outputs" / "eda" / "correlations_meteo.png",
    }
    return {k: v.exists() and v.stat().st_size > 0 for k, v in fichiers.items()}


def run() -> None:
    print("[BC02] Nettoyage + EDA...")
    executer_nettoyage()
    executer_eda()
    checks = verifier_sorties()
    print("[BC02] Vérification sorties:", checks)


if __name__ == "__main__":
    run()

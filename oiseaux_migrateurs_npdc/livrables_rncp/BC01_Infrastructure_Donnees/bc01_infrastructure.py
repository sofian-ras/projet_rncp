from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.acquisition import executer_acquisition


def verifier_sorties() -> dict:
    fichiers = {
        "observations_gbif": ROOT / "donnees" / "brutes" / "observations_gbif.csv",
        "meteo_npdc": ROOT / "donnees" / "brutes" / "meteo_npdc.csv",
    }
    return {k: v.exists() and v.stat().st_size > 0 for k, v in fichiers.items()}


def run() -> None:
    print("[BC01] Lancement acquisition...")
    executer_acquisition()
    checks = verifier_sorties()
    print("[BC01] Verification sorties:", checks)


if __name__ == "__main__":
    run()

from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.entrainer_modele import executer_entrainement


def verifier_sorties() -> dict:
    fichiers = {
        "pipeline_ml": ROOT / "modeles" / "pipeline_ml.pkl",
        "random_forest": ROOT / "modeles" / "random_forest.pkl",
        "logistic_regression": ROOT / "modeles" / "logistic_regression.pkl",
        "evaluations": ROOT / "modeles" / "evaluations.csv",
    }
    return {k: v.exists() and v.stat().st_size > 0 for k, v in fichiers.items()}


def afficher_resume_evaluations() -> None:
    eval_path = ROOT / "modeles" / "evaluations.csv"
    if eval_path.exists():
        df = pd.read_csv(eval_path, index_col=0)
        print("[BC03] Evaluations:")
        print(df)


def run() -> None:
    print("[BC03] Entrainement modeles...")
    executer_entrainement()
    checks = verifier_sorties()
    print("[BC03] Verification sorties:", checks)
    afficher_resume_evaluations()


if __name__ == "__main__":
    run()

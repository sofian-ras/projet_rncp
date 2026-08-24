from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def run() -> None:
    """
    Livrable BC04 separe.
    Ce script materialise le bloc Deep Learning et produit un plan executable.
    """
    plan = {
        "objectif": "Mettre en place un pipeline Deep Learning sur donnee non structuree (texte)",
        "etat": "a_completer",
        "dataset_cible": "corpus sentiment (texte)",
        "modele_cible": "Embedding + LSTM (TensorFlow/Keras)",
        "sorties_attendues": [
            "modeles/deep_learning_model.keras",
            "modeles/deep_learning_metrics.json",
            "outputs/dl/confusion_matrix.png"
        ],
        "commande_cible": "python scripts/deep_learning.py"
    }
    out_file = OUT / "bc04_plan_execution.json"
    out_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[BC04] Plan d'implementation ecrit: {out_file}")


if __name__ == "__main__":
    run()

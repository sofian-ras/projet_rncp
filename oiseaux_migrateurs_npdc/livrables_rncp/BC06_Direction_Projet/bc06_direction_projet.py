from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def audit_documents() -> dict:
    docs = {
        "readme": ROOT / "README.md",
        "readme_complet": ROOT / "README_COMPLET.md",
        "architecture": ROOT / "docs" / "ARCHITECTURE.md",
        "plan_operationnel": ROOT / "docs" / "PLAN_OPERATIONNEL.md",
        "guide_soutenance": ROOT.parent / "GUIDE_SOUTENANCE_RNCP35288_6BLOCS.md",
        "test_acquisition": ROOT / "tests" / "test_acquisition.py",
    }
    return {k: v.exists() for k, v in docs.items()}


def run() -> None:
    rapport = {
        "bloc": "BC06",
        "objectif": "Pilotage projet, gouvernance documentaire, qualite",
        "documents_disponibles": audit_documents(),
        "actions_recommandees": [
            "Ajouter cahier des charges chiffre",
            "Ajouter retroplanning detaille",
            "Ajouter budget estimatif",
            "Ajouter KPI de suivi projet"
        ]
    }
    out = OUT / "bc06_rapport_projet.json"
    out.write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[BC06] Rapport genere: {out}")


if __name__ == "__main__":
    run()

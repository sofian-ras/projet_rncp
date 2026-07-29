from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]


def verifier_api(base_url: str = "http://127.0.0.1:8000") -> dict:
    result = {"health": False, "species": False, "predict": False}
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        result["health"] = r.status_code == 200
    except Exception:
        pass

    try:
        r = requests.get(f"{base_url}/species", timeout=5)
        result["species"] = r.status_code == 200
    except Exception:
        pass

    payload = {
        "espece": "hirondelle_rustique",
        "latitude": 50.5,
        "longitude": 2.75,
        "meteo": {
            "temperature_max": 18.5,
            "temperature_min": 12.3,
            "precipitation_sum": 2.1,
            "vent_max": 15.0,
            "humidite_moyenne": 65.0,
            "jour_annee": 120,
        },
    }
    try:
        r = requests.post(f"{base_url}/predict", json=payload, timeout=8)
        result["predict"] = r.status_code == 200
    except Exception:
        pass

    return result


def verifier_dashboard() -> bool:
    dash = ROOT / "dashboard.py"
    return dash.exists() and dash.stat().st_size > 0


def run() -> None:
    print("[BC05] Vérification industrialisation...")
    print("[BC05] Dashboard file:", verifier_dashboard())
    print("[BC05] API checks:", verifier_api())


if __name__ == "__main__":
    run()

"""
Rend importables, pour les tests de BC06 :
  - `commun`   -> depuis la racine du projet
  - `acquisition` -> depuis le vrai code de BC01 (plus de copie dans BC06)
"""

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
BLOC_BC01 = RACINE / "blocs" / "bc01_infrastructure_donnees"

for chemin in (RACINE, BLOC_BC01):
    if str(chemin) not in sys.path:
        sys.path.insert(0, str(chemin))

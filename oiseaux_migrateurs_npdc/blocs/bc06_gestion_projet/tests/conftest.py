from pathlib import Path
import sys

# tests/ n'a pas de sys.path[0] automatique vers son dossier parent (contrairement a un
# script lance directement) -- ce hack reste necessaire ici pour que
# "from acquisition import ..." et "from commun.config import ..." resolvent.
DOSSIER_BLOC = Path(__file__).resolve().parents[1]
if str(DOSSIER_BLOC) not in sys.path:
    sys.path.insert(0, str(DOSSIER_BLOC))

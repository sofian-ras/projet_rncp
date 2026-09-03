# =============================================================================
#  Installation de l'environnement du projet - Windows
# =============================================================================
#  Cree le venv a un chemin COURT (%USERPROFILE%\venv_rncp) pour contourner la
#  limite Windows de 260 caracteres sur les chemins, qui fait echouer
#  l'installation de TensorFlow (bloc BC04) quand le venv est dans un dossier
#  profondement imbrique.
#
#  A lancer une seule fois, depuis le dossier oiseaux_migrateurs_npdc/ :
#
#      powershell -ExecutionPolicy Bypass -File setup_venv.ps1
#
#  Puis, dans chaque nouveau terminal, activer l'environnement :
#
#      & "$env:USERPROFILE\venv_rncp\Scripts\Activate.ps1"
#
#  (Linux / macOS : pas de limite de chemin, un simple
#   `python -m venv .venv && pip install -r requirements.txt` suffit.)
# =============================================================================

$ErrorActionPreference = "Stop"

$venv = Join-Path $env:USERPROFILE "venv_rncp"
$req  = Join-Path $PSScriptRoot "requirements.txt"

if (-not (Test-Path $req)) {
    Write-Error "requirements.txt introuvable. Lancez ce script depuis le dossier oiseaux_migrateurs_npdc/."
}

if (Test-Path $venv) {
    Write-Host "Environnement deja present : $venv"
} else {
    Write-Host "Creation de l'environnement : $venv"
    python -m venv $venv
}

$py = Join-Path $venv "Scripts\python.exe"

Write-Host "Installation des dependances (peut prendre plusieurs minutes, TensorFlow est volumineux)..."
& $py -m pip install --upgrade pip
& $py -m pip install -r $req

Write-Host "Enregistrement du kernel Jupyter (pour les notebooks)..."
& $py -m ipykernel install --user --name python3 --display-name "Python 3 (venv_rncp)"

Write-Host ""
Write-Host "============================================================"
Write-Host " Installation terminee."
Write-Host "============================================================"
Write-Host " Activer l'environnement dans un nouveau terminal :"
Write-Host "   & `"$venv\Scripts\Activate.ps1`""
Write-Host ""
Write-Host " Puis, depuis oiseaux_migrateurs_npdc/ :"
Write-Host "   python blocs/bc01_infrastructure_donnees/run.py"
Write-Host "   python blocs/bc02_analyse_exploratoire/run.py"
Write-Host "   ... (bc03, bc04, bc05, bc06)"
Write-Host "============================================================"

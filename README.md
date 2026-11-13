# Launcher C + Python Embedded 3.14.10 AMD64

Ce projet construit un exécutable Windows unique qui embarque :
- Python Embedded 3.14.10 AMD64 fourni dans `vendor/`
- `requests` et ses dépendances (installés dans le payload)
- les scripts présents dans `scripts/`

Au premier lancement, `Application.exe` extrait `payload.zip` dans :
`%LOCALAPPDATA%\GregPythonBundle\3.14.10\`
puis lance `runtime\python.exe scripts\main.py`.

## Prérequis sur la machine de compilation

1. Windows 10/11 x64.
2. MinGW-w64 x64 avec `gcc` et `windres` accessibles depuis PATH.
3. Python 3 installé sur la machine de préparation, avec pip.
4. Accès réseau au moment de préparer le payload pour télécharger `requests` et ses dépendances.

La machine cible n'a pas besoin d'avoir Python ou requests installés.
Le lanceur utilise Windows PowerShell (`Expand-Archive`) pour décompresser le payload.

## Construction

1. Décompresser ce projet.
2. Modifier `scripts/main.py` et ajouter tes autres scripts `.py` dans `scripts/`.
3. Lancer `prepare_payload.bat`.
   - Cette étape utilise le Python installé sur la machine de compilation uniquement.
   - Elle installe `requests` dans le dossier embarqué `site-packages`.
   - Pour une préparation hors ligne, télécharger au préalable les wheels compatibles et adapter la commande pip dans `prepare_payload.py`.
4. Lancer `build.bat`.
5. Le fichier à distribuer est `Application.exe`.

## Test

Lancer `Application.exe`. Au premier démarrage, l'extraction peut prendre quelques secondes.
Le script de démonstration affiche la version Python et celle de requests.

## Ajouter des dépendances

Ajouter les noms des packages dans `requirements.txt`, puis relancer :
- `prepare_payload.bat`
- `build.bat`

Les dépendances doivent être compatibles avec Windows x64 et Python 3.14.

## Ajouter des scripts

Placer les fichiers `.py` dans `scripts/`. Le point d'entrée doit rester `scripts/main.py`.
Les imports entre scripts fonctionnent normalement si les modules sont dans ce dossier.

## Nettoyage / réinstallation

Supprimer le dossier :
`%LOCALAPPDATA%\GregPythonBundle\3.14.10\`

Le prochain lancement réextraira le payload.

## Notes importantes

- Le payload est extrait sur disque : ce n'est pas une protection contre l'inspection ou la récupération des scripts.
- Ne stocke pas de secrets ou de clés privées dans les scripts embarqués.
- L'archive ZIP est une ressource `RCDATA` dans l'EXE.
- Le lanceur attend la fin du script et retourne son code de sortie.
- `CreateProcess` lance Python comme processus enfant, ce qui facilite le diagnostic et l'isolation.
- Le premier lancement requiert PowerShell avec le module `Microsoft.PowerShell.Archive` (présent sur les versions Windows modernes).
- Pour une distribution maîtrisée, teste l'EXE sur une machine Windows propre, sans Python installé.

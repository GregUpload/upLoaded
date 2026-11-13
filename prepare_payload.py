from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
EMBED_ZIP = ROOT / "vendor" / "python-3.14.10-embed-amd64.zip"
WORK = ROOT / "_payload_build"
RUNTIME = WORK / "runtime"
PAYLOAD_ZIP = ROOT / "payload.zip"
SITE = RUNTIME / "packages" / "site-packages"
SCRIPTS = RUNTIME / "scripts"

def main():
    if not EMBED_ZIP.is_file():
        raise SystemExit(f"Archive Embedded introuvable: {EMBED_ZIP}")

    if WORK.exists():
        shutil.rmtree(WORK)
    RUNTIME.mkdir(parents=True)
    with zipfile.ZipFile(EMBED_ZIP) as zf:
        # Reject unsafe paths even though this is a locally supplied archive.
        for info in zf.infolist():
            p = Path(info.filename)
            if p.is_absolute() or ".." in p.parts:
                raise SystemExit(f"Chemin dangereux dans l'archive: {info.filename}")
        zf.extractall(RUNTIME)

    SITE.mkdir(parents=True)
    SCRIPTS.mkdir(parents=True)

    pth = RUNTIME / "python314._pth"
    pth.write_text(
        "python314.zip\n"
        ".\n"
        "packages/site-packages\n"
        "scripts\n"
        "import site\n",
        encoding="ascii"
    )

    requirements = ROOT / "requirements.txt"
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--disable-pip-version-check",
        "--no-warn-script-location",
        "--no-compile",
        "--only-binary=:all:",
        "--target", str(SITE),
        "-r", str(requirements),
    ]
    print("Installation des dépendances dans le payload...")
    subprocess.check_call(cmd)

    # Sample script is copied from the project scripts directory.
    for source in (ROOT / "scripts").glob("*.py"):
        shutil.copy2(source, SCRIPTS / source.name)

    # Ensure a main script exists.
    if not (SCRIPTS / "main.py").exists():
        raise SystemExit("scripts/main.py est absent.")

    if PAYLOAD_ZIP.exists():
        PAYLOAD_ZIP.unlink()
    with zipfile.ZipFile(PAYLOAD_ZIP, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zf:
        for path in WORK.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(WORK).as_posix())

    print(f"Payload créé: {PAYLOAD_ZIP}")
    print(f"Taille: {PAYLOAD_ZIP.stat().st_size:,} octets")
    print("Le payload contient Python Embedded 3.14.10 AMD64 et requests.")

if __name__ == "__main__":
    main()

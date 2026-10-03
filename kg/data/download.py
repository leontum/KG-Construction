"""Lädt den BioRED-Korpus (BioCreative VIII, Track 1) nach data/raw/ (idempotent).

Aufruf: python -m kg.data.download [--force]
"""
import argparse
import urllib.request
import zipfile
from pathlib import Path

URL = "https://ftp.ncbi.nlm.nih.gov/pub/lu/BioRED/BIORED.zip"
RAW_DIR = Path("data/raw")
ARCHIVE = "BIORED.zip"
# Nur diese Archiv-Mitglieder werden entpackt (Zielname = Basename).
MEMBERS = [f"BioRED/{split}.PubTator" for split in ("Train", "Dev", "Test")]


def download(raw_dir: Path = RAW_DIR, force: bool = False) -> list[Path]:
    """Lädt und entpackt den Korpus; vorhandene Dateien werden übersprungen."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    targets = [raw_dir / Path(m).name for m in MEMBERS]
    if not force and all(t.exists() for t in targets):
        print(f"Bereits vorhanden: {raw_dir} (nichts zu tun)")
        return targets

    archive = raw_dir / ARCHIVE
    if force or not archive.exists():
        print(f"Lade {URL} ...")
        tmp = archive.with_suffix(".part")
        urllib.request.urlretrieve(URL, tmp)
        tmp.replace(archive)

    with zipfile.ZipFile(archive) as zf:
        for member, target in zip(MEMBERS, targets):
            target.write_bytes(zf.read(member))
            print(f"Entpackt: {target}")
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="erneut herunterladen")
    args = parser.parse_args()
    download(force=args.force)


if __name__ == "__main__":
    main()

"""Statistik über BioRED: Dokumente, Entitäten und Relationen pro Typ und Split.

Aufruf: python -m kg.data.stats --split test   (oder: train, dev, all)
"""
import argparse
from collections import Counter
from pathlib import Path

from kg.data.biored import RAW_DIR, SPLITS, Document, load_split


def compute_stats(docs: list[Document]) -> dict:
    return {
        "documents": len(docs),
        "entities": Counter(e.type for d in docs for e in d.entities),
        "relations": Counter(r.type for d in docs for r in d.relations),
        "novelty": Counter(r.novelty for d in docs for r in d.relations),
    }


def format_stats(split: str, stats: dict) -> str:
    out = [f"== {split} ==", f"Dokumente: {stats['documents']}"]
    for key, title in (
        ("entities", "Entitäten"),
        ("relations", "Relationen"),
        ("novelty", "Novelty"),
    ):
        counter = stats[key]
        out.append(f"{title}: {sum(counter.values())}")
        out += [f"  {name:<28}{n:>6}" for name, n in sorted(counter.items())]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=(*SPLITS, "all"), default="all")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    args = parser.parse_args()
    splits = SPLITS if args.split == "all" else (args.split,)
    for split in splits:
        print(format_stats(split, compute_stats(load_split(split, args.raw_dir))))


if __name__ == "__main__":
    main()

"""Parser für BioRED im PubTator-Format.

Gold-Annotationen dienen nur der Evaluation, nicht als Graph-Input.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

SPLITS = ("train", "dev", "test")
RAW_DIR = Path("data/raw")


@dataclass(frozen=True)
class Entity:
    start: int  # Zeichenoffset (Titel und Abstract getrennt durch ein Leerzeichen)
    end: int
    text: str
    type: str  # z. B. GeneOrGeneProduct, ChemicalEntity, DiseaseOrPhenotypicFeature
    ids: tuple[str, ...]  # normalisierte IDs (mehrere bei zusammengesetzten Mentions)


@dataclass(frozen=True)
class Relation:
    type: str  # z. B. Association, Positive_Correlation, Bind
    id1: str
    id2: str
    novelty: str  # "Novel" oder "No"


@dataclass
class Document:
    pmid: str
    title: str
    abstract: str
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)


def split_path(split: str, raw_dir: Path = RAW_DIR) -> Path:
    if split not in SPLITS:
        raise ValueError(f"Unbekannter Split {split!r}, erwartet: {SPLITS}")
    return raw_dir / f"{split.capitalize()}.PubTator"


def parse_pubtator(lines: Iterable[str]) -> Iterator[Document]:
    """Parst PubTator-Zeilen (Titel, Abstract, Entitäts- und Relationszeilen)."""
    doc = None
    for line in lines:
        line = line.rstrip("\r\n")
        if not line.strip():
            if doc:
                yield doc
            doc = None
            continue
        if "|t|" in line or "|a|" in line:
            pmid, kind, text = line.split("|", 2)
            if doc is None:
                doc = Document(pmid=pmid, title="", abstract="")
            if kind == "t":
                doc.title = text
            else:
                doc.abstract = text
            continue
        parts = line.split("\t")
        if doc is None or parts[0] != doc.pmid:
            raise ValueError(f"Zeile ohne zugehöriges Dokument: {line[:80]!r}")
        if len(parts) == 6:
            _, start, end, text, etype, ids = parts
            doc.entities.append(
                Entity(int(start), int(end), text, etype, tuple(ids.split(",")))
            )
        elif len(parts) == 5:
            _, rtype, id1, id2, novelty = parts
            doc.relations.append(Relation(rtype, id1, id2, novelty))
        else:
            raise ValueError(f"Unerwartetes Zeilenformat: {line[:80]!r}")
    if doc:
        yield doc


def load_documents(path: Path) -> list[Document]:
    with open(path, encoding="utf-8") as f:
        return list(parse_pubtator(f))


def load_split(split: str, raw_dir: Path = RAW_DIR) -> list[Document]:
    return load_documents(split_path(split, raw_dir))

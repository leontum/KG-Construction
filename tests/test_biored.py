from pathlib import Path

import pytest

from kg.data.biored import Entity, Relation, load_documents, load_split, split_path
from kg.data.stats import compute_stats, format_stats

FIXTURE = Path(__file__).parent / "fixtures" / "sample.pubtator"


@pytest.fixture
def docs():
    return load_documents(FIXTURE)


def test_documents_and_text(docs):
    assert [d.pmid for d in docs] == ["1000001", "1000002"]
    assert docs[0].title == "Aspirin reduces risk of colon cancer."
    assert docs[0].abstract.startswith("We show that aspirin")


def test_entities(docs):
    ents = docs[0].entities
    assert len(ents) == 6
    assert ents[0] == Entity(0, 7, "Aspirin", "ChemicalEntity", ("D001241",))
    assert ents[3].ids == ("D015179", "D003110")


def test_relations(docs):
    assert docs[0].relations == [
        Relation("Negative_Correlation", "D001241", "D015179", "Novel"),
        Relation("Association", "672", "D015179", "No"),
    ]


def test_document_without_annotations(docs):
    assert docs[1].entities == [] and docs[1].relations == []


def test_crlf_and_missing_trailing_blank_line(tmp_path):
    path = tmp_path / "x.pubtator"
    path.write_bytes(FIXTURE.read_bytes().replace(b"\n", b"\r\n").rstrip())
    assert len(load_documents(path)) == 2


def test_stats(docs):
    stats = compute_stats(docs)
    assert stats["documents"] == 2
    assert stats["entities"]["ChemicalEntity"] == 2
    assert stats["relations"]["Association"] == 1
    assert stats["novelty"] == {"Novel": 1, "No": 1}
    assert "Dokumente: 2" in format_stats("sample", stats)


def test_split_validation():
    with pytest.raises(ValueError):
        split_path("val")
    assert split_path("test", Path("d")) == Path("d/Test.PubTator")
    with pytest.raises(FileNotFoundError):
        load_split("test", Path("does-not-exist"))

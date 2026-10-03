# KG-Construction

Wissensgraph-Konstruktion aus biomedizinischen Abstracts. Schritt 1: BioRED laden, parsen, Statistik.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m kg.data.download        # lädt nach data/raw/ (idempotent, --force für erneut)
.venv/bin/python -m kg.data.stats --split test   # train | dev | test | all
.venv/bin/pytest
```

## Datensatz und Format

Quelle: BioRED (Luo et al. 2022), das Korpus hinter BioCreative VIII Track 1,
<https://ftp.ncbi.nlm.nih.gov/pub/lu/BioRED/BIORED.zip>.
Es enthält 600 PubMed-Abstracts mit Gold-Annotationen: **Train 400 / Dev 100 / Test 100**.

Hinweis: Die Dateien im BC8-Verzeichnis (`/pub/lu/BC8-BioRED-track/`) enthalten nur 500 annotierte
Trainings-Abstracts; Val-/Test-Sets sind dort unannotiert (Test: 10 000 Abstracts, Gold verdeckt).
Für die Evaluation mit Gold-Daten wird daher `BIORED.zip` verwendet (Splits 400/100/100 statt 600/400).

Verwendet wird das PubTator-Format (`data/raw/{Train,Dev,Test}.PubTator`), Dokumente durch Leerzeile getrennt:

```
PMID|t|Titel
PMID|a|Abstract
PMID<TAB>start<TAB>end<TAB>Text<TAB>Entitätstyp<TAB>ID[,ID...]      # Entität
PMID<TAB>Relationstyp<TAB>ID1<TAB>ID2<TAB>Novel|No                   # Relation
```

- Entitätstypen: `GeneOrGeneProduct`, `ChemicalEntity`, `DiseaseOrPhenotypicFeature`, `SequenceVariant`,
  `OrganismTaxon`, `CellLine`.
- Relationstypen: `Association`, `Positive_Correlation`, `Negative_Correlation`, `Bind`, `Cotreatment`,
  `Comparison`, `Drug_Interaction`, `Conversion`; Novelty-Label `Novel` / `No`.
- Relationen verweisen auf normalisierte IDs (nicht auf Mentions); Mentions können mehrere IDs haben.

## Code

- `kg/data/download.py` – Download und Entpacken
- `kg/data/biored.py` – Parser (`Document`, `Entity`, `Relation` als Dataclasses; `load_split`)
- `kg/data/stats.py` – Statistik pro Split

Gold-Annotationen dienen **nur** der Evaluation, nicht als Graph-Input.

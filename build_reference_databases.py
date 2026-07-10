from __future__ import annotations

from pathlib import Path
import gzip
import json
import re
import shutil
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT / "reference"
ARSM_HMM = REFERENCE / "arsM_hmm"
ARSM_DB = REFERENCE / "arsM_public_database"
CRASS = REFERENCE / "crAssphage_reference"
LOGS = REFERENCE / "logs"

for directory in [ARSM_HMM, ARSM_DB, CRASS, LOGS]:
    directory.mkdir(parents=True, exist_ok=True)


def download(url: str, out: Path, timeout: int = 300, retries: int = 4) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        print(f"download attempt {attempt}/{retries}: {url}")
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Codex arsM reference builder; academic use"},
        )
        try:
            tmp = out.with_suffix(out.suffix + ".tmp")
            with urllib.request.urlopen(req, timeout=timeout) as response, open(tmp, "wb") as handle:
                shutil.copyfileobj(response, handle)
            tmp.replace(out)
            return {"file": str(out), "url": url, "bytes": out.stat().st_size}
        except Exception as exc:
            last_error = exc
            time.sleep(min(2 * attempt, 10))
    raise RuntimeError(f"Download failed after {retries} attempts: {url}") from last_error


def gunzip(src: Path, dest: Path) -> dict:
    with gzip.open(src, "rb") as compressed, open(dest, "wb") as handle:
        shutil.copyfileobj(compressed, handle)
    return {"file": str(dest), "derived_from": str(src), "bytes": dest.stat().st_size}


def count_fasta(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith(">"):
                count += 1
    return count


def read_fasta(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    header: str | None = None
    parts: list[str] = []
    with open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(parts)))
                header = line[1:]
                parts = []
            else:
                parts.append(line)
    if header is not None:
        records.append((header, "".join(parts)))
    return records


def write_fasta(records: list[tuple[str, str]], path: Path, width: int = 80) -> None:
    with open(path, "wt", encoding="utf-8", newline="\n") as handle:
        for header, seq in records:
            handle.write(f">{header}\n")
            for i in range(0, len(seq), width):
                handle.write(seq[i : i + width] + "\n")


def dedup_fasta_by_sequence(input_files: list[Path], output_file: Path) -> dict:
    seen: set[str] = set()
    records: list[tuple[str, str]] = []
    for path in input_files:
        for header, seq in read_fasta(path):
            normalized = re.sub(r"[^A-Za-z*]", "", seq).upper()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            records.append((header, normalized))
    write_fasta(records, output_file)
    return {"file": str(output_file), "records": len(records), "source_files": [str(p) for p in input_files]}


def download_interpro_hmms() -> list[dict]:
    items = [
        (
            ARSM_HMM / "PTHR43675_arsenite_methyltransferase_panther.hmm.gz",
            "https://www.ebi.ac.uk/interpro/wwwapi/entry/panther/PTHR43675?annotation=hmm",
        ),
        (
            ARSM_HMM / "PF31200_AS3MT_C_terminal_domain.hmm.gz",
            "https://www.ebi.ac.uk/interpro/wwwapi/entry/pfam/PF31200?annotation=hmm",
        ),
        (
            ARSM_HMM / "IPR026669_interpro_metadata.json",
            "https://www.ebi.ac.uk/interpro/api/entry/interpro/IPR026669?format=json",
        ),
        (
            ARSM_HMM / "PF31200_interpro_metadata.json",
            "https://www.ebi.ac.uk/interpro/api/entry/pfam/PF31200?format=json",
        ),
    ]
    manifest: list[dict] = []
    for out, url in items:
        manifest.append(download(url, out, timeout=180))
        if out.suffix == ".gz":
            manifest.append(gunzip(out, out.with_suffix("")))
    return manifest


def uniprot_url(query: str, fmt: str, fields: str | None = None, size: int | None = None, stream: bool = False) -> str:
    params = {"compressed": "false", "format": fmt, "query": query}
    if fields:
        params["fields"] = fields
    if size:
        params["size"] = str(size)
    endpoint = "stream" if stream else "search"
    return "https://rest.uniprot.org/uniprotkb/" + endpoint + "?" + urllib.parse.urlencode(params)


def download_uniprot_references() -> list[dict]:
    manifest: list[dict] = []
    fields = "accession,reviewed,id,protein_name,gene_names,organism_name,length,xref_interpro,xref_panther"
    queries = [
        ("uniprot_reviewed_IPR026669.faa", "(xref:IPR026669) AND (reviewed:true)", 500),
        ("uniprot_reviewed_EC_2.1.1.137.faa", "(ec:2.1.1.137) AND (reviewed:true)", 500),
        ("uniprot_gene_arsM_first500.faa", "gene_exact:arsM", 500),
        ("uniprot_name_arsenite_methyltransferase_first500.faa", 'protein_name:"arsenite methyltransferase"', 500),
    ]
    fasta_files: list[Path] = []
    for filename, query, size in queries:
        fasta = ARSM_DB / filename
        metadata = ARSM_DB / filename.replace(".faa", ".metadata.tsv")
        manifest.append(download(uniprot_url(query, "fasta", size=size), fasta, timeout=240))
        manifest.append(download(uniprot_url(query, "tsv", fields=fields, size=size), metadata, timeout=240))
        fasta_files.append(fasta)

    # Full InterPro family stream. This can be slow; if it fails, the partial public db still exists.
    try:
        query = "(xref:IPR026669)"
        gz = ARSM_DB / "uniprot_IPR026669_all.faa.gz"
        url = "https://rest.uniprot.org/uniprotkb/stream?" + urllib.parse.urlencode(
            {"compressed": "true", "format": "fasta", "query": query}
        )
        manifest.append(download(url, gz, timeout=600))
        fasta = ARSM_DB / "uniprot_IPR026669_all.faa"
        manifest.append(gunzip(gz, fasta))
        fasta_files.append(fasta)
    except Exception as exc:
        manifest.append({"file": "uniprot_IPR026669_all.faa.gz", "error": repr(exc)})

    manifest.append(dedup_fasta_by_sequence(fasta_files, ARSM_DB / "arsM_uniprot_public_dedup.faa"))
    return manifest


def ncbi_esearch(db: str, term: str, retmax: int = 10000) -> list[str]:
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        + urllib.parse.urlencode({"db": db, "term": term, "retmode": "json", "retmax": str(retmax)})
    )
    with urllib.request.urlopen(url, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["esearchresult"].get("idlist", [])


def ncbi_efetch(db: str, ids: list[str], rettype: str, out: Path, batch_size: int = 200) -> dict:
    total = 0
    with open(out, "wb") as handle:
        for i in range(0, len(ids), batch_size):
            batch = ids[i : i + batch_size]
            url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
                + urllib.parse.urlencode(
                    {"db": db, "id": ",".join(batch), "rettype": rettype, "retmode": "text"}
                )
            )
            with urllib.request.urlopen(url, timeout=180) as response:
                chunk = response.read()
            handle.write(chunk)
            total += len(batch)
            time.sleep(0.34)
    return {"file": str(out), "db": db, "rettype": rettype, "ids": len(ids), "bytes": out.stat().st_size}


def download_ncbi_references() -> list[dict]:
    manifest: list[dict] = []
    # Protein-name search is deliberately narrow; broad SAM-methyltransferase queries are not suitable.
    terms = {
        "bacteria_archaea": 'arsenite methyltransferase[Protein Name] AND (bacteria[Organism] OR archaea[Organism])',
        "all_taxa": 'arsenite methyltransferase[Protein Name]',
    }
    all_ids: list[str] = []
    for label, term in terms.items():
        ids = ncbi_esearch("protein", term, retmax=12000)
        (ARSM_DB / f"ncbi_protein_ids_{label}.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
        manifest.append({"file": str(ARSM_DB / f"ncbi_protein_ids_{label}.txt"), "term": term, "ids": len(ids)})
        all_ids.extend(ids)
        if label == "bacteria_archaea" and ids:
            manifest.append(ncbi_efetch("protein", ids, "fasta", ARSM_DB / "ncbi_arsenite_methyltransferase_bacteria_archaea.faa"))
            # fasta_cds_na is not available for all protein records; still useful where NCBI can resolve CDS.
            manifest.append(
                ncbi_efetch(
                    "protein",
                    ids[:2000],
                    "fasta_cds_na",
                    ARSM_DB / "ncbi_arsenite_methyltransferase_bacteria_archaea_first2000_cds.fna",
                    batch_size=100,
                )
            )
    unique_ids = sorted(set(all_ids))
    (ARSM_DB / "ncbi_protein_ids_all_unique.txt").write_text("\n".join(unique_ids) + "\n", encoding="utf-8")
    manifest.append({"file": str(ARSM_DB / "ncbi_protein_ids_all_unique.txt"), "ids": len(unique_ids)})

    fasta_files = [
        ARSM_DB / "arsM_uniprot_public_dedup.faa",
        ARSM_DB / "ncbi_arsenite_methyltransferase_bacteria_archaea.faa",
    ]
    manifest.append(dedup_fasta_by_sequence(fasta_files, ARSM_DB / "arsM_public_protein_initial_dedup.faa"))
    return manifest


def download_crassphage_reference() -> list[dict]:
    manifest: list[dict] = []
    records = [
        (
            "NC_024711.1",
            "crAssphage / Carjivirus communis complete genome, commonly used prototype crAssphage reference",
        )
    ]
    for accession, note in records:
        fasta = CRASS / f"{accession}_crAssphage_complete_genome.fna"
        gb = CRASS / f"{accession}_crAssphage_complete_genome.gb"
        manifest.append(
            download(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
                + urllib.parse.urlencode({"db": "nuccore", "id": accession, "rettype": "fasta", "retmode": "text"}),
                fasta,
                timeout=120,
            )
        )
        manifest[-1]["note"] = note
        manifest.append(
            download(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
                + urllib.parse.urlencode({"db": "nuccore", "id": accession, "rettype": "gb", "retmode": "text"}),
                gb,
                timeout=120,
            )
        )
    return manifest


def write_readme(summary: dict) -> None:
    readme = REFERENCE / "README.md"
    readme.write_text(
        f"""# Reference Databases

Built for the arsM/crAssphage pilot workflow.

## arsM HMM

- `arsM_hmm/PTHR43675_arsenite_methyltransferase_panther.hmm`: primary family HMM from InterPro/PANTHER.
- `arsM_hmm/PF31200_AS3MT_C_terminal_domain.hmm`: auxiliary Pfam C-terminal domain HMM. Do not use as the sole arsM detector.
- Metadata JSON files are saved beside the HMMs.

## arsM Public Database

- `arsM_public_database/arsM_public_protein_initial_dedup.faa`: initial deduplicated protein reference set.
- `arsM_public_database/arsM_uniprot_public_dedup.faa`: UniProt-derived deduplicated subset.
- `arsM_public_database/ncbi_arsenite_methyltransferase_bacteria_archaea.faa`: NCBI Protein supplement.
- `arsM_public_database/ncbi_arsenite_methyltransferase_bacteria_archaea_first2000_cds.fna`: CDS nucleotide sequences resolvable by NCBI for the first 2000 bacterial/archaeal protein hits.

This is a usable initial database, not the final publication-grade curated catalog. After WSL2 is ready, run HMMER/BLAST checks and threshold benchmarking before final filtering.

## crAssphage Reference

- `crAssphage_reference/NC_024711.1_crAssphage_complete_genome.fna`: prototype crAssphage/Carjivirus communis complete genome.
- GenBank format is saved beside it for annotation provenance.

## Summary

```json
{json.dumps(summary, indent=2, ensure_ascii=False)}
```
""",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    manifest: dict[str, list[dict]] = {}
    manifest["hmm"] = download_interpro_hmms()
    manifest["uniprot"] = download_uniprot_references()
    manifest["ncbi"] = download_ncbi_references()
    manifest["crassphage"] = download_crassphage_reference()
    summary = {
        "arsM_hmm_primary_exists": (ARSM_HMM / "PTHR43675_arsenite_methyltransferase_panther.hmm").exists(),
        "arsM_hmm_auxiliary_exists": (ARSM_HMM / "PF31200_AS3MT_C_terminal_domain.hmm").exists(),
        "uniprot_dedup_proteins": count_fasta(ARSM_DB / "arsM_uniprot_public_dedup.faa"),
        "initial_public_proteins": count_fasta(ARSM_DB / "arsM_public_protein_initial_dedup.faa"),
        "ncbi_cds_records_first2000": count_fasta(ARSM_DB / "ncbi_arsenite_methyltransferase_bacteria_archaea_first2000_cds.fna"),
        "crAssphage_records": count_fasta(CRASS / "NC_024711.1_crAssphage_complete_genome.fna"),
    }
    (LOGS / "reference_build_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (LOGS / "reference_build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_readme(summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

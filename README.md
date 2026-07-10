# Workflow

This repository documents an arsM/crAssphage screening workflow for urban river metagenomes.

The workflow builds reference databases, selects pilot rivers from public sample metadata, screens the arsenic methylation marker `arsM`, and compares the signal with a crAssphage sewage marker.

# 1. Software used in this workflow

## 1.1 Recommended installation paths

The examples below assume a Linux server or WSL2 workstation. Keep software, references, raw data, and results separated so that large temporary files can be cleaned without touching the workflow repository.

```shell
# Conda or micromamba environment
~/miniconda3/envs/arsm_crass/bin

# Project repository
~/projects/arsM-crassphage-urban-river-workflow

# Large raw reads and intermediate assemblies
/mnt/f/As/raw_reads
/mnt/f/As/river_runs
/mnt/f/As/tmp

# Local reference database copy
~/projects/arsM-crassphage-urban-river-workflow/reference
```

On this Windows/WSL workstation, large generated files were kept outside the GitHub repository, under `F:\As` or `D:\codex`, rather than on the C drive.

## 1.2 Core software

[Python3](https://www.python.org/downloads/)

[pypdf](https://pypdf.readthedocs.io/)

[Axel](https://github.com/axel-download-accelerator/axel) or [aria2](https://aria2.github.io/)

[Sra-tools](https://github.com/ncbi/sra-tools)

[Fastp](https://github.com/OpenGene/fastp)

[MEGAHIT](https://github.com/voutcn/megahit)

[Prodigal](https://github.com/hyattpd/Prodigal)

[HMMER](http://hmmer.org/)

[CD-HIT](https://sites.google.com/view/cd-hit)

[Bowtie2](https://bowtie-bio.sourceforge.net/bowtie2/manual.shtml)

[Samtools](https://www.htslib.org/)

[SeqKit](https://bioinf.shenwei.me/seqkit/)

[MUSCLE](https://github.com/rcedgar/muscle)

[IQ-TREE 2](https://github.com/iqtree/iqtree2)

[BLAST+](https://blast.ncbi.nlm.nih.gov/)

## 1.3 Example environment setup

```shell
conda create -n arsm_crass -c conda-forge -c bioconda \
    python=3.11 pypdf sra-tools fastp megahit prodigal hmmer cd-hit \
    bowtie2 samtools seqkit muscle iqtree blast aria2

conda activate arsm_crass
```

# 2.1 Metadata file inspection

Use local metadata files to summarize sample tables and extracted text.

```shell
python inspect_si_files.py > si_overview.json
python summarize_si_overview.py
```

PDF text can be extracted separately:

```shell
python extract_si_text.py
```

# 2.2 Pilot river selection

Pilot rivers were selected to keep the first screening run small while preserving a strong sewage-gradient signal.

Recommended minimum pilot:

```text
ShiQi River + Plata River + Ter River = 27 samples
```

Recommended stronger pilot:

```text
ShiQi River + Plata River + Ter River + Suze River + Han River = 54 samples
```

The accession list and selection rationale are recorded in `pilot_river_selection.md`.

# 2.3 Reference database construction

This step downloads arsM-related HMMs and public protein references from InterPro, UniProt, and NCBI, then downloads the prototype crAssphage genome `NC_024711.1`.

```shell
python build_reference_databases.py
```

Outputs are written under `reference/`.

Current reference summary:

```json
{
  "arsM_hmm_primary_exists": true,
  "arsM_hmm_auxiliary_exists": true,
  "uniprot_dedup_proteins": 8177,
  "initial_public_proteins": 14553,
  "ncbi_cds_records_first2000": 627,
  "crAssphage_records": 1
}
```

# 2.4 Download of publicly available metagenomic data

For each pilot river, download public SRA/ENA reads by accession. Prefer ENA FASTQ download when available because it avoids extra SRA conversion and temporary disk use.

```shell
# Example placeholder. Use the accessions in pilot_river_selection.md.
while IFS= read -r accession; do
    echo "Download $accession from ENA FASTQ when available, otherwise use SRA."
done < accessions.txt
```

# 2.5 FASTQ format from SRA files

Use this only when ENA FASTQ files are not available.

```shell
for accession in SRR* ERR*; do
    if [ -f "$accession" ]; then
        fasterq-dump --split-3 "$accession" -O . -e 30
    fi
done
```

# 2.6 Read trimming

```shell
for file in *_1.fastq.gz; do
    prefix="${file%_1.fastq.gz}"
    fastp --thread 16 \
        --in1 "${prefix}_1.fastq.gz" \
        --in2 "${prefix}_2.fastq.gz" \
        --out1 "${prefix}_1.clean.fq.gz" \
        --out2 "${prefix}_2.clean.fq.gz"
done
```

For single-end samples, switch to `fastp --in1 ... --out1 ...`.

# 2.7 crAssphage abundance counting

Build the Bowtie2 index:

```shell
bowtie2-build reference/crAssphage_reference/NC_024711.1_crAssphage_complete_genome.fna crAssphage_NC_024711
```

Use streamed counting to avoid saving large BAM files:

```shell
bowtie2 --no-unal -x crAssphage_NC_024711 \
    -1 sample_1.clean.fq.gz \
    -2 sample_2.clean.fq.gz \
    2> sample.crAssphage.bowtie2.log \
    | samtools view -c - > sample.crAssphage.mapped_reads.txt
```

Treat this single genome as a narrow sewage marker. Zero mapping to `NC_024711.1` does not prove absence of sewage signal.

# 2.8 Assembly

```shell
megahit \
    -1 sample_1.clean.fq.gz \
    -2 sample_2.clean.fq.gz \
    --min-contig-len 1000 \
    --k-min 121 \
    --min-count 3 \
    --no-mercy \
    -t 4 \
    --memory 0.45 \
    -o sample_assembly
```

These settings are resource-adjusted for a 16GB Windows/WSL workstation. Use higher-memory settings on a dedicated server.

# 2.9 arsM catalog construction

Predict genes:

```shell
prodigal \
    -i sample_assembly/final.contigs.fa \
    -d sample.genes.fna \
    -a sample.proteins.faa \
    -p meta
```

Screen candidates with the PANTHER HMM as the primary detector and the Pfam C-terminal HMM as auxiliary evidence:

```shell
hmmsearch --domtblout sample.arsM.PTHR43675.domtblout \
    reference/arsM_hmm/PTHR43675_arsenite_methyltransferase_panther.hmm \
    sample.proteins.faa > sample.arsM.PTHR43675.out

hmmsearch --domtblout sample.arsM.PF31200.domtblout \
    reference/arsM_hmm/PF31200_AS3MT_C_terminal_domain.hmm \
    sample.proteins.faa > sample.arsM.PF31200.out
```

Parse HMMER `domtblout` fields carefully. Use full E-value `$7`, domain conditional E-value `$12`, and domain independent E-value `$13`; do not compare score `$14` to an E-value cutoff.

Manual/curated filtering should check conserved-domain support and cysteine-position motifs as documented in `reference/arsM_hmm/arsM_conserved_domain_filtering.md`.

# 2.10 Build river-level arsM catalogs and abundance matrices

After each sample yields small candidate files, merge candidates at the river level, remove redundancy, and align the final candidate set.

```shell
cat */arsM_candidates.faa > river.arsM_candidates.faa
cd-hit -i river.arsM_candidates.faa -o river.arsM_candidates.nr.faa -c 0.97 -n 5 -d 0 -M 16000 -T 8

muscle -super5 river.arsM_candidates.nr.faa -output river.arsM_candidates.nr.afa
```

Re-download or reuse clean reads one sample at a time, map reads back to the river-level arsM catalog, and remove large read/assembly intermediates after each sample is complete.

```shell
bowtie2-build river.arsM_catalog.fna river_arsM_catalog

bowtie2 --no-unal -x river_arsM_catalog \
    -1 sample_1.clean.fq.gz \
    -2 sample_2.clean.fq.gz \
    2> sample.arsM.bowtie2.log \
    | samtools view -c - > sample.arsM.mapped_reads.txt
```

# 2.11 Phylogenetic analysis

```shell
muscle -super5 river.arsM_candidates.nr.faa -output river.arsM_candidates.nr.afa
iqtree2 -s river.arsM_candidates.nr.afa -B 1000 -T AUTO --prefix river_arsM_iqtree
```

# 3. Repository layout

```text
.
|- README.md
|- requirements.txt
|- build_reference_databases.py
|- extract_si_text.py
|- inspect_si_files.py
|- summarize_si_overview.py
|- pilot_river_selection.md
|- arsM_pipeline_lessons.md
|- reference/
|  |- README.md
|  |- arsM_hmm/
|  |- arsM_public_database/
|  |- crAssphage_reference/
|  `- logs/
|- si_text/
`- supplementary_files/
```

# 4. Operational notes

The file `arsM_pipeline_lessons.md` records practical decisions from early pilot runs, including WSL memory limits, cleanup policy, HMMER parsing rules, paired-end/single-end handling, and disk-safe two-pass processing.

# 5. Data availability

The workflow uses public supplementary files and public sequence databases. Large raw reads, intermediate assemblies, BAM/SAM files, and temporary workflow outputs should not be committed to this repository.

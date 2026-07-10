# Reference Databases

Built for the arsM/crAssphage pilot adapted from Xia et al. 2024.

## arsM HMM

- `arsM_hmm/PTHR43675_arsenite_methyltransferase_panther.hmm`: primary family HMM from InterPro/PANTHER.
- `arsM_hmm/PF31200_AS3MT_C_terminal_domain.hmm`: auxiliary Pfam C-terminal domain HMM. Do not use as the sole arsM detector.
- Metadata JSON files are saved beside the HMMs.
- `arsM_hmm/arsM_conserved_domain_filtering.md`: tiered conserved-domain and cysteine-position filtering criteria.

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
{
  "arsM_hmm_primary_exists": true,
  "arsM_hmm_auxiliary_exists": true,
  "uniprot_dedup_proteins": 8177,
  "initial_public_proteins": 14553,
  "ncbi_cds_records_first2000": 627,
  "crAssphage_records": 1
}
```

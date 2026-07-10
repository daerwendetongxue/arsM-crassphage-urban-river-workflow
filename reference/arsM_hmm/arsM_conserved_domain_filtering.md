# arsM Conserved Domain and Motif Filtering Criteria

Purpose: define an arsM filtering rule analogous to the hgcA/hgcB manual motif check in Xia et al. 2024, but adapted to ArsM biology.

## Why hgcAB rules cannot be copied directly

The hgcA/hgcB workflow removes sequences missing a specific HgcA cap-helix motif or HgcB ferredoxin-binding motifs. ArsM is different. It belongs to the SAM-dependent methyltransferase superfamily, and ArsM proteins vary in length and domain architecture. A simple exact short motif rule would either admit many ordinary SAM methyltransferases or discard real ArsM variants.

## Reference Features

Use the following features for manual and automated screening:

1. ArsM family/domain support
   - Primary model: `PTHR43675_arsenite_methyltransferase_panther.hmm`
   - InterPro family: `IPR026669`, Arsenite methyltransferase-like
   - This is the primary evidence that the sequence belongs to the ArsM/AS3MT family.

2. SAM-binding region
   - ArsM is an As(III) S-adenosylmethionine methyltransferase.
   - Candidate sequences should retain the SAM-dependent methyltransferase region.
   - Sequences that only hit unrelated SAM-dependent methyltransferases should not be accepted as arsM.

3. Conserved cysteine residues
   - Canonical ArsM studies use conserved cysteine residues corresponding to CmArsM Cys44, Cys72, Cys174, and Cys224.
   - A literature-supported strict rule is: retain sequences with SAM-binding domains and at least 3 of these 4 conserved cysteine positions after alignment.
   - Later work shows some active non-canonical ArsM proteins may require only two conserved cysteine residues, so the 3/4 rule is conservative rather than universal.

4. C-terminal ArsM domain
   - Auxiliary model: `PF31200_AS3MT_C_terminal_domain.hmm`
   - Do not require PF31200 for every candidate. Many small ArsMs have only A and B domains and lack the C-terminal domain.
   - PF31200 support increases confidence for larger AS3MT-like proteins but is not a mandatory filter.

## Proposed Screening Tiers

### Tier 1: canonical high-confidence ArsM

Use for strict sensitivity analysis and final conservative claims.

Required:

- significant hit to `PTHR43675`;
- retained SAM-binding methyltransferase region;
- at least 3 of 4 conserved cysteine positions corresponding to CmArsM Cys44/Cys72/Cys174/Cys224;
- no obvious frameshift, severe truncation, or implausible length.

Suggested label:

```text
canonical arsM
```

### Tier 2: putative or non-canonical ArsM

Use in the main pilot if Tier 1 becomes too sparse, but always report Tier 1 as a strict sensitivity check.

Required:

- significant hit to `PTHR43675`;
- retained SAM-binding methyltransferase region;
- at least 2 conserved cysteine positions, preferably including the central As-binding pair corresponding approximately to CmArsM Cys174/Cys224 or a documented BlArsM-like pattern;
- sequence clusters with known ArsM/AS3MT references rather than unrelated SAM methyltransferases.

Suggested label:

```text
putative arsM-like methyltransferase
```

### Reject

Remove candidates if any of the following apply:

- no `PTHR43675` family support;
- only a generic SAM-dependent methyltransferase hit;
- only PF31200 C-terminal hit without ArsM family support;
- missing the SAM-binding methyltransferase region;
- no conserved cysteine evidence after alignment;
- severe truncation or obvious assembly/prodigal artifact;
- close BLAST/HMM support points to unrelated methyltransferase families.

## Recommended Project Use

For the first river pilot:

```text
main exploratory table = Tier 1 + Tier 2
strict sensitivity table = Tier 1 only
```

For a manuscript-style claim:

```text
Use Tier 1 for conservative "canonical arsM" claims.
Use Tier 1 + Tier 2 only when phrased as "arsM-like methyltransferase potential" and supported by sensitivity analysis.
```

## Implementation After WSL2 Is Ready

1. Run `hmmsearch` against predicted proteins using `PTHR43675`.
2. Align candidate proteins plus known references using `hmmalign` or MUSCLE.
3. Map candidate alignment columns to reference CmArsM cysteine positions C44/C72/C174/C224.
4. Score each sequence as Tier 1, Tier 2, or Reject.
5. Save manual review notes and the final accepted FASTA files.

Expected output:

```text
arsM_candidate_hits.tsv
arsM_domain_check.tsv
arsM_cysteine_position_check.tsv
arsM_tiered_filtered.faa
arsM_tiered_filtered.fna
arsM_filtering_decisions.tsv
```

## Core Literature Support

- Ye et al. 2017, Scientific Reports: used SAM-binding domains and at least 3 of 4 conserved cysteine residues corresponding to CmArsM C44/C72/C174/C224.
- Chen and Rosen 2023, Environmental Science & Technology: ArsM proteins can have A/B/C domain diversity; small ArsMs may lack the C-terminal domain.
- Huang et al. 2018, Environmental Microbiology: BlArsM is an active non-canonical ArsM requiring only two conserved cysteine residues.
- Qin et al. / PaArsM work: microbial ArsM proteins commonly show four conserved cysteines and three SAM-interaction motifs.

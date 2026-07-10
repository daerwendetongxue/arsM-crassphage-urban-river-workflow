# Pilot River Selection for arsM Screening

Source file: `Xia_2024_hgcAB_SI/41467_2024_53479_MOESM3_ESM.xlsx`, Supplementary Data 1 and 2.

## Selection Logic

Use a small subset first, not all 19 rivers. The first pilot should prioritize:

- small sample count, preferably 6-14 metagenomes per river;
- high crAssphage detection in the original dataset;
- clear hgcA-crAssphage relationship in the original paper, used here only as a data-quality and sewage-gradient proxy;
- enough samples to see whether `arsM` is detectable and whether an `arsM ~ crAssphage` signal exists.

Do not treat original hgcA detection as a biological requirement for arsenic methylation. It is only a practical signal that the river has a strong sewage gradient and usable metagenomic data.

## First-Round Candidates

| Priority | River | Samples | Original crAssphage-positive | Original hgcA-positive | hgcA-crAssphage R | p | Why use |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | ShiQi River | 7 | 7/7 | 7/7 | 0.933 | 2.19e-3 | Very small, complete detection, strong sewage signal |
| 2 | Plata River | 8 | 8/8 | 8/8 | 0.927 | 9.37e-4 | Very small, complete detection, strong correlation |
| 3 | Ter River | 12 | 12/12 | 12/12 | 0.860 | 3.37e-4 | Still small, all-positive original signal |
| 4 | Suze River | 14 | 14/14 | 12/14 | 0.899 | 1.21e-5 | Small enough, strong correlation, European urban river |
| 5 | Han River | 13 | 12/13 | 9/13 | 0.875 | 8.87e-5 | Small enough, independent from larger Han River Basin set |

Recommended minimum pilot:

```text
ShiQi River + Plata River + Ter River = 27 samples
```

Recommended stronger pilot:

```text
ShiQi River + Plata River + Ter River + Suze River + Han River = 54 samples
```

## Optional / Second-Round Candidates

| River | Samples | Original crAssphage-positive | Original hgcA-positive | hgcA-crAssphage R | p | Comment |
|---|---:|---:|---:|---:|---:|---|
| Yamuna River | 6 | 5/6 | 6/6 | 0.890 | 1.74e-2 | Very small, but n=6 is weak for correlation |
| Leine river | 12 | 12/12 | 10/12 | 0.897 | 7.52e-5 | Good hgcA signal, but hgcB correlation was weak in the original data |
| Bardello River | 8 | 6/8 | 4/8 | 0.925 | 2.83e-3 | Useful as a stress test, not ideal as first positive screen |

## Accessions

### First-Round Stronger Pilot

ShiQi River:

```text
SRR26856463
SRR26856462
SRR26856461
SRR26856460
SRR26856459
SRR26856458
SRR26856457
```

Plata River:

```text
SRR8573788
SRR8573789
SRR8573790
SRR8573791
SRR8573793
SRR8573796
SRR8573804
SRR8573807
```

Ter River:

```text
SRR5298537
SRR5306398
SRR5306399
SRR5306400
SRR5306401
SRR5306402
SRR5306403
SRR5306404
SRR5306406
SRR5306407
SRR5306409
SRR5306410
```

Suze River:

```text
ERR4408280
ERR4408281
ERR4408282
ERR4408283
ERR4408284
ERR4408285
ERR4408286
ERR4408287
ERR4408288
ERR4408289
ERR4408290
ERR4408291
ERR4408292
ERR4408293
```

Han River:

```text
SRR12487035
SRR12487002
SRR12487024
SRR12487034
SRR12487037
SRR12487038
SRR12487040
SRR12486991
SRR12486992
SRR12486994
SRR12487043
SRR12487044
SRR12487041
```

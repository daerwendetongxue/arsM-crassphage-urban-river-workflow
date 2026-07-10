# Additional River Candidates

These river datasets are independent of the current pilot list. They are suitable for expanding the arsM/crAssphage workflow without reusing the same river collection.

## Recommended Core Additions

| Priority | River | Region | Public archive | Usable WGS libraries | Why it is useful |
|---|---|---|---|---:|---|
| 1 | Kanda River | Tokyo, Japan | [PRJNA976879](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA976879) | 44 | Eleven sites sampled across seasons; a wastewater treatment plant lies between the upper and lower sites, giving a strong spatial gradient. |
| 2 | Tijuana River | Mexico-United States border | [PRJEB57859](https://www.ebi.ac.uk/ena/browser/view/PRJEB57859) | 22 | Water samples span transboundary urban-flow and estuary locations, with clear human sewage influence. |

Use Kanda River for the main new analysis because it has the best combination of sample number, paired-end depth, and within-river gradient. Use Tijuana River as a geographically independent validation set.

## Exploratory Geographic Additions

| River | Region | Public archive | WGS run | Read type | Use case |
|---|---|---|---|---|---|
| Marecchia River | Rimini, Italy | [PRJEB104705](https://www.ebi.ac.uk/ena/browser/view/PRJEB104705) | `ERR15985447` | Paired-end | A high-depth urban river-mouth sample; use for a geographic contrast, not correlation testing. |
| Marano Torrent | Riccione, Italy | [PRJEB104705](https://www.ebi.ac.uk/ena/browser/view/PRJEB104705) | `ERR15985446` | Paired-end | A second urban river-mouth contrast from the same coastal region. |
| Rio Melo River | Riccione, Italy | [PRJEB104705](https://www.ebi.ac.uk/ena/browser/view/PRJEB104705) | `ERR15985448` | Paired-end | A third urban river-mouth contrast from the same coastal region. |

Each Italian river has one pooled WGS library. Keep these three rivers out of any river-level correlation test; they can be used to test whether arsM candidates and crAssphage mapping remain detectable in a different urban setting.

## Suggested Study Design

```text
Primary discovery: Kanda River (44 samples)
Independent validation: Tijuana River (22 samples)
Geographic contrast: Marecchia + Marano + Rio Melo (3 single libraries)
```

This design adds five rivers while keeping the statistical analysis honest: correlation is performed only within the two multi-sample rivers, while the Italian samples remain exploratory.

## Current Rivers That Can Be Replaced

The existing river list is not biologically invalid. These recommendations only rank datasets by their usefulness for a first-pass arsM/crAssphage association analysis.

| Replacement priority | River | Samples | crAssphage detection | Existing marker-crAssphage R | p | Recommendation |
|---|---|---:|---|---:|---:|---|
| 1 | Lockwitzbach River | 58 | 45/58 | 0.010 | 0.942 | Replace first. Despite its large sample count, the existing metadata show no usable within-river association. |
| 2 | Alexander River | 16 | 14/16 | 0.496 | 0.051 | Replace with Tijuana River when a clearer sewage-gradient validation set is needed. |
| 3 | Kampala River | 20 | 20/20 | 0.570 | 0.00868 | Retain only if regional coverage is important; otherwise replace with Kanda River for a stronger spatial and seasonal design. |

If only one current river is removed, remove Lockwitzbach River. If three are removed, replace Lockwitzbach, Alexander, and Kampala with Kanda River, Tijuana River, and one Italian river-mouth sample for geographic contrast.

## Download Identifiers

Kanda River contains 44 paired-end WGS runs under `PRJNA976879`. Retrieve the WGS runs from the project metadata rather than downloading the project's 16S and single-cell records.

Tijuana River contains 22 paired-end WGS runs:

```text
ERR11181229
ERR11181230
ERR11181231
ERR11181232
ERR11181233
ERR11181234
ERR11181235
ERR11181236
ERR11181237
ERR11181238
ERR11181239
ERR11181240
ERR11181241
ERR11181242
ERR11181243
ERR11181244
ERR11181245
ERR11181246
ERR11181247
ERR11181248
ERR11181249
ERR11181250
```

For `PRJEB104705`, download only the three `ERR15985446`-`ERR15985448` WGS runs. The remaining records in that project are 16S amplicon libraries and should not enter the arsM workflow.

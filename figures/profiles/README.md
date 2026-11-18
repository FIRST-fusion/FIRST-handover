# Five profile plots

Each case has q, pressure, ⟨J·B⟩, and poloidal and toroidal Jacobian-weighted current profiles.
The horizontal axis is normalized toroidal flux s; native signs, sampling, and endpoints are kept.
Each case's `metadata.json` records the source fields, units, and flux conversion; [run commands are on the home page](../../README.md#3-run).

| Case | Overview | Five-page PDF | Data | Source and hash |
|---|---|---|---|---|
| chease_c50 | [PNG](chease_c50/overview.png) | [PDF](chease_c50/profiles.pdf) | [CSV](chease_c50/profiles.csv) | [JSON](chease_c50/metadata.json) |
| chease_c51 | [PNG](chease_c51/overview.png) | [PDF](chease_c51/profiles.pdf) | [CSV](chease_c51/profiles.csv) | [JSON](chease_c51/metadata.json) |
| vmec_lowbeta | [PNG](vmec_lowbeta/overview.png) | [PDF](vmec_lowbeta/profiles.pdf) | [CSV](vmec_lowbeta/profiles.csv) | [JSON](vmec_lowbeta/metadata.json) |
| vmec_smooth | [PNG](vmec_smooth/overview.png) | [PDF](vmec_smooth/profiles.pdf) | [CSV](vmec_smooth/profiles.csv) | [JSON](vmec_smooth/metadata.json) |
| freep80_high256 | [PNG](freep80_high256/overview.png) | [PDF](freep80_high256/profiles.pdf) | [CSV](freep80_high256/profiles.csv) | [JSON](freep80_high256/metadata.json) |
| vmec_p80_513 | [PNG](vmec_p80_513/overview.png) | [PDF](vmec_p80_513/profiles.pdf) | [CSV](vmec_p80_513/profiles.csv) | [JSON](vmec_p80_513/metadata.json) |
| p6_s033_c050_fine_exact320 | [PNG](p6_s033_c050_fine_exact320/overview.png) | [PDF](p6_s033_c050_fine_exact320/profiles.pdf) | [CSV](p6_s033_c050_fine_exact320/profiles.csv) | [JSON](p6_s033_c050_fine_exact320/metadata.json) |
| vmec_p6_s033_c050_fine_exact320_2049 | [PNG](vmec_p6_s033_c050_fine_exact320_2049/overview.png) | [PDF](vmec_p6_s033_c050_fine_exact320_2049/profiles.pdf) | [CSV](vmec_p6_s033_c050_fine_exact320_2049/profiles.csv) | [JSON](vmec_p6_s033_c050_fine_exact320_2049/metadata.json) |

## High bootstrap: five separate plots

| Quantity | A=1.4 CHEASE p80 | A=1.4 VMEC p80 | A=1.2 CHEASE | A=1.2 VMEC |
|---|---|---|---|---|
| q | [PNG](freep80_high256/q.png) · [PDF](freep80_high256/q.pdf) | [PNG](vmec_p80_513/q.png) · [PDF](vmec_p80_513/q.pdf) | [PNG](p6_s033_c050_fine_exact320/q.png) · [PDF](p6_s033_c050_fine_exact320/q.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/q.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/q.pdf) |
| Pressure [Pa] | [PNG](freep80_high256/pressure.png) · [PDF](freep80_high256/pressure.pdf) | [PNG](vmec_p80_513/pressure.png) · [PDF](vmec_p80_513/pressure.pdf) | [PNG](p6_s033_c050_fine_exact320/pressure.png) · [PDF](p6_s033_c050_fine_exact320/pressure.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/pressure.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/pressure.pdf) |
| ⟨J·B⟩ [A·T/m²] | [PNG](freep80_high256/jdotb.png) · [PDF](freep80_high256/jdotb.pdf) | [PNG](vmec_p80_513/jdotb.png) · [PDF](vmec_p80_513/jdotb.pdf) | [PNG](p6_s033_c050_fine_exact320/jdotb.png) · [PDF](p6_s033_c050_fine_exact320/jdotb.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/jdotb.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/jdotb.pdf) |
| Poloidal weighted current [A] | [PNG](freep80_high256/poloidal_current.png) · [PDF](freep80_high256/poloidal_current.pdf) | [PNG](vmec_p80_513/poloidal_current.png) · [PDF](vmec_p80_513/poloidal_current.pdf) | [PNG](p6_s033_c050_fine_exact320/poloidal_current.png) · [PDF](p6_s033_c050_fine_exact320/poloidal_current.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/poloidal_current.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/poloidal_current.pdf) |
| Toroidal weighted current [A] | [PNG](freep80_high256/toroidal_current.png) · [PDF](freep80_high256/toroidal_current.pdf) | [PNG](vmec_p80_513/toroidal_current.png) · [PDF](vmec_p80_513/toroidal_current.pdf) | [PNG](p6_s033_c050_fine_exact320/toroidal_current.png) · [PDF](p6_s033_c050_fine_exact320/toroidal_current.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/toroidal_current.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/toroidal_current.pdf) |

The tutorial cases are not the same physical equilibrium, so their differences cannot be used directly as a cross-solver error. The VMEC wout files used for research were taken from the local archive and are not in the original Git input package; the exact paths are in the metadata. There was no new solver or stability execution.

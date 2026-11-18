# Historical research inputs for about 99% bootstrap current

**14 equilibrium inputs found: 10 CHEASE and 4 VMEC.** Retrieved on 2026-11-18 from the original FIRST research directory, keeping the original input bytes, the required restarts, the historical results, and SHA-256. This directory stores historical data. Later new runs were done only for the p80 pair and for edited cases, **not a re-acceptance of all 14 or a stability certificate**. See the [run evidence](../../evidence/ACCEPTANCE.md).

[Back to the handover home page](../../README.md) · [Full sources and hashes](manifest.json) · [Run conditions and parameter-adjustment notes](RUNTIME.md)

**Every step for creating a case, editing an input, running, and viewing plots is on the [handover home page](../../README.md).** This page keeps only the research cases, the physical definitions, and the historical limits.

## Start with these two pairs

- **A=1.4 / lower-β branch:** [CHEASE p80](cases/freep80_high256/inputs) → [paired VMEC513](cases/vmec_p80_513/inputs), fBS about 99.16% / 99.17%. Each includes historical DCON settings, logs, and summaries for n=1, 2, and 3 and wall b/a=1.2.
- **A=1.2 / candidate for the advisor's goal:** [CHEASE exact320](cases/p6_s033_c050_fine_exact320/inputs) → [paired VMEC2049](cases/vmec_p6_s033_c050_fine_exact320_2049/inputs), fBS about 99.29%, βN about 5.60. The VMEC→DCON near-axis problem is unsolved, finite n=1–3 is not finished, and this is not a demonstrated second-stability region.

## Case index

| Case (select for the inputs) | Solver | A | fBS [%] | βvac [%] | NS |
|---|---|---:|---:|---:|---:|
| [freep80_high256](cases/freep80_high256/inputs) | CHEASE | 1.4 | 99.160292 | 36.838307 | 256 |
| [freep80_high320_phase9](cases/freep80_high320_phase9/inputs) | CHEASE | 1.4 | 99.160335 | 36.838270 | 320 |
| [freep90_high256_phase9](cases/freep90_high256_phase9/inputs) | CHEASE | 1.4 | 99.465158 | 44.755893 | 256 |
| [freep98_high256_phase9](cases/freep98_high256_phase9/inputs) | CHEASE | 1.4 | 99.612084 | 51.847865 | 256 |
| [freep98_high320_phase9](cases/freep98_high320_phase9/inputs) | CHEASE | 1.4 | 99.612133 | 51.847821 | 320 |
| [free54_refined](cases/free54_refined/inputs) | CHEASE | 1.4 | 99.616444 | 53.773235 | 128 |
| [free54_high256](cases/free54_high256/inputs) | CHEASE | 1.4 | 99.616060 | 53.773101 | 256 |
| [free54_high320](cases/free54_high320/inputs) | CHEASE | 1.4 | 99.616112 | 53.773055 | 320 |
| [vmec_p80_513](cases/vmec_p80_513/inputs) | VMEC | 1.4 | 99.169525 | 36.838335 | 513 |
| [vmec_p98_513](cases/vmec_p98_513/inputs) | VMEC | 1.4 | 99.621140 | 51.847885 | 513 |
| [vmec_selfconsistent513](cases/vmec_selfconsistent513/inputs) | VMEC | 1.4 | 99.625381 | 53.773445 | 513 |
| [p6_s033_c050_fine128_024](cases/p6_s033_c050_fine128_024/inputs) | CHEASE | 1.2 | 99.290589 | 15.187460 | 128 |
| [p6_s033_c050_fine_exact320](cases/p6_s033_c050_fine_exact320/inputs) | CHEASE | 1.2 | 99.288578 | 15.187458 | 320 |
| [vmec_p6_s033_c050_fine_exact320_2049](cases/vmec_p6_s033_c050_fine_exact320_2049/inputs) | VMEC | 1.2 | 99.287075 | 15.187526 | 2049 |

βvac is the volume-averaged β defined with the vacuum reference field, not βN. NS is each solver's own radial setting and does not mean the two use the same flux coordinate. The A=1.4 geometry is R0=1 m, B0=1 T, κ=3, δ=0.5; A=1.2 is R0=0.45 m, a=0.375 m, B0=1 T, κ≈2.4, δ≈0.4795. They cannot be ranked by the size of β alone.

## How to read the files

- `cases/<case>/inputs/`: CHEASE `namelist + EXPEQ + NIN`; VMEC `input.test`. **NIN is the original restart. Do not omit it or replace it with another case at will.**
- `cases/<case>/historical/`: the original `summary.json` and `run.log`, and, when present, the bootstrap audit, current profiles, geometry handoff, and resolution settings. `valid=true` in a historical summary is not a successful rerun for this handover, and it is not full stability.
- `historical/dcon_n*_w0.2_g512_s5_robust/` for the two p80 cases: `equil.in / dcon.in / vac.in / run.log / summary.json` for three values of n. Absolute paths in the original settings are source records only. A rerun must point at that run's own new equilibrium output.
- `source-reports/`: snapshots of the historical research reports and the independent audit. Old links, run instructions, and the status of that time in the `.txt` files are not this task and are not the live status.
- `manifest.json`: source, size, hash, and case summary for each file. The CHEASE closure residual names its source with `closure_field`. A=1.2 uses `closure_fixed_seed`, which matches that case's seed; the default-seed diagnostic must not be used by mistake.

This is a **selected set of inputs plus the key historical outputs**, not a complete backup of every large file. For example, `wout_test.nc` and the full mapping remain in the original FIRST research directory named by the manifest. A new run must produce them itself. Do not treat them as if Git already contained them.

## What 0.99 actually means

This table uses `fbs_total_hirshman`, the **global integral fraction** from the collisionless Hirshman current decomposition, `fBS = 1 − Iaux / Ip`. It is not the weighted approximation `fbs_weighted_hirshman`, and it is not an input switch set to 0.99.

This CHEASE set uses `NBSOPT=0`: bootstrap self-consistency was finished by an external iteration, and what was stored is the pressure and current profiles after that iteration. **Running the saved equilibrium input once is not doing bootstrap self-consistency again.** After the pressure, seed, or boundary is changed, the iteration, fBS, and closure residual must be computed again; the original 99% is not kept automatically. `p80/p90/p98` labels the pressure-gradient amplitude of the original branch, not a bootstrap percentage.

This fBS diagnostic uses Zeff=2, pe=pi, Te=Ti, and a specified gradient assumption, and it handles the diamagnetic and Pfirsch–Schlüter parts by the original method. It is not a general transport model. CHEASE integrates again from this run's `linliu_profiles.dat`; VMEC computes again from the Fourier and Jacobian content of this run's `wout_test.nc`. VMEC `Iaux_A/Itotal_A` is in amperes. The original CHEASE `itotal` is a normalized current and must not be labeled directly as amperes.

In a new run's `summary.json`, `fbs_percent` is a percentage and `fbs_total_hirshman` is a fraction; for example, 0.9916029189 equals 99.16029189%, not 0.9916%. For a custom input, `historical_fbs/fbs_difference` is null. VMEC `closure_below_1e-3=null` means there is no fixed-seed closure certificate. A custom CHEASE seed goes in `bootstrap-settings.json` in the same directory as the input, with `seed_axis`, `seed_center`, and `seed_width` (width > 0). If they are not given, seed closure is not certified.

## Source pairing across solvers

| VMEC | Actual CHEASE parent |
|---|---|
| `vmec_p80_513` | `freep80_high256` |
| `vmec_p98_513` | `freep98_high256_phase9` |
| `vmec_selfconsistent513` | **`free54_refined`**, not high256/high320 |
| `vmec_p6_s033_c050_fine_exact320_2049` | `p6_s033_c050_fine_exact320` |

CHEASE profiles use a coordinate related to poloidal flux; VMEC uses normalized toroidal flux. Profile reconstruction must retain that conversion; matching radial indices alone does not identify the same flux surface.

## Stability boundary: high bootstrap ≠ full stability

- **p80:** historical finite positive-energy results exist for CHEASE and VMEC at the specified near wall b/a=1.2 and n=1–3; the CHEASE local-stability refinement checks across nine phases are more complete. This cannot be extended to every n, to no wall, or to a claim that the VMEC near-axis warning has been removed.
- **p90 / p98:** at wall b/a=1.3 there are modes with negative energy or modes that did not pass the quality filter. Local stability also cannot stand in for a finite-n check.
- **free54:** βvac≈53.77% and fBS≈99.62%. High-n edge ballooning did not pass. Positive energy for near-wall n=1–5 is not proof of full stability, and the n=6 timeout is unknown.
- **A=1.2:** the CHEASE local check passed. VMEC→DCON still has a near-axis Mercier warning and missing surfaces. The second-stability region and finite n=1–3 have not been accepted.

See the [Lin–Liu numerical tables](source-reports/linliu-numerical-tables.txt), [research conclusions](source-reports/linliu-results.txt), [A=1.2 historical report](source-reports/aspect12-historical-readme.txt), and [independent audit](source-reports/aspect12-independent-audit.json).

## Check handover-file integrity only (do not run a solver)

From the repository root:

```sh
python3 tools/check_research_inputs.py
```

Success only means the inputs and historical evidence are undamaged and the index agrees with the original summaries. It is not a new numerical-reproduction acceptance.

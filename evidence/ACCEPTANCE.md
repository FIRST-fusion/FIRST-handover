# Acceptance for this handover (2026-11-18)

## Scope and data

FIRST `ncku-first` / `ouvic`, isolated root directory `/home/ouvic/first-handover-20261118`. Existing source, binaries, schedules, and containers were not modified, and no parameter search was started.

Each of the four cases had one reference round, then one independent replay from the same set of fixed inputs; both rounds reran the equilibrium solver and DCON. Every DCON run is n=1, the specified wall, and psihigh=.99; this is not a complete scientific stability acceptance.

| Case | Equilibrium convergence metric | DCON q0 | DCON betan (native diagnostic) | Reference pipeline time |
|---|---:|---:|---:|---:|
| chease_c50 | RESIDU=7.07985e-11 | 4.264 | 8.566 | about 20 seconds |
| chease_c51 | RESIDU=9.73762e-11 | 4.281 | 8.452 | about 20 seconds |
| vmec_lowbeta | FSQR=9.76e-13; the other residuals are smaller | 1.250 | 0.9089 | about 3 seconds |
| vmec_smooth | FSQR=9.92e-14; the other residuals are smaller | 2.279 | 14.17 | about 20 seconds |

Different cases are not the same physical setup, so the table above is not a ranking of results. The times were measured then and are not guaranteed to be the same on every run. The formal machine-readable comparison is in `replay_comparison.json`; the actual summaries from the second round are in `replays/`.

## Verification layers

1. First round: four equilibrium stages and four DCON stages completed, and the convergence, interface, and required-output checks passed.
2. Second round: the four complete pipelines were rerun; the fixed inputs, runtime, DCON control-file hashes, key values, classifications, and floating-point warnings were compared.
3. Reference-data integrity: `reference_manifest.json` covers 44 selected original outputs, settings, and summaries; `tools/check_reference.py` checks SHA-256.
4. Python tests: comparison tolerances, missing fields, NaN, a bad schema, false-valid, and the reference not being modifiable; also tests that a nonconverged equilibrium fails, that a fatal DCON message fails, and that a missing fixed-boundary label must not be inferred as stable. The record of the latest run is in `acceptance.json`.
5. GitHub CI only runs static tool tests and integrity checks of stored outputs; it does not claim that CI newly ran a solver.

## Limits and warnings that are kept

Every DCON reference has IEEE floating-point flags; division, overflow, and similar flags cannot be declared free of problems only because the final number is finite. The original logs, flags, and reported classifications are kept in full, and the scientific status is uniformly NOT_CERTIFIED.

This is a reproducible teaching and regression baseline, **not four solutions already proved stable**. Validation across arbitrary n, complete magnetic-surface coverage for global/local stability, grid convergence, wall scans, and bootstrap self-consistency were not completed, and the numerical warnings of the original DCON were not fixed.

All older research and failed outputs are kept. The trial-run and acceptance containers from this handover also remain exited; rm/prune was not run.

## Checked again after a fresh GitHub checkout

`clean_checkout.json` records the commit freshly cloned from GitHub, and that checkout was then copied exactly into a new directory on FIRST. 19 tool tests passed, and hashes of 44 files passed; CHEASE c50 and VMEC lowbeta each reran the whole pipeline and passed comparison. GitHub credentials were not copied to FIRST. Later commits only added acceptance records; the solver execution tools were not changed.

## Automatic five plots: new FIRST execution acceptance (2026-11-18 14:09–14:16, Taipei)

Both runners were updated: scientific Python is checked first, and after the solve and diagnostics this run's output is read and plotted automatically, with the PNG overview and PDF paths listed; a plotting failure keeps `valid=false`. The old remote tools were kept first in `backups-profile-20261118T1409/`. The original solver, images, historical cases, and schedules were not changed.

All four tutorial examples were rerun as equilibrium → DCON → profiles, and all four reference comparisons passed. `freep80_high256` and `vmec_p80_513` were also rerun as equilibrium → bootstrap → profiles. Each of the six cases has five single plots, **30 single plots** in total; each case has 15 plot, value, and source files.

Source-file SHA-256 was checked for the six cases, every CSV column matches the new output point by point, all 15 required files are complete, and the CHEASE and VMEC tutorial overviews and the p80 representative overviews were opened and checked. 28 tests passed once each on the local machine and on FIRST; hashes of 44 reference files and 136 research inputs are unchanged. These are operational and plotting checks, not a new stability certificate; p80 did not run DCON this time.

[Machine-readable receipt](remote_profile_acceptance.json)

## Editable inputs (2026-11-18)

`tools/case.py init/run` and `--input-dir` on both runners were added, so a custom input copy, that run's snapshot and hash, and automatic five plots after an edit are supported. Three edited cases were actually solved on FIRST, and the pressure scale was checked to change with the input; the p80 fBS was recomputed rather than taken from the historical value. The original VMEC low-beta example was run once more as a regression and passed. 37 tests passed on each of the local machine and FIRST.

[Operating instructions](../README.md) · [machine-readable receipt](editable_input_acceptance.json)

<a id="fresh-profiles"></a>

<details>
<summary>Plots from six new equilibrium runs (expand to view)</summary>

These plots were produced automatically from new solves by `ouvic@ncku-first`. They are not copies of the archived plots in `figures/profiles`.

Run root: `/home/ouvic/first-handover-20261118`. The full output of each case is in `runs/profile-accept-20261118-<case>/`, and the five single plots, PDF, CSV, and metadata are in its `profiles/` subdirectory.

The original source is that run's `equilibrium/linliu_profiles.dat` and `namelist` (CHEASE), or `equilibrium/wout_test.nc` (VMEC). SHA-256, the point-by-point CSV check, and the run times are in the [acceptance receipt](remote_profile_acceptance.json); the figures are not a stability certificate.

### Four tutorial examples

![VMEC lowbeta](remote_profiles/vmec_lowbeta.png)

![CHEASE c50](remote_profiles/chease_c50.png)

![CHEASE c51](remote_profiles/chease_c51.png)

![VMEC smooth](remote_profiles/vmec_smooth.png)

### High-bootstrap p80: solved again this time

CHEASE fBS = 99.1602918859%; VMEC fBS = 99.1695246833%. The outer iteration and DCON were not redone, and this does not add a stability certificate. Native signs are kept; J·B and the poloidal weighted current were not replaced by absolute values.

![CHEASE p80](remote_profiles/freep80_high256.png)

![VMEC p80](remote_profiles/vmec_p80_513.png)

</details>

<a id="edited-profiles"></a>

<details>
<summary>Plots from three edited-input cases (expand to view)</summary>

FIRST / ouvic, three new custom cases; [full receipt](editable_input_acceptance.json). The results remain in `/home/ouvic/first-handover-20261118/runs/<case names below>/`. Each case has 15 plot, data, and source files; every input-snapshot SHA-256 matches the editable file, and the CSV matches this equilibrium's output point by point. This is not a stability certificate.

| Custom case | Edit | New pressure / original pressure | New fBS |
|---|---|---:|---:|
| editable-vmec-20261118 | PRES_SCALE: 2000 → 1500 | 0.75 | not computed by the tutorial workflow |
| editable-chease-20261118 | B0EXP: 1 → 0.95 | 0.9025 | not computed by the tutorial workflow |
| editable-p80-20261118 | PRES_SCALE: 1 → 0.99 | 0.99 | 98.7676431932% |

p80 no longer reuses the original 99.1695%. A custom input is not judged a successful regression by the old reference numbers. The original VMEC lowbeta was also run once without editing the input and still passed the existing reference comparison. 37 tests passed on each of the local machine and FIRST; hashes of 44 reference files and 136 research inputs are unchanged.

When the p80 edit was first prepared, the duplicate-setting check found that the original file already contained lowercase `pres_scale=1.0` and stopped before any solve. The three cases were started only after that existing setting was edited. There was no repeated solve and no overwrite of an old result.

![Custom VMEC](editable_inputs/editable-vmec-20261118.png)

![Custom CHEASE](editable_inputs/editable-chease-20261118.png)

![Custom p80](editable_inputs/editable-p80-20261118.png)

</details>

## Single run_case.py entry point (2026-11-18)

Root `run_case.py` was added as a thin entry to the same runner. `tools/run_case.py` now accepts a file, a folder, and every tutorial and research example name directly, and no longer requires init or a prepared case.json first. `--bootstrap` recomputes fBS from a custom input. This corrects a confirmed entry-point limit. The user's actual failing command and error were not provided, so this record does not claim to have reproduced that unknown error.

ouvic ran three commands from the repository root: a VMEC file with an arbitrary name (a different old input.test was placed beside it on purpose), a CHEASE folder with no case.json, and an arbitrarily named VMEC file plus `--bootstrap`. The specified file hashes match that run's solver snapshot. The pressure ratios, in order, are 0.875, 0.9409, and 0.995; the new fBS is 98.9691505388%. Each case produced five plots, and the CSV matches the new equilibrium point by point. The original lowbeta regression was also run from the root entry and passed. 43 tests passed on each of the local machine and FIRST; hashes of 44 reference files and 136 research inputs passed.

The full commands are in the host file `runs/direct-cli-acceptance-20261118.sh`, and the outputs are `runs/direct-cli-{vmec,chease,bootstrap,baseline}-20261118/`. The receipt was added to the existing [editable_input_acceptance.json](editable_input_acceptance.json) key `direct_run_case_entrypoint`. No separate Markdown file was opened.

## One equilibrium: bootstrap and DCON together (2026-11-18)

`run_case.py INPUT --bootstrap --dcon` now solves the equilibrium only once, makes five plots, computes the Hirshman bootstrap current, and then gives that same interface to the existing tutorial classic DCON. A research example uses `run_case.py CASE --dcon`. Without the flag, the existing defaults remain. The two runners share the DCON step, and the control-file SHA matches the original baseline (n=1, mpsi=mtheta=128, psi=1e-4–0.99, fixed 300-second limit).

ouvic ran the following three cases and checked them point by point. Each case had only one equilibrium container and one DCON container. The source interface and the DCON copy have identical SHA values, the five-plot CSV matches the new equilibrium point by point, and profiles from the same input also match the earlier output. Results are in `/home/ouvic/first-handover-20261118/runs/`:

| Result directory | fBS this run (%) | DCON free-boundary report | Ballooning report | Mercier report |
|---|---:|---|---|---|
| `combined-dcon-chease-custom-20261118` | 97.9179284129 | stable | unstable | stable |
| `combined-dcon-vmec-custom-20261118` | 98.9691505388 | stable | unstable | unstable |
| `combined-dcon-chease-p80-20261118` | 99.1602918859 | stable | unstable | stable |

**This verifies workflow completion and data provenance, not stability.** All three cases above carry a local instability label, and every fixed-boundary report is unknown. Flags including IEEE_DENORMAL, OVERFLOW, and UNDERFLOW are kept, and VMEC also has DIVIDE_BY_ZERO. Warnings were not hidden, the truncation range was not adjusted, and no stable setting was searched for automatically. This round did not perform a current self-consistency outer iteration, an n scan, or complete-surface or resolution-convergence validation.

The original `vmec_lowbeta` was also run to `combined-dcon-baseline-20261118` and passed the original reference comparison. 56 tests passed on each of the local machine and FIRST, including a bootstrap failure that still runs DCON, a DCON failure that keeps fBS and the plots, NaN rejection, and compatibility with the default modes. Hashes of 44 reference files and 136 research inputs are unchanged. The acceptance script and log on the host are `runs/combined-dcon-accept-20261118.sh` and `.log`. The detailed receipt is merged into the existing [editable_input_acceptance.json](editable_input_acceptance.json) key `combined_bootstrap_dcon`.

The VPN dropped during acceptance. After it returned, the original PID and the completion marker (16:10:51 +08:00) were checked, and the calculation was not resubmitted. Existing research, inputs, results, and schedules were all kept.

# FIRST operating commands

## 1. Login

```sh
ssh ouvic@140.116.16.7
cd /home/ouvic/first-handover-20261118
```

## 2. Prepare input

If you already have an input, run it by that path. To edit an example, copy it to a new name first:

**VMEC**

```sh
mkdir -p inputs
cp -R examples/vmec_lowbeta inputs/my-vmec
nano inputs/my-vmec/input.test
```

**CHEASE**

```sh
mkdir -p inputs
cp -R examples/chease_c50 inputs/my-chease
nano inputs/my-chease/namelist
```

| Solver | Input to specify | Files in the same folder |
|---|---|---|
| VMEC | `input.test`, or a custom filename containing an `&INDATA` namelist | This handover example needs only the main input |
| CHEASE | `namelist`, containing an `&EQDATA` / `$EQDATA` namelist | Prepare `EXPEQ` and `NIN` as the input requires; the copy above already includes them |

Edit `PRES_SCALE=2000` in the VMEC example, save, and then run.

## 3. Run

**Equilibrium + five profiles + bootstrap + DCON, in one line:**

```sh
# VMEC
python3 run_case.py inputs/my-vmec/input.test --bootstrap --dcon

# CHEASE
python3 run_case.py inputs/my-chease/namelist --bootstrap --dcon
```

After editing the input and saving, rerun the same line. Each result is stored in a new directory.

Replace `INPUT` below with your file or folder path:

| What to run | Command |
|---|---|
| Equilibrium + five plots + bootstrap + DCON | `python3 run_case.py INPUT --bootstrap --dcon` |
| Equilibrium + five plots + bootstrap | `python3 run_case.py INPUT --bootstrap` |
| Equilibrium + five plots + DCON (ordinary custom input) | `python3 run_case.py INPUT` |
| Check the environment and input only | `python3 run_case.py INPUT --preflight` |

Run an existing high-bootstrap example, including DCON:

```sh
python3 run_case.py vmec_p80_513 --dcon
python3 run_case.py freep80_high256 --dcon
```

## 4. Arguments

| Argument | Purpose |
|---|---|
| `INPUT` | An input file, folder, or example name; if omitted, the current folder is read. Inside a folder, use `input.test` or `namelist`. |
| `--bootstrap` | For a custom input, compute the Hirshman bootstrap current / fBS, without a self-consistent outer iteration; research examples already enable this by default. |
| `--dcon` | Also run DCON on the same equilibrium, `n=1`; the ordinary tutorial workflow already enables this by default. |
| `--timeout SECONDS` | Equilibrium time limit, 1–14400 seconds; the ordinary workflow defaults to 300 seconds and the bootstrap workflow to 3600 seconds. DCON is fixed at 300 seconds. |
| `--output DIR` | A result directory that does not yet exist; the default creates `runs/<name>-<timestamp>/` automatically. |
| `--preflight` | Check only; do not compute. |
| `--solver chease` / `--solver vmec` | Choose the solver when a folder has both kinds of input; otherwise it is identified automatically. |
| `--input PATH` | Use a named argument instead of the positional `INPUT`. |
| `--input-dir DIR` | Specify the input folder; cannot be combined with `--input`. |
| `--plot-python PYTHON` | Python used for plotting; it needs numpy / scipy / matplotlib. ouvic already provides one, so this is usually left unset. |
| `-h` / `--help` | Show the arguments. |

For example, lengthen the equilibrium time limit and name the result directory:

```sh
python3 run_case.py inputs/my-vmec/input.test --bootstrap --dcon --timeout 3600 --output runs/my-result-01
```

## 5. View results

The terminal prints this run's result directory. Open the files there:

| File | Contents |
|---|---|
| `profiles/overview.png` | Five-plot overview: q, pressure, ⟨J·B⟩, poloidal / toroidal weighted current |
| `profiles/profiles.pdf` | PDF of the five plots |
| `summary.json` | Run status, `fbs_percent` (percent), and each DCON classification |
| `equilibrium/bootstrap.json` | Bootstrap diagnostic |
| `dcon/run.log` | Full DCON output |
| `profiles/profiles.csv`, `profiles/metadata.json` | Plotted values and source files |

[Project goals](docs/PROJECT.md) · [Research input list](research-inputs/bootstrap99/README.md) · [Acceptance record](evidence/ACCEPTANCE.md)

# Runtime reference for the research inputs

Day-to-day operation is on the [handover home page](../../README.md). The research path by default runs the equilibrium, five plots, and a bootstrap audit; adding `--dcon` runs the existing tutorial DCON (n=1) on that same equilibrium and does not rerun the equilibrium. `run_case.py` accepts a research starting-point name; one's own input with `--bootstrap --dcon` runs the two diagnostics in one invocation, `--bootstrap` alone keeps the mode that does not run DCON, and an old `case.json` can still be used. What was actually run, and its limits, follow the [acceptance record](../../evidence/ACCEPTANCE.md); finishing the workflow is not a stability certificate.

## Differences from the introductory examples

| Item | Condition required for the research cases |
|---|---|
| CHEASE capacity | NS256/320 and a high-resolution restart need the highres build. The standard tutorial binary cannot be treated as directly compatible; a restart may be read before conversion onto the new grid. |
| CHEASE executable | FIRST `/home/ouvic/linliu-reproduction-20260911/src_highres/chease_linliu.x`; SHA-256 `6c69f71a88605b9d6963a5f474316393018648a183dcfbf20c7c227eecbd221b`. The original summary for A=1.2 exact320 records this hash directly; the A=1.4 build record is in the historical reproduction manifest. |
| VMEC executable | FIRST `/home/ouvic/workspace/ESTCombo/Stellarator-Tools/build/_deps/parvmec-build/xvmec`; SHA-256 `af9851222f1418b43642d02576fa4067757aada16a546ef9e8129a5745599938`. |
| DCON version | The DCON summary for p80 in this package is marked `gpec_balnorm`, not the classic DCON of the tutorial runner. The historical binary is `/home/ouvic/linliu-reproduction-20260911/reference/GPEC_balnorm/bin/dcon`, SHA-256 `8647117100daaba0369f30248f2aef632433fda36ff04a229e811f3fbeaff3a3`. |
| Historical images | The reproduction manifest records tools image `sha256:fb45041b0fd94cfff4458f7d019629317c62429c31c77863e9b9587039f975bf` and VMEC image `sha256:018ecc40f0f336be7bc46eba3f86166877701ecda4433dc4a5d75546cfada8d6`; this is a historical record, not proof of a new container run for this handover. |
| Time | Historical CHEASE NS320 runs took about 491–618 seconds, and VMEC2049 about 1,346 seconds; the tutorial timeout of 300 seconds does not apply. Different hardware and resource limits can take longer. |
| Output | The CHEASE mapping / VMEC `wout_test.nc` must be newly produced by that case before it is given to a compatible DCON; an intermediate file from another case cannot be used. |

Sources: [historical reproduction manifest](source-reports/linliu-reproduction-manifest.json), [exact320 summary](cases/p6_s033_c050_fine_exact320/historical/summary.json). The programs and images are not in Git; the scope of use still follows [NOTICE](../../NOTICE.md).

## Current runner and account limits

- CHEASE highres uses image `sha256:641ae18660a48900fa8ad7340f9fbc2f716b2bf2295ef382344590194400a708`; VMEC uses the `018ecc…` image in the table above. Each run creates a new container with networking disabled and a read-only rootfs, the binary is mounted read-only, and only the new working directory is writable.
- Each container has 2 CPU / 8 GB, with BLAS/OpenMP single-threaded, and uses the UID/GID of the account that runs it; the full command, image ID, and binary hash are kept in the new `summary.json`.
- Postprocessing on ouvic uses the existing `/home/ouvic/linliu-reproduction-20260911/.venv_uv/bin/python` and does not install system packages.
- **The ubuntu tutorial examples passing does not mean the 14 research cases were also verified on ubuntu.** highres CHEASE still requires a license and read permission; the standard tutorial binary cannot replace it.
- The research runner defaults to a timeout of 3600 seconds. The 2026-11-18 p80 measurements were about 225 seconds for CHEASE and about 97 seconds for VMEC, solver stage only, excluding plots and the audit, and are not guaranteed to repeat.
- Research DCON, if needed, uses a matching version, a new equilibrium interface, the settings for each n and wall, and a full magnetic-surface check. The historical p80 GPEC_balnorm settings cannot be replaced by the tutorial classic DCON and then used to carry the research conclusions forward; A=1.2 cannot borrow the p80 result.

The A=1.2 seed and pressure formula are kept in the [original summary](cases/p6_s033_c050_fine_exact320/historical/summary.json) and [pressure_model](cases/p6_s033_c050_fine_exact320/historical/pressure_model.json); the flux coordinate, units, and seed need to be checked. Replaying one equilibrium is not doing bootstrap self-consistency again, and it does not treat some value of NBSOPT as "setting 99%".

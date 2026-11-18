# FIRST handover maintenance

This is a reproduction/teaching repository, not a parameter-search campaign.
- Work in Traditional Chinese. Preserve original sources, data and existing containers/jobs.
- Never commit credentials, shell histories, restricted solver sources/binaries or Docker images.
- Licensed execution is restricted to the authorized FIRST/NCKU environment. Do not assume clone permission grants a solver license.
- Inputs and reference outputs are immutable baselines. New runs use fresh directories; never auto-update reference to make tests pass.
- Never use docker prune/rm, broad kill, shared-rundir scripts, sudo compiler changes or an automatic scheduler.
- Keep input, executable SHA-256, image ID, controls and output provenance together.
- Reproduction pass is not scientific stability acceptance. Nonfinite/missing output/nonconvergence must fail; floating flags remain visible.
- Tests: python3 -m unittest discover -s tests -v. FIRST commands: README.md; recorded acceptance: evidence/ACCEPTANCE.md.

# Project goals and handover boundary

## Advisor's goal

An equilibrium with low aspect ratio A≈1.2, high βN≈7–8, maintained mainly by the bootstrap current, and evidence of a second stability branch; then study improved confinement and an accessible path from startup → transport evolution → the final state.

Reference: Miller, Y. R. Lin-Liu, et al., Stable equilibria for bootstrap-current-driven low aspect ratio tokamaks, Physics of Plasmas 4,1062 (1997), https://doi.org/10.1063/1.872193 . The original paper uses A=1.4, and its finite-n conclusions include a conducting-wall condition, so they cannot be extrapolated directly to A=1.2.

## Historical research status, not a new validation for this handover

The 2026-11-07 handover follows the 10/27–29 record: the A=1.2 candidate has βN≈5.60 and fBS≈99.29%; a second stability branch is not yet demonstrated, the VMEC/DCON near-axis comparison and surface coverage have problems, and the BALOO interface once connected but did not pass scientific acceptance. Detailed entry on the host:

`/home/ouvic/plasma-research-handover-20261107/START_HERE.md`

The incoming agent should first check the current owner, outputs, and locks. The four demonstrations in this new repository do not mean the problems above are solved. FIRST direct-search and the other existing schedules remain managed by the original owner.

## Expected first-week handover outcomes

1. On an authorized FIRST account, finish running the four examples and submit the new summary and compare results.
2. Explain the difference between EXPEQ/NIN/namelist, input.test, and INP1/dcon_test.txt.
3. Identify one result that executed normally but does not mean stability, together with its warnings and limits.
4. Use read-only commands to find one's own container, the binary/image used, the data location, and the host disk space.
5. Then choose the next work package from the research handover documents; do not expand a tutorial run into a whole-host restart or a parameter search.

## Original course materials as a reference library

Original package: `FIRST-完整教材-20261014` (original edition, 138 pages, 220 slides, 9 videos of about 177 minutes, plus a remade edition). This repository does not duplicate the large videos.

- Read first on taking over: M8 workflow and debugging, M9 modification and verification.
- Code topics: M4 CHEASE, M5 VMEC, M6 DCON; for bootstrap research, also read M7.
- Theory supplement: M1–M3, consult as needed.
- Local path on the holder's machine: `~/Library/Mobile Documents/com~apple~CloudDocs/電漿所資料/參考資料/FIRST-完整教材-20261014`. This path does not appear automatically after clone. The person handing over provides it separately, subject to organizational permission.

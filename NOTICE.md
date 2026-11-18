# Scope of use and license

This private repository is for handover use by the licensed FIRST/NCKU team. It does not contain CHEASE, VMEC, or DCON source, executables, or container images, and it does not grant a new license for third-party programs.

The existing FIRST CHEASE `README.md` states: use by Subproject II members, do not install on hosts outside NCKU, and do not distribute CHEASE without EPFL approval; discussion outside the team must still follow the existing license procedure. Private GitHub access is not permission to use the programs.

`runtime/first.json` points to the execution environment already licensed on FIRST and records binary SHA-256 values and image IDs. An image ID identifies local content; it is not a registry digest that can be pulled from Docker Hub. No image was pushed to a registry.

The example data and outputs from this handover are for internal handover only and do not include an open-source redistribution license. Rights and licenses must be checked separately before making the repository public, uploading a solver, or deploying it at another institution. Source locations for comparison are FIRST-fusion/CHEASE, FIRST-fusion/DCON, and FIRST-fusion/Stellarator-Tools; GitHub HEAD may differ from the locally modified code used for the installed binaries.

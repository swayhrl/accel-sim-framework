# Changed files

No accepted parent simulator file is modified in the execution commit.
Simulator implementations are preserved as reproducible generated patches
because P0 and P1 were built in isolated runtimes.

## Review pack

`docs/vm_tlb/review_packs/AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1/`
contains the source-path audit, inherited comparator receipt, P0/P1 design and
qualification evidence, generated core patches, formal result tables, final
decision, run receipts, raw-data index and hash closure.

## Reproducibility tools

`util/vm_tlb/awma/r101r4_local_service_path_localization_v1/` contains the P0
and P1 patch builders, directed tests, hook auditors, regression/smoke runners,
formal CONTEXT2 runners, immutable-run summarizers and closure tools.

Python bytecode caches are excluded from the commit.  Large trace, runtime and
raw artifacts remain on node164 and are addressed by the raw index and SHA-256
manifests.

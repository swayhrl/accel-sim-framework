# Reproduction

The committed runners are in
`util/vm_tlb/awma/r19_fastweight_authority/`. Recreate the public prompt with
`prepare_input.py`, using the pinned reproduction source and Banking77 source
listed in `SOURCE_RECEIPT.json`.

Run `fastweight_boundary.py` only while holding
`/data/c16/locks/c16_gpu_campaign.lock`. The checkpoint directory must contain
the exact Hub revision and the compatibility-only `CONFIG_STRICT_COMPAT.patch`.
The frozen environment versions are recorded in `ENVIRONMENT.txt`.

The script performs the semantic canary first, then all five paired arms in
three alternating groups, and emits every sample to `RESULT.json`.

# Unknown provenance / review required

These objects are deliberately not repaired, regenerated, or silently promoted
by V0.

## RTX4080 items

1. `rtx4080_exact_llama_model`: U4 admission says no source-local exact asset
   or Hugging Face token was available.  Destination presence is unproven.
2. `rtx4080_r5_u5_u6_u9_raw`: the committed R5 pack records PASS summaries,
   but does not expose raw stdout, function/address-map, static-map payload
   paths, sizes, or per-file SHA values.  Locate a receipt-bound manifest before
   any later copy; do not infer it from R5 status.
3. `rtx4080_frozen_input_bundle`: the frozen four hashes are defined in the
   admission parser, but the current source container does not expose its
   payload directory.  Bind its source path and size before transfer.

## RTX3090 local items excluded from transfer

The 3090 closeout labels the following 17 paths `UNKNOWN_REVIEW_REQUIRED`.
They are neither minimum comparison inputs nor replacement authority:

1. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/COMMAND.txt`
2. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/G1_RUNNER_RECEIPT.json.preflight.json`
3. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/LLAMA_S0_G1.nsys-rep`
4. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/LLAMA_S0_G1.sqlite`
5. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/PARENT_LEASE.json`
6. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/PARENT_LEASE.json.closeout.json`
7. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/SUPERVISOR.log`
8. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/catalog/HEAVY_TAIL_KERNELS.tsv`
9. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/catalog/KERNEL_SEMANTIC_MAP.tsv`
10. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/catalog/NATIVE_BASELINE.tsv`
11. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/catalog/RUNTIME_IMPLEMENTATION_AUDIT.tsv`
12. `raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/catalog/SEMANTIC_COVERAGE.tsv`
13. `raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_DYNAMIC/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/CHILD_RECEIPT.json`
14. `raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_DYNAMIC/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/CHILD_RECEIPT.json.preflight.json`
15. `raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_DYNAMIC/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/PARENT_LEASE.json`
16. `raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_DYNAMIC/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/PARENT_LEASE.json.closeout.json`
17. `raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_DYNAMIC/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/PRODUCER_MANIFEST.json`

The closeout’s file inventory contains their individual sizes and SHA256 values.
They remain source-retained and excluded, without changing any RTX3090 frozen
scientific conclusion.

# Diagnostic binary receipt

`DIAGNOSTIC_SOURCE.patch` is the complete narrow source delta. It changes only `shader.cc`; no accepted source/runtime is modified. The first build omitted preserved AccelWattch objects and the first layout attempt added a POD stats field; both pre-target engineering failures are retained in `RAW_DATA_INDEX.tsv`. The final ABI-preserving build uses existing `vm_ideal_translations` plus explicit environment binding as the target-I0 receipt.

The diagnostic code is disabled by default and P8/P34 disabled controls reproduce every required scientific metric exactly (see `NEUTRALITY_RESULTS.tsv`).

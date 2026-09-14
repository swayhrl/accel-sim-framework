# C16 U5–U7 non-executing infrastructure readiness

`U4_LOCAL_ASSET_IMPORT_PENDING` blocks all Llama execution. The following
contracts are prepared but intentionally not executed:

- U5 validates the fixed `S0/B1/T128/Decode4/TEXT` identity, exact model
  revision, input/token receipt, dtype, CUDA-only residency, attention backend,
  output checksum, and native wall-clock reference.
- U6 records the RTX4080-local kernel census from a successful U5 process only;
  it rejects RTX3090 kernel ordinals, launch IDs, static ranges, and target maps.
- U7 accepts only a frozen NCU 2025.1.1 metric manifest and an U6-bound kernel,
  uses a bounded command, stores `.ncu-rep` under `/data/c16/ncu`, reopens the
  report for CSV export, and hashes raw/export/argv/target identity.

No Llama command, NCU model capture, target binding, or result is authorized
until the U4 importer returns `U4_LOCAL_ASSET_EXACT_CLOSURE_PASS`.

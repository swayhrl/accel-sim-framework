# C16 E1 trace-pressure scanner

This directory contains the one-heavy-pass trace scanner and bounded parallel
orchestrator for `C16_E1_TRACE_REUSE_SET_PRESSURE_CHARACTERIZATION_174NEW_V1`.
It is independent of the B16 timing runner.  It reads immutable postprocessed
`.traceg.xz` files and does not launch Accel-Sim/GPGPU-Sim.

## Claim boundary

Every dynamic count emitted here is either `TRACE_ADDRESS_REFERENCE` or
`128B_LINE_REFERENCE_PROXY`.  It is not actual L2 traffic, a cache hit/miss,
an eviction, or timing.  Explicit constant/local/shared instructions are
excluded.  Generic `LD`/`ST` follows the accepted trace frontend's first-active
address classification against the kernel header's shared/local ranges.

The C++ scanner mirrors the accepted list, base/stride and base/delta decoding.
It fails closed on a non-contiguous base/stride mask because the accepted
frontend leaves such a record's later active lanes undefined.

## Per-kernel files

`analysis_root/kernels/<kernel-id>/` contains:

- `summary.json`: identity, instruction/CTA/global-reference counts, 28 target
  class counts, exact expected-target boundary ordinals, prefix/suffix counts,
  provenance and mapper identity.
- `all_unique_lines.u64`, `non_target_unique_lines.u64`: sorted aligned byte
  addresses, each encoded as a little-endian `uint64_t`.
- `all_line_refs.u64`, `non_target_line_refs.u64`: sorted repeated
  `(line_address, reference_count)` pairs. `all_*` is the Phase C/D authority
  for layer-relative pressure (the other 27 qweight classes remain pressure);
  `non_target_*` means outside the union of all 28 regions and is the separate
  Phase B classification.
- `prefix_*` and `suffix_*`: the same binaries for references before the first
  and after the last reference to the kernel's expected up-projection class.
  These preserve exact cross-kernel reuse-gap endpoints without rescanning.
- `non_target_set_refs.u64`: 32768 little-endian `uint64_t` counters; index is
  `subpartition * 2048 + set_index`.  With `--skip-mapper` it is zero-filled
  and `summary.json` explicitly marks it semantically invalid.
- `all_set_refs.u64`: the corresponding dense histogram for all line-reference
  proxies. Prefix/suffix segments carry both dense histograms as well.

Top-level `TRACE_REFERENCE_SUMMARY.json` and `.tsv` index the selected kernels.
By default the orchestrator validates every scanner instruction/CTA count and
artifact byte identity against `trace-root/control/TRACE_ARTIFACT_INDEX.tsv`.
A complete 4515-kernel run additionally closes against 16,313,481,995 dynamic
instructions and 3,653,040 CTAs.

Static 28-region mapping is built independently without reading traces:

```bash
python3 build_static_mapping.py \
  --mapper /path/to/accepted_l2_mapper_cli \
  --mapper-identity-json /path/to/mapper_identity.json \
  --sidecar /path/to/ORACLE_QWEIGHT_L2_SIDECAR.tsv \
  --output QWEIGHT_L2_SET_MAPPING.mapper.json
```

## Build and bounded execution

```bash
./build_scanner.sh /path/to/trace_pressure_scanner
python3 orchestrate_trace_pressure.py \
  --scanner /path/to/trace_pressure_scanner \
  --mapper /path/to/accepted_l2_mapper_cli \
  --mapper-identity-json /path/to/mapper_identity.json \
  --trace-root /path/to/qualified-trace \
  --kernel-sequence /path/to/full-kernel-sequence.tsv \
  --sidecar /path/to/ORACLE_QWEIGHT_L2_SIDECAR.tsv \
  --sidecar-sha256 6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6 \
  --analysis-root /fresh/output/root \
  --workers 16 --require-kernel-count 4515
```

The mapper interface is intentionally narrow:

```text
accepted_l2_mapper_cli map --input-lines-u64 FILE --output-tsv FILE
```

The TSV must have `line_address_hex`, `subpartition`, and `set_index` columns
and preserve input order.  `--skip-mapper` supports scanner-only qualification.
Use `--start/--stop` for bounded smoke chunks. Formal scans require a fresh
analysis root; resumable reuse is deliberately rejected to avoid provenance
mixing after a scanner, sidecar, mapper, sequence, or trace identity change.

## Tests

`python3 test_trace_pressure.py` builds the scanner and tests exact decoding,
space exclusions, target/prefix/suffix accounting, malformed-mask failure,
the mapper contract, set-histogram closure and top-level orchestration.

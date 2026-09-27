# Accepted RTX4080 L2 mapper

This helper maps `MODELED_L2_GET_ADDR` numeric addresses to the accepted
RTX4080-model L2 `(subpartition, set)` pair. It is an offline characterization
tool; it does not simulate cache hits, misses, traffic, replacement, or timing.

The implementation intentionally contains no copied address-mapping or XOR
formula. The build compiles and calls the accepted Core implementations:

- `linear_to_raw_address_translation::addrdec_tlx` for subpartition;
- `l2_cache_config::set_index`, including its `partition_address` step, for set;
- `bitwise_hash_function` through the configured `X` set-index path.

`build_accepted_l2_mapper.sh` fails closed unless Core is exactly
`a2322069b9701597db7019080b5b54d29518e3a2` and the accepted RTX4080 config
SHA-256 is exactly
`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`.
It extracts all mapper parameters from that verified config and generates build
metadata outside the repository.

Build and test:

```bash
util/vm_tlb/c16/e1_trace_pressure/test_accepted_l2_mapper.sh
```

Batch use:

```bash
mapper=$(util/vm_tlb/c16/e1_trace_pressure/build_accepted_l2_mapper.sh)
printf '%s\n' 0x7ea94e000000 0x7ea906000000 | "$mapper" map
```

Input accepts decimal and `0x`-prefixed addresses, whitespace separated, with
`#` comments. Standard output is TSV with columns `line_address_hex`,
`subpartition`, and `set_index`; provenance is printed on standard error.

The compact-summary integration mode consumes sorted little-endian `uint64_t`
128B line addresses and writes TSV directly:

```bash
"$mapper" map --input-lines-u64 UNIQUE_LINES.u64le --output-tsv LINE_MAP.tsv
```

This mode fails on a partial trailing record, an unaligned address, or a
descending address. Duplicate adjacent lines are accepted. Use `--no-header`
for a headerless stream, `--provenance` for machine-readable build identity,
and `--self-test` for the L0/L14/L27 nine-point canary.

The source namespace is frozen as `MODELED_L2_GET_ADDR` with
`IDENTITY_NUMERIC_NO_ADDRESS_REWRITE`. Reusing this mapper after a non-identity
address transform or with another Core/config pair is invalid and fails the
documented authority boundary.

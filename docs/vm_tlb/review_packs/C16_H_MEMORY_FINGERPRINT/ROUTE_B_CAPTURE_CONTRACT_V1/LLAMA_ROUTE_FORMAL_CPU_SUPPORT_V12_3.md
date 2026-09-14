# Llama S0 Route-B/Route-C formal CPU support

`util/vm_tlb/c16/lane_g/llama_route_formal_support.py` is CPU-only and has no
GPU launch path.  Every command is no-overwrite and fail-closed.

The fixed identity in every accepted/generated receipt is:

```json
{"gpu":"RTX3090/SM86","model":"meta-llama/Llama-3.2-1B","scenario":"S0/B1/T128/Decode4"}
```

## Route-B after an admissible final selection

1. Generate deterministic all-`GLOBAL && has_mref` `(static_index,mref_ordinal)`
   whitelists from a fresh exact-map index.  The index is
   `C16_ROUTE_B_SELECTED_MAP_INDEX_V1`, hash-closes each map, and requires
   explicit `width_bytes` and `mref_count`:

   ```bash
   python3 util/vm_tlb/c16/lane_g/llama_route_formal_support.py freeze-whitelists \
     --selection FINAL_SELECTION.json --map-index SELECTED_MAP_INDEX.json \
     --output REPRESENTATIVE_WHITELISTS.json
   ```

2. Assign each emitted `request_id:static_index:mref_ordinal` exactly once in
   `C16_ROUTE_B_PARTITION_ASSIGNMENTS_V1`; freeze it:

   ```bash
   python3 util/vm_tlb/c16/lane_g/llama_route_formal_support.py freeze-partitions \
     --whitelists REPRESENTATIVE_WHITELISTS.json --assignments ASSIGNMENTS.json \
     --output FORMAL_PARTITIONS.json
   ```

3. After a bounded capture, validate either the canary or a formal partition.
   Metadata must state the actual serialized JSONL byte count, the exact
   4-GiB cap, and a duration no greater than 20 minutes.  The validator checks
   the producer terminal, event count, zero overflow/drop, stream-global
   sequence, predicate-aware executing lanes, and composite launch/instance
   scope before it writes a PASS receipt:

   ```bash
   python3 util/vm_tlb/c16/lane_g/llama_route_formal_support.py validate-canary \
     --whitelists REPRESENTATIVE_WHITELISTS.json --raw-jsonl RAW.jsonl \
     --terminal TERMINAL.json --metadata METADATA.json --output CANARY.json
   python3 util/vm_tlb/c16/lane_g/llama_route_formal_support.py formal-capture \
     --whitelists REPRESENTATIVE_WHITELISTS.json --raw-jsonl RAW.jsonl \
     --terminal TERMINAL.json --metadata METADATA.json --partitions FORMAL_PARTITIONS.json \
     --partition-id P0 --output FORMAL_CAPTURE.json
   ```

For a formal partition, each event must be in that partition; the validator
uses the exact function mangle in addition to `(static_index,mref_ordinal)`,
so equal static indices in separate exact functions are never conflated.

## Route-C and closeout

`analyze-route-c` consumes only a hash-closed full census
(`C16_LLAMA_S0_FULL_CENSUS_V1`) and a Route-C coverage reference
(`C16_ROUTE_C_PHASE_COVERAGE_V1`).  It reports both phase denominators and
duration coverage; it rejects unrecognized IDs rather than shrinking a
denominator.

`closeout` accepts `C16_LLAMA_MODEL_CLOSEOUT_INPUTS_V1` containing exact
path/SHA/status entries for all ten required stages: `S0_CENSUS`, `Q1`,
`Q2_PREFILL`, `Q2_DECODE`, `CUTLASS_OWNER`, `SELECTION`, `ROUTEB_CANARY`,
`ROUTEB_PARTITIONS`, `ROUTEC`, and `REMOTE_CLOSURE`.  Only then can it write
the fixed `MODEL_TRACE_COMPLETE` string; it cannot write a partial success.

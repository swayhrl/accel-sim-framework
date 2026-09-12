# Source, Changes, and Validation

## Provenance

| Item | Value |
|---|---|
| Framework branch base | `f222e66f49af56cfd4ded671c4a50c6811237cc2` |
| Initial Lane-H implementation | `9530d6074a1c7bfae5cc3f8727b86c3e048a3492` |
| Real-capture admission hardening | `20c5ece86a9fae4a3c83e7722fb2e58bbbc81dfc` |
| Object-map parser | `util/vm_tlb/c16/lane_h/runtime_object_map_v2.py` |
| Fingerprint parser | `util/vm_tlb/c16/lane_h/memory_fingerprint.py` |
| Full tracer interface reviewed | `util/tracer_nvbit/tracer_tool/common.h`, `inject_funcs.cu`, `tracer_tool.cu` |
| Raw data in Git | None; fixtures only |

## Semantic change summary

- Adds conservative V2 runtime range attribution with storage-generation identity, direct release evidence, view/tied-storage handling, grow/replace semantics, and an `UNKNOWN_RUNTIME` default.
- Hardens attribution to a hash-bound, receipt-backed object-map snapshot/cutoff per window. Allocation and view history is time-versioned; unproven temporal placement forces `UNKNOWN_RUNTIME` rather than using final state.
- Adds conservative GLOBAL/LOCAL/SHARED/UNKNOWN_SPACE labeling. Only GLOBAL uses GPU-VA page buckets; SHARED and unknown space cannot be promoted to GPU VA.
- Restricts current order admission to `SET_ONLY`; `TRACEG + LOCAL_STREAM_ORDER` is rejected. Renames line modulo arithmetic to a projection proxy, not a hardware cache-set mapping.
- Adds an exact future memory-only comparison gate but makes no memory-only tool change; the review decision remains `NO_GO`.

## Validation record

| Command | Result |
|---|---|
| `python3 -m unittest discover -s tests/vm_tlb/c16/lane_h -p 'test_*.py' -v` | PASS: 10 directed tests |
| `python3 util/vm_tlb/c16/lane_h/runtime_object_map_v2.py --object-map tests/vm_tlb/c16/lane_h/fixtures/object_map_v2.json --output /tmp/c16-h-object-map-audit.json` | PASS: 7 storage-generation records |
| Review TSV header equivalence against `FINGERPRINT_COLUMNS`, `VALIDATION_COLUMNS`, and `REUSE_COLUMNS` | PASS |
| `python3 -m py_compile util/vm_tlb/c16/lane_h/*.py tests/vm_tlb/c16/lane_h/test_*.py` | PASS |
| `git diff --check` | PASS |

## Raw-log index and open issues

There are no raw GPU traces, NCU reports, or model artifacts in this local pack. G-owned raw inputs must remain external and be indexed by its fixed commit, manifest SHA256, trace SHA256, receipt, size, and terminal status before H consumes them.

Open dependency: a real G committed capture and matching direct runtime object-map receipt are required before emitting any scientific `MEMORY_FINGERPRINTS.tsv` data rows, cross-window dynamic conclusions, or C16-5 claims.

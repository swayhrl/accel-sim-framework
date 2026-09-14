# Source, Changes, and Validation

## Provenance

| Item | Value |
|---|---|
| Framework branch base | `f222e66f49af56cfd4ded671c4a50c6811237cc2` |
| Initial Lane-H implementation | `9530d6074a1c7bfae5cc3f8727b86c3e048a3492` |
| Real-capture admission hardening | `20c5ece86a9fae4a3c83e7722fb2e58bbbc81dfc` |
| Mixed-domain validation preservation | `20701d2119dccd98351098fcbdbd12f6c48f396f` |
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
| `python3 -m unittest discover -s tests/vm_tlb/c16/lane_h -p 'test_*.py' -v` | PASS: 13 directed tests, including RAW_CTA prefix/active-mask and 32B/64B three-way-overlap fixtures |
| `python3 util/vm_tlb/c16/lane_h/runtime_object_map_v2.py --object-map tests/vm_tlb/c16/lane_h/fixtures/object_map_v2.json --output /tmp/c16-h-object-map-audit.json` | PASS: 7 storage-generation records |
| Review TSV header equivalence against `FINGERPRINT_COLUMNS`, `VALIDATION_COLUMNS`, and `REUSE_COLUMNS` | PASS |
| `python3 -m py_compile util/vm_tlb/c16/lane_h/*.py tests/vm_tlb/c16/lane_h/test_*.py` | PASS |
| `git diff --check` | PASS |
| Recovery-V2 six-raw RAW_CTA canary | PASS: 3×8192 Prefill and 3×64 Decode target records; 21 pairwise and 7 three-way Decode set rows |

## Raw-log index and open issues

There are no raw GPU traces, NCU reports, or model artifacts in this local pack. G-owned raw inputs must remain external and be indexed by its fixed commit, manifest SHA256, trace SHA256, receipt, size, and terminal status before H consumes them.

Open dependency: a real G committed capture and matching direct runtime object-map receipt are required before emitting any scientific `MEMORY_FINGERPRINTS.tsv` data rows, cross-window dynamic conclusions, or C16-5 claims.

## Llama S0 V1 exploratory addition

`LLAMA_S0_V1/` indexes two retained M4A Llama NVBit 1.7.6 TRACEG inputs by
raw SHA and analyzes explicitly selected GLOBAL `LDG.E.U16` PCs.  The raw
headers and historical workload manifests establish a real B8/T64/TP4 Llama
capture, but not C16 S0 B1/T128/Decode4 provenance.  The pack consequently
uses `EXPLORATORY_HISTORICAL_CAPTURE`, `UNKNOWN_RUNTIME`, and `SET_ONLY` only.
It records absent Decode2/3/4 as `NOT_AVAILABLE`; it does not backfill or
promote the results to this pack's formal canonical tables.

## Llama S0 formal Recovery-V2 addition

`LLAMA_S0_FORMAL_V1/` consumes the immutable Recovery-V2 publication at
`2e955e007bcabcd3ec24a5f9d24768d27caaee27`. Its committed
`PUBLISH_MANIFEST.json` has SHA256
`0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc`.
The six raw payloads are intentionally external to Git but are copied without
deleting producer sources to `/root/share/c16_recovery_v3/.../formal/`; source
and destination SHA256/size receipts are in `FORMAL_RAW_INDEX.tsv`.

The existing parser already decodes the frozen `RAW_CTA` record grammar. The
Llama selected-PC analyzer now consumes an explicit trace format so that its
CTA/warp prefix cannot be mistaken for a PC, validates the expected opcode,
and emits 32B/64B plus three-way set-overlap relations. A synthetic RAW_CTA
fixture covers active-mask lane reconstruction and target-PC selection.

No raw trace is committed. Formal admission applies only to the six selected
targets and their stated structural metrics. Object attribution remains
`UNKNOWN_RUNTIME`, and the pack makes no physical address, temporal reuse,
TLB, cache, or whole-model claim.

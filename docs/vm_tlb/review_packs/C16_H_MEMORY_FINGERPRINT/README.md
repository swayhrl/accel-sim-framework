# C16 H — Memory Fingerprint Review Pack

Status: `C16_H_MEMORY_FINGERPRINT_READY_FOR_REVIEW` for the local C16-0.5/C16-0.8 deliverables. Dynamic C16-4.5 through C16-5.5 findings are deliberately `PENDING_G_COMMITTED_CAPTURE`, not inferred from fixtures.

This is the sole entry point for review.

## Source anchors

- C16-H branch base: `f222e66f49af56cfd4ded671c4a50c6811237cc2`.
- Local implementation commit: `9530d6074a1c7bfae5cc3f8727b86c3e048a3492` (`vm: add C16 H object-map and memory fingerprint tools`).
- Frozen full-tracer interface reviewed: `util/tracer_nvbit/tracer_tool/{common.h,inject_funcs.cu,tracer_tool.cu}` at that implementation commit. The parser supports that tracer's list/base-stride/base-delta address formats.
- Detailed source/change/test record: `SOURCE_AND_CHANGELOG.md`.

## Delivered local gates

| C16 stage | Status | Evidence |
|---|---|---|
| C16-0.5 Runtime Object Map V2 | PASS | `OBJECT_MAP_V2_SPEC.md`; object-map fixture and directed tests |
| C16-0.8 parser/fingerprint fixtures | PASS | `OFFLINE_TOOL_TESTS.tsv`; `FINGERPRINT_VALIDATION.tsv` schema |
| C16-4.4 memory-only observer | NO_GO | `MEMORY_ONLY_AUDIT.md`; full tracer remains the fallback |
| C16-4.5 address fingerprint | PENDING_G_COMMITTED_CAPTURE | manifest/SHA-bound CLI and empty, non-scientific output schemas |
| C16-4.6 reuse/order | PASS_FOR_SET_OVERLAP_ONLY | `ORDER_MODEL_AUDIT.md`; global-L2-order metrics are unavailable |

## What the code guarantees

- `util/vm_tlb/c16/lane_h/runtime_object_map_v2.py` validates directly observed allocation/view/grow/replace/release events and only accepts `WEIGHT`, `QUANT_METADATA`, `KV_CACHE`, and `UNKNOWN_RUNTIME`.
- `util/vm_tlb/c16/lane_h/memory_fingerprint.py` decodes every active lane from the NVBit mask and width, handles list/base-stride/base-delta encodings, classifies read/write/atomic, accounts for 4KiB/64KiB VA buckets and 128B lines, and accepts an incomplete final record only for a manifest-declared `BOUNDED_PARTIAL` capture.
- The fingerprint CLI refuses an unpinned manifest, mismatched trace SHA, absent identity fields, and a CTA-file-order claim. It emits structural metrics with `address_domain=GPU_VA_OBSERVED`.
- Per-object metrics are exact only for lane-request and observed-VA structural semantics stated in the output schema. They are not hardware TLB misses, hardware page-size facts, PA locality, bytes transferred by a cache, or a global L2 reuse curve.

## Consuming G data

H consumes only a G committed/exchanged `c16-trace-manifest-v1` plus the manifest SHA recorded in G's receipt. Each entry must bind run/deployment/scenario/phase/kernel identity, trace path+SHA, capture/terminal state, source receipt, trace format, tool version, and `GPU_VA_OBSERVED` domain.

```bash
python3 util/vm_tlb/c16/lane_h/memory_fingerprint.py \
  --trace-manifest /workspace/c16_exchange/imports/TRACE_MANIFEST.json \
  --expected-manifest-sha256 <G-published-manifest-sha256> \
  --object-map /workspace/c16_exchange/imports/RUNTIME_OBJECT_MAP_V2.json \
  --output /workspace/c16_exchange/imports/MEMORY_FINGERPRINTS.tsv \
  --validation-output /workspace/c16_exchange/imports/FINGERPRINT_VALIDATION.tsv \
  --reuse-output /workspace/c16_exchange/imports/REUSE_AND_OVERLAP.tsv
```

No live G directory is a scientific input. A missing hash, wrong target identity, or a mutable/non-committed manifest is a refusal condition.

## Review files

- `OBJECT_MAP_V2_SPEC.md` — runtime evidence and conservative object boundaries.
- `MEMORY_ONLY_AUDIT.md` — the current explicit NO_GO decision.
- `ORDER_MODEL_AUDIT.md` — legal set/local-order metrics and forbidden claims.
- `OFFLINE_TOOL_TESTS.tsv` — commands and exact fixture coverage.
- `MEMORY_FINGERPRINTS.tsv`, `FINGERPRINT_VALIDATION.tsv`, `REUSE_AND_OVERLAP.tsv` — versioned schemas intentionally empty until qualified G capture arrives.
- `C16_H_STATUS.tsv` — gate ledger and external dependency.

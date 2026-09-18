# CODEX RESUME — 109 Q05 Prefix LDC.U8 Semantic Recovery V1

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_PREFIX_LDC_U8_SEMANTIC_RECOVERY_V1`

Node:

`109 / RTX4080`

## Start point

Read coordination branch:

`hrl/awma-q05-prefix-ldc-recovery-handoff-v1`

Then read:

- `docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md`
- `docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md`
- `docs/vm_tlb/chatgpt_handoff/awma/Q05_CONTIGUOUS_PREFIX_CAPTURE_CONTRACT_V1.md`
- this resume file.

Execution parent:

```text
hrl/awma-q05-contiguous-prefix-capture-109-v1
78f153eb8da6e8e54467382d655f2a55d3eb43fa
```

Recommended branch:

`hrl/awma-q05-prefix-ldc-recovery-109-v1`

The existing P34 raw capture is diagnostic but valuable and MUST be preserved:

`/data/c16/awma/q05_prefix_v1/p34_formal_20260918T013000Z/raw`

Do not recapture merely because the frozen validator rejected member 2.

## Accepted evidence before recovery

R1 single-Q05 regression: PASS.

R2 launches 33->34 same-context canary: PASS.

P34 producer lifecycle produced all 35 members in one CUDA context:

`ctx_0x5b5ba0bd1a60`

All 35 members have terminal COMPLETE with:

- device_reported = receiver_accepted = raw_records;
- drop_count = 0;
- overflow_count = 0.

Member 2 alone was the first frozen-validator failure:

`TRACEG_GRAMMAR_REJECT: memory opcode has zero/missing width: LDC.U8`

No member was skipped and no node164 formal bundle was admitted.

## Scientific/source diagnosis to verify before editing

This stage must first reproduce and document the following accepted-source chain.

### Producer

In the accepted Route-B instrumentation path, operand collection explicitly ignores constant operands and sets `is_mem=1` only when NVBit exposes an `MREF` operand.

Therefore an LDC instruction with no MREF is emitted as a non-address-bearing record by the frozen producer path, with memory-width field 0.

The raw formatter's `opcode_width_bytes()` can decode `.U8` as one byte, but it is only used when `packet.is_mem` is true. Do not infer that the observed raw record should be rewritten to width 1.

### Frozen Accel-Sim opcode/parser semantics

Accepted `gpu-simulator/ISA_Def/ampere_opcode.h` states:

```cpp
// For now, we ignore constant loads, consider it as ALU_OP, TO DO
{"LDC", OpcodeChar(OP_LDC, ALU_OP)},
```

Accepted `trace_parser.cc` creates `memadd_info` only when the serialized memory-width field is >0. Width 0 therefore intentionally leaves `memadd_info == NULL`.

Accepted `trace-driven/trace_driven.cc` has an explicit `OP_LDC` path:

```cpp
case OP_LDC:
  data_size = 4;
  memory_op = memory_load;
  const_cache_operand = 1;
  space.set_type(const_space);
  cache_op = CACHE_ALL;
  break;
```

Thus the current simulator has a pre-existing constant-load approximation that can execute LDC without trace-provided dynamic address/width payload.

Important: this frozen simulator behavior hardcodes `data_size=4`; this stage MUST NOT claim that `LDC.U8` is being modeled as a true 1-byte constant load.

## D0 — Raw evidence audit

Before modifying validator source:

1. inspect the actual member-2 raw and traceg records around every `LDC.U8`;
2. count occurrences;
3. prove whether each rejected LDC record has width 0 and no serialized address payload;
4. verify there is no missing/corrupted record boundary;
5. verify member 2 terminal receipt and xz integrity;
6. record the exact member-2 kernel identity from the accepted sequence.

Output:

`LDC_U8_REAL_RECORD_AUDIT.md`

## D1 — Narrow validator semantic repair

Repair only the strict admission validator.

Preferred rule:

- preserve `access_kind(LDC)=READ`;
- preserve `memory_space(LDC)=CONSTANT`;
- add a narrow exact-base-opcode exception allowing width 0 / no dynamic address payload for `base_opcode == "LDC"` under the frozen producer/parser contract.

Do NOT:

- make all `LD*` width-zero records legal;
- invent width=1;
- invent constant addresses;
- modify raw or traceg records;
- modify `gpu-simulator/trace-parser/trace_parser.cc`;
- modify `gpu-simulator/trace-driven/trace_driven.cc`;
- change the accepted simulator binary/config semantics;
- broaden to `ULDC` or another opcode unless a real later failure occurs and accepted source proves an equivalent implicit/non-address-bearing parser contract.

The existing exact `LDGDEPBAR` validator exception remains unchanged.

## D2 — Compiled regression fixtures

Build the strict validator against the repository-authoritative frozen trace parser.

Required compiled fixtures:

1. `LDC.U8`, width 0, no address -> PASS.
2. actual member-2 LDC representation -> PASS.
3. `LDG.E.32`, width 0 -> FAIL.
4. `LDGSTS`, width 0 -> FAIL.
5. ordinary valid address-bearing load/store -> PASS.
6. missing-address address-bearing load -> FAIL.
7. existing LDGDEPBAR control fixture -> PASS.

Run the full existing consumer/grammar test suite.

Add a source-backed note that passing LDC width 0 means "accepted by the frozen implicit constant-load representation", not "the width is scientifically known to be zero".

## D3 — Reuse existing P34 capture first

The 35/35 raw capture already has the required same-context terminal closure.

Therefore, after validator repair:

1. do NOT immediately use the GPU;
2. postprocess any members that do not already have canonical traceg;
3. run the repaired strict validator over all 35 members in order;
4. produce a complete `MEMBER_VALIDATION.tsv`.

If all 35 pass, the existing P34 raw execution may be promoted without recapture, provided:

- all raw member hashes are closed;
- exact order 0..34 is unchanged;
- all members share the same CUDA context;
- every terminal receipt remains zero-drop/zero-overflow;
- no raw member was modified;
- postprocessing is deterministic/canonical;
- the only scientific admission change is the source-backed validator classification.

Record:

`P34_PROMOTION_WITHOUT_RECAPTURE_AUDIT.md`

If another validator failure appears later in the 35-member sequence:

- ordinary parser/build/index bugs are solve-and-continue;
- a new opcode may be repaired without another ChatGPT round only when accepted source **unambiguously** proves the same kind of implicit/non-address-bearing representation and the repair is exact-opcode/narrow with compiled fixtures;
- otherwise STOP_FOR_SCIENTIFIC_REVIEW.

## D4 — Page-overlap analysis after all-member validation

Only after all 35 members pass grammar.

Derive Q05 predecessor overlap from the same-run validated context traces.

Keep translation-relevant address scope source-backed and consistent across all members. Do not include shared/constant/control records merely because they contain opcode text.

Report separately:

```text
P1
P2
P4
P8
P16
P34
```

for both 4KiB and 64KiB page identities:

- Q05 page count;
- predecessor-union page count;
- intersection;
- Q05 coverage fraction;
- nearest predecessor position for overlapping Q05 pages where well-defined.

These are trace-address overlap metrics, not hardware TLB-residency measurements.

Preserve the historical native/offline VPN vs simulator-key identity-domain boundary.

## D5 — Formal context-bundle closure and node164 publication

If D3/D4 pass, package the existing P34 execution as the formal 35-member same-run context bundle.

Required:

- 35 members exactly, ordered 0..34;
- same CUDA context receipt;
- expected/observed sequence table;
- per-member raw+traceg SHA;
- terminal receipts;
- validator receipts;
- producer/build/runtime receipt;
- page-overlap tables;
- bundle manifest/hash root.

Publish through the already-qualified node164 partial -> verify -> admit -> ACK data plane.

Do not overwrite the old isolated Q05 SIM_INPUT identity.

Do not create warm-prefix simulation results on node109.

## D6 — GPU recapture policy

GPU recapture is a fallback only.

Recapture the full P34 context only if:

- the existing raw directory is missing/corrupted;
- terminal/member hashes cannot be closed;
- the multi-kernel producer itself must change in a way that changes raw scientific semantics;
- or promotion provenance cannot prove the existing execution satisfies the formal contract.

If recapture is required, repeat R1/R2 before P34.

Otherwise, reuse the current complete raw execution.

## Required deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_PREFIX_LDC_U8_RECOVERY_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_PREFIX_LDC_U8_RECOVERY_109_V1/`

At minimum:

- README.md
- SOURCE_ANCHORS.md
- LDC_U8_REAL_RECORD_AUDIT.md
- LDC_U8_SIMULATOR_SEMANTICS.md
- VALIDATOR_PATCH_BOUNDARY.md
- COMPILED_FIXTURE_RESULTS.md
- FULL_TEST_RESULTS.txt
- MEMBER_VALIDATION.tsv
- P34_PROMOTION_WITHOUT_RECAPTURE_AUDIT.md
- PAGE_OVERLAP_4K.tsv
- PAGE_OVERLAP_64K.tsv
- Q05_PAGE_PREDECESSOR_DISTANCE.tsv
- CONTEXT_BUNDLE_RECEIPT.json
- TRANSFER_ACK.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Success marker:

`AWMA_Q05_PREFIX_LDC_U8_SEMANTIC_RECOVERY_V1_COMPLETE_WITH_SCOPE`

If source audit contradicts the narrow repair or the real record requires fabricated address/width semantics:

`STOP_FOR_SCIENTIFIC_REVIEW`

Then commit -> push -> remote verify -> clean worktree -> release GPU lock if held -> STOP.

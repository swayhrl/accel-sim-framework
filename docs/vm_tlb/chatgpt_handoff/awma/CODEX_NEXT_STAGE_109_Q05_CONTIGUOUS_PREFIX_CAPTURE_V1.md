# CODEX NEXT STAGE — 109 Q05 Contiguous Prefix Capture V1

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_CONTIGUOUS_PREFIX_CAPTURE_109_V1`

Node: 109 / RTX4080.

## Start point

Read coordination branch:

`hrl/awma-q05-contiguous-prefix-warm-replay-handoff-v1`

Read:

- `CURRENT_STATE.md`
- `DISCUSSION_REFERENCE.md`
- `Q05_CONTIGUOUS_PREFIX_CAPTURE_CONTRACT_V1.md`
- `CODEX_NEXT_STAGE.md`

Execution parent:

```text
hrl/awma-q05-native-context-109-v1
64a2e51943a6737b84132bc7daa5f4d7c74f8099
```

Recommended branch:

`hrl/awma-q05-contiguous-prefix-capture-109-v1`

## Objective

Replace the rejected lightweight page observer with one formal same-run simulator-native context bundle containing the exact frozen Prefill launch sequence 0..34, where launch 34 is Q05.

Do not run NCU, mechanism experiments, Qwen3/DeepSeek or LDC.U8 side-lane work.

## A0 — Freeze sequence authority

Use the accepted:

`Q05_PREDECESSOR_SEQUENCE.tsv`

Re-run a lightweight launch census only if needed to prove the exact frozen run still emits the same ordered function/grid/block sequence 0..34.

Fail closed on mismatch.

## A1 — Audit accepted Route-B single-target lifecycle

Base producer semantics on:

`5143b4e10aaf2fc47bb60492155d2464b0b726fd`

Document the current single-target assumptions, including:

- global terminal flag after the sole selected target;
- writer state UNOPENED->OPEN->TERMINAL_ACKED->CLOSED;
- persistent per-context channel/receiver;
- per-kernel flush/drain;
- instrumentation disable after selected target.

Design the smallest extension that captures multiple sequential selected kernels while preserving the official NVBit 1.7.7.1 context/channel/receiver lifecycle.

No callback-time channel destroy/recreate.

Output: `MULTIKERNEL_PRODUCER_DESIGN.md`.

## A2 — Implement multi-member capture mode

Add an opt-in contiguous-range mode. Default one-target mode must remain unchanged.

For multi-member mode:

- select exactly launches 0..34 only after each runtime launch matches the expected ordered sequence;
- keep one context/channel/receiver alive across all members;
- close one trace member after its kernel terminal;
- reset only the writer/member counters needed to arm the next member;
- do not set global capture terminal until Q05/member34 closes;
- disable instrumentation for a completed member function only if doing so cannot suppress a later required occurrence; otherwise preserve exact per-launch gating;
- record one sequence receipt with context identity and member order.

Do not alter raw record grammar/formatter semantics.

## A3 — Regression gates

Gate R1: accepted one-target Q05 mode.

Require:

- exact Q05 identity;
- 13,490,624 raw records unless a source-backed reason proves otherwise;
- terminal COMPLETE;
- drop=0;
- overflow=0;
- mode2=0;
- frozen validator PASS.

Gate R2: two-member same-run canary = launches 33..34.

Require:

- same CUDA context;
- exact sequence identities;
- two separate terminally closed raw/traceg members;
- both validator PASS;
- no host abort/deadlock;
- natural host/workload continuation after Q05 capture closes.

If either gate fails, solve routine lifecycle bugs only if trace semantics stay unchanged. Stop on any need to weaken semantics.

## A4 — Formal full-prefix capture

Capture exact launches 0..34 in one frozen execution.

Bounds:

- max 35 selected members;
- 16 GiB compressed bundle;
- 45 minutes.

Every member must have:

- exact function/grid/block identity;
- raw record count;
- terminal receipt;
- zero drop/overflow;
- mode2=0;
- canonical traceg;
- validator PASS.

One unsupported interior member blocks formal admission. Do not skip it.

## A5 — Offline page/context characterization from the formal bundle

Without new GPU execution, derive per-member global-memory page sets using one consistent extraction rule.

Report both 4KiB and 64KiB identities.

Compute P1/P2/P4/P8/P16/P34 predecessor-union overlap against Q05 and nearest predecessor-kernel distance for each overlapping Q05 page where well-defined.

Do not report page overlap as TLB residency.

## A6 — Publish to node164

Package as one immutable context bundle with at least:

- sequence manifest;
- ordered kernelslist;
- all raw + traceg members;
- per-member target identity and terminal/validator receipts;
- same-context/address-context receipt;
- page-overlap tables;
- producer/build/runtime receipt;
- bundle manifest + SHA root.

Publish via the qualified node164 data plane and independently verify destination/ACK.

Do not create the old single-kernel SIM_INPUT identity.

## Required deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_CONTIGUOUS_PREFIX_CAPTURE_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_CONTIGUOUS_PREFIX_CAPTURE_109_V1/`

At minimum:

- README.md
- SOURCE_ANCHORS.md
- MULTIKERNEL_PRODUCER_DESIGN.md
- WORKLOAD_IDENTITY.json
- EXPECTED_SEQUENCE.tsv
- OBSERVED_SEQUENCE.tsv
- MEMBER_STATUS.tsv
- PAGE_OVERLAP_4K.tsv
- PAGE_OVERLAP_64K.tsv
- Q05_PAGE_PREDECESSOR_DISTANCE.tsv
- CONTEXT_BUNDLE_RECEIPT.json
- TRANSFER_ACK.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Expected success marker:

`AWMA_Q05_CONTIGUOUS_PREFIX_CAPTURE_109_V1_COMPLETE_WITH_SCOPE`

Then commit, push, remote verify, clean worktree, release GPU lock and STOP.

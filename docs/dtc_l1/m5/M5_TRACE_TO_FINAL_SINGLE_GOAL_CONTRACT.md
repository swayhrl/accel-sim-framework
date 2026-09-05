# M5 trace-to-final single persistent Goal contract

Status: **ACTIVE — M5_0BT_CAPTURE_PACKAGE_V100_READY; WAITING_FOR_CAPTURE_HOST**

This active-branch contract revalidates the isolated review input
`M5_SINGLE_GOAL_TRACE_TO_FINAL_REVIEW.md@eeaba7375e5895c531b30b07e02095610b5b52d7`.
It supersedes only stale transition wording; it preserves historical evidence.

## Frozen authority

- V100/SM7-style 80 SM; global lower cap 10240; 128 credits/SM.
- `-gpgpu_l1_cache_write_ratio 0`; 80-SM/cap-256 is historical
  `CURRENT_INVALID_SUSPECT` only.
- Trace is formal only after M5.0BT representative qualification. A
  source-backed workload-local exception does not revert other workloads.

## Continuous state machine

`T0_CAPTURE_CONTRACT_REPAIR -> T1_V100_PREFLIGHT_BICG_CAPTURE ->
T2_BICG_TRACE_REPLAY_QUALIFICATION -> T3_GESUMMV_SECOND_QUALIFICATION ->
T4_REMAINING_PAPER_TRACE_CAPTURE_TRANSFER -> M5.0BT -> M5.0C -> M5.0D ->
M5.0E -> MAIN_MATRIX_PARALLEL_ACQUISITION -> M5.1 -> M5.2 ->
PARALLEL_{M5.3,M5.4,M5.5,E2}_ACQUISITION -> M5.3 -> M5.4 -> M5.5 -> M5.6
-> E3 -> M5.COMPUTE_FREEZE -> M5.12 ->
M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`.

T0 is PASS: workload specifications, conditional CLI/source checks, immutable
bundle/archive/transfer recovery, storage admission, source TSV, host handoff,
and SIM_HOST orchestrator have passed no-GPU regression.
At every ordinary problem use: observe, reproduce, classify, source/trace/config
investigate, repair or reconstruct, regress, invalidate affected identity, resume.
Do not pause at a normal stage transition or one workload-local failure.

## Payload-aware formal identity

Every replay result uses:

`{core_sha, framework_sha, config_sha256, execution_payload_kind,
workload_source_sha, input_sha256, payload_identity, parser_schema}`.

For TRACE, `payload_identity` includes `TRACE_BUNDLE_ID`, capture-result
manifest hash, `kernelslist.g` hash, traceg-set hash, tracer-source hash and
trace format. PTX execution exceptions retain binary/PTX/runtime identity.
One triplet may never mix payload kinds or trace bundle IDs.

## Execution and scheduling

M5.0BT captures BICG first, measures raw/grouped/archive bytes and compression,
checks destination space, then admits the remaining resumable Paper queue.
Bundles are transferred only after archive SHA and destination SHA match, and
are stored once in an immutable shared replay store.

After M5.0E, acquire all eligible Paper Base/IO/OO rows through a dynamic
worker pool; M5.1 analysis closes before M5.2 analysis, but acquisition is not
serialized. After M5.2, M5.3/M5.4/M5.5 and Extended E2 acquire concurrently.
Before each wave measure CPU, p95 RSS, memory, swap, trace I/O and disk; derive
and refill `N_safe` rather than retain a conservative fixed worker count.

## Acceptance chain

## Stage-level HARD contract and automatic transition

Each row requires its predecessor PASS, compact registry/review evidence and
an explicit invalidation of any changed identity. `C` means correctness hard;
`F` means fidelity hard. A PASS commits/pushes its handoff and immediately
enters the listed successor; ordinary build, trace, parser, counter, timeout,
negative-performance, or workload-local failure uses the repair lifecycle.

| stage | C/F acceptance and required artifact | reuse / PASS successor |
| --- | --- | --- |
| T0 | capture scripts/tests/config family; `M5_0BT_TRACE_CAPTURE_HANDOFF.md` | none; T1 |
| T1 | V100 UUID/CC, pinned tracer, BICG checker/complete bundle; result manifest | immutable bundle; T2 |
| T2 | BICG same-bundle Base/IO/OO parser/path/drain/conservation; qualification pack | triplet reusable; T3 |
| T3 | GESUMMV contrasting qualification under same rules | reusable; T4 |
| T4 | all Paper exact bundles, hashes, transfer/store verification | payload identities; M5.0BT PASS |
| M5.0BT | Q1 trace formal path valid or documented local exception | capture changes invalidate trace rows; M5.0C |
| M5.0C | 80SM/cap10240 family, payload/geometry/active-SM audit | only exact config reuse; M5.0D |
| M5.0D | Fig4.2/4.7 directed tests, parser schema, timing-neutral proof | parser change invalidates affected parsing; M5.0E |
| M5.0E | ATAX/SpMV/2MM/2DConv same-payload triplets and causal pack | `PILOT_FORMAL_REUSABLE`; M5.1 wave |
| M5.1 | ten valid Base rows and reconciled Fig4.2 | matching Base reused; M5.2 |
| M5.2 | ten same-payload triplets, Fig4.5/4.7/traffic/HOL review pack | activates E2 and sensitivity acquisition |
| M5.3 | 16/32/64 logical-only sensitivity | exact 16K reuse; M5.4 closure |
| M5.4 | approved physical points, source-proven deadlock classification | matching 32K row reuse; M5.5 closure |
| M5.5 | PIB-only 32/64/128/192 sensitivity and HOL analysis | matching rows reused; M5.6 |
| M5.6 | Paper causal classification/review pack | Paper ready; await/continue E3 |
| M5.E1 | 20 source/input/checker/payload eligibility rows | frozen E1 rows; await M5.2 |
| M5.E2 | 60 payload-aware exact triplets/review pack | no sensitivity reruns; E3 |
| M5.E3 | 20 causal classes and Extended aggregates | Extended ready; COMPUTE_FREEZE |
| COMPUTE_FREEZE | M5.6+E3, clean pushed branches, immutable SHAs | freeze prevents rewrite; M5.12 |
| M5.12 | Paper+Extended+graphics-unavailable synthesis/limitations | terminal review state |

- M5.0BT: exact capture identities, BICG+GESUMMV Base/IO/OO replay/drain,
  all ten transferred trace bundles or explicit source-backed local exception.
- M5.0C: frozen cap10240 config family, payload/parser/trace-store identity,
  geometry and active-SM/CTA-wave audit without post-result input tuning.
- M5.0D: frozen Fig4.2/Fig4.7 semantics; capture correctness, trace identity,
  replay terminal and accounting status stay distinct.
- M5.0E: ATAX/SpMV/2MM/2DConv formal triplets or approved local exception.
- M5.1/M5.2: ten Base rows then ten complete same-payload triplets.
- M5.6 + E3: causal classifications and aggregates; then immutable compute
  freeze and M5.12 including accepted graphics-unavailable evidence.

Only exhausted source-backed ambiguity that changes mechanism, formal identity,
approved platform/input meaning, requires a proxy, or makes valid hardware/
storage evidence impossible is a researcher boundary.

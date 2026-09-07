# Window C — SPECULATIVE M4B DEVELOPMENT 当前交接

结论：`C0-C4 PASS；C5 SKIPPED_POLICY；C6 closeout；C7/C8 analysis-only；C9 design-only；C10-A partial；C10-A2 static blocker closure 完成`。

保留标签：`SPECULATIVE_CANDIDATE`、`REFERENCE_APPROX_SUBENTRY_16`。不得作为 target paper 精确复现或正式性能结论。

## 当前 authoritative identity

| 项目 | SHA / 状态 |
|---|---|
| Framework branch | `hrl/vm-m4b-speculative-v0` |
| Framework C10-A2 evidence HEAD | `447ad52cf867e35a616fa16ab12e32b8914f50b9` |
| Core branch | `hrl/vm-m4b-speculative-v0` |
| Core C10-A2 static-closure HEAD | `12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e` |
| Core C10-A starting parent | `c21137bcb86010215c008292f272aacefac175d3` |
| C9 architecture SHA | `04be2899a19b1fe756956dbe5e459494ae1da8df` |

## C9 frozen architecture

- privileged registration, real `PA_base + (VA-VA_base)` mapping;
- N=8 local replicated Segment table, one provisioned ASID;
- `HIT_FIRST / MISS_JOIN`;
- 5/10/20 Segment latency sensitivity;
- pinned immutable inference epoch;
- object map telemetry-only;
- fair standalone sub-entry G96;
- charged Segment+sub-entry G32;
- historical 768-group profile never equal-cost.

## C10-A2 result

Final state:

`C10A2_STATIC_BLOCKERS_CLOSED_COMPILE_AND_RUNTIME_DEFERRED`

Source/static closure completed for:

- transactional semantic registration rejection -> zero live image -> conventional fallback;
- explicit `INACTIVE -> INSTALLING -> ACTIVE -> REVOKING` Segment lifecycle and per-replica acknowledgements;
- production READ/WRITE/ATOMIC classification;
- runtime fair-arm selector for F0-F4/F6-F9, F5 blocked, H0 permanently rejected;
- conventional ASID generation bound to lookup/MSHR/fill and stale-fill/outcome discard after shootdown.

No C10-A/A2 Core has yet been compiled/linked/run after these deltas. No performance result exists.

Remaining C10-B obligations:

- compile/link;
- standard-mode regression;
- focused runtime execution of registration/lifecycle/access/order/generation/fair-arm tests;
- post-delta translation and cross-layer telemetry conservation;
- F5 physical PWC implementation/validation or explicit continued block;
- bounded fair-arm sanity before requesting C5.

Evidence:
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C10A2_NAMED_BLOCKER_STATIC_CLOSURE/`.

## External Window A gate

Window A early C4 reference remains `2e491abec2afb0c745ca26aae0d86f8f35ad096b` and is motivation/observability context only.

C10-B is **not authorized while A C3 is still running**.

A terminal finalization handoff prepares a shared attestation whose first line is exactly:

`A_TERMINAL_CONFIRMED`

Expected path:
`/workspace/m4c-c3-formal-20260905-v1/A_TERMINAL_ATTESTATION.txt`

The attestation proves A terminal status only; C must still pass its own memory/swap/iowait resource gate.

## Prepared next stage

Prepared but self-gated:

`C10B_POST_A_TERMINAL_BUILD_AND_RUNTIME_VALIDATION`

Read:

- `docs/vm_tlb/codex_handoff/spec_m4b/C10B_POST_A_TERMINAL_BUILD_AND_RUNTIME_VALIDATION.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C10B_ACCEPTANCE_MATRIX.md`

Mandatory order:

`compile/link -> standard regression -> focused B2-B7 runtime -> telemetry conservation -> F5 status -> fair-arm bounded sanity -> STOP for review`

C5 does not start automatically even if C10-B passes.

Until A terminal + resource gate, Window C remains frozen: no build, simulator, C5, trace workload, KV segmentation, 12K or M5.
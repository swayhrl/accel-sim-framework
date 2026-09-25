# Baseline frontend source audit

Status: **PASS / VERIFIED_CODE**

Authority: `AWMA_RTX4080_SIM_BASELINE_V1`
`8d1f14a32f5538660d74da86ccb03a2c504c5735`.

The independent-review finding is reproduced: mixed V2 shader SHA256
`1b9c03a...` contains `if (passive_last_result) break;` inside the resident
accessq prelaunch traversal. V2R1 removes that condition. Mixed V2 evidence is
retained unchanged and is used only as `MIXED_INTERVENTION_DIAGNOSTIC`.

The automated audit compares the frozen-V1 and V2R1 frontend control-flow
signatures and records full-file and extracted-block hashes. It verifies:

- reverse iteration remains `entries.rbegin()` to `entries.rend()`;
- applied and cross-page filters retain their order;
- the same address, size, SID, ASID, UID, access type and cycle feed the sole
  fallback prelaunch `translate()` call;
- `ready_application_v2` remains the consume-policy argument and is false in
  this stage;
- READY observation and optional application retain their frozen ordering;
- passive mode has no prelaunch skip, break or extra translation call;
- accounting is observational and adds no `translate()` invocation.

Whole-block hashes intentionally differ because the candidate source also
contains previously accepted C1 branches and V2R1 accounting. The exact
machine-readable checks are in
`/root/awma_passive_last_translation_result_forwarding_v2r1_runtime/frontend_source_audit.json`.

| item | SHA256 |
|---|---|
| frozen V1 `shader.cc` | `b8caf666a367ecd41e09a34bf2caf1c5484fd199948094b877d7366b185fb978` |
| mixed V2 `shader.cc` | `1b9c03aeb2e509529cc27264cddacb21e8bf46a05c38298eb5c15716a110a821` |
| V2R1 `shader.cc` | `bced12fc7d84d4fd4ccec9daa9d2e5ceeb394253db701eef3c61cd00e43d0610` |
| frozen V1 extracted prelaunch block | `d629d0c6c9025d00fecdfc8215d93d39977a570e34d5ae0c8a7813a078faa877` |
| V2R1 candidate/fallback block | `7ca1d3251f7f484c97c6efaec86783810db036f8ec9a3016d9b8c3df2fc1f634` |

Already-launched prelaunch work is not cancelled. On a forwarding hit, an
active lookup or MSHR waiter is detached from architectural application but
continues through the existing finite controller resources to completion.
The controller drains that result without a second downstream application and
without a new port. This support path is required for quiescence; it is not an
additional translation service.

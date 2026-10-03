# Status after R27R1 review

Date: 2026-10-03 (Asia/Shanghai)

This supersedes `STATUS_AFTER_R27R1_AUTHORIZATION_2026-10-03.md` for current AWMA activity.

## Current state

- R27R1 / Lane G / node109: **COMPLETE / STOP**.
- Accepted classification: `R27R1_INPUT_OR_SOURCE_NOT_QUALIFIED`.
- Gate A: PASS, `R27R1_PARENT_AUTHORITY_QUALIFIED`.
- Gate B0: STOP at zero bytes.
- Gate B1 / implementation freeze / Gate C / Gate D: NOT RUN.
- CUDA/JIT: 0.
- GPU lock acquisitions: 0.
- R27 remains closed and unchanged.
- No current AWMA GPU Goal is authorized.

Exact R27R1 result:

- execution commit: `254d66f69ec81bf932add705f721f36255feef2c`
- tree: `ebefec69e9ba153adfaf5d1f7860a956964d09cb`
- exact handoff parent: `ad361be589de85787c3f724582ae1862cb3c3539`

Scientific review:
`../empirical/R27R1_VARIED_BATCH_CAPACITY_REVIEW_2026-10-03.md`

## Blocking dependency

Current AWMA state is:

`WAITING_FOR_EXACT_R27_INPUT_SEED`

The required public scientific payload is still identified by official source metadata:

- file: `wikitext-2-raw-v1/train-00000-of-00001.parquet`
- exact bytes: 6,357,543
- SHA256: `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`

The blocker is transport into an execution/storage environment, not uncertainty about the intended file identity.

Do not open R27R2 merely to repeat server-side URL attempts. First obtain one exact byte copy through an external environment that can reach the public source, verify its SHA/size, and place it into a controlled staging location. Then create a new reviewed continuation whose first action is durable node164 admission and readback; after admission it may continue to bank/numerical qualification, implementation freeze, capacity and positive-only 32-step gates.

## Frozen scientific boundary

R26 remains the latest accepted capacity result, limited to the repeated-sequence tied-W experiment. R27/R27R1 provide no varied-input result and are not negative capacity evidence.

No formal timing, profiler, node174/Accel-Sim, hardware/PPA, production/default change, second corpus/model, all-parameter training or deployment is authorized.

C16 Stage A and DTC-L1 remain separate.

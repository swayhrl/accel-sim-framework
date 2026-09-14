# RTX3090 Campaign Final State

## Frozen scientific state

| Item | Frozen status |
|---|---|
| Q1 | PASS |
| Q2 Prefill | COMPLETE |
| Q2 Decode | COMPLETE |
| Route-A -> Q2 bridge | PASS |
| V2 static map | 34 / 36 exact |
| Two required CUTLASS rows | FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED |
| Representative selection | BLOCKED |
| Representative canary | NOT_AUTHORIZED |
| Formal capture | NOT_AUTHORIZED |

No V0 classification changes any of these facts. RTX4080 is excluded from RTX3090 authority.

## Snapshot

- Git evidence tree: `ec620d9a6227acd934656c4d0c86079820d7a339`.
- Recovery endpoint: `/root/share/c16_recovery_v3`.
- Files inventoried: 4052; bytes represented: 74835853037.
- RTX3090 authority rows: 75. The broader endpoint has 84 receipt/commit-authoritative rows, including excluded other-model material.
- Local files whose SHA256 was intentionally skipped because they exceed `536870912` bytes: 17.
- Llama-looking files lacking exact receipt binding: 17; listed in `UNKNOWN_REVIEW_REQUIRED.md`.

## Major authority paths found

- Immutable authority commits: V12.8 offline review `cbc63026651abb0715a29918915a77726c57b976`; frozen G1 science `ef0d89b1ce297518f86c51cddce190abd47e7364`; recovery/copyback `62428f2cea9ed4cd2def11339311d4347282d9c7`.
- Git frozen authority: `docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/ROUTE_B_Q1_RESULT.json`, `llama_s0_g1_campaign/ROUTE_B_MAP_RESULTS_V2.json`, `C16_ROUTE_A_BRIDGE_REFERENCE_V1.json`, `ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json`, and the CUTLASS closure audit.
- Existing analysis products retained as non-authority analysis context: `Q2_ANCHOR_MEMORY_CHARACTERIZATION_V1.md` and `ROUTE_B_SELECTION_SENSITIVITY_V1.json`. Their conclusions were not reinterpreted.
- Local Q1 raw: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_Q1/q1_tiny_88168889_20260914T072246Z/raw.jsonl`.
- Local Q2 Prefill: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_{DYNAMIC,STATIC_MAP}/...` (dynamic raw has prior SHA closure; it was not rehashed above the V0 threshold).
- Local Q2 Decode: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_Q2_DECODE_{DYNAMIC,STATIC_MAP}/...`.
- Local Route-A formal raw: `/root/share/c16_recovery_v3/raw/llama_3p2_1b/S0/recovery_v2/formal/...`.
- Local V2 map and CUTLASS diagnostics: `/root/share/c16_recovery_v3/raw/llama32_1b/S0/route_b_v2_*` and `ROUTE_B_V122_CUTLASS_OWNER_*`.
- Runtime/model/environment provenance remains in the committed G1 profile/runner receipts and the recovery endpoint's matching G1 receipts; these are inventoried without changing the frozen model/runtime contract.

## Missing or external-only authority

No recovery-defined required raw artifact was regenerated. `POST_RESTART_RECOVERY_RECEIPT_V1` records zero scientific remote-only required files; historical remote paths are therefore recorded as provenance only, not treated as a current local endpoint. The 17 unbound Llama entries remain `UNKNOWN_REVIEW_REQUIRED`, not replacement authority.

## RTX4080 isolation

Path-level RTX4080 matches within the frozen Git tree and recovery endpoint: 0. Separate workspace worktrees observed but not opened, inventoried, or used: /workspace/worktrees/accel-sim-c16-4080-admin-bootstrap, /workspace/worktrees/accel-sim-c16-4080-host-protection, /workspace/worktrees/accel-sim-c16-4080-migration. Other-model files represented in this inventory: 3794; each is excluded from RTX3090 authority.

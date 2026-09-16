# AWMA 174-new — LDGDEPBAR strict-validator hotfix

## Purpose

Repair one consumer-side false rejection discovered by node109 Route-B Q05 canary without weakening the simulator-input contract or changing the simulator binary/baseline.

Accepted starting authority:

- branch: `hrl/awma-sim-consumer-prep-174new-v1`
- commit: `25aa29862239a408099639ae9d5f1a0ea4fee1e1`
- accepted status: `174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1`
- baseline ID: `SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964`

Producer checkpoint proving the conflict:

- branch: `hrl/awma-sim-compat-terminal-recovery-109-v2`
- commit: `e46193b94dd969a988126fc9fa5545da08b26d18`
- review pack: `docs/vm_tlb/review_packs/AWMA_ROUTE_B_BASE_DELTA_RECOVERY_109_V2/`
- producer state: exact Q05 canary COMPLETE, 13,490,624 records, drop=0, overflow=0, mode2=0

This is a CPU-only consumer-validator correction. Do not run simulation in this stage.

## Root cause already reviewed

The accepted strict validator in `util/vm_tlb/awma/simulation/traceg_grammar_smoke.cc` currently uses a lexical heuristic:

```cpp
if (starts_with(base, "LD") || starts_with(base, "TEX") ||
    starts_with(base, "SULD"))
  return "READ";
```

Therefore `LDGDEPBAR` is incorrectly classified as an address-bearing READ and `width == 0` is rejected.

This conflicts with simulator semantics:

- Accel-Sim ISA maps `LDGDEPBAR` to `OP_LDGDEPBAR, ALU_OP`.
- trace-driven code describes `LDGDEPBAR` as the control instruction that groups previous ungrouped `LDGSTS` operations and sets `m_is_ldgdepbar`.
- the frozen simulator `trace_parser.cc` accepts the real Q05 trace with `LDGDEPBAR` encoded as width 0/no address.
- Route-B instrumentation reports no NVBit MREF for `LDGDEPBAR`; producer must not fabricate width/address.

The producer is therefore not to be changed for this opcode.

## Required implementation

Create a fresh implementation branch/worktree from this coordination branch, suggested branch:

`hrl/awma-sim-consumer-validator-ldgdepbar-174new-v1`

Patch only the strict consumer validation semantics needed to distinguish addressless control opcodes from true address-bearing memory opcodes.

Preferred minimal form:

```cpp
bool addressless_control_opcode(const std::string &opcode) {
  const std::string base = base_opcode(opcode);
  return base == "LDGDEPBAR";
}

std::string access_kind(const std::string &opcode) {
  const std::string base = base_opcode(opcode);
  if (addressless_control_opcode(opcode)) return "";
  ... existing rules unchanged ...
}
```

Equivalent structure is acceptable, but the rule must be explicit and source-backed.

Do **not** solve this by any of the following:

- allowing arbitrary `LD*` opcodes to use width 0;
- making `width == 0` automatically non-memory for every opcode;
- adding fake addresses or fake width for `LDGDEPBAR`;
- rewriting `LDGDEPBAR` to another opcode;
- changing workload/target identity;
- changing the simulator binary or simulator ISA semantics;
- changing `SIM_BASELINE_ID`.

## Required regression gates

Add exact positive and negative fixtures/tests.

At minimum:

1. `LDGDEPBAR` with width 0 and no address must PASS the strict validator.
2. `LDG.E.32` (or equivalent real address-bearing global load) with width 0 must still FAIL.
3. `LDGSTS` width 0 must still FAIL unless source evidence proves a specific non-address variant; do not relax it by prefix association with `LDGDEPBAR`.
4. Existing valid memory instructions with width/address remain PASS.
5. Existing malformed width/address negative tests remain FAIL.
6. All pre-existing `test_simulation_foundation.py` tests remain PASS.
7. Build the real `traceg_grammar_smoke` against the repository authoritative `trace_parser.cc` and exercise the new fixtures through the compiled binary, not only helper-level unit logic.

The prior mode-2 base-delta issue is a separate frozen-baseline compatibility limitation. Do not broaden this hotfix into simulator parser replacement. The current Route-B producer already guarantees mode2=0. Record that boundary in the review pack.

## Q05 real-trace cross-check

After the local fixture/test suite passes, publish the hotfix commit. Then node109 will fetch the exact hotfix source and run the newly built strict validator against the already existing Q05 R3 canary trace from producer checkpoint `e46193b94dd969a988126fc9fa5545da08b26d18`.

Do not require 174 to copy or replay the large Q05 artifact for this hotfix unless it is already locally available. The authoritative real-trace cross-check can be performed on 109 using the committed validator source.

## Review-pack requirements

Create:

`docs/vm_tlb/review_packs/AWMA_SIM_CONSUMER_LDGDEPBAR_HOTFIX_174NEW_V1/`

Include at least:

- README with exact claim boundary;
- source diff;
- source/compiled parser SHA256;
- ISA/trace-driven source anchors documenting `LDGDEPBAR` as ALU/grouping control;
- positive `LDGDEPBAR width0` fixture result;
- negative `LDG.E.32 width0` result;
- negative `LDGSTS width0` result;
- full existing unittest result;
- grammar-smoke build command/receipt;
- statement that simulator binary and `SIM_BASELINE_ID` are unchanged;
- statement that producer data was not modified;
- statement that this corrects a false-positive validator classification, not a scientific relaxation of address-bearing memory requirements.

Report:

`docs/vm_tlb/codex_handoff/awma/SIM_CONSUMER_LDGDEPBAR_HOTFIX_174NEW_REPORT.md`

## Success state

Only if every gate passes, report:

`174NEW_SIM_CONSUMER_LDGDEPBAR_VALIDATOR_HOTFIX_PASS`

Then commit, push, and leave the worktree clean.

Do not issue `SIM_INPUT_ID` in this hotfix stage and do not run the 10k current-model simulation yet. After PASS, node109 resumes existing Q05 R3 parser cross-check and formal producer capture/READY closure.
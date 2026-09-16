# AWMA 174-new Goal — first current-model simulator admission and 10k baseline replay

## Goal

Consume the completed node109 simulator-native Q05 producer bundle on 174-new and close the first current-model simulation evidence chain:

```text
producer READY / durable bundle
-> independent destination rehash
-> exact consumer admission
-> stable SIM_INPUT_ID
-> structural trace diagnostics
-> fixed-window 10000-cycle replay
-> bounded repeat / determinism
-> SIM_RUN_ID
-> normalized telemetry
-> SIM_EVIDENCE catalog closure
```

Expected terminal state:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
FIRST_CURRENT_MODEL_BASELINE_SIM_PASS
```

This Goal is simulation admission / baseline replay only. Do not start TLB/PTW/cache/segment mechanism sweeps, Native-vs-Simulation numerical calibration, or full-ROI claims.

## Accepted authorities

### Consumer / validator

Accepted consumer branch / commit:

```text
hrl/awma-sim-consumer-validator-ldgdepbar-174new-v1
fb5d0bebee421a0153661239e1f7c2bc088d5c9e
```

Status:

```text
174NEW_SIM_CONSUMER_LDGDEPBAR_VALIDATOR_HOTFIX_PASS
```

This retains the accepted consumer foundation from `25aa29862239a408099639ae9d5f1a0ea4fee1e1` and adds only the exact `LDGDEPBAR` addressless-control strict-validator correction. The repository-authoritative simulator parser and simulator binary were not changed by that hotfix.

Frozen baseline identity:

```text
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
scope = HASH_BOUND_FIXED_WINDOW_10000
```

Previously qualified simulator binary SHA256:

```text
34deedd99e85e52fb309852de2ecc5fecd9471436a33a5e77d40bc038a2c31c4
```

### Producer

Final producer branch / commit:

```text
hrl/awma-sim-compat-terminal-recovery-109-v2
5143b4e10aaf2fc47bb60492155d2464b0b726fd
```

Producer state:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

Formal producer run:

```text
C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9
```

Durable bundle path:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9
```

Frozen producer hashes:

```text
bundle manifest SHA256 = fb8a5b9d4923610bb7cf1e10931988747b241df9133257cfbc7c2e88509496f3
trace-member hash root = 00fe079c21a68664727a8c3a48f8776e1d98e1146ba26291194e365af18aaa12
terminal receipt SHA256 = 6e6e483e1dbf44bc522f9d0e8b980397df85a6cf1c8d8048360e350caa1cce72
kernelslist raw SHA256 = 674a9c8c0c37027523a91fdcdefa1e690f20012afdb6d05f66e0031837e75602
traceg member SHA256 = be4215cc353070af1843852589a26eaa9d650abfa230086502f078cf96f261f0
address context SHA256 = 24b3e89b19534dbf9d7e9dc81f2a916fc4e079a35e6de37b042309c1375656ca
```

Formal capture facts:

```text
records = 13,490,624
terminal = COMPLETE
drop_count = 0
overflow_count = 0
address mode 2 count = 0
```

Q05 identity remains:

```text
model_id = Qwen/Qwen2.5-0.5B-Instruct
model_revision = 7ae557604adf67be50417f59c2c2f167def9a775
scenario_id = S2_TEXT
input_class = TEXT
phase = PREFILL
batch = 1
prefill_tokens = 2048
decode_tokens = 32
backend = sdpa
dtype = float16
target_id = Q05_PREFILL_ATTN_FLASH
target_function_occurrence = 0
```

R3 was promoted without GPU recapture because the actual execution fulfilled the formal producer contract; its historical `canary` label is not part of the scientific identity.

## Runtime preservation

During the validator hotfix, the pre-existing ~5.3 GB simulation runtime was preserved at:

```text
/root/workspace/awma_runtime_preserved_before_ldgdepbar_hotfix_174new_v1
```

A recoverable stash was also retained.

Do not rebuild the simulator/runtime merely because `.awma_runtime/` is absent from the implementation worktree.

First inspect the preserved runtime and verify the qualified binary/config/tool hashes against the accepted baseline receipts. Prefer using the preserved runtime in-place, or restoring it atomically only if a path-sensitive wrapper actually requires the old location. Do not overwrite or delete the preserved copy. Rebuild only if the preserved runtime fails hash/functional verification, and if that happens treat the rebuild as an engineering recovery that must reproduce the same qualified baseline identity before continuing.

## Execution policy

Use a fresh implementation branch/worktree based on the accepted consumer hotfix commit. Suggested branch:

```text
hrl/awma-first-current-model-replay-174new-v1
```

Use solve-and-continue mode. Once an engineering gate passes, continue directly to the next gate; do not stop for ordinary intermediate milestones.

Fail closed only for a new scientific/semantic identity conflict, an unrecoverable simulator-input incompatibility, or an external hard blocker. Ordinary path/runtime/build/catalog issues must be diagnosed, minimally repaired, regression-tested, documented, and continued.

## Stage A — independent durable-bundle verification

Do not trust the node109 local source tree or its earlier remote ACK as the only admission authority.

Operate on the durable node164 path and independently recompute:

- all file SHA256 values;
- bundle manifest SHA256;
- trace-member hash root;
- kernelslist SHA256;
- terminal receipt SHA256;
- address-context SHA256;
- xz integrity for every compressed trace member.

Verify exact equality with the frozen producer receipts above.

Also verify:

- `COMPLETE`;
- `drop_count == 0`;
- `overflow_count == 0`;
- mode-2 address records remain absent under the accepted frozen-baseline compatibility policy;
- exact workload / target / runtime / launch identity;
- no C16WARP1/MREF reconstruction or Native-to-traceg conversion was introduced.

## Stage B — formal consumer admission and SIM_INPUT_ID

Build the strict grammar validator from exact consumer commit:

```text
fb5d0bebee421a0153661239e1f7c2bc088d5c9e
```

Hash-close validator source and binary.

Run the exact strict validator plus repository-authoritative `trace_parser.cc` against every listed `*.traceg.xz` member from the durable bundle. Preserve parser receipts.

The validator must retain the narrow semantics already reviewed:

- exact `LDGDEPBAR` width-0 / no-address control is accepted;
- true address-bearing `LDG.E.32 width=0` remains rejected;
- `LDGSTS width=0` remains rejected;
- malformed width/address records remain rejected.

Then run the formal consumer admission path in `util/vm_tlb/awma/simulation/simulation_foundation.py` against the durable manifest and exact parser binary.

On PASS, create/catalog the stable `SIM_INPUT_ID` exactly once using the accepted immutable catalog mechanism. Record both the ID and its semantic identity payload. Re-running admission over identical bytes must yield the same ID / NOOP-identical behavior, not a second identity.

Expected status after this stage:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
```

## Stage C — structural trace diagnostics

Before simulation, emit a compact immutable diagnostic receipt covering at least:

- kernel count / listed members;
- CTA count;
- warp structure;
- total dynamic instruction count;
- opcode histogram or a stable summary hash;
- memory access-kind / memory-space counts derived under the accepted semantic rules;
- required control-opcode presence including `LDGDEPBAR` as control, not address-bearing memory;
- address encoding mode counts;
- parser instruction total versus producer record total where definitions are comparable.

Do not reinterpret Native evidence or claim quantitative Native/Simulation calibration here.

## Stage D — restore/verify the fixed 10k simulation baseline

Verify the preserved runtime against the accepted baseline identity before the first current-model replay.

Required baseline identity remains:

```text
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
HASH_BOUND_FIXED_WINDOW_10000
```

Confirm the simulator binary SHA256 is still:

```text
34deedd99e85e52fb309852de2ecc5fecd9471436a33a5e77d40bc038a2c31c4
```

Use the already-qualified base config / VM overlay / telemetry exporter / normalizer / fixed-window wrapper from the baseline receipts. Do not silently substitute another simulator build or config.

If path relocation causes wrapper breakage, repair paths without changing semantic config contents; hash-close the effective command/environment and document the relocation.

## Stage E — first current-model 10k replay

Run the admitted Q05 `SIM_INPUT_ID` against the accepted baseline with exactly:

```text
gpgpu_max_cycle = 10000
claim_scope = FIXED_WINDOW_10000
```

This is not a full-ROI run.

PASS may end at the expected maximum-cycle boundary. Preserve:

- exact command and environment hashes;
- simulator binary/config/overlay hashes;
- stdout/stderr/raw log SHA256;
- execution-status classification;
- normalized telemetry SHA256;
- all VM/TLB/PTW/PWC/cache/memory/queue/stall/performance telemetry produced by the accepted exporter;
- simulator parser/admission status.

Create/catalog the corresponding `SIM_RUN_ID` using the immutable catalog mechanism.

## Stage F — bounded repeat / determinism

Run at least one additional 10k replay under the same admitted `SIM_INPUT_ID`, baseline, config, overlay and runtime environment.

Compare deterministic scientific outputs. At minimum verify equality of:

- execution-status class;
- fixed-window terminal cycle;
- normalized telemetry artifact/hash, unless the accepted normalizer intentionally includes run-local metadata in which case compare the semantic telemetry payload after documented metadata normalization;
- core VM/TLB/PTW/cache/memory metric values;
- parser-visible input identity.

If logs contain timestamps or nondeterministic file paths, do not require raw-log byte identity; distinguish raw-log nondeterminism from scientific telemetry nondeterminism.

A material metric mismatch is not a PASS: diagnose before proceeding.

## Stage G — SIM_EVIDENCE closure

After replay and determinism PASS, create the immutable `SIM_EVIDENCE` record binding:

- `SIM_INPUT_ID`;
- `SIM_BASELINE_ID`;
- accepted `SIM_RUN_ID`;
- raw log SHA256;
- normalized telemetry SHA256;
- `claim_scope = FIXED_WINDOW_10000`;
- formal scientific status.

Close a review pack with source anchors, commands, hashes, parser receipts, replay receipts, determinism comparison and claim boundaries.

Suggested review pack:

```text
docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/
```

Suggested report:

```text
docs/vm_tlb/codex_handoff/awma/FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1_REPORT.md
```

Commit and push the implementation branch and leave the worktree clean.

## Final success state

Only after all stages pass, report:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
FIRST_CURRENT_MODEL_BASELINE_SIM_PASS
```

Include final IDs:

```text
SIM_INPUT_ID
SIM_BASELINE_ID
SIM_RUN_ID
SIM_EVIDENCE_ID
```

and key telemetry/hash receipts.

Then STOP this baseline stage. Do not automatically start mechanism sweeps or Native-vs-Simulation calibration.
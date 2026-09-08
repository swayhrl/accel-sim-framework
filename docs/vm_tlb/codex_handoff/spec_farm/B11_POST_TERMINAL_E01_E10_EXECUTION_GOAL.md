# Window B — Post-terminal E01–E10 execution Goal

Goal: `B11_POST_TERMINAL_E01_E10_EXECUTION_GOAL`

Status: `GOAL_MODE / CONTINUOUS_EXECUTION / RESOURCE_WAIT_IS_NOT_STOP`.

## 1. Goal boundary

Window A C3 is formally terminal. The authoritative external terminal evidence is:

- A progress-review branch: `hrl/vm-llm-m4b-c3-progress-review-20260907`
- A terminal checkpoint: `14edbe200859f6ddf42bc3d459334f184a920a82`
- `C3_FINAL_STATUS = TERMINAL_PASS`
- shared attestation: `/workspace/m4c-c3-formal-20260905-v1/A_TERMINAL_ATTESTATION.txt`
- attestation first line: `A_TERMINAL_CONFIRMED`

The previous pre-terminal `B10_CONCURRENT_E01_CANARY` is superseded and must not be used.

This Goal must carry B continuously through the complete already-frozen B9 execution set **E01–E10**, validate/synthesize the results, commit/push the evidence pack, and then STOP for review. Do not invent E11–E18 or a new research direction in this Goal.

Evidence remains `SPECULATIVE_DIAGNOSTIC`.

## 2. Authoritative B inputs

- repo: `swayhrl/accel-sim-framework`
- branch: `hrl/vm-spec-farm-v0`
- pre-Goal branch HEAD: `11d39dc8936f42b0f7d364cf6581358b63f53c90`
- B9 evidence: `b9119d4dfe0f8c04f432caa2b7974c3ccfc38152`
- B9 pack: `docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT/`
- B simulator SHA-256: `2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915`
- B scratch: `/workspace/vm-spec-farm/`

Strictly reuse B9's:

- `E01_E10_EXECUTION_MANIFEST.tsv`
- `ARM_DELTA_WHITELIST.tsv`
- `EXPECTED_OBSERVABLES.tsv`
- deterministic 16+16 selector
- existing runner/miner contracts

Do not silently change an experiment simply to make it pass.

## 3. Resource policy: transient pressure means WAIT, not STOP

The earlier resource gate was intentionally conservative and treated any positive PSI-full delta as failure. For Goal mode, use a bounded percentage gate instead of requiring an impossible exact zero on a busy 512-logical-CPU host.

For every heavy step, sample a 10-second window and compute:

`full_pct = delta_full_total_us / (10 * 1,000,000) * 100`

Require all of:

- `MemAvailable >= max(64 GiB, MemTotal/5)`;
- `SwapFree >= 512 MiB` when swap exists;
- swap-in delta = 0 and swap-out delta = 0 during the sample;
- memory PSI `full_pct <= 0.5%`;
- io PSI `full_pct <= 1.0%`;
- CPU iowait <= 10%;
- no unexplained host failure state.

The previously observed sub-0.05% PSI-full windows are not, by themselves, a reason to abort.

### Shared heavy-slot lock

Before every simulator run or trace-mining worker, acquire:

`/workspace/vm_tlb_post_terminal_heavy_slot.lock`

using `flock`.

Only one new B/C heavy operation may hold this lock at a time. Do not hold it while merely parsing small TSVs or sleeping. Release it after each coherent heavy job so Window C can make progress.

If the lock is busy or the resource gate fails:

1. record the sample in `RESOURCE_WAIT_HISTORY.tsv`;
2. do only lightweight bookkeeping/analysis;
3. sleep about 5 minutes;
4. retry;
5. **do not terminate the Goal merely because the host is temporarily busy**.

Do not busy-spin. Do not kill, renice, repin, pause, or otherwise manipulate Window A/C processes to obtain resources.

## 4. Resume-safe execution

Implement or adapt a small Goal supervisor so execution is resumable.

Maintain machine-readable state for E01–E10 with at least:

- `NOT_STARTED`
- `RUNNING`
- `PASS`
- `FAILED_DIAGNOSING`
- `INVALID`

Never overwrite a valid completed result.

If an attempt created an incomplete output directory, first prove it is incomplete, then quarantine it under a timestamped `failed_attempts/` area before retrying. Never delete valid evidence to make a rerun possible.

Effective B heavy concurrency remains **1**.

## 5. Execute E01–E10

Run the frozen set in dependency-safe order.

### E01–E06 simulator smoke/control experiments

Execute the exact B9 arms for:

- E01 PWC finite-32
- E02 PWC finite-512
- E03 PWC ideal
- E04 2 MiB page diagnostic
- E05 VM-disabled control
- E06 ideal-translation control

Each arm must preserve B9's delta whitelist and immutable binary/trace/config provenance.

For every simulator arm retain at least:

- exit/status and exact command;
- cycles / IPC;
- L1/L2 TLB hit/miss;
- translation MSHR allocation/merge/full/wait;
- PWQ;
- walker;
- PWC;
- PTE request/response/DRAM/wait;
- realized page/config/profile;
- object Weight/KV/UNKNOWN where available;
- downstream/cross-layer pressure observables available in the existing telemetry.

Do not infer performance from miss rate alone.

### E07–E08 RSS calibration

Run the one-kernel decode and prefill trace-miner RSS calibrations sequentially under the same host lock/resource gate.

Capture `/usr/bin/time -v` evidence and derive the calibrated peak/span inputs required by B9.

### E09–E10 matched static mining

Only after E07/E08 calibration passes, run the deterministic matched 16-kernel prefill/decode mining.

Preserve selector provenance and conservation checks. Do not reinterpret metadata matching as proof of matched dynamic memory behavior.

## 6. Problem-solving policy

The purpose of Goal mode is to finish the task with high quality, not to stop at the first obstacle.

### Transient resource issue

Wait/retry as above. `RESOURCE_DEFERRED` is an intermediate state, not a final Goal status.

### Script/path/config/harness issue

Reproduce -> root-cause -> make the smallest B-local repair -> static/dry-run validate -> checkpoint -> retry.

Do not stop merely because a path moved, a helper is brittle, or the first attempt fails.

### Simulator/miner failure

Inspect the actual log/output, distinguish infrastructure/harness error from an experiment-semantic failure, and attempt a correct repair when it does not alter the frozen experiment semantics.

Do not blindly rerun the identical failing command repeatedly. After repeated identical failure, switch to diagnosis.

### Hard STOP only for

- immutable provenance/binary/trace mismatch that cannot be repaired without changing the experiment identity;
- evidence corruption that makes the requested comparison invalid;
- a required B9 semantic/config contract is internally inconsistent;
- fixing the problem would require modifying Window A/C or changing the scientific question.

Ordinary engineering difficulty is not a hard blocker.

## 7. Result synthesis

After E01–E10 complete, create:

`docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B11_POST_TERMINAL_E01_E10_EXECUTION_GOAL/`

At minimum:

- `INPUT_PROVENANCE.tsv`
- `GOAL_STATE.tsv`
- `RESOURCE_WAIT_HISTORY.tsv`
- `E01_E10_RESULT_MATRIX.tsv`
- `E01_E06_TRANSLATION_AND_PERF.tsv`
- `E07_E08_RSS_CALIBRATION.tsv`
- `E09_E10_STATIC_MINING_SUMMARY.tsv`
- `CONSERVATION_AND_VALIDATION.tsv`
- `HYPOTHESIS_UPDATE.md`
- `ANOMALIES_AND_GAPS.md`
- `NEXT_EXPERIMENT_RECOMMENDATIONS.md`
- `FINAL_REPORT.md`

Update H1–H6 from B8 explicitly as `SUPPORTED`, `WEAKENED`, `UNRESOLVED`, or `FALSIFIED_WITHIN_SCOPE`. Keep smoke/static/full-ROI evidence levels separate.

Do not execute E11–E18 in this Goal. Recommendations may reprioritize them for the next review.

## 8. Commit discipline

Use explicit-path staging only. Never `git add .` or `git add -A`.

Checkpoint coherent harness fixes separately from evidence closeout where practical. Push only B-owned branch changes.

## 9. Final status

Use exactly one final Goal status:

- `B11_E01_E10_COMPLETE_READY_FOR_REVIEW`
- `B11_HARD_BLOCKER_WITH_EVIDENCE`

Do not use `RESOURCE_DEFERRED` as the final status. If resources are temporarily unsuitable, remain in Goal-mode wait/retry until they recover or a genuine hard blocker appears.

STOP after E01–E10 evidence synthesis and push. Do not automatically start E11–E18.
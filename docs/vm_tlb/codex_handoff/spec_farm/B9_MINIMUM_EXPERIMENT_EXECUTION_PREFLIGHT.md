# B9：最小信息实验执行级预检

Goal：`B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT`

状态：`READY_TO_EXECUTE / ANALYSIS_ONLY / SPECULATIVE_DIAGNOSTIC`。

## 1. 目的

B8 已把 1,321 个缺口压缩成 6 个可证伪假设和 18 个高信息量实验 bundle，第一批为 E01--E10。B9 不再讨论“该研究什么”，而是把 E01--E10 变成 A terminal 后可安全、可复现、可机器判定地执行的实验包。

本轮不执行任何 E01--E10，不启动 simulator/worker，不生成 trace，不 rebuild。完成后应能让下一执行轮在不重新解释配置语义的情况下直接按 manifest 启动。

## 2. 冻结输入

Window B authoritative input：
- branch：`hrl/vm-spec-farm-v0`
- B8 HEAD：`3c5700cba44739a9abb2470c863d1942c20e1079`
- B8 minimum set：`docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B8_CROSS_WINDOW_HYPOTHESIS_AND_EXPERIMENT_PRIORITIZATION/MINIMUM_INFORMATION_EXPERIMENT_SET.tsv`
- B7/B8 review packs and current B scratch provenance
- current B simulator binary SHA-256：`2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915`

Window A external read-only checkpoint：
- branch：`hrl/vm-llm-m4b-c3-progress-review-20260907`
- checkpoint：`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`
- seven terminal arms; `prefill-paper` still running at checkpoint

B9 may read only committed A checkpoint files via `git show <sha>:<path>` or remote fetch. It must not access A private scratch/worktree/processes.

## 3. A checkpoint implications that must be reflected in preflight

A is supporting external evidence, not numerically poolable with B. It does, however, change what B9 must observe:

- decode1 disabled and ideal are identical in A terminal evidence;
- decode1 generic is about 3x the disabled/ideal cycles, and paper is about 3.15x;
- decode1 paper has fewer L1/L2 TLB misses and far fewer MSHR-full events than generic, yet is slower;
- prefill generic currently has a much smaller translation penalty than decode generic; prefill-paper was not terminal at checkpoint.

Therefore B9 must not define success using hit/miss rate alone. E01--E06 observables must include queue/stall/resource-pressure metrics such as MSHR-full/PWQ-full, walk/PTE activity, and cycle/IPC outcome. A evidence does not cancel B-local E05/E06; they remain B-local control validation because executable/config contexts differ.

Record the A provenance difference: some completed decode arms were launched before later Framework documentation/exporter commits, but simulator binary/Core/trace-list hashes were unchanged. Do not use A as a B performance baseline.

## 4. Hard resource boundary

B9 is static/preflight only. Forbidden:
- Accel-Sim/GPGPU-Sim execution;
- any B worker;
- trace generation or full trace scan;
- simulator rebuild;
- E01--E10 execution;
- modifying B Core;
- modifying/reading A or C private scratch/worktrees;
- large data copies/decompression.

Allowed:
- source/config/script inspection;
- small manifest/TSV/MD reads;
- command construction;
- config diff/semantic validation;
- shell/Python syntax checks;
- `--dry-run` or equivalent no-execution validation;
- lightweight resource-gate logic validation using synthetic inputs.

## 5. E01--E06 exact simulator smoke preflight

For each E01--E06, freeze:
- experiment ID and hypothesis IDs;
- exact immutable trace/kernel/ROI selection;
- exact baseline arm;
- exact config delta from baseline;
- expected simulator binary/runtime hashes;
- command line and working directory;
- output directory and non-overwrite policy;
- required telemetry fields;
- semantic realization checks;
- PASS / FAIL / INVALID_CONFIG / INCONCLUSIVE criteria.

E01--E06 are:
- E01: decode1 generic baseline vs PWC=32
- E02: decode1 generic baseline vs PWC=512
- E03: decode1 generic baseline vs PWC=IDEAL
- E04: decode1 64KB generic vs valid 2MiB diagnostic
- E05: decode1 translation-disabled diagnostic
- E06: decode1 ideal-translation diagnostic

For every arm, produce an `ARM_DELTA_WHITELIST` showing all intentionally changed config options and proving no unrelated VM/cache/clock/trace option drifts.

The minimum telemetry schema must include when available:
- cycles, IPC;
- translation lookup requests/completions;
- L1/L2 TLB hit/miss;
- MSHR alloc/merge/full;
- PWQ full/enqueue if available;
- walker starts/completions/occupancy if available;
- PWC access/hit/miss;
- PTE requests/responses/DRAM responses/wait latency;
- object Weight/KV/UNKNOWN accounting and conservation;
- realized page size / PWC capacity / control mode.

If a required option or realization check does not exist in current B binary/config, mark that experiment `PREFLIGHT_BLOCKED_CONFIG`, do not patch implementation in B9.

## 6. E07/E08 RSS calibration preflight

Prepare one representative decode miner and one representative prefill miner job with:
- exact input kernel and provenance;
- streaming mode only;
- `/usr/bin/time -v` or equivalent peak-RSS capture;
- MemAvailable before/after;
- swap-in/out window;
- iowait;
- output integrity/hash check;
- no concurrent B high-load worker.

Freeze the admission formula already accepted by B6/B7. Do not lower resource thresholds in B9.

E07/E08 are not executed now.

## 7. E09/E10 matched static-mining preflight

Freeze the exact algorithm for selecting 16 prefill and 16 decode kernels using the same signature-stratification/budget rule.

The selection must be deterministic and auditable. Output:
- selected kernel IDs;
- signature features used for matching;
- unmatched strata and fallback rule;
- immutable trace-list/map versions;
- object-map boundary policy;
- Weight/KV/UNKNOWN mass;
- page/line/sector footprint;
- stride/sequentiality metrics;
- reuse-distance metric or explicit approximation label.

Do not scan the selected traces in B9 beyond tiny metadata needed to verify the selector. Actual E09/E10 mining waits for E07/E08 resource calibration and later execution authorization.

## 8. Execution script requirements

Prepare a script such as:
`util/vm_tlb/run_b9_e01_e10_after_a_terminal.sh`

It must default to dry-run and must NOT execute experiments during B9.

Required safety properties:
- requires an explicit future execution enable flag;
- refuses overwrite of existing evidence directories;
- effective simulator concurrency fixed to 1 for E01--E06;
- E07/E08 one job at a time;
- resource gate before every job;
- persistent swap activity blocks launch;
- preserves B1--B8 scratch/evidence;
- never splits a stateful continuous ROI into per-kernel simulator processes;
- logs exact binary/config/trace hashes and command before execution;
- supports per-experiment start/stop so a failed arm does not erase completed evidence.

B9 should run only shell/Python syntax/static validation and dry-run command rendering.

## 9. Machine-readable result contract

Create a future result schema with at least:
- experiment_id
- arm_id
- evidence_label
- baseline_id
- command_sha256/config_sha256
- binary/runtime/trace hashes
- semantic_realization_pass
- simulator_exit_status
- terminal_count_gate
- resource_gate_snapshot
- requested observables
- missing_observables
- result_class (`PASS`, `FAIL`, `INVALID_CONFIG`, `INCONCLUSIVE`, `RESOURCE_DEFERRED`)
- hypothesis implications

A null metric must be `NOT_AVAILABLE`, never numeric zero.

## 10. Output

Create:
`docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT/`

At minimum:
- `README.md`
- `INPUT_PROVENANCE.tsv`
- `A_CHECKPOINT_IMPLICATIONS.md`
- `E01_E10_EXECUTION_MANIFEST.tsv`
- `ARM_DELTA_WHITELIST.tsv`
- `EXPECTED_OBSERVABLES.tsv`
- `RESULT_ACCEPTANCE_MATRIX.tsv`
- `RESOURCE_GATE_CONTRACT.md`
- `DRY_RUN_VALIDATION.md`
- `FINAL_REPORT.md`

The execution helper script may be added under `util/vm_tlb/`, but no experiment may run.

## 11. Final status

B9 must choose exactly one:
- `EXECUTION_PACK_READY_AFTER_A_TERMINAL`
- `PREFLIGHT_BLOCKED_CONFIGURATION_MISMATCH`
- `PREFLIGHT_NEEDS_USER_DECISION`

Even if the pack is ready, do not auto-run E01--E10. Commit/push and STOP for review.

All evidence remains `SPECULATIVE_DIAGNOSTIC`; A terminal results remain external supporting evidence, not B-local experiment results.
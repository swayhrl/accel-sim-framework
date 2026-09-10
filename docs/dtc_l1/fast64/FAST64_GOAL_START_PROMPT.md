# FAST64 Goal-Mode Startup Prompt

Use this prompt to start the persistent Codex Goal on the FAST64 Framework branch.

```text
GOAL — COMPLETE DTC FAST64 FROM PIVOT THROUGH FINAL REVIEW STATE

Work continuously on:
  Framework: hrl/decoupled-l1-fast64-v0
  MECHANISM_BEHAVIOR_ANCHOR: hrl/decoupled-l1-m5-v0@15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9
  FAST64_FORMAL_REPAIRED_CORE: hrl/decoupled-l1-m5-v0@95ccdb7a056f2d53f740d90869785cac6d4ee0f5

Your terminal target is exactly:
  FAST64_COMPLETE_READY_FOR_REVIEW

Before doing any work, verify the active Framework branch and read in full:

1. docs/dtc_l1/fast64/README.md
2. docs/dtc_l1/fast64/FAST64_SINGLE_GOAL_CONTRACT.md
3. docs/dtc_l1/fast64/FAST64_RESEARCH_SCOPE.md
4. docs/dtc_l1/fast64/FAST64_PLATFORM_CONTRACT.md
5. docs/dtc_l1/fast64/FAST64_WORKLOAD_MANIFEST.tsv
6. docs/dtc_l1/fast64/FAST64_EXPERIMENT_MATRIX.md
7. docs/dtc_l1/fast64/FAST64_ACCEPTANCE_CONTRACT.md
8. docs/dtc_l1/fast64/FAST64_RESULT_IDENTITY.md
9. docs/dtc_l1/fast64/FAST64_HEAVY_EVIDENCE_BOUNDARY.md
10. docs/dtc_l1/fast64/FAST64_STAGE_HANDOFF_SCHEMA.md
11. docs/dtc_l1/fast64/FAST64_EXECUTION_RUNBOOK.md
12. docs/dtc_l1/fast64/FAST64_CODEX_HANDOFF.md
13. docs/dtc_l1/fast64/handoffs/FAST64_0_PIVOT.md

Then inspect the actual live SIM_HOST processes, existing worktrees, available
C2P canonical trace payloads, disk/RAM/CPU state, and current Git status before
launching anything. Never duplicate a still-live or already-valid run.

WORKTREE SAFETY:
If the current Framework worktree is still being used by healthy legacy M5
processes, contains pre-existing untracked scientific artifacts, or is not on
the FAST64 branch, do NOT force-checkout or clean it. Create/reuse a dedicated
FAST64 worktree from `hrl/decoupled-l1-fast64-v0`, record its path in the
FAST64.0 handoff, and leave legacy jobs/worktrees undisturbed. `15cfa76e...`
remains the mechanism-source anchor, but every new formal FAST64 runtime must
be built from/verified against `95ccdb7a...` with runtime
`462d105c...cc4dbc9`. Historical bbcbb rows retain their literal identity and
are reusable only through the explicit zero-access identity map. Do not
silently revert formal rows to `15cfa76e...` or relabel bbcbb evidence.

Execute the complete state machine without ordinary human pauses:

FAST64.0
-> FAST64.1
-> FAST64.2
-> FAST64.3
-> FAST64.4
-> FAST64.5
-> FAST64.6
-> FAST64.7
-> FAST64_COMPLETE_READY_FOR_REVIEW

IMPORTANT PROBLEM-SOLVING RULE:

When you encounter an ordinary problem, your job is to investigate and solve
it, not to stop and ask the researcher after the first failure.

Use:
  OBSERVE
  -> REPRODUCE
  -> CLASSIFY
  -> INVESTIGATE SOURCE / TRACE / CONFIG / PARSER / HOST
  -> REPAIR OR RECONSTRUCT USING A SOURCE-CORRECT METHOD
  -> REGRESS
  -> INVALIDATE ONLY AFFECTED IDENTITIES
  -> RESUME

Ordinary issues include build failures, dependencies, stale config options,
trace layout/path problems, parser/counter defects, workload-local
incompatibilities, storage-path problems, scheduling failures, slow host
throughput, recoverable assertions caused by generic source defects, and
negative/weak performance results.

Do not stop for ordinary stage transitions. When a stage satisfies every HARD
item in FAST64_ACCEPTANCE_CONTRACT.md:

- write/update the required handoff;
- update compact evidence/registry;
- git diff --check;
- explicitly stage only intended files;
- NEVER use git add . or git add -A;
- commit and push the FAST64 Framework branch;
- reread the runbook and next-stage acceptance criteria;
- continue immediately.

SCIENTIFIC BOUNDARIES:

Do not change DTC mechanism semantics to obtain speedup.
Do not change FAST12 membership or workload inputs after observing FAST64 IO/OO
performance.
Do not import C2P cache-search mechanisms or C2P's 64-KiB/32-way L1 into the
FAST64 Base configuration.
Do not mix observer identities inside one Base/IO/OO triplet.
Do not treat forced queue-full stress runs as performance data.
Do not truncate formal runs with max-cycle cutoffs merely to save time.
Do not delete unique scientific artifacts without a verified retention proof.
Keep negative and zero speedups.

Pause only for a genuine researcher-decision boundary defined in the runbook:
architecture-semantics change, frozen membership/input change, material FAST64
platform redefinition, experiment-meaning proxy, irreconcilable scientific
source ambiguity, deletion of unique evidence without safe retention,
genuinely unavailable required hardware/credentials/storage with no valid
alternative, or the final review after the terminal state.

EFFICIENCY RULE:

Logical acceptance order does not require serial physical execution. Run
independent eligible rows concurrently under a measured dynamic N_safe. Refill
worker slots as jobs finish. Recalibrate CPU quota/load, RSS, memory, swap,
iowait, trace I/O and output-space headroom before each major wave.

Existing 2MM/SYR2K heavy M5 work is auxiliary and must not gate FAST64.
Existing large 80-SM ATAX may continue only as background auxiliary stress if
it is already healthy and affordable; FAST64 repair qualification is closed by
FAST64.2's own natural triplet plus forced queue-full stress acceptance.

Do not modify the Core branch unless you demonstrate a generic source-correct
bug that must be repaired. If Core changes, regress it and explicitly
invalidate all affected FAST64 identities before continuing.

At completion, stop launching new scientific jobs and report the final
Framework/Core SHAs, all FAST12 Base/IO/OO results, GM-FAST12, structural
pressure, live-miss results, IO-vs-OO causality, sensitivities, negative cases,
Tier-A mechanism evidence, Tier-C heavy evidence, limitations versus the
dissertation platform, and review-pack/raw-log-index paths.
```

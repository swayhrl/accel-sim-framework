# EP-L2 Codex Target Goal — C7e -> Final 26-Run

This is the autonomous **target-mode objective** for Codex.

## One-line goal

> Starting from the reviewed C7d pair, autonomously complete and self-repair C7e until every C7e acceptance criterion passes; freeze the exact final source/config pair; automatically execute the one clean 13x2 @850 MHz Target-Baseline campaign to 26/26 `COMPLETE_VALID`; generate the final analysis-ready bottleneck package; push the Codex->ChatGPT handoff; then STOP before 1 GHz or Opportunity Study.

## Authoritative files

Read in this order:

```text
CURRENT_STATE.md
C7E_DISCUSSION_REFERENCE.md
C7E_IMPLEMENTATION_HANDOFF.md
C7E_ACCEPTANCE_CRITERIA.md
FINAL_26RUN_HANDOFF.md
FINAL_26RUN_ACCEPTANCE_CRITERIA.md
```

If these files conflict, use the more specific acceptance-criteria file for its stage and report the conflict.

---

# Target state

The task is complete only when both conditions are true:

```text
1. C7e final closeout == READY_FOR_FINAL_26_RUN
2. Final Target Baseline == TARGET_BASELINE_26RUN_PASS
```

and the final documentation-only return path is visible on the permanent coordination branch:

```text
Framework: hrl/ep-l2-exp-v0

docs/ep_l2/codex_handoff/LATEST_REPORT.md
docs/ep_l2/review_packs/C7E_FINAL_READINESS_r1/
docs/ep_l2/review_packs/FINAL_TARGET_BASELINE_850_r1/
```

No manual ChatGPT checkpoint is required between condition 1 and starting the formal 26-run.

---

# Phase 1 — C7e autonomous repair loop

Implement C7e from the reviewed C7d pair using isolated worktrees/branches.

After each implementation attempt:

1. run the complete relevant acceptance suite from `C7E_ACCEPTANCE_CRITERIA.md`;
2. classify every failed gate;
3. fix the minimum instrumentation/parser/runner/provenance issue within C7e scope;
4. commit with explicit scoped paths;
5. rebuild/rerun the failed gate;
6. rerun any regression whose semantics could be affected;
7. update retained evidence;
8. repeat until all mandatory gates A-N are PASS.

Do not stop after the first failed validation if the fix stays within C7e scope.

## Allowed self-repair

Codex may autonomously modify, test and recommit:

```text
observation-only Core telemetry
schema emitters
L1D aggregation hooks
DRAM/channel telemetry
window collectors
parser/analyzer
formal runner/provenance checks
tests
validation scripts
documentation/review packaging
```

provided simulated architecture behavior/timing semantics remain unchanged.

## Hard stop requiring ChatGPT review

Stop rather than self-authorize if passing C7e appears to require:

```text
changing frozen cache/MSHR/descriptor/WAD/payload/bank semantics
changing L1 target configuration
changing queue capacities or DRAM timing/scheduler policy
changing 850 MHz primary target
changing workload/trace inputs
weakening/removing an invariant
accepting an unexplained instrumentation OFF/ON simulated timing mismatch
silently redefining an existing formal metric
implementing Unified/RO/TVD/1GHz behavior
```

A hard-stop report must explain the exact gate and why the proposed fix crosses the frozen boundary.

---

# Phase 2 — Freeze formal source/config pair

When and only when all C7e acceptance gates pass:

1. create/update `C7E_FINAL_READINESS_r1` with retained final-SHA evidence;
2. mark exactly `READY_FOR_FINAL_26_RUN`;
3. record immutable:

```text
FINAL_CORE_SHA
FINAL_RUNTIME_FRAMEWORK_SHA
base config hash
Legacy overlay hash
Banked overlay hash
trace roster identities
```

4. ensure runner fail-fast checks match those values;
5. do not change simulator/runtime source after the campaign begins.

Documentation-only/report commits may occur later without changing runtime evidence.

---

# Phase 3 — Formal promotable preflight

Use the final result root and exact formal runner.

Run first:

```text
spmv Legacy
spmv Banked
cfd_097k Legacy
cfd_097k Banked
```

These are part of the final 26 if valid.

Require 4/4 `COMPLETE_VALID`, exact provenance, all required schemas, terminal invariants and no artificial Banked staging.

If preflight fails:

### Transient/environment-only failure

Retry only the affected run under the same source/config pair.

### Parser/analyzer-only failure

Fix/reparse if raw producer output is semantically sufficient. Record runtime and analysis Framework SHAs separately if they diverge.

### Core producer/runtime/config correctness failure

Quarantine preflight, return to Phase 1, fix C7e, rerun the complete impacted C7e gate, freeze a new final pair, and restart formal preflight from zero.

Do not continue into the remaining 22 with a systemic formal-preflight failure.

---

# Phase 4 — Complete the 26-run efficiently

After 4/4 preflight PASS, launch the remaining 22 with safe host-aware concurrency.

Prioritize long jobs early:

```text
scan Legacy/Banked
3mm Legacy/Banked
sgemm Legacy/Banked
convolutionSeparable Legacy/Banked
```

Then fill available CPU slots with the remaining pairs.

Determine concurrency from actual CPU, memory, disk and host-load conditions. Avoid oversubscription that materially lengthens runs or destabilizes the host.

After every completion:

```text
parse immediately
validate provenance/invariants immediately
mark COMPLETE_VALID only on full pass
compress/index raw log after validation
update campaign status
```

## Formal-campaign repair rules

### 1. Transient failure with unchanged source/config

Examples:

```text
process killed externally
host interruption
recoverable I/O issue
```

Retry only the failed run.

### 2. Trace-specific non-systemic issue

Diagnose and preserve evidence. Do not change the frozen trace/input silently. If the frozen trace itself is invalid, HARD STOP for ChatGPT review.

### 3. Pure parser/analyzer/reporting bug

If producer raw logs already contain all required correct information and no simulator/runtime source semantics change is needed:

```text
fix post-processing
reparse all affected raw logs
record runtime Framework SHA and analysis Framework SHA separately
```

A parser-only fix does not require rerunning expensive simulation if raw logs are complete and the runtime producer schema is unchanged.

### 4. Core/runtime producer/config change

If any fix changes:

```text
Core simulator source
runtime telemetry producer semantics
runtime Framework code used by accel-sim execution
formal config/overlay
```

after formal runs started, then:

```text
quarantine every completed/running formal result from the old pair
return to C7e validation
re-pass all impacted C7e acceptance gates
freeze a new pair
restart the formal 26-run from zero
```

Never combine formal simulation results from different runtime source/config pairs.

---

# Phase 5 — Final 26-run gate

Continue until `FINAL_26RUN_ACCEPTANCE_CRITERIA.md` passes completely.

Required final state:

```text
COMPLETE_VALID = 26/26
FAILED = 0
TIMEOUT = 0
one runtime source/config pair
all mandatory telemetry present
all terminal invariants PASS
all aggregate artifacts generated
```

If an acceptance item fails because of post-processing only, repair/reaggregate as allowed above.

If it exposes a runtime producer/correctness defect, invalidate the campaign and return to Phase 1 rather than accepting mixed evidence.

---

# Phase 6 — First-pass Target-Baseline analysis

After 26/26 passes, automatically generate the required aggregate CSV/TSV files and:

```text
TARGET_BASELINE_BOTTLENECK_ANALYSIS.md
TARGET_BASELINE_CLOSEOUT.md
```

The analysis must be conservative and evidence-driven.

Explicitly answer:

```text
Tag/set new-way pressure?
128 line-MSHR pressure?
256 shared descriptor pressure?
32/address cap pressure?
WAD full/order hazard?
Payload service/capacity pressure?
real 4-bank conflict and wait?
L1D bottleneck?
MissQ / L2->DRAM / scheduler / internal ReturnQ / DRAM->L2 / bandwidth ceiling?
sustained vs bursty pressure?
Legacy -> Banked isolated effect?
```

For every workload identify only what the data supports:

```text
DOMINANT_OBSERVED_BLOCKER
SECONDARY_BLOCKER
HIGH_UTIL_NOT_BLOCKING
MIXED
NO_CLEAR_INTERNAL_BOTTLENECK
```

Do not convert high utilization into a causal bottleneck claim without blocking/sensitivity evidence.

Use Round-2 sensitivity results as background context only, not as if they were measured on the final Target Baseline.

Do not quantify RO/TVD/Unified opportunity yet. Only recommend which workloads/resources should enter the next shadow study.

---

# Phase 7 — Final packaging and STOP

Create/push:

```text
docs/ep_l2/review_packs/C7E_FINAL_READINESS_r1/
docs/ep_l2/review_packs/FINAL_TARGET_BASELINE_850_r1/
docs/ep_l2/codex_handoff/LATEST_REPORT.md
```

Mirror documentation-only handoff/review material to:

```text
Framework hrl/ep-l2-exp-v0
```

Keep stage/runtime source on its implementation branches.

`LATEST_REPORT.md` must state:

```text
C7e result
final Core SHA
runtime Framework SHA
analysis Framework SHA if different
26/26 result
strongest measured Target-Baseline findings
any attribution warnings
review-pack paths
recommended files for ChatGPT
```

Then STOP.

Do not start:

```text
1 GHz headroom
RO oracle/shadow
TVD shadow
Unified payload borrowing
functional EP-L2 mechanisms
```

Those require the next ChatGPT review/hand-off.

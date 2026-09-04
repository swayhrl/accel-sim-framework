# M5 v3 Parallel Tracks Approval and Roadmap

Status: **RESEARCHER-APPROVED — PAPER COMPUTE + EXTENDED-20; GRAPHICS RESEARCH CLOSED SOURCE-BACKED-UNAVAILABLE**

Approval date: 2026-09-04.

This document is the authoritative scheduling/ownership refinement for M5. It preserves the scientific definitions already frozen by M5 v1 and the ratio-zero dirty-victim resolution. It supersedes only the earlier assumption that all graphics work must wait until M5.6 and that M5.6 alone is the compute-freeze boundary.

Graphics research has now completed and its independent closeout is accepted by `M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`.

## 1. Scientific tracks

M5 has three coordinated tracks:

1. **Paper Compute** — the ten Chapter-4 compute workloads and Figures 4.2/4.5/4.7/4.8/4.9/4.10.
2. **Extended Compute** — a pre-performance selected set of 20 additional common GPU workloads used only for generalization evidence.
3. **Graphics** — provenance/path recovery for the five thesis glmark2 workloads. M5.7/M5.8 are now closed at `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`; no formal graphics execution is authorized from current evidence.

Extended-20 never substitutes for Paper-10 and must never be mixed into a paper Figure 4.x label without an explicit supplemental/generalization label.

## 2. Approved dependency graph

```text
Paper Compute:
M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6
                                                       |                  |
                                                       |                  v
                                                       |             PAPER-10 SYNTHESIS
                                                       |
                                                       +----> Extended Compute:
                                                              M5.E1 -> M5.E2 -> M5.E3

Graphics research, independent Framework-only branch:
M5.7 provenance -> M5.8 path recovery -> GRAPHICS_SOURCE_BACKED_UNAVAILABLE
                                      [CLOSED/ACCEPTED]

Join barrier:
M5.6 PASS + M5.E3 PASS + no unresolved correctness/fidelity issue
        -> M5.COMPUTE_FREEZE
        -> M5.12 negative-evidence synthesis
```

M5.9/M5.10/M5.11 are skipped under the accepted graphics closeout. They may be reopened only if genuinely new original/source-backed graphics artifacts satisfy the explicit M5.8 admission contract.

## 3. Extended-20 activation

The selection proposal at Framework branch
`hrl/decoupled-l1-exp-m5-extended20-select-v0`, commit
`d43b6eec93f68efa94057f34ffa699463b53e6a6`, is independently reviewed and accepted subject to the launch re-freeze gates in `M5_EXTENDED20_APPROVAL.md`.

The Extended formal track uses:

- `M5.E1` — source/build/input/output/PTX/config/parser re-freeze and batch readiness;
- `M5.E2` — 20 x {PAPER_BASE, PAPER_IO, PAPER_OO} = 60 primary formal runs;
- `M5.E3` — generalization/causal synthesis and targeted anomaly diagnostics only when scientifically needed.

The 60-run primary wave must begin only after M5.2 has frozen the common Base/IO/OO metric/counter interpretation used for main-result analysis. E1 metadata/build preparation may proceed earlier if it does not disturb active Paper-10 runs.

## 4. Parallel execution requirement

Long independent simulator jobs are not to be executed one-by-one by default. Use the dynamic worker-pool rules in `M5_PARALLEL_BATCH_POLICY.md` and the measured host-concurrency envelope from M5.0A/current recalibration.

Parallel execution affects wall clock only; simulator-cycle results remain identified by source/config/workload hashes. Host contention must not be used as a performance metric.

## 5. Compute freeze is a join barrier

`M5.COMPUTE_FREEZE` is allowed only when both are complete:

- Paper-10 through M5.6;
- Extended-20 through M5.E3.

At the freeze:

- record immutable `COMPUTE_FREEZE_CORE_SHA` and `COMPUTE_FREEZE_FRAMEWORK_SHA`;
- finish Paper-10 and Extended-20 review packs;
- ensure branches are pushed/clean and `git diff --check` passes;
- write `docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md`;
- no later graphics work may rewrite these compute FORMAL results.

If Extended-20 exposes a source-correct simulator defect before freeze, repair/regress under the normal M5 problem-resolution policy and invalidate affected Paper/Extended formal data as required.

## 6. Graphics closeout and branch ownership

Graphics research completed on Framework branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0@ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`

Accepted result:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Authoritative review:

`docs/dtc_l1/m5/M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`

Consequences:

- keep the graphics-research branch as frozen evidence;
- do not modify GPGPU-Sim Core for graphics under current evidence;
- do not create M5.9 integration branches after compute freeze merely to restate unavailability;
- do not run graphics Base/IO/OO formal simulations;
- do not emit `GM-GRAPHICS` or `GM-ALL-PAPER`;
- preserve four source-equivalent scene mappings plus unresolved `2D-tex` as provenance/negative evidence;
- reopen only when new original/source-backed artifacts satisfy the M5.8 reopening contract.

## 7. M5.12 dependency and final reporting groups

M5.12 requires:

1. Paper-10 M5.6 PASS;
2. Extended-20 M5.E3 PASS;
3. `M5.COMPUTE_FREEZE` recorded;
4. accepted graphics closeout `ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d` included in the final evidence;
5. no unresolved correctness/fidelity issue.

Final aggregate labels are distinct:

- `GM-CE` — thesis cache-efficient compute subset;
- `GM-GP` / `GM-PAPER10` — ten thesis compute workloads;
- `GM-EXTENDED20` — twenty supplemental workloads;
- `GM-ALL-COMPUTE30` — Paper-10 + Extended-20, supplemental/generalization only.

Under the accepted graphics-unavailable closeout:

- no `GM-GRAPHICS`;
- no `GM-ALL-PAPER`.

Extended-20 is never included in `GM-ALL-PAPER` even if graphics is reopened in the future.

## 8. Final M5 state

Current expected terminal state after compute completion and M5.12 synthesis:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

If genuinely new graphics artifacts later reopen and successfully complete M5.9-M5.11, the alternate success state remains `M5_FULL_REPRO_READY_FOR_REVIEW`; that path is not active now.

Figure 4.6 fresh RTL/synthesis area reproduction remains outside M5 and requires separate M6 authorization.

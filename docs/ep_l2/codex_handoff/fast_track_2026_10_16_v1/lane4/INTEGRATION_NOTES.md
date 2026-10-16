# Lane 4 integration notes — review_r2 continuation

Consumed continuation: `aec01450d3c527524ee09ee59242f582fafe5354`,
`fast_track_2026_10_16_review_r2/REVIEW.md` and `CONTINUE.md`.
The original scientific contract remains `6c136e2a56a008695f8c8b815723bf8f1a760db9`.

R0 is the frozen Lane1 release, Core `126394be46b15f55b9756d43eb9ca9a9baae1c84`,
Framework `37dec04d223ae65167c5584e56887c74f6540d27`, binary SHA256
`0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698`.
Lane5 independently qualifies and runs R0 B16/U_WB16 immediately. Diagnostics
are not an R0 prerequisite; Lane4 does not rebuild or replace this binary.

The Lane4 candidate Core `b8b3d55b392fcff793d0aec684bddb73ba3065a9` already
consumes exact R0 and adds default-OFF I_WB/I_META/I_READ_HIT/I_WB_META.
The r2 `CORE_MINIMAL.patch` is the complete delta from R0 to that candidate.
Lane1 applies it in its isolated R1 integration worktree and publishes the
actual new producing commits and immutable binary. Patch replay checks the
entire resulting tree, rather than merely checking that the patch applies.
Existing 12 C++/6 illegal-mode/16 parser tests and three legacy application
runs remain frozen evidence; none of those applications is rerun by this
continuation. The third run verifies the latest candidate's all-OFF behavior
against all seven CSV families. It is not a B16 baseline.

Lane5's frozen R1 baseline spec remains owned by Lane5. It must bind the same
Core, Framework, binary, workload, epoch, trace, feature vector, configs/aux
and environment as the requested ideal cell. The ideal spec only appends one
three-flag overlay. R0 rows are never the matched numerator of R1 ideal rows.
`prepare_ft_lane4_b16.py` pins the qualification envelope SHA; the runner
checks it before and after execution and records the matched baseline key.

R1-only adapter metadata: add `ideal_gates` to the Lane5 normalized qualified
release, keyed by `I_WB`, `I_META`, `I_READ_HIT`, or `I_WB_META`. Each consumed
entry has `status: PASS`, `production_driven: true`, the exact `ideal_vector`,
and `evidence_path` / `evidence_sha256`. This records the independent ideal
qualification required by review_r2; it is not a new hardware/scientific gate.
Only the requested mode needs an entry, permitting rolling execution. The
normal R0 runner/schema is unchanged and requires no ideal gate. All ordinary
Lane5 production gates and feature-vector qualification still apply to R1.
Synthetic adapter tests establish rejection behavior only; their fixtures
cannot qualify a release or constitute performance evidence.

The inherited QV100 config includes a quoted DRAM timing value spanning
physical lines. The adapter tokenizes the whole file while retaining Lane5's
other release/content checks and rejecting unexpanded nested config inputs.
Lane5 can independently apply the same lexer correction to its own runner;
Lane4 does not edit Lane5's worktree.

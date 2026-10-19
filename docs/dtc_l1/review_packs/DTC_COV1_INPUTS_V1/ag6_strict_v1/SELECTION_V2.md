# Fixed AG6 selection: pure source handoff

**SOURCE_PREPARED_NOT_EXECUTED.** No import, AST/syntax check, boundary-case call,
parser call, actual STRICT read, resource sample or simulation was performed.
`selection_v2.py` and `selection_boundary_cases.py` have no filesystem/process/
network/clock/CLI APIs. They do not open or modify SELECTION.json, issue a
dispatch permission, select holdout inputs or change any frozen UUID.

## Rule provenance and exact tie meaning

Read in full: fixed `f81ca1c5054a78ed2c09f316bac0501c3bbc9322`,
`docs/dtc_l1/iscas2027/parallel_ag_ba_20261019_v1/MASTER_COORDINATION_V2.md`
(fast-path item5), `LANE_BA_V2_CONTINUE_AND_DISPATCH.md` (item6), and
`AG6_AUTHORIZATION_V2.json.selected_candidate_rule`. These explicitly preserve
the earlier rule and require both independent imported BASEs and all four
qualified ON results, otherwise provisional O with no promotion.

The earlier authoritative text is fixed
`46df82670a56a4498b6d6e23ad57859eb7c36945`,
`docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/MASTER_PLAN.md` section3:

> AE或AD须满足 min(s_i)>=0.98 且 geometric_mean(s_i)>=1.02。两者均合格时取GM较大者；GM之比差小于0.5%固定优先AE

The same commit's PLAN_CONTRACT.json.candidate_selection fixes inputs
GEMM/Gaussian, complete calibrated AE+AD screen, minimum0.98, minimumGM1.02,
maximizeGM, tie_relative_fraction0.005, priorityAE/AD, incomplete provisional O,
no per-workload cherry picking and no combination. The fixed coordination,
lane, authorization, original plan and contract contain no more explicit tie
denominator/formula. Original Chinese says **ratio difference strictly less
than**0.5%; the exact implementation follows that ratio interpretation:

```text
s_input = accepted same-input BASE integer cycles / ON integer cycles
P_arm = s_GEMM * s_Gaussian       # positive GM_arm = sqrt(P_arm)
qualifies = min(s_input) >= 49/50 and P_arm >= (51/50)^2
both qualify: tie iff max(GM)/min(GM) < 201/200
              equivalently max(P)/min(P) < 40401/40000
tie -> AE; otherwise larger P (equivalently larger positive GM)
```

This is the precise arithmetic expression of the original “GM之比差” rule,
not a newly sourced formula or altered percentage denominator. Equality at
exactly0.5% is **not** a tie under the original strict “小于”; choose the larger
GM. Equal GMs satisfy the tie rule. AE priority is a predetermined
implementation preference, with no measured area advantage implied.

Every comparison uses Fraction and positive integer cycles. There is no float
threshold, square-root rounding, wall time or tolerance. Returned exact GM is
represented as a positive-square-root operation with rational radicand; parent
may add clearly cosmetic decimal formatting without changing the decision.

## Actual input contract

```python
selection = select_v2(
    ordered_four_actual_STRICT_byte_strings,
    base_cycles={"GEMM": 1071405, "Gaussian": 3278356},
    preregistration=exact_original_AG6_preregistration_bytes,
    base_decision=exact_qualified_BASE_decision_bytes,
    old_selection=exact_preserved_original_SELECTION_bytes,
)
```

The three metadata byte hashes are independently fixed in the source:
preregistration844591f6…, scoped BASE decisiona8e83409…, old selectiond4c90110….
Parent current source `7268d0fb46f951ae51b9879988b89dd35c8dc9c4` exposes the
decision bytes and registered BASE cycles/UUIDs; they join the exact frozen
preregistration. Both original BASE scope/old-executor limitations and producer
dossier hashes are retained in the returned comparison metadata. Integer
cycles must be actual int, not bool/float/string.

The four receipt slots are exactly this order:

| Point | New UUID |
| --- | --- |
| AE_GEMM | 77cbc367-150c-418d-85e0-3be23d952498 |
| AE_Gaussian | f9295c5b-29b9-4e6c-9b9c-531c21acfc99 |
| AD_GEMM | fe022881-b5b2-4d99-9229-d7940761fc66 |
| AD_Gaussian | 182cfb53-32c3-428d-a964-44e4f47d9727 |

Each actual receipt must be the parent's full closed
PASS_ACTUAL_REGISTERED_AG6_FULL_STRICT_EVIDENCE, with performance_accepted and
scientific_strict_pass true, actual accepted scope, exact point/arm/input/UUID,
positive integer ON cycles, same-input BASE_cycles, unchanged exact integer
BASE/ON ratio, full kernel/CTA/instruction counts, publication and identity/
mapping/resource closure hashes and positive actual runtime sample count.
These fields match the existing close_attempt_v2.collect output. The pure
selector checks their structure and joins; parent must independently bind
each **exact receipt byte hash** to the actual immutable execution evidence.
Claimed JSON fields alone cannot authenticate an experiment, and every result
retains actual_provenance_requires_parent_immutable_join=true.

Four accepted complete receipts are mandatory even if one complete arm already
looks qualified. Missing, failed, malformed, wrong UUID/order, extra slots,
bad integer type or missing BASE qualification returns
PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN, final_F=null, nominated_arm=null and
no partial arm ranking. Known accepted/failed receipt hashes and reasons are
retained; missing values never become zero speedups. Parent keeps all original
actual failed starts/receipts and ledger independently.

Only all four accepted same-input rows permit FINAL_F_FROM_COMPLETE_FOUR_POINT_AG6_SCREEN.
Then one qualifying arm wins, both qualifying arms use exact GM/tie logic,
and neither qualifying yields final_F=O. Accepted slowdowns remain valid
negative outcomes and participate in the fixed two-input denominator. This
single global F cannot choose an arm per input. New N/P/R results cannot
reselect F. Output is a pure JSON-serializable dict for the parent to publish
as a new SELECTION_V2; old SELECTION.json remains byte-identical.

## Small pure boundary source

`run_boundary_cases(selection_module, preregistration=..., base_decision=...,
old_selection=...)` has four fixed groups, unexecuted here:

1. Exact inclusive min0.98 and GM1.02, then rational epsilon1/10^24 below
   either threshold (product otherwise held exactly at its boundary).
2. AD GM ratio to AE just below, exactly at and just above201/200: expected
   AE / AD / AD, respectively. No floating arithmetic in the comparisons.
3. A complete declared synthetic AE pair alone cannot nominate; four declared
   accepted synthetic receipts allow only the pure global decision and retain
   the parent-provenance requirement. The fixtures carry explicit synthetic
   markers and dummy closure hashes; they are not actual AG6 results.
4. All four declared valid baseline-speed rows yield final O; a float cycle
   or wrong UUID holds provisional O with no nomination. The float here is an
   expressly invalid type fixture, never part of the selector's arithmetic.

No production module is imported by the test source; parent supplies its
source-bound module object and metadata after a separate source freeze and
actual CPU admission. Four PASS boundary groups would qualify only this small
arithmetic/schema interface, not actual AG6 receipt provenance, performance,
runtime authority or a scientific F. There is no execution or resource release
in this source delivery.

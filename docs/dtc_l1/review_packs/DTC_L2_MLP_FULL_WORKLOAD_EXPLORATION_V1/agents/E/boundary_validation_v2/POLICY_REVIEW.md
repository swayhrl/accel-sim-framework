# Supplementary boundary validation policy V2: review candidate

This package is **not activated**. The frozen V1 adaptive source, its 1% contract,
past outputs, simulation identities and initial matrix remain unchanged. Main
must approve, archive and visibly announce this supplementary version before
installation. The change implements the user's existing authorization to keep
exploring an improving parameter boundary, rather than silently changing input or
architecture contracts. At design time the initial all35 matrix is incomplete;
the rule is not fitted after choosing a full-suite winning configuration.

## Why an additional layer is necessary

V1 transparently preregistered a 1% whole-suite/marginal threshold, but that was an
operational choice by the agent, not a user requirement. A deterministic sequence
such as GM 1.002 → 1.004 remains improving, yet V1 calls it saturation. A fixed
suite can also improve substantially while the all35 GM is diluted. Either case
can suppress a legitimate boundary or useful combination prematurely.

V2 retains 1% as a **materiality label**. Positive eligibility uses an epsilon of
1e-12 only to avoid floating-point roundoff; it does not claim experimental
statistical uncertainty. Existing numerical GM/cycle values are never modified.

## Complete algorithm

1. Verify the exact35 input domain and immutable program/suite membership against
   scope. Require all350 initial cells to be terminal, including CH P0. Pending,
   missing and engineering-only records are not terminal performance data.
2. Require all35 DH P0 records accepted for any additional inference. Each added
   direction must itself have all35 accepted DH records; it cannot be inferred
   from the fast 6–9 inputs, a reduced common subset or failure-free survivors.
3. For each single-factor family inspect its highest registered level and the
   immediately preceding tested level. A pending or unaccepted higher level
   holds that family's boundary; never skip over it to extrapolate from a lower
   successful level.
4. If full35 `P0/top > 1+1e-12` and `lower/top > 1+1e-12`, propose doubling that
   factor. 1% determines the material tags only. Stop for nonpositive overall or
   incremental gain, exact saturation, source integer/constructor bounds,
   evidenced resource constraints or missing scientific evidence. There is no
   scientific total-start cap or arbitrary E768/M16/Q128/F256 stop.
5. Define immutable contexts: ALL35 and each frozen suite with at least three
   inputs. A global direction is useful if its full35 GM is positive by epsilon.
   A suite direction requires GM>=1.01 and strictly more than half its inputs
   positive by epsilon. These suite rules are declared before final all35 data.
6. Within each context choose one useful completed level per factor by its context
   GM, breaking ties toward lower resources. Propose the five supported pairs
   E×M, E×Q, E×F, M×Q and M×F; with three or more useful directions, also propose
   one union. Deduplicate identical parameter vectors across contexts and V1.
   This is evidence-gated uniform-configuration search, not per-program best-of
   and not a full Cartesian grid. Every additional DH matrix has all35 inputs.
7. Existing V1 moderate/high-resource candidates retain full35 CH matching. In
   addition, rank all completed full35 uniform profiles, including P0, by their
   full35 GM. Ties prefer lower normalized logical resource cost, then the profile
   name. The best globally positive uniform profile must receive CH35 regardless
   of whether it was initial or has less than1% gain. Each fixed-suite useful
   uniform champion also receives CH35; the other suites' regressions remain in
   that matrix. Retain the prior rule that useful completed noninitial profiles
   receive CH35. Matching does not delete negative or missing CH inputs. Profiles
   that are not useful do not automatically trigger mechanical CH repetition.
8. A canonical parameter/design/all35-input identity generates exactly the same
   64-hex proposal ID as V1. Existing registered, failed, pending or previously
   evaluated cells are not regranted. Historical known IDs absent from the matrix
   explicitly wait for registry reconciliation, not scientific completion. A
   partially present matrix is a reconciliation hold rather than a new reduced
   batch masquerading as35 inputs.

New proposal phases identify V2 boundary, fixed-context pair/union, and matched CH
validation. Each proposal retains exact parameters, all35 identities, evidence
population, context GM/positive count, global GM, logical resource counts and the
FR-FCFS `shared credits=F+191` coupling. Cache capacity remains10MiB, DRAM850MHz,
and all non-target options—including DTC structures and Hash family—stay fixed.

## Statistics and candidate interpretation

No suite GM is relabeled as the all35 GM. All35 negative cases remain included in
the actual result consumer. Candidate materiality annotations report both
deterministic positive improvement and the original V1 materiality boolean;
the original candidate fields and original decision hash are preserved. CH/DH
ratios and formal adoption still require identical valid all35 populations.
Area is not matched; logical slots are not an RSS/physical-byte/area model.

Candidate revision2 additionally prevents this omission: if initial E384 improves
all35 GM by0.9%, E768 by0.8%, and other profiles are flat, the older1% formal-class
heuristic can omit E384's CH matching. Revision2 explicitly reports
`best_global_uniform_profile` and `best_global_uniform_GM`, and requests E384 CH35.
It does not rewrite V1 `formal_candidates`. That best field is **best observed
completed uniform performance**, not an assertion that all unexplored settings
were exhausted. All incomplete profiles are listed. The highest-resource class
is an exploration point, not a performance upper bound and not necessarily the
fastest point. The best record reports exact CH registered/accepted/missing counts;
`global_best_CH_qualified` and
`supplementary_uniform_CH_qualification_complete` stay false for pending or
unaccepted CH cells and block adoption/completion. This revision is still an
unactivated review candidate; the previous7f2e3d source preimage is retained.

## Integration order for main review

The pure API is:

```python
updated = boundary_module.augment(existing_decision, summary, scope, history)
```

It has no filesystem, source loading, registration, controller or model code.
It never changes an existing false adoption/completion flag to true, and it
preserves registry-journal holds. The final outer guard remains mandatory:

```python
prior_recommend = adaptive_instance.recommend  # already journal-guarded
def recommend_with_v2(summary, scope, history=None):
    original = prior_recommend(summary, scope, history)
    augmented = boundary_module.augment(original, summary, scope, history)
    return registry_journal_guard.guard_decision(augmented)
# Install only after main source/QA review and a versioned public activation record.
```

Preserve original V1 code/contract/readbacks and all previous decisions. Archive
V2 policy/module/source SHA and qualification plus an explicit activation receipt.
Do not rewrite old choices retroactively. Any actual future grant still passes
the same sole-owner journal, native source/build/identity checks and dynamic
resource admission. This candidate package does not activate any of those steps.

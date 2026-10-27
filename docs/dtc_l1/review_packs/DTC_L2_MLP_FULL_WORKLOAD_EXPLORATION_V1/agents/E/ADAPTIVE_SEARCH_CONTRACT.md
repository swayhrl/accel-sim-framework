# DTC L2 MLP adaptive search contract V1

This rule set is written before this campaign's performance results. It creates
proposals only. Agent E does not register, launch, retry, signal, or archive models.
Only DTC-MAIN can accept a proposal and register its new finite matrix. There is no
fixed total simulation count or reset of prior budgets.

## Fixed scientific boundary

All proposals retain all 35 frozen ordinary input identities, including inputs
whose old original matrix was incomplete. The seven unresolved program identities
remain excluded pending scientific adjudication. No best input or best profile
per program is used to construct a suite GM. Failed and regressing inputs stay
visible. Data, DTC structures, Hash family, L2 geometry/address mapping, and all
clocks remain fixed; DRAM remains 850 MHz. Only `entries`, `merge`, `miss_queue`,
and `frfcfs` change through Agent A's verified generator.

The initial matrix is DH P0/E384/E768/M8/M16/Q64/Q128/F128/F256 plus CH P0 on all
35 inputs. Six strictly proven matching P0 reuse cells are references, not starts.
The 344 fresh initial starts are an initial registered matrix, not a scientific
total-start limit.

## Predeclared significance and comparison rules

The operational threshold for a useful whole-population direction is geometric
mean speedup at least **1.01** (one percent). This is a search-policy threshold,
not a claim of statistical measurement error. Cycles are deterministic model
outputs; all individual positive/negative changes remain reported by Agent D.
This threshold is fixed independently of which application benefits.

Initial proposals wait for every initial profile's registered cells to terminate,
including CH P0. A strict archived negative is terminal but unaccepted. A pending
cell, a missing result, and an engineering-only postprocessing event are not
terminal performance data. They cannot be imputed to zero or speedup one.

Each family is compared on the identical intersection of accepted identities for
P0 and all its completed levels. Incomplete coverage is explicitly provisional,
with the full excluded/missing list. Pair and multi-factor proposals recheck every
parent's gain on the same joint population; gains from different populations are
never silently combined. A formal candidate requires all 35 accepted DH results,
then exact-profile CH validation for all 35. A valid full35 candidate remains
valid even if a different exploratory profile has preserved terminal negatives.

## Adaptive expansion

1. Sort completed single-factor levels by the resource parameter.
2. If the top level improves over P0 by at least 1% **and** improves over the next
   lower tested level by at least 1%, propose doubling that factor. Thus a newly
   useful boundary is not stopped merely because its lower level did not help.
3. Otherwise stop that family for saturation or regression and retain its data.
4. Do not leap over a registered but pending higher family level.
5. Source integer/constructor safety bounds apply. A coordinator can add an
   explicitly evidenced resource bound/hold in history; the reason is emitted.
   Such a hold is an operational constraint, not a fabricated scientific cap.

There is no arbitrary hard stop at E768/M16/Q128/F256. Extensions are generated
as data justify them. Extending a single-factor direction also makes its new level
available to subsequent supported combinations.

## Combination search

Choose the highest-GM completed useful level in each family, breaking exact ties
toward the lower resource level. Propose only these supported pairs:

- entries × merge;
- entries × miss queue;
- entries × FR-FCFS;
- merge × miss queue;
- merge × FR-FCFS.

When at least three directions are independently useful on one common population,
also propose one union of those directions. This avoids an unsupported Cartesian
product. Every proposed DH profile runs on all 35 frozen inputs. Results of a
combination are measured directly; parent gains are never multiplied to invent
its expected speedup. No extra performance or identity claim is inferred from
the recommendation itself.

## Uniform classes and CH matching

The baseline is P0. The high-resource class uses the highest normalized logical
slot score among full35 accepted DH profiles, breaking ties toward higher
whole-suite GM. The moderate class uses a different parameter vector: among all
remaining profiles with full35 accepted DH results and GM>=1.01, it uses the lowest
resource score. If none of those improves, report the lowest-resource remaining
tested profile as unimproved. Both require CH on all 35 before formal adoption.
Intermediate rankings are explicitly provisional while any newly registered
search is pending. `whole_suite_DH_ranking` separately preserves the full measured
performance ranking; the high-resource label never implies it won that ranking.

The normalized score is the sum of baseline-normalized MSHR address entries,
MSHR request-reference capacity, miss-queue slots, and FR-FCFS slots. It is only
an ordering heuristic, not a byte or area model. The two classes must use distinct
parameter vectors when at least two non-P0 full35 DH vectors exist, even if only
one improves. If fewer exist, emit `insufficient_distinct_candidates=true` and
`adoption_ready=false`; do not create an unsupported simulation merely to fill a
class. High-resource and moderate configurations may be **unimproved**, with
matched CH requests; `improvement_proven` reports the actual status. Do not call
an unimproved class better or a physical upper bound. A strictly higher-resource
frontier beyond the best measured configuration remains an explicit limitation.

Quiescence only means no recommendation or live registered cell remains. Terminal
unaccepted cells and engineering-only states require explicit engineering review;
they cannot make the scientific Goal complete. The API emits
`requires_engineering_review`, `engineering_cells`, and `scientific_stage_complete`
in addition to `adoption_ready`. A fully matched candidate remains scientifically
valid independently of an unrelated failure, but the campaign does not claim all
engineering work finished while review remains outstanding.

Logical resources are 40 banks × entries, 40 × entries × merge request references,
40 × miss queue slots, and 20 × FR-FCFS slots. FR-FCFS changes also alter the shared
credit limit per controller to `F+191`; private credits remain two. L2 data storage
is fixed at 10 MiB. Silicon area, metadata encoding and hardware realism are not
established by these counts. Host RSS is separately measured by the coordinator.

## Pure API and history

```python
from l2_adaptive import recommend
decision = recommend(agent_D_summary, scope, history)
```

The summary is Agent D's `DTC_L2_MLP_AUTO_SUMMARY_V1`, using `table`, `programs`,
and `profiles`. Scope contains D's `points` and optional `frozen_input_count`
(default 35). Production must retain all 35. Fixtures use three synthetic inputs.

History is optional and JSON serializable:

```json
{
  "profiles": {
    "E1536": {"parameters": {"entries": 1536}},
    "E768_M16": {"parameters": {"entries": 768, "merge": 16}}
  },
  "proposal_ids": [],
  "resource_constraints": {
    "max_parameters": {},
    "blocked_proposal_ids": [],
    "reason": "Attach actual source/RSS/risk evidence if imposing a hold"
  }
}
```

Retain accepted/proposed IDs in history to prevent repeated recommendations while
registration is in progress. Add every newly registered profile's exact parameter
identity to `history.profiles`. The first nine profiles have built-in identities.
Names cannot override built-in identities. Unknown profile metadata is rejected.

Each output proposal includes full35 `workloads`, exact `parameters`, one `cell`,
an immutable identity-derived `proposal_id`, `new_cells` for only unregistered
cells, phase/reason, common population, and logical resource costs. A cell already
registered with the same parameters/CH-or-DH/input is never silently resubmitted,
even if its earlier execution failed. The coordinator must verify the snapshot,
legal authority, source hashes and resource admission before any actual launch.

Run `qualify_adaptive.py` for CPU-only fixtures. No simulator imports, subprocesses,
SSH, budget changes or scientific registration occur in those fixtures.

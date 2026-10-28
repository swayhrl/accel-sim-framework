Primary large-target coverage V1: CPU-qualified candidate, not installed

Original aging source SHA:
b4e69ea06c017898ce9c5f5fcbb57cfb380ee47942c19cd88520abfaaf07d1ff

Only target choices and target sort key change in advance(). Every other line
of the existing advance is retained; see EXACT_ADVANCE_SELECTION_DIFF.patch.
Both CH/DH and P0/variants can be targets. Ranking retains never-started program
and first eligible age precedence, then prefers P0 when those are equal, then
uses input digest/cohort deterministically. No performance result is consulted.

Eligibility reads the existing actual pending rows, live ScopeSYNC authority,
MATRIX_CURRENT, registry admitted/consumed/sealed, canonical spec SHA and
current memory scope. Reference, preserved supplemental, typed-negative,
unknown/mismatched/unqualified identity, existing INTENT, claims and active
input are excluded. There is no additional saved cohort allowlist. Future
ScopeSYNC primary extensions become eligible through the same live sources.

Installation API (Main only after publication and independent review):
module.apply_in_owner()
Reverse: module.restore_in_owner(engine.assert_parent_lease)
Both run on the existing Main thread under the same aging.lock. Only the
existing state.advance instance callable is changed; state, chooser, provider,
FrameGuard, private CPU2/resource leaf, lock, claims and pool keep identity.
The ordinary function closure survives FrameGuard deepcopy/rollback without
copying bound self. Identity-source failures raise the actual installed
FrameUnavailable sentinel, so the existing guard rolls back and returns HOLD.
Restore removes the instance callable and returns to the original class method.

The75% strict-natural realized-release rule,25% backfill fence, PSS freshness,
feasibility and all RAM/CPU/pressure/disk/IO gates are unchanged. Installation
does not create retroactive completion credit or reset any aging state.

CPU_QUALIFICATION.json has17 focused checks, including real Lav identities,
negative identity kinds, variant protection, no-closure zero-credit, synthetic
natural75% credit and actual FrameGuard second-fresh rollback. All memory
releases in these fixtures are fictional and are not production credits.
No production install, hook, grant, model, consumer or signal was performed.

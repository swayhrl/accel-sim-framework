# Independent review: aging target coverage

The installed selector has a real coverage gap: `large_job_aging.py:37-39` permits only unspent DH-P0. After lavamd DH-P0 completes, its CH-P0 and eight DH factor variants cannot become protected targets. `BASELINE_REPRODUCTION.json` reproduces target=None/R=0 with the nine real fixed-snapshot identities. Its resource frame/costs are explicitly synthetic CPU inputs, not a production admission certificate.

## Minimal acceptable operational rule

Select one aged large target from the **existing pending pool**, after exact joins to the same live registry, primary MATRIX, canonical spec and qualification/route evidence. Permit CH/DH and every legally registered profile. Unknown, supplemental, initial-reference, correctness-only, unregistered, spent, sealed, claimed, INTENT-bearing or identity-mismatched rows must not silently become eligible. Never infer PRIMARY from a missing role flag: the original RuntimeFrames.pending contains no such flag. Use the existing authorities; do not maintain a second cohort list.

Retain the original age/large-size thresholds, active-input restriction and never-started-program preference. Give P0 priority only after equal program-start status and age, so an older variant is not indefinitely displaced by younger P0 work. Choose deterministically. Keep a current target rather than preempting it merely because a higher-ranked row arrives. Once a target is genuinely observed live or terminal, the next eligible row can be considered.

Only the target-choice predicate and tie-break key should change. Frame pending and ordinary backfill remain intact. The same state, lock, completion witnesses, seen-completion set, pending-release tokens, protected amount and prior margin must survive installation. Keep the 75% protected / 25% backfill rule, bounded actual positive margin, recent effective-future/anonymous-PSS witnesses and verified natural strict acceptance. Unknown failures, external frees, heap shrink, padding growth and repeated completions earn no invented credit. Preserve own-drain impossibility release, full claim accounting/virtual R=0, spent-no-retry behavior, CPU2, full forecast, source/disk/claim/pre-exec gates and all budgets/scientific identities.

## Current guard compatibility

Actual CPU2 library/owner, Tiny facade and ScopeSYNC sources were read. They pin immutable source files, current resource/chooser callables and existing aging/frames/gate/memory objects; no inspected guard pins `state.advance` or `state.__class__`. A private plain-function override on the same state can therefore preserve their identities. This source review does not claim fresh production-object introspection.

The existing FrameReadGuard is important: it deep-copies `aging.state.__dict__` before choosing and restores it on a second-frame read failure. An instance `MethodType` can be copied with a cloned bound self. Use a plain closure capturing the original state and keep it identical through deepcopy/rollback; do not replace the class, chooser or frame provider. Qualification must exercise the **actual FrameGuard** after advance followed by a second-frame partial JSON read, then confirm same state, same closure, unchanged prior credit/seen set and no double credit. Context read/identity errors should raise its real FrameUnavailable sentinel so the existing owner fails closed and rolls private accounting back, without killing healthy models.

The candidate must retain source pins and a reversible Main-only instance install. B is the sole candidate writer; this review copies and imports B source without changing it. Candidate QA is a private CPU test, not a production installation.

## Fairness and throughput effects

- Coverage extension can reserve memory for lavamd CH/variants and other large profiles that previously depended only on incidental fitting. It may reduce short-job throughput while accumulating genuine released capacity; this is the intended fairness tradeoff, bounded by existing 25% backfill and one target.
- The active-input restriction still serializes protected targets against live/claimed same-input work. The extension does not authorize launching all lavamd variants together or bypassing any RAM/CPU gate.
- P0 tie priority helps denominator dependencies without excluding variants. Current finite initial work prevents an infinite P0 stream; later dynamically registered points still need exact primary/authority joins.
- The existing RuntimeFrames age witness is shared from the original qualification epoch. This patch preserves it, so a later legally registered profile may already appear aged; do not describe that as thirty minutes measured since its own registration. Any future age-clock change is a separate disclosed operational choice.
- Own-drain feasibility and release credit are operational estimates bounded by observed safe-margin movement, not a mathematical guarantee against external allocations. Target coverage does not reduce a model's full forecast or canonical limits.

## Independent focused checks

`check_candidate.py` uses private fixture authority/resources, actual copied installed advance and actual FrameReadGuard. It checks CH-P0 and variant-only coverage; rejection of unknown/supplemental/stale-authority rows; spent/claim/active exclusions; bounded P0 priority; unchanged 75% natural release; failed-completion zero credit; closure identity through deepcopy; second-frame rollback preserving seen history; exact restore. It performs no model launch, signal, grant or production install. See source-pinned `INDEPENDENT_CPU_REVIEW.json` for the actual outcome rather than treating this proposed check list as a PASS.

**Final outcome:** 12 focused independent CPU checks PASS on B candidate SHA `af09621e85945e489d6022f1b22b6c8702374af8ad81d5e14945977fed039b57`, installed original SHA `b4e69ea06c017898ce9c5f5fcbb57cfb380ee47942c19cd88520abfaaf07d1ff` and actual FrameGuard SHA `c38a9cff23f18b8ecbd61e545cfbb775b19fe2ad732fb4ed80eee7e2851c93c2`. This does not replace B's actual native-context validation or Main's final installation review. An earlier unfrozen candidate syntax error was reported to B and fixed by B; its preimage remains separately named. An initial independent resource fixture lacked sufficient own-drain capacity for the intended credit test; adding its intended still-live witness made that test feasible. Neither correction changed production, B's frozen final source or the original credit algorithm.

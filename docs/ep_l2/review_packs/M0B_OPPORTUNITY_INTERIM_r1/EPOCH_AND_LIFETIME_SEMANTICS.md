# Epoch and Lifetime Semantics

Identity is `(Line-MSHR address, monotonically increasing allocation epoch)`.
A new accepted Line-MSHR with lower-read work replaces the map entry and
increments the epoch, so later address reuse cannot merge independent
incarnations.  The lower issue producer is `L2interface::push`; fill is
observed after native `mark_ready` processing.

| Milestone | Status | Meaning |
|---|---|---|
| allocation | `EXACT_SOURCE_EVENT` | accepted new Line-MSHR lower-read path |
| allocation → first lower issue | `DERIVED_FROM_EXACT_EVENTS` | allocation and actual `L2interface::push` timestamps |
| allocation → first fill | `DERIVED_FROM_EXACT_EVENTS` | allocation and native fill timestamp |
| allocation → all required sectors ready | `DERIVED_FROM_EXACT_EVENTS` | post-`mark_ready` pending-sector state |
| allocation → last lower issue | `NOT_EMITTED` | no one-shot final-issue source paired to retirement |
| allocation → final retirement | `NOT_EMITTED` | `commit_next_access` has no sidecar completion callback |
| last lower issue → final retirement | `NOT_EMITTED` | same reason |
| all-ready → final retirement | `NOT_EMITTED` | same reason |

Observed post-issue/post-ready lifetime is only candidate transferable
pending-state lifetime.  It is not proven avoidable MSHR lifetime.

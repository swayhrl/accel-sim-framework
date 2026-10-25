# R8 qualified pre-INTENT queue correction

The R7 host adapter successfully started ten original unused model cells on
distinct verified physical CPUs. While BFS-CM was still preparing and therefore
not yet in the consumed registry, R7 considered it pending again. The duplicate
future overwrote/removed its pre-fork reservation. The unchanged native guard
refused the original run before INTENT/model fork. BFS-CM has no consumed start;
the existing ten live model generations continue. The pre-fork issue evidence
is preserved here and is not a performance failure, zero speedup or budget refund.

R8 changes only finite parent scheduling, not the host execution adapter,
scientific runtime, memory accounting, model argv, input/config, hard caps,
Core/cache mechanism, strict parser or archive format. Pending selection excludes
both running futures and pre-INTENT claims, not just consumed cells. Recognized
resource HOLDs may defer30s ONLY if the exact cell has neither an INTENT nor a
consumed row. Once either exists there is no automatic model retry. Unique
per-admission metadata logs retain refused attempts. Cooling-down unstarted cells
remain part of the finite outstanding work and cannot cause premature closure.

R8 preserves the entire current139spent prefix, adopts each still-live original
frontend/strace/model generation without restart, and transfers only the parent
controller lease. Parent-only retirement is serialized against authority writers;
it is allowed only when every closed attempt already has a complete result and
all unresolved spent attempts are actual live native generations. No model or
frontend is signaled. The previously qualified R7 CPU-only lifetime/flock
transport remains the same stdlib/Linux operation.

The same HOST_CPU_CACHE_AWARE_V1 contract and maximum12 individually gated model
slots remain. R8 replays existing canonical archive and native-restore receipts
directly when available, avoiding duplicate immutable archive-log filenames.
New archives still use the epoch2 pinned outbox entry and real receiver/cohort
exclusion. Any unknown native/strict issue checkpoints without retry. All
original eligible cells, R6 Cutcp, exclusions/HOLDs and final full-Goal checks
remain required. This package records11zero-model checks and source publication
before activation; actual launch/parent-retirement receipts establish outcomes.

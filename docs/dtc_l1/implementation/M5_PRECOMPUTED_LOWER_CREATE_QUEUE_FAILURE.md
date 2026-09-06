# M5 precomputed replay lower-create queue recovery

Status: **ACTIVE RECOVERY — no M5.0BT/M5.0C acceptance claim**.

## Observed HARD failure

The exact trace-driven, frozen 80-SM / cap-10240 / ratio-zero precomputed
pool exposed the same fail-closed assertion in two independently captured,
immutable Paper bundles:

| Workload | Mode | Old runtime outcome | Exact assertion |
| --- | --- | --- | --- |
| ATAX | PAPER_IO | abort after 83.81 s | `shader.cc:2972`, IO lower-create queue capacity |
| ATAX | PAPER_OO | abort after 84.96 s | `shader.cc:3241`, OO lower-create queue capacity |
| MVT | PAPER_IO | abort | `shader.cc:2972`, IO lower-create queue capacity |
| MVT | PAPER_OO | abort | `shader.cc:3241`, OO lower-create queue capacity |

The preserved outputs are under
`/workspace/m5-precomputed-returned-80sm-cap10240-20260906/{atax,mvt}/{io,oo}`.
They are failure evidence only, never registry records or formal results.

## Source-backed classification

The M2 IO contract requires a DTC-owned **bounded** lower-request queue and
requires a miss/lower-request-queue-full stall category.  The old integration
called the frontend `access()` first; a `NEW_MISS` had already committed the
Tag-to-physical Pending allocation when it attempted to append the future
lower request.  When global lower credits remained unavailable long enough,
the candidate queue filled and the post-mutation capacity assertion aborted.

This is a source-reachable DTC lifecycle defect, not a trace corruption,
deadlock, output mismatch, workload checker failure, or permission to weaken
pending-write/scoreboard/accounting assertions.

## Repair

Core commit `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` adds non-mutating
front-end lookahead and performs capacity reservation before frontend
allocation.  A full candidate queue now yields the existing retriable
backpressure return (`BK_CONF`) and a separately reported counter:

- `DTC_L1_io_lower_create_queue_full_stalls`
- `DTC_L1_oo_lower_create_queue_full_stalls`

The reservation is exact for whole-line IO/OO misses.  Sector OO derives a
conservative request count from the requested invalid sectors before mutation.
Valid/Pending hits do not require a lower candidate and remain serviceable
when the queue is full.  The former post-access assertions remain in place as
internal safety invariants.

## Verification and invalidation

An isolated Release Core build passed all three existing DTC CTests:
`dtc_l1_m1_common_test`, `dtc_l1_bad_generation_test`, and
`dtc_l1_completion_accounting_test`.  An isolated trace frontend runtime was
then built from the exact Core commit and current Framework source; its binary
SHA-256 is
`796f0b4ad9299f434d6d7f1a2aa33b542d948a20361bd30f5798a0722d787a67`.

The next required evidence is exact-bundle ATAX IO/OO recovery past the old
failure point and natural terminal/parser/accounting closure; MVT IO/OO then
require the same treatment.  No legacy failed row, pre-repair Base row, or
old-Core triplet can be silently reused as a formal post-repair result.
Already-running old-runtime jobs are preserved as provenance/diagnostic
evidence and are not relabeled as repaired results.

### Identity invalidation scope

The repair is a Core behavior change.  Therefore all trace replay outputs
using pre-repair Core `120978646e4c8bae2707ddfc6b31512a4a0c76c8` are retained
as mechanism/diagnostic anchors only and are **not** silently promoted to the
post-repair formal identity.  This includes the previously qualified BICG T2
triplet and the still-running GESUMMV T3 triplet.  They may complete naturally
without interruption, but the repaired Core requires same-bundle replacement
triplets before those logical gates can PASS under the active identity.

ATAX IO/OO recovery replays were launched in the separate
`/workspace/m5-lowerq-recovery-80sm-cap10240-20260906/atax/{io,oo}` namespace
using that runtime and the unchanged ATAX bundle/config identities.  At 101 s
wall time, both had exceeded the old 83.81 s / 84.96 s abort window, remained
CPU-active, and had empty `simulator.stderr` with no assertion, fatal,
deadlock, or error signature.  This is an **old-failure-window recovery
observation only**; natural terminal, output, strict-parser, and accounting
closure remain required.

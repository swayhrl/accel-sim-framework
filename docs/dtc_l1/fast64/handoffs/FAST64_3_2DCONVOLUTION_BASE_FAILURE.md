# FAST64.3 — 2DConvolution/Base failed-attempt record

Status: **FAILED ATTEMPT PRESERVED; NOT A FAST64.3 RESULT**

The immutable historical-Core attempt
`fast64_3_2DConvolution_base_cap8192_a1_v2` naturally reached its terminal
receipt at `2026-09-10T12:50:39Z` with exit status `1`; it is not live and must
not be restarted, relabelled, or promoted.  Its immutable attempt UUID is
`844f1ba7-58a9-4208-98e5-71e01b1a6885`, Core/runtime are
`bbcbb5e...` / `6a8743b4...`, and its exact trace-list SHA-256 is
`23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64`.

The raw terminal diagnostic proves a simulator deadlock, not a timeout: after
approximately 2.33M current-grid cycles it reports no instruction commits on
cores 3, 29 and 51; 129 L1D latency-queue fetches remain
`MEM_FETCH_INITIALIZED`, with reserved conventional-L1 ways and reservation
retry diagnostics.  The runner captured a SIGABRT backtrace after the
deadlock detector, with no output/checker verdict available.

The adopted zero-access change is source-inert for PAPER_BASE because its
outer predicate is IO/OO-only.  Therefore a blind repaired-Core rerun cannot
be represented as a repair for this Base deadlock.  The next action is
source-backed root-cause/reproduction analysis of the conventional Base
reservation/lower-progress path; only an identified source-correct remedy may
create a fresh replacement namespace.  FAST64.3 remains ACTIVE.

## Prepared ownership diagnostic (not a formal result)

Core commit `1c69f97aac7cb7267faecb5d07658ee5321d6fd8` adds no timing or
mechanism change.  It extends only `baseline_cache::display_state()` so a
fatal dump reports every `m_extra_mf_fields` fill owner: root request UID,
block/address, cache index and sector-response `pending_read`.  This closes a
specific blind spot in the preserved dump, which showed four reserved ways but
not their corresponding fill-owner map.  The isolated Release build succeeded
at `/tmp/dtc-fast64-2d-fill-owner-YXYc7J/accel-sim.out` (SHA-256
`420423894d3561fe4b254dc5942d10932e4820d4841c09b3e6c0de2d37bde928`).

When a resource-safe slot becomes available, the directed diagnostic will use
the exact frozen 2DConvolution trace and Base configuration in a fresh,
nonformal namespace.  It will not replace or promote this failed attempt.
The dump will distinguish: (1) reserved lines with a live fill owner, which
requires tracing that owner's lower/response path; (2) reserved lines with no
fill owner, which localizes loss before/at cache ownership retirement; and
(3) a sector owner with nonzero `pending_read`, which identifies incomplete
child-response aggregation.  No functional repair or new formal result is
authorized until that observation supports a root-cause classification.

### Frozen source transition map for terminal classification (2026-09-11)

This is a source map, not a diagnosis.  The formal Core-95 to diagnostic-Core
`f2836ea1...` diff changes only fatal-state observability in
`gpu-cache.cc`/`shader.cc`; it does not change the following Base timing
transitions.  The future terminal analyzer must use the map to classify the
observed state before any repair is proposed:

| transition | source-backed state change | implication if terminal evidence shows the state |
| --- | --- | --- |
| first conventional read miss | `baseline_cache::send_read_request()` first obtains the L1 lower credit, then reserves/accesses the tag, inserts MSHR and `m_extra_mf_fields`, rewrites the root to atom size and appends it to the miss queue | A reserved line with no matching extra-field owner cannot be attributed to the lower cap alone; the observation must be traced across ownership creation, outbound issue, and final fill. |
| outbound injection | `baseline_cache::cycle()` removes only the miss-queue head after `m_memport->full()` permits `push()` | An owner still present with an empty miss queue requires inspection of the downstream/response route, not a rollback of the tag reservation. |
| sector response aggregation and final fill | `baseline_cache::fill()` finds the root owner, decrements `pending_read`, retains the root until the final sector, then fills the tag, marks the MSHR ready, erases the owner and releases the L1 lower credit | Nonzero `pending_read` is source-backed evidence of incomplete sector aggregation.  An owner present with zero `pending_read` is a response/fill-path observation requiring further evidence; it is not itself a repair decision. |
| frontend retry | `ldst_unit::process_memory_access_queue()` maps a conventional `RESERVATION_FAIL` to `BK_CONF` and deletes only its newly allocated request | Repeated `BK_CONF` proves retry backpressure but does not release a pre-existing reserved cache line, MSHR, owner, or lower credit. |

The table does not infer an owner-loss cause from a snapshot and does not
authorize changes to tag allocation, pending-write/scoreboard assertions, or
the frozen formal Core identity.

## Reproducible future-only dispatch preparation

`util/dtc_l1/dispatch_fast64_3_2d_base_diagnostic_v1.sh` was prepared and
dry-run validated without creating a run directory or starting a simulator.
It refuses a non-clean diagnostic-Core tree, a hash mismatch, or a preexisting
namespace. Its default `--dry-run` is read-only; its explicit `--dispatch
--cpu N` path uses the exact frozen Base config SHA `1a016e3c...`, exact
trace-list SHA `23bcc08b...`, atomic-receipt immutable runner SHA
`bf9a84c8...`, and a fresh namespace
`fast64_3_2DConvolution_base_coref283_diag_v1`.

The diagnostic binary is the clean observational Core `f2836ea1...` Release
build (`361aada1...`): it includes the prior baseline fill-owner dump and
adds only an OO deadlock-state print. This directed run is explicitly
`NONFORMAL_DIAGNOSTIC_NOT_RESULT`; it is deferred until a resource-safe slot
exists and must never displace the live Stage3/4 or FAST64.6 rows.

The accompanying read-only analyzer,
`util/dtc_l1/analyze_fast64_3_2d_base_diagnostic_v1.py`, accepts only a
terminal diagnostic stdout and a previously absent output path. It records
deadlocked cores plus each L1D reserved block, its matching root fill-owner
record (if any), and any nonzero sector-child `pending_read`. Its JSON is
observation-only and cannot select a repair, create a formal result, or
advance FAST64.3.

## Terminal diagnostic classification and repair boundary (2026-09-11)

The exact nonformal diagnostic reached its natural terminal state with exit
`1`; its immutable attempt UUID is `a970b692-22d5-441d-ad6a-faa500d9d573`.
The fail-closed, read-only collector was invoked once and published
`generated/fast64_3_diagnostics_v1/fast64_3_2d_base_coref283_diag_v1.json`.
Its classification is permanently `NONFORMAL_DIAGNOSTIC_NOT_RESULT`.

The dump gives the source-backed **B** classification: deadlocked L1Ds have
reserved tags but no matching fill-owner, while the ordinary MSHR and
miss-queue state is empty.  It is not sector-child aggregation (`pending_read`
is absent), nor an outbound-injection stall.  `BK_CONF` is a frontend retry
symptom, not the root cause.

Source inspection identifies the violating transition.  With
`gpgpu_flush_l1_cache=1`, `gpgpu_sim::cycle()` can call
`baseline_cache::invalidate()` when an SM has no runnable threads but before
its accepted conventional miss lifecycle drains.  `tag_array::invalidate()`
then removes the tag reservation without removing the corresponding
MSHR/owner.  A later MSHR merge can reserve a second tag, but
`baseline_cache::fill()` still completes through the original owner cache
index; it erases that owner/MSHR and releases its lower credit while leaving
the second tag reserved and ownerless.  This exactly matches the observed
terminal state.

The pending Core repair preserves the invalidation request, but retires it
only after the conventional miss queue, fill-owner map, and MSHR/ready-response
state are quiescent.  It changes neither DTC admission/arbitration nor
pending-write, scoreboard, lower-credit, or assertion semantics.  It requires
a separate Core commit, focused regression, fresh formal runtime identity and
a new immutable formal 2DConvolution/Base attempt before any FAST64.3
promotion.

Its isolated regression
`util/dtc_l1/test_fast64_3_2d_base_diagnostic_v1.sh` uses a versioned,
synthetic dump only.  It verifies the parser's owner-present, owner-absent,
deadlocked-core, and nonzero-`pending_read` paths while asserting the output
remains `NONFORMAL_DIAGNOSTIC_NOT_RESULT`.  It does not read or modify the
live diagnostic namespace.

## Diagnostic acquisition active (2026-09-10)

After Btree / 24-KiB / OO naturally completed, its CPU 34 slot was re-audited:
about 147 GiB `MemAvailable`, zero sampled memory PSI, no CPU-34 occupant and
115.6 GB output headroom. The hash-pinned dispatcher preflight passed, then
atomically published a fresh START receipt for
`/workspace/fast64-diagnostics/fast64_3_2DConvolution_base_coref283_diag_v1`.
It runs on CPU 34 with attempt UUID
`a970b692-22d5-441d-ad6a-faa500d9d573`, diagnostic Core `f2836ea1...`, binary
`361aada1...`, the frozen Base config/trace and classification
`NONFORMAL_DIAGNOSTIC_NOT_RESULT`. It is an observational reproduction only:
it cannot replace the preserved failed attempt, enter any formal collector or
advance FAST64.3. It will be allowed to reach its natural terminal state.

`collect_fast64_3_2d_base_diagnostic_v1.py --collect` is a separate,
fail-closed, read-only terminal collector for this exact attempt UUID. It
refuses any manifest/receipt/binary/config/trace/Core mismatch, never launches
or signals a process, and accepts terminal exit 0 or 1 only as a diagnostic
observation. Once the immutable TERMINAL receipt exists, it invokes the
ownership analyzer to atomically publish an observation-only JSON; that JSON
is not a FAST64 result and cannot advance a stage.

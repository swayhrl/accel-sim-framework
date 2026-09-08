# C10B final report

Final state: `C10B_HARD_BLOCKER_WITH_EVIDENCE`.

C10B-0 through C10B-5 passed. The final full link bound Framework `b0926503`
to Core `5b409493`; its binary SHA-256 is
`74307f3a9b975300e469a7768be1324444c927498e3b19d40d39dc326df31345`.
The standard M1--M3/M4C regression suite passed. Directed C10 tests passed
non-identity mapping, atomic registration rejection, 35-replica lifecycle,
READ/WRITE/ATOMIC routing, HIT_FIRST/MISS_JOIN, one lower launch, retry/no
re-probe, mismatch failure, stale exact/sub-entry outcomes, F0--F9 selection,
G96/G32 geometry, and permanent H0 rejection.

C10B-3 verified emitted telemetry instead of source fields alone. A final
binary bounded three-kernel F8 run using existing immutable decode1 input
passed its parser: 35 replicas, N=8, Lseg=10, 512 Segment hits, no mapping
mismatch, one MSHR with 15 merges, 4/4 PTE traffic, drained queues and exact
object-attribution conservation. This is a bounded correctness observation,
not performance evidence.

C10B-4 faithfully realizes C9 F5 as a separate 120-entry physical pointer
PWC (40/40/40, four-way, one port/queue) plus E=656 exact remainder for
64,745 charged bits. Directed emitted telemetry validates the geometry,
payloads, port pressure, replacement, flush and drain. C10B-5 validates every
executable fair arm and F7/F8 latency points 5/10/20; these too are not
performance conclusions.

The Goal stops because C5 preflight cannot bind prefill candidate arms without
inventing prohibited C10 provenance: the C workspace has no prefill V2
privileged non-identity registration and no immutable prefill trace-list. The
old prefill V1 identity map and object map are insufficient by C9. This is an
evidence/provenance hard blocker, not a request to start C5 or to modify the
architecture. Decode1 has valid bounded provenance, but partial ROI
availability cannot be silently promoted to the requested prefill+decode C5
matrix.

`SPECULATIVE_CANDIDATE` and `REFERENCE_APPROX_SUBENTRY_16` remain unchanged.
No C5 replay, KV segmentation, 12K, M5, or Window-A/B operation was performed.

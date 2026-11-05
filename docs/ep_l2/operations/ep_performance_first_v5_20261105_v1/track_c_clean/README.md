# V5 Track C: real production handshake prototype, incomplete quota integration

This advances beyond the V4 independent Python transaction model. It modifies a private, separately administered Core clone and builds actual production C++ cache, memory-partition and DRAM paths. It does not install a shared Native entry, register a budget or start an application model.

The old bf4 Core and bab27c ELF remain unchanged. Their CPU/parser evidence and the V4 12 directed groups plus 3,185 two-row combinations are indexed for reuse, not rerun. New tests address new reservation, completion and clock/queue wiring only.

## Actual implementation

core_candidate/src/gpgpu-sim/ep-l2-quota-row-port.h implements fixed K=1/2 slots and an explicit L2-domain READ followed by a nonoverlapping COMMIT. Same-row collisions refuse the second intent, prepared slots block new READ batches, and cancelling a reservation does not refund its READ beat. Repeated faster-DRAM callback polls cannot advance the L2 tick or acknowledge anything. UID, row incarnation, payload generation and state form the grant identity.

lower_ready must obtain metadata service before the original miss-queue head can be erased or pushed to the lower memport. Bank data service remains separately charged. lower_accepted uses the prepared identity and consumes the grant during the actual existing row transition. There is no push-then-HOLD path.

Production set_done now returns readiness. A refused completion retains its original packet, request tracker and arbitration credit. The subpartition commits its row and tracker before the partition returns credit; callers delete/pop only on success. Detailed DRAM places WB completions into its existing bounded return queue, without introducing an invisible completion FIFO. Simple DRAM retains its existing finite latency-queue head. This incurs real return-queue occupancy and head-of-line stalls.

The completion CAM is paid once at READ and its single finite cached ticket/context is reused at COMMIT. It is not queried once for preflight and then queried again for free. Physical circuit CDC and clock closure remain unqualified.

## Honest completion boundary

This is a PARTIAL production prototype, NOT a completed costed CLEAN-quota implementation and NOT eligible for a scientific application start.

Only lower-WB acceptance and WB completion are connected to the row-service governor. They have zero CLEAN-count delta. Frontend installation, clean replacement, reclaim, promotion, reader pin/retirement, rollback and epoch cleanup still use their original synchronous paths. The C++ ordered signed net-delta reducer is tested but has not replaced those actual production count writes.

No full-pipeline atomicity, quota-update throughput, six-producer fairness, timed cleanup, complete generation/rollback integration, physical CDC or PPA claim is made. The original generation/incarnation, payload pin, sector-version and WB-UID invariants remain; preserving them is not proof that future asynchronous integration is complete. No Core862 repair/source qualification is inherited.

A complete implementation must reserve every affected tag/allocator/MSHR/lower resource before destructive mutation; publish all row/count deltas together; handle more than K intents through a qualified multibeat transaction or HOLD; charge reader/retirement/cleanup service; and prove cancellation and credit conservation at every origin. An unavailable metadata port after an externally visible enqueue is unacceptable.

## K=1 versus K=2 cost

K1 can serve at most one row in two L2 beats. K2 can serve at most two different rows in two beats when both are ready. Downstream waits extend the batch; K2 speedup is not guaranteed. K2 requires two selected-row metadata read/write paths, decoder/mux/write-enable and arbitration resources, or conflict-aware banking. The existing four payload banks/P1 do not supply free metadata ports.

A pending key needs at least 185 logical bits per row slot under the recorded widths. One completion context is bounded to one existing packet identity and selected incarnation. The proposed CLEAN commit uses one signed counter lane: 8-bit count/cap, 3-bit K2 net sum and 9-bit projected intermediate. These are logical minima, not synthesized area. The actual nonzero counter commit path remains missing. Tag geometry, Payload 1168/slice, four data banks/P1, WAD/TVD 128, D512 and lineMSHR128/merge32 remain explicit invariants of the proposed scientific profile.

## Source, qualification and requests

PRIVATE_SOURCE_COMMIT.json, final SOURCE5_BUILD_IDENTITY.json, PRODUCTION_CPU_DELTA_RECEIPT.json and PRODUCTION_IMPLEMENTATION_BOUNDARY.json distinguish the new private Source from unchanged bf4. New option -gpgpu_ep_l2_quota_row_lanes has 0 legacy/off, 1/2 engineering prototype. A prospective formal profile would add this option to the prior 283 fields; full echo/Host/Native mapping is not qualified.

No CLEAN scientific request is ready now. After complete production integration and bounded mode/Host/Native qualification, prepare a newSource FWT cap128 baseline of exactly 1 start first. Later cap64/0 would be a separate exact 2-start request under the same Source/input/resources. K1 comparison and GEMM expansion need their own evidence-based scope; no automatic six-point sweep. Old bf4, Source78 and Core862 performance cannot be denominators for this new Source.

Application NI and B0/M0a remain unproved within their actual scope. Physical PPA is not made a blocker for unrelated A/B/D engineering, but unresolved functional reservation/rollback/cleanup gaps are genuine C admission blockers.

Large build products/logs are on genuine164. Native has a 5GiB actual floor. Source KEEP, deletion 0, model starts 0, Native consume 0, scientific budget registration 0, shared route changes 0, Git remote publications 0.

## Final measured engineering result

New private Core: bf0727871db05bec266099e703a551b02180eabb. ELF SHA256: aff0d05ac6bfb60abe77f8a12e5300c68b39f2504ab0f5526367dee9b941782e. libgpgpusim SHA256: 3757ab2e47a9e7694bbf71194c545bfec1e0dedec580a41ab7c7800e7f751e61. Full consistent build PASS; no target has NDEBUG. Four new production cases PASS, each 22 row ACKs with complete packet/credit/tracker drain. K1 and K2 both required 139 L2 ticks in the simple-memory case and 140 in detailed DRAM, with 3 DRAM polls per L2 tick. K2 gave no gain in this bounded sequence. This is useful negative engineering evidence, not application cycles. The independent C++ component demonstrated the two-distinct-row K2 batch; the selected production sequence did not reach a paired batch. A second metadata port should therefore remain a costed alternative, not an assumed requirement.

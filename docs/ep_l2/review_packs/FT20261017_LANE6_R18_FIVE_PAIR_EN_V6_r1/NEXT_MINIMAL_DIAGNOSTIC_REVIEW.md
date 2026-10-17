# Proposed minimal diagnostic — review only, NOT authorized or executed

The present WB-only speedup case is weak: five fixed development inputs give
1.0016002037656606× geomean B16/U-WB16 and include CFD regression. Copy removal
and local staging relief are observed; independent elasticity speedup and the
limiting downstream resource are unresolved. Keep all five results, not only
the positive ones. No new config file, launch spec, build, lease or simulator
is created by this proposal.

## One controlled variable and a bounded matrix

Propose changing **only L2→DRAM queue depth per slice**, 128→256, symmetrically
for B16_BANKED and U_WB16. The effective current option is
`-gpgpu_dram_partition_queues 64:128:64:64`; a proposed, unapproved value is
`64:256:64:64`. Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`,
`src/gpgpu-sim/l2cache.cc:975` maps the second component to `m_L2_dram_queue`.
Keep the other three queues, DRAM scheduler/return queue, latency/bandwidth,
clocks, credit policy, 1168 L2 slots, banks, tags, WAD, descriptors and trace
bytes unchanged. This is finite buffering headroom, not ideal memory service.

| Workload | B16/original | U/original | B16/256 | U/256 | Reason |
|---|---|---|---|---|---|
| convolutionSeparable | Existing accepted | Existing accepted | Proposed | Proposed | High WBUF pressure and higher U downstream denials |
| FWT_7_21 | Existing accepted | Existing accepted | Proposed | Proposed | Strong pressure shift despite low aggregate model bandwidth fraction |
| cfd_097k | Existing accepted | Existing accepted | Proposed | Proposed | Regression/ordering counterexample; no recorded L2→DRAM-full attempts |

Twelve cells total; six are existing immutable accepted runs, at most **six new
full runs** after approval. First priority is Convolution/FWT (four new cells);
CFD remains predeclared as the two-cell counterexample, not dropped if flat or
worse. Do not add an Ideal matrix, search queue sizes, replace inputs, or tune
DRAM timings if the first comparison is neutral.

The exact frozen binary is SHA256
`23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`;
Framework producer `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`.
Existing V2 launch certificates admit only the original exact configs. Therefore
the proposed configs **cannot run under current authorization**. Before any
launch: user approves the science/resource change; Lane5 independently verifies
the actual option's physical meaning, queue-entry/data-carrier/credit coupling,
same-binary support, byte ordering and lossless/full/drain/exact-once behavior;
then publishes explicit new config identities and launch qualification. If the
option implicitly enlarges credits or another structure, stop and revise the
proposal rather than call it a single-resource test.

Extra buffer capacity is +128 queue entries/slice = +8192 chip entries. Their
carrier, pointer/transaction, tracking and occupancy storage are not free; derive
an explicit hardware representation and bounded host-memory/output budget before
approval. No C++ sizeof-to-area conversion. This diagnostic is not an equal-PPA
competitor. Current 48GiB+2GiB build gate, 64GiB available-memory / Share40GiB
production policy and max-two-long-run limits stay intact; original Lane5 owns
any future experiment only after a new explicit authorization, with other
projects protected. This document does not restart that completed Goal.

## Predeclared question and interpretation

For each workload let `S(q)=cycles_B(q)/cycles_U(q)` and compare
`I=log(S(256))-log(S(128))`. Use matched whole native commandlists and the same
termination scope; retain exact cycles and instruction counts. A larger positive
interaction together with reduced U downstream pressure would support the
headroom hypothesis in this controlled model. It would not establish general
GPU speedup or significance. A reduction in blocked attempts with unchanged
cycles suggests those denials were not the critical service delay; an unchanged
interaction must be retained. Capacity alone does not improve DRAM service rate.

Collect exactly the existing full native parser/64-slice closure, WB created/
lower-accepted/completed, copy/send-read/rollback, model bank grants/logical ops/
conflict waits, WBUF/pool/WAD-full and WAD-hazard events/waits, eligible issue
attempts and all downstream denial fields. For all32 channels retain the **last
application-cumulative** scheduler/return occupancy/full-channel-cycles and
successful bytes/issues; cross-check with64-slice byte totals. Never sum repeated
kernel-boundary snapshots or subtract cumulative denials from global cycles.
Channel averages may hide hot partitions/banks, so retain the32-channel records.
Absent service-latency attribution remains absent; do not infer it from events.

For CFD, the current clues are169 extra U cycles, WAD-hazard9841→13400, actual
WB31123→31063 and write bytes3983744→3976064. Queue relief may have no effect;
that is an informative negative outcome. Existing logs do not provide a complete
per-transaction critical path. If ordering needs new event attribution, propose
a separate source/instrumentation qualification before adding it, rather than
modify the frozen binary or label the hazard count as the cause.

## Separate equal-total static control — also pending review

The proposed resident/bypass/WB split `1024/112/32` sums to1168 slots,146KiB per
slice. Per bank this is `256/28/8 =292`, against B16's `256/32/4 =292`. Preserve
1024 visible tags,4 physical banks,1 op/bank/physical cycle,128B copy latch,
128 WAD,512 descriptors and the original queues. Copy remains explicit in this
static design. Define eligibility, backpressure and rollback before coding.

The frozen 8/16-WBUF interface does not implement this quota split: selecting
WBUF32 naively produces1184 slots. Thus it requires a separate exact source,
binary, config, capacity/bank/lifecycle gates and independent scientific
qualification. WBUF8 has1160 slots and cannot substitute. Comparing a newly
implemented static control with U must use a common qualified binary and keep
runtime cost/latency differences explicit. No implementation or experiment is
performed here.

## Research decision

Do not present WB-only as an established application accelerator. If the bounded
interaction test remains near neutral, narrow the claim to the ownership/copy
mechanism and its service tradeoffs, or evaluate TVD/RO as separate independently
qualified mechanisms. Do not seek favorable inputs or suppress CFD/SAD. Strong
static controls and real RTL/macros/STA/power evidence remain separate gaps.

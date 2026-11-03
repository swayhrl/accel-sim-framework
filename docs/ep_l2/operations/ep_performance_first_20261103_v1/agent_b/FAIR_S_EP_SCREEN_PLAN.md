# System performance screen and fair S/EP contract

Status: engineering candidates; 0 new model starts, 0 budget writes. Main remains the sole scientific entry and integrator. This package does not grant science permission.

## Decision

Start with the existing Source78 DRAM service family, after family-specific CPU/Host/native qualification and user approval. This can test system headroom while new local-bank/metadata structures are engineered. It avoids waiting for a new Core. Reuse the 45 exact historical system-background pairs before scheduling repeats.

Proposed first6:

| Input (identity prefix) | Exact treatment | Modes | New starts |
|---|---|---|---:|
| FWT fc3a9062 | DRAM850 ->1020MHz | S / WV_ZERO_RO |2|
| GEMM 140f6ed3 | DRAM850 ->1020MHz | S / WV_ZERO_RO |2|
| Vector4M ddf26d4f | DRAM850 ->1275MHz | S / F |2|

All other effective options remain bit-for-bit equal to each accepted reference. Clock strings are 1132.0:1132.0:1132.0:1020.0 or :1275.0; L100, Tag32x8, 64 slices, 32 channels, physical1168 payload, P1, D512, WAD128 and MSHR128 remain unchanged. FWT is WV_ZERO_RO, not a fabricated RO-F. Each point's preview contains the full actual282 keys, precise original Source5, input identity and observer environment. A preview is not a frozen runnable spec: Main must bind new scope/profile, qualification and sole-entry authority.

DRAM1020 is a finite architectural resource candidate with physical power/timing/area unknown. It is not a claim about the original GPU. DRAM1275/1700 are explicitly DIAGNOSTIC_RELAXED. The DRAM timing integers remain fixed in DRAM cycles, so raising the DRAM clock changes both service bandwidth and nanosecond bank timings. This tests a service family, not isolated bus bandwidth.

## What is already known, without reruns

The accepted Source78 Vector4M1020 pair accelerates absolute S 1.177986x and F 1.173868x vs each850 REF; matched S/F remains0.995820x. Conv1020 gives absolute S1.067237x and F1.075707x, matched S/F0.996344x. Thus DRAM service has substantial application headroom, but those points alone do not establish an EP-specific benefit. They are inputs to exploration, not a reason to terminate the service family.

Old L2MissQ256 on Conv gives absolute S1.009045x/F1.004199x; Vector ICNT512->1024 leaves F unchanged and S+0.184%; old lowerFIFO256 is close to neutral. Do not repeat these exact pairs. Reuse JSON/CSV includes 45 pairs with accepted point/spec/archive hashes. Existing geometrical combinations are context, not single-factor isolation.

## Adaptive continuation candidates, for a range authorization

These are proposed cells, not automatic budget:

1. Within DRAM family, FWT/GEMM S/WV1020 may proceed to1275 (4 starts) if either absolute EP gain is at least3%, or the matched EP ratio improves at least1%, or clear service pressure remains despite positive first-point gain. Preserve results where both S and EP improve equally. At most one subsequent1700 diagnostic pair per retained input, only after1275; do not skip qualification.
2. Vector4M1275 may proceed to1700 (2 starts) if absolute S or F still gains at least3% vs1020. The intended question is remaining memory-service headroom, not causing extra detaches.
3. FWT/GEMM L2MissQ128->256 S/WV (4 starts) is the first finite-queue continuation only where existing accepted B0 shows nonzero relevant MissQ/full rejection. If256 remains saturated or yields at least2% absolute EP gain, prepare512 pair. If the queue is not exposed or response is near zero and saturation absent, prune.
4. FRFCFS128->256 or ReturnQ192->384 only when their own accepted causal/occupancy evidence supports the family. Treat credit coupling explicitly. Do not launch all Cartesian combinations. At most one two-family interaction for a given workload after both retained individual effects, with same-background S/EP controls.
5. Stencil/Scan are medium/long validation after fast-screen families survive. Current StencilWV is protected and must finish naturally; never restart it for this package.

The number of cells is a consequence of the selected range and staged releases, not an arbitrary global limit on the research goal. Main can submit a revised exact family range where evidence supports additional density. No unapproved cells, retries or refund.

## Fair comparisons and acceptance

For each q, report S_REF850/S_q, EP_REF850/EP_q, matched S_q/EP_q, and (S_q/EP_q)/(S_REF850/EP_REF850). The first two measure absolute application potential; the latter two distinguish EP-specific release from a faster system. Report absolute cycles as well as ratios. Keep S and EP on the same exact source/ELF, clocks, geometry, physical payload, banking, queues and input.

S and WV/F differ only by their formally defined mode flags and required RO binding. S's static resource roles remain its historical formal model; no weakening of S. Reference reuse requires exact Source5/input/geometry/observer/mode acceptance with archive closure. A new source for P2/D/MSHR requires new-source REF anchors; oldSource78 results remain a separate series.

Instructions/CTA/kernel commandlist, drain/ownership/generation invariants, limits and numeric-output UNKNOWN boundaries remain unchanged. DRAM lower-admission byte counts are not renamed completed memory bytes or real bus utilization.

## Qualification status and actual checks

PASS: existing tiny accepted-summary reuse; exact Source78 source inspection; six282-option previews; 12 offline plan-builder positive/negative controls. PASS: four actual calls to frozen mode_contract.check_background show oldREF accepted and new clock/profile/MissQ refused. No guard was changed. These are configuration-engineering tests, not production constructor/drain or application NI.

PARTIAL: production supports finite queue/clock/latency options. NOT_QUALIFIED: new family Host/native profiles. The current W runtime explicitly requires REF32x8_L100 and identical background. Main must implement an explicit family allowlist, not bypass check_background/validate_anchor. New S_q reference must match EP_q hardware; oldS850 is an absolute REF, never the matched S_q control.

MSHR, descriptor/merge and P2 in WV/F require a new Core. Source78 gpu-cache.h3340,3347,3355,3373 pins MSHR128 and D512, and3347 pins merge32/P1 for RO. ep-l2-ro-transactions.h86 also requires D512/exact1168. The nominal cache A:128:1 merge field is not the effective descriptor cap: gpu-cache.cc721-726 uses32 with D512. Do not assume changing nominal merge1 is a meaningful M/T experiment. Agent A owns bank/V changes; Agent C owns RO capacity/protection.

Payload data-free diagnostic is distinct from P2 and can only test a limited local-bank upper reference if exact mode CPU/Host qualification passes; it is not real hardware or an infinite-memory bound. Queue0 is excluded from the first scope because production also makes partition credits unlimited.

## Resource and runtime

Read actual historic DONE: FWT S/WV826.6/893.5s, peakRSS~0.65GiB; GEMM4435.6/4525.9s,~3.75GiB; Vector4M705.3/817.2s,~0.5GiB. Six points cumulative historical process time~3.39h, about1.7h ideal two-slot wall, operational estimate about2h plus engineering qualification/admission. FWT and Vector are short; GEMM is medium. Use fresh actual load/foreign commitments, not old2h/4h forecasts as rigid reservations. Scaling may change simulation workload and host wall time.

Observed peak hot outputs were below4MiB each for these references. Main should derive a bounded cap from observed compressed raw and validation sizes with actual safety margin, hold one sequential restore workspace, and retain about1GiB emergency SSD floor plus foreign-owner guarantees. No repeated large pool per point. Increasing host queue entries adds pointers/metadata; measured model RSS and plan-specific growth govern admission. Large traces/results stay true164, no Trace copy or repeated body hash. At most two formal EP models concurrently; read input authority once through existing verified identity chain.

## Implementation notes for interpretation

Partition tuple is icnt->L2, L2->DRAM, DRAM->L2, L2->ICNT (l2cache.cc993-998). Fixed-latency deadline is GPU-cycle based and actual residence also includes later scheduler eligibility. FRFCFS and ReturnQ capacity jointly determine shared partition credit: 128+192-1=319 baseline, FRFCFS256 gives447, ReturnQ384 gives511 (l2cache.cc478-486). Changing either cannot be described as perfectly isolated scheduler/return service. ICNTnetwork_mode2 is local crossbar; in/out512 are local buffers, not BookSim mesh VC capacity.

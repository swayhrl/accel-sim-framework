# Target Baseline interim bottlenecks (22/26)

Provisional only: 11 completed Legacy/Banked pairs at 850 MHz.  All values use Core `200cb485c2fe27a7b0a867d2f173b63582fcaece` and Framework `81b9dfbc0c567590fc35724cbec94ade1d3f6aa9`.  Four long runs remain outside this analysis.

## Per-workload observations

| Workload | Dominant observed blocker | Secondary | High-util but not proven blocking | Legacy → Banked | Classification |
|---|---|---|---|---|---|
| vectorAdd_4M | DescriptorPool | Lower path | line-MSHR max=92/128; full-event telemetry not emitted | 1.005x cycles; bank conflict rate 0.5000 | metadata-bound |
| spmv | Payload | Bank | line-MSHR max=97/128; full-event telemetry not emitted | 1.011x cycles; bank conflict rate 0.5000 | mixed |
| convolutionSeparable | DescriptorPool | Payload | line-MSHR max=125/128; full-event telemetry not emitted | 1.015x cycles; bank conflict rate 0.5000 | metadata-bound |
| cfd_097k | Payload | Bank | line-MSHR max=69/128; full-event telemetry not emitted | 1.048x cycles; bank conflict rate 0.5064 | mixed |
| dwt2d | Payload | Bank | line-MSHR max=60/128; full-event telemetry not emitted | 0.999x cycles; bank conflict rate 0.5000 | mixed |
| sad | Payload | Bank | line-MSHR max=7/128; full-event telemetry not emitted | 0.998x cycles; bank conflict rate 0.5000 | mixed |
| sgemm | Payload | Bank | line-MSHR max=23/128; full-event telemetry not emitted | 1.005x cycles; bank conflict rate 0.5000 | mixed |
| btree | Payload | Bank | line-MSHR max=60/128; full-event telemetry not emitted | 1.010x cycles; bank conflict rate 0.5000 | mixed |
| gemm | Payload | Bank | line-MSHR max=76/128; full-event telemetry not emitted | 1.207x cycles; bank conflict rate 0.5000 | mixed |
| FWT_7_21 | Payload | Bank | line-MSHR max=104/128; full-event telemetry not emitted | 1.145x cycles; bank conflict rate 0.5000 | mixed |
| FWT_11_19 | Payload | Bank | line-MSHR max=97/128; full-event telemetry not emitted | 1.079x cycles; bank conflict rate 0.5000 | mixed |

## Required interim questions

* **btree/shared descriptor model:** the legacy fixed-merge-fragmentation counter is not in EPL2B0V1; do not claim a direct before/after disappearance.  Current descriptor occupancy/block events are reported in the CSVs.
* **128 line MSHRs:** max occupancy is measured, but no explicit LINE_MSHR_FULL event is emitted; no fullness claim is inferred.
* **256-descriptor pool:** `descriptor_max=256` plus descriptor blocker events is evidence of pool pressure, not a claim about a per-address cap.
* **32/address cap, WAD hazard, Tag/Set:** per-address, hazard, and tag/set blocker counters are not emitted.  WAD full blocker is emitted and remains separately reported.
* **B0-Banked attribution:** the overlay diff is limited to payload mode (`1` Legacy versus `2` Banked); base-config and trace hashes match within every pair.  A material cycle change is still marked `ATTRIBUTION_WARNING` because EPL2B0V1 lacks arbitration-wait and operation-type telemetry needed to close causal magnitude.
* **L1 and lower ceiling:** only aggregate L1 and lower blocker events are emitted; detailed L1 component and DRAM scheduler/BW attribution are not fabricated.

## C5c terminal sanity

| Gate | PASS runs | Notes |
|---|---:|---|
| descriptor lifetime | 22 | terminal descriptor_used=0 |
| WAD | 22 | terminal wad_live=0 |
| payload owner/generation | 22 | owner consistency=1, double owner=0 |
| pending sector | 22 | resident_pending=0 |
| bank no-loss | 22 | bank_pending=0 |
| stale-fill count | NOT_EMITTED_BY_EPL2B0V1 | no explicit counter in EPL2B0V1 |

No C5c terminal invariant failure was observed in the 22 completed runs.

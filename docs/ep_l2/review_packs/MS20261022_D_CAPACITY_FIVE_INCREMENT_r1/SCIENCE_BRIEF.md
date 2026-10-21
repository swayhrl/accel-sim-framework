# Scientific decision brief: complete five-pair joint diagnostic

## Accepted results and increment

| Input | OFF cycles | ON cycles | ON−OFF | Speedup OFF/ON−1 | ON class |
|---|---:|---:|---:|---:|---|
| Conv | 292,932 | 268,117 | -24,815 | +9.2553% | UNKNOWN |
| CFD | 79,093 | 79,742 | +649 | -0.8139% | UNKNOWN |
| DWT | 166,519 | 157,034 | -9,485 | +6.0401% | UNKNOWN |
| SAD | 110,773 | 110,634 | -139 | +0.1256% | UNKNOWN |
| Vector | 73,696 | 42,788 | -30,908 | +72.2352% | UNKNOWN |

The fixed-five geometric mean is 1.1465847062× (+14.6585%). This is diagnostic headroom in a joint intervention, separate from MAIN. No outcome is excluded. The unchanged five-input main61 S/F GM is 0.9977331348587999×; the original-seven MAIN denominator remains incomplete/UNKNOWN. Old Vector MAIN and DWT MAIN negative results, Btree HOLD, FWT incomplete records, and all old failures are preserved.

E's CURRENT_ACCEPTED records bind full instructions, kernel order, 64 slices, normal native exit/wait and hardware drain. D projects these identities; it does not regrant native qualification. See E_SOURCE_INDEX and the exact ten identity objects, including config, source, binary, trace, qualification, run-key, endpoint receipt and raw hashes. Four old pairs are reused byte-for-byte from D's accepted_snapshot_04; only Conv is new.

## Conv: measured facts

Conv OFF/ON is 292,932/268,117 cycles: 24,815 fewer cycles, +9.2553% speedup, or an 8.4712% cycle reduction. Both accepted endpoints contain 714,547,200 instructions and two kernels.

| Elapsed phase | OFF | ON | ON−OFF |
|---|---:|---:|---:|
| K1 convolutionRows | 161,236 | 158,906 | −2,330 |
| K2 convolutionColumns | 131,696 | 109,211 | −22,485 |
| Final residual | 0 | 0 | 0 |

K2 accounts for 90.6105% of the observed elapsed reduction. This partitions measured application time; it does not partition exclusive bank stalls or causal mechanism savings.

Conv terminal logical copy reads and writes each fall 546,865→0, and physical bank grants 9,217,033→0. Lower-interface reads fall 2,359,526→0 (75,504,832→0 bytes), and WB bytes fall 69,787,264→0. OFF WB-created/lower-accepted/completed counts are each 546,865; ON counts are each zero. These are service-accounting events; zero lower WB traffic does not mean hardware drain flushed dirty resident lines to DRAM, nor does it prove numerical host output equivalence.

K1/K2 lower-read reductions are nearly equal: 37,756,096/37,748,736 bytes. Eliminated physical grants are 4,509,709/4,707,324, and eliminated logical copies are 252,901/293,964 per direction. Nevertheless, elapsed savings differ by almost 10×. Event volume alone does not establish critical-path importance.

Reported first-block admission request-wait sums fall 2,725,714→0; copy/data/MissQ/same-address-WB/WB-space wait sums fall 546,865/433,239/180,063/638,854/848,913→0. They overlap across requests, slices and causes and cannot be added into GPU program stalls. V/RO query and landing wait fields are zero in the observed traditional-S path; feature-disabled or absent V/RO counters must not be promoted from UNKNOWN to measured service zero.

Each endpoint separately has exact requester/response closure: OFF 5,216,912/5,216,912 and ON 5,202,476/5,202,476. The cross-run requester population differs by 14,436 despite the full matching instruction stream, so there is no one-to-one cross-run request timing proof. Host simulation wall time also rises (about 2,527→8,884 s); host simulator cost is distinct from simulated GPU cycles.

## Interpretation classes and identification limits

**Source-derived interpretation, reused rather than re-audited:** the previously frozen host-prefill excerpt from Core fe7e1fc1 shows untimed initialization of matching Tag/payload state, not a forced read-hit mode. Expanded residency plus prefill can remove later lower reads. Final Conv resident_or_fill slots are 65,536→884,737 across slices; this supports retained residency, not a capacity-only causal estimate.

**Measured resource boundary:** ON enlarges finite resources (64× designated capacities) and sets l2_data_free. Other ideal switches, including forced read-hit, remain OFF; Unified/V/RO remain disabled. Conv's covered Tag high-water is 13,825/65,536 per slice (21.0953%). MissQ full-check coverage is absent for all 64 slices in every ON run, so all five classifications remain UNKNOWN even where high-water/refusal fields print zero. Native ROP storage is outside the enlarged vector (Conv observed slice high-water up to161); this is not removal of every L2 constraint.

**Testable causal hypotheses, not proven conclusions:** altered residence, eliminated data-service waits and changed downstream issuance can change overlap/queue timing, with Conv K2 more exposed than K1. The joint intervention cannot identify their independent contributions. No new runs are requested or authorized by this analysis. A lower-event reduction is not a GPU-stall budget, and the two kernels' counter savings are not copy-benefit shares.

## Five-input synthesis and retained adverse evidence

CFD still adds649 cycles: K4+5 and K5+644; lower reads decline only212,308→206,448 while WB bytes fall3,983,744→0. Fewer lower events do not imply positive timing change. DWT saves9,485 cycles (K1/K5/K8 save8,773), preserving adverse K9+6 and K10+1. SAD saves139 (K3−40, final residual−99), with its two earlier phases unchanged. Vector saves30,908 (kernel−30,769, residual−139). These are elapsed-stage observations, not a causal assignment to a single resource.

The fixed-five rollup addresses measured joint diagnostic sensitivity. It neither repairs missing original-seven MAIN inputs nor replaces any complete-F result, and it is not a hardware upper bound. EN-v22 remains untouched.

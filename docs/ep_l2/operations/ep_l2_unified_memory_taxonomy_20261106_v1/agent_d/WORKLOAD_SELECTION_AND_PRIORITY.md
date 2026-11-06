# Workload selection and priority V1

The next development set is broader than Vector4M and is selected from observed behavior, not from its final speedup.

## First scientific request: pressure-positive candidates, four starts

Conv3072 and Scan are independent input families; Core812 Fbaseline/Fpressure pairs at850/L100/G32x8 allow a short and long group in one approval. Source78 ordinary line-MSHR full events motivate selection. Their absence in Vector4M/6M and SGEMM makes those weaker activation candidates. Do not equate RO merge traffic with pressure. New Core812 qualification is still required for both inputs; no inheritance from a successful Vector run. There is no requirement that the short pair finish before the long pair starts.

Conv is the first short generalization input: it combines actual ordinary-MSHR/WAD pressure with a different two-kernel access pattern, and already has exact whole-command certified RO metadata. Scan is an independent long multi-kernel pressure candidate with high WB activity and low realized V service. Its long cost is justified by a distinct mechanism-pressure contrast rather than extra coverage alone. It may run beside Conv if resources allow.

Neither Conv nor Scan was used to design the Core812 Vector pressure candidate, so both are holdouts for that design. They are **not a statistically independent blind holdout**, because these historical features informed selection; the term holdout is relative to candidate implementation/design. Do not claim universal prediction accuracy from these two.

Reuse the accepted Core812/Vector4M/1700 baseline and optimized result as a no-activation overhead negative control. Repeating Vector would add no activation evidence. Vector6M repeats much the same streaming population and has S line-MSHR peak110/full0; it is not a mandatory second main input. SGEMM has a high measured RO merge fraction but low ordinary-line pressure, making it useful historical evidence that traffic/merging is not pressure; it is not currently a better pressure-positive experiment than Conv/Scan.

## Victim development: choose for retention, avoid dead-end cold filtering

1. **Stencil** is the principal sustained-retention positive. Source78 F actually serves4930616 retained-sector responses; G32x8 S5242939/WV4768893 versus G64x8 S4299729/WV4282418 shows both capacity benefit and the smaller residual WV gain. Do not remove it from Victim-positive classes merely because larger Tag substitutes for retention. It is a long input; use its evidence to design a real-cost bank/retention candidate before spending another full model.
2. **GEMM** is the next clean-retention/service validation input, with Source78 WV609858 realized retained-sector responses and explicit accepted G32/G64 contrasts. It broadens beyond the FWT design input. Its current complete sector reuse-distance distribution is UNKNOWN, and observed service is not avoided DRAM.
3. **3MM** is an independent long capacity/retention contrast: Source78 retained-sector service exists, G64x8 S1666917/WV1662803 and G32x8 S1696618/WV1671121 are already accepted. Reuse them. Small WV increment at G64x8 is a substitution result, not no reuse.
4. **Scan** is a high-WB/low-realized-V negative contrast: Source78 F WB5312352 versus5584 Victim responses. It helps prevent a WB-volume heuristic from misclassifying V usefulness. Ordinary-MSHR pressure simultaneously makes it a RO candidate; labels are multi-axis.
5. **FWT** has WB data-space pressure and realized retained-sector service but participated in cold-filter design. Core7b4 ON reduced total frontend queries1.076% while slowing full application0.628%. Stop broadening this tested candidate without a new causal improvement. FWT should remain a cheap regression/control, not the only workload used to judge Victim design.
6. **Transpose** is a measured low-opportunity/zero-capacity-response contrast in the tested background: G64x8 S200330/WV200972 equals its corresponding same-mode references. It is a valuable existing negative/zero result and does not need a duplicate model simply to fill a family.

For all these, realized Victim response proves retained-sector revisit service in a bound application stratum; the full input temporal-reuse opportunity population and eviction-distance distributions remain UNKNOWN unless exact-input analysis already exists. Source-unbound historical Motivation/Streaming summaries are not promoted into Source78 labels.

## Memory sensitivity and negative controls

Use accepted matched service perturbations when they exist. Vector4M has exact Source78 850-to-1020 matched service response: S77184-to-65522 (-15.11%) andF77237-to-65797 (-14.81%). Its Source78 F at850 is nevertheless slightly slower thanS. This is a measured memory-sensitive/current-EP-low-increment negative control. Separately, Core812/1700 is a no-activation RO service-overhead control; Source78 sensitivity is not silently inherited as a new Source812 measurement. Other low-realized-V examples cannot be called memory-sensitive merely because they stream or issue many memory requests. Transpose, SGEMM and Scan sensitivity must remain UNKNOWN absent a legal same-Source service pair; their known mechanism and performance outcomes remain separate labels.

## What is not worth paying for now

No new Stencil/FWT/capacity repeats, no immature V Source, no Scan WV run without closed mode qualification, no universal threshold scan, no extraNI or CLEAN model and no historical raw rescans. A future new Victim Source will need its own same-Source old-policy baseline and bounded optimized point; it cannot borrow old Source78 cycles as a reference. Its resource cost must include actual Tag/Payload/Bank/directory ports, finite WB competition and query/update cycles.

The finite next request is four starts, not a project cumulative limit. Existing accepted reference results are reused at zero new-start cost. Main retains current dynamic cap10 and ownership, true164 archive/fullSHA/two independent restores, Source KEEP and no automatic retries.

## Current evidence coverage, independently joined

The current Agent A exact ledger inventory has286 accepted endpoints across28 exact input SHAs, plus5 unaccepted endpoints; these are execution points, not286 independent workloads. The retained frozen row population remains103 (96content groups plus7slots), including35representatives and42targets/slots. Agent C projects actual V counters in151accepted endpoints and19strict matched comparisons;15input rows have a positive-V context and17have an explicit-zero context, with possible overlap across configurations. These two row counts must not be added as disjoint classes. Full program opportunity distributions remainUNKNOWN.

Direct same-Source WV retention comparison: Stencil G32x8 served4930426 retained sectors andG64x8 served2547; GEMM609858 versus0; FWT88069 versus0; 3MM1176490 versus177467. These reductions accompany accepted capacity gains and directly support the capacity/retention substitution explanation without redefining the inputs by their speedup.

## Reused W-background V-enable controls

Three accepted Source78 pairs differ only in CLEAN/DIRTY Victim enable bits, at the same ordered input and full hardware background: Stencil W5240684 -> WV4768893; FWT W181635 -> WV178951; GEMM W558957 -> WV550642. They validate conditional V benefit more directly than S/WV, while leaving W interactions intact. All are reused with zero new starts. They do not replace future new-Source matched baselines.

Conv also has a measured Source78 service response: F335088 ->311505 (-7.04%) andS331234 ->310366 (-6.30%) for850 ->1020 alone, while baselineF is slower thanS. It can simultaneously be memory-service-sensitive, pressure-positive, and a current-EP negative result; this is why a multi-axis taxonomy matters. Scan service sensitivity remainsUNKNOWN in this bounded evidence set, despite observed pressure. BlackScholes shows zero cycle response in both S andF for the same service perturbation; no extra model is needed to retain that measured service-insensitive contrast.

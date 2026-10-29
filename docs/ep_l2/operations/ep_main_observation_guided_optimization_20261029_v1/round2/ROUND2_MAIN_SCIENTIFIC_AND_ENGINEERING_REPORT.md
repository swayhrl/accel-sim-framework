# EP-L2 Main: parallel observation and implementation review, round 2

**Decision:** review the confirmed ordinary-request T path correction before new T science. Continue W-only/WV qualification independently, then prefer the two cheap FWT/GEMM W-only pilots if separately authorized; retain the Stencil/Scan four-point positive/negative package as a separate decision. Do not start a parameter scan, integrate candidates automatically, or treat any CPU result as an application speedup.

A/B/C/D actually ran concurrently after the user's explicit round2 instruction. All bounded tasks, D's diagnostic followup and Main integration are now complete. This is new analysis and engineering beyond f29b3e8, not re-registration of round1. New formal applications, new registrations and new scientific budget consumed: **0**.

## Source and immutable scientific scope

Frozen accepted parent: Core78f4b59e865b136eede74df74c44c210f5b4ca04, Framework9dd1ee57a83d83b56b7874bc7c716185ab52c8f7, ELF78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a. Source78 accepted code/archive/modelELF and tracked Core/FW remained unchanged. Source92 P2, host-writeV3, MSHR64, new Host, the T correction and scalar observer are separate engineering identities. No merged new scientific Core/ELF exists.

The current REF is64slices/32setsx8ways/L100, not the original16-way GPU default. S/F share nominal1168 Payload slots/slice (9.125MiB total), but not equal role-reachable capacity: S has fixed Tag-index resident landing and WB16, while FT2 may pool free color-compatible slots. Static-stranded storage is an explicit organization opportunity, not hidden area reduction or proof all1168 slots are simultaneously useful. Main independently checked four accepted pilot pairs'282 effective options: only formal FT/TVD/RO controls/certificates differ.

## A: what the positive and negative examples actually establish

[Deepening report](agent_a/WORKLOAD_OBSERVATION_DEEPENING_REPORT.md) and its six-input CSV give exact identities and arithmetic. Stencil F reduces cycles9.026% while cumulative bank_wait rises30.873%. Scan F increases cycles2.849% while bank_wait falls34.828% and WB_DATA_SPACE distinct heads fall1,737,618 to0. Scan same-address WB first-block population rises390 to1,913, but the corresponding cleared-request mean stays553.792 to553.801.

PROVEN: aggregate bank/head waits are not exclusive application critical-path cycles. LIKELY: Stencil's substantial actual V service with little WAD/MSHR pressure makes it a useful positive control; Scan's little V service and residual coupled pressure make it a negative control. UNKNOWN: independent W/V/M/T contributions and the cause of Scan's extra cycles. No measured blocked-population delta is automatically a saved-cycle delta.

A recovered exact historical Motivation10-row CSV/index and Streaming12-row sector evidence from two publication heads. Historical Vector4M line reuse can be spatial with zero sector-temporal reuse; line reuse cannot predict Victim hit rate. Historical content roots and complete ordered command/kernel binding to current Source78 remain unresolved, and Streaming is still PREFINAL. These small datasets are retained in their own Source lineage; no name-only join or new Trace/raw scan.

## B: actual W-only and Host engineering progress

Use the [readable W-only report](agent_b_encoding_addendum/W_ONLY_QUALIFICATION_REPORT.md), exact receipts and source capsule. The original frozen B Markdown had encoding damage; the additive English report supersedes only that presentation. Original numerical evidence and manifest bytes remain unchanged.

Actual Source78 CPU components passed:32x8 W-only construction; real partition/WAD128/lower-full/drain; A1 version/reorder/identity/drain. An additional real32x8/IPOLY control passed nine requests, seven pending reads, dirty replacement/WB, reverse return, P1 and full drain. The WAD stress and legacy A1 controls have their own geometries; they are not all32x8 or application NI.

The earlier exact3 was a precompile RAM HOLD, not a protocol failure. New attempts preserve a compile wall-time limit and previously unexecuted CPU input adapters (unregistered ROP option, one-channel partition indexing, IPOLY set selection). Private fixes affect only fixture inputs/adapters. No old science start was retried/refunded.

Thirty-eight private Host component controls passed. The old draft wrongly rejected the actual accepted SUMMARY_STAGE wire environment; the private candidate fixes this while rejecting unsupported variants. Numeric factory body/suffix preservation was verified. This is not a full-wrapper/native authorization test. Main modeCPU signoff, full HostQ/parser binding, nativeQ/entry whitelist, input eligibility and any required application NI remain pending. The Host candidate is32x8 only and explicitly rejects16set.

S-to-W measures pooled organization plus copy elimination, not copy alone. W-to-WV measures the entire V package including lookup, forward, retention and bank service. C1 service-aware optional reclaim remains HYPOTHESIS: preserve mandatory/pinned lifetimes, owner/generation, bank color, revision and preview purity; synchronize the two distinct selectors and reset on dirty-promotion incarnation. Logical1024-byte bit-state estimate excludes real comparator/port/timing/PPA costs. No policy code is merged and no gain demonstrated.

## C: strict reuse and T opportunity

[M/T report](agent_c/M_T_OPPORTUNITY_DEEPENING.md), [collector/NI](agent_c/MINIMAL_COLLECTOR_AND_NI.md) and [F-minus-T plan](agent_c/F_MINUS_T_MODE_AND_PLAN.md) distinguish measured and missing populations. Live merge fractions do not establish strict requested-sector-before-ready reuse. New production-transactions CPU proves that a request to an already-ready sector can set reuse_seen while another required sector is pending, excluding detach for the transaction lifetime. This is a conservative policy, not a proven safety bug.

Vector6M REF ordinary line-MSHR peak0 coexists with RO pending distinct-line peak70/slice. SGEMM has43 ordinary and8 RO pending maxima; Conv has128 and102. Do not add separate maxima. Current REF Conv already has14 actual detach; separate Conv16x8 has237. Neither count proves T independent performance. Vector4M and Vector6M are distinct inputs.

The88-byte C++ scalar candidate separates strict revisit/new sector/ready-other-pending/ready-draining for accepted live merges. Four final module executions form two T0/T1 OFF/ON semantic pairs using actual transactions/D512 and a reference Payload adapter. Four16x8 real partition controls pass T0 progress, T1 old-return/generation, sector reorder and ReturnQ backpressure. Initial scope-assertion and macro-helper-return failures are preserved and excluded from final evidence. The pressure T0/T1 tests have9/10 requester populations, so their fixture ticks are not a speedup comparison.

Production hook, full T-joint observer, normal+RO simultaneous address union, application output and host-overhead measurements are NOT implemented/measured. The88bytes describe only scalar state. S/F/WV common-hook NI cannot be inherited from a module or another mode. True ingress, first-head, admission, backend probe and actual completion remain separate.

## D: confirmed implementation omission and reviewed candidate

[Complete fidelity audit](../agent_d/IMPLEMENTATION_AND_PERFORMANCE_FIDELITY_AUDIT.md) reports one P1, no new P0 confirmed within the bounded audit. Ordinary non-RO raw TagFAIL returns early in gpu-cache.cc preview before it can reach ep-l2-ft-cache.inc's generic RO relieve. CPU Source78 READ/WRITE stay head with eight eligible old same-set RO, despite available normal resources. Old returns eventually permit progress, so this is avoidable blocking rather than proven deadlock/data corruption.

[Candidate V2](../agent_d_candidate_v2/CANDIDATE_V2_REVIEW.md) closes virtual-relief and consulted/intermediate consistency while preserving raw TagFAIL. Ten production-class CPU runs, five same-binary diagnostic OFF/ON pairs, all fully drain and have equal semantic signatures. READ/WRITE show rawFAIL to virtualMISS to actual backendFAIL/relieve/detach/new acceptance. T0/reuse stay blocked; MSHRfull can see virtual opportunity but still denies before backend/detach. Repeated previews preserve identity/resources and do not charge the ledger.

This is a reviewed engineering candidate, not a full newSource or accepted simulator. Descriptor/per-address/MissQfull, ready-only, directory/payload exhaustion and exhaustive clock cases still need qualification. No protection was relaxed. Application incidence and cycles effect remain UNKNOWN. Old Source78 cycles remain observations of that model; do not erase them or blame all F losses on this omission. Backend TagFAIL=0 cannot exclude a request denied before backend, while independently low RESERVED occupancy still supports genuine no-pressure negatives in its own lineage.

P2 costs remain real modeled restrictions: finite paid TVD/RO lookups, bank service/color, WAD and mandatory/pinned lifetimes, descriptors and conservative reuse protection. P3 includes optional retention value, metadata port/PPA/timing closure and coarse statistics. Coarse payload_block includes multiple RESERVATION_FAIL causes; it is not pool-full. Host execution time, GPU cycles, stage-event counts and observer overhead are different units.

## Exact next science options: prepared, not authorized

[Six exact drafts and budget](agent_b/EXACT_SPEC_AND_BUDGET_MANIFEST.json): Source78 unchanged, complete282 each, only formal mode deltas, same input/geometry/hardware. Option1: FWT/GEMM W-only two cheap points. Option2: Stencil/Scan W-only and WV four points. Allsix only if separately approved; authorized/registered/consumed0. Exact old S/WV controls require current reuse qualification. Runtime is UNKNOWN for new modes; historical anchors are FWT14-15min, GEMM1.2-1.4h, Stencil4.8-8h, Scan8.1-8.9h. Qualification/NI/newSource controls are not silently included in six.

Conv16x8 Source78 F-minus-T draft has all282 options and only T1-to0, M1. One conditional start could test legacy implemented T using old same-ELF F after complete qualification; old Host/native rejects the mode and B's32x8 Host controls do not qualify16x8. A corrected newSource needs its own F-minus-T/F, and isolating correction requires a same-new-ELF old-policy/corrected-policy control. Old F cannot fill that counterfactual. No new Source/options/budget are fabricated.

Main's order is: finish formal engineering/source and Host/native review; select the bounded two-point or four-point package for user review; complete minimal T correction qualification before expanding intended-T claims; use an independent frozen input set only after choosing one unified configuration. Preserve slowdowns, null results and UNKNOWN. No per-input-best geometric-mean promotion or unlimited scan.

## Live background and archive

Old automatic controller naturally accepted LavaMD-F at5738976cycles versus S5581479 (F slower2.8218%). Readback shows223accepted/111pairs; SYRK-S/F remain pending in the original dispatcher. Earlier feature snapshots at222/110 remain as-of evidence. Original archive/publisher owns those results and has pushed its own branch; Main did not intervene.

All new CPU source, receipts, failed attempts and private test builds have genuine164 archives with full SHA and independent native restore; Git excludes private executables/libraries. See unified archive receipts and LIVE_LONGTAIL_READBACK.json. Accepted Source, old budgets/ledgers and protected data remain unchanged. This round completes research/engineering preparation, not application qualification or proof of an optimized EP-L2 speedup.

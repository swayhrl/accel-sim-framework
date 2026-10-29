# M/T opportunity and measurement: round 2

No application/GPU runs, Trace/raw scans, dispatcher, ledger or production Source changes occurred. Existing observations reuse the first-round sealed 15-point projection. This delivery adds C++ engineering, actual module and partition CPU controls, a 282-option causal specification and new conclusions; the prior 13 Python checks are not relabeled as production NI.

## New evidence

**PROVEN (code and actual CPU):** Source78 `ep-l2-ro-transactions.h:197-201` sets `reuse_seen=true` after any successful live merge obtains its shared D512 descriptor. The incoming required sectors need not be unready. The new real-transactions/native-MSHR module fixture makes sector0 ready while sector1 remains pending, then merges a request needing only sector0. This is not strict requested-sector-before-ready reuse, yet it immediately forbids detach (`can_detach:211-213`). The protection persists to transaction retirement. This is the current conservative policy, not a proven correctness bug; relaxing it has no safety proof.

The new bounded C++ counter separates: previously-required unready revisit; newly-required unready sector; requested sectors ready while another required sector remains pending; all required sectors ready but response draining. Successful accepted-merge population is the denominator; a rejected duplicate requester adds no counter. OFF/ON module semantics match. The production hook is NOT implemented.

Consequently Vector6M 74.99%, SGEMM 92.82% and Conv 71.54% live merges do not establish strict fill-before-ready reuse. Accepted-requesters / admitted-transaction is approximately 4.00, 13.92 and 3.51 respectively: lifetime multiplicity, not simultaneous waiters. A per-address cap32 does not bound cumulative merges over a whole transaction lifetime after descriptors retire.

| Source78 REF32x8/L100 | accepted RO / admitted transactions | normal line peak | RO pending distinct-line peak/slice | descriptor peak | actual detach |
|---|---:|---:|---:|---:|---:|
| Vector6M efced2c | 1500000 / 375109 | 0 | 70 | 369 | 0 |
| SGEMM ab4ac5d | 1135915 / 81582 | 43 | 8 | 169 | 0 |
| Conv 438eefd | 1322070 / 376204 | 128 | 102 | 409 | 14 |

All peaks are maxima over slices, not simultaneous GPU-wide peaks; do not sum them. Vector6M RO bypasses the ordinary line-MSHR, so ordinary peak0 is not absence of MLP and does not motivate expanding ordinary MSHRs. SGEMM normal peak43 and RO pending distinct-line peak8 show no observed line-full pressure; descriptor-per-address retries and strict pre-ready reuse remain different issues. Conv normal line-full S/F observations are 6499/2986 repeated head checks, not unique requests or exclusive GPU stall cycles. Ordinary, RO, WAD and W/V competition must be separated causally.

New same-population derivation: RO runtime entries / FT-accepted certified reads are Vector6M100%, SGEMM about49.02%, Conv about93.09%. These are NOT RO rejection rates: certified cache/TVD hits need not create or merge an RO transaction. Exact integers, input SHA, Source5 and evidence references are in `MT_RESOURCE_NEED_AND_LIMITS.json`. Do not infer missing implementation from this entry fraction alone.

## D audit changes the T claim boundary

**PROVEN (D real partition CPU):** ordinary non-RO READ/WRITE can be denied at old preview for64 ticks with eight pending RO Tags and eight eligible candidates in the same set, although direct backend can relieve and accept. D's isolated patch admits, detaches and drains while retaining protection. It still lacks diagnostic `consulted/intermediate` synchronization and application qualification. Frozen D manifest: `../../agent_d/DELIVERY_MANIFEST.json`, SHA `235826fff40646e51090fbafba7c35ff8b3a51d8702af41cd1c265bd2a938382`.

**UNKNOWN:** frequency and cycles impact in accepted Vector6M/SGEMM/Conv. Existing small summaries do not contain same UID/set/tick raw-full plus structural-eligible joint events. Do not multiply marginals. Zero backend production TagFAIL or detach is not sufficient proof of absent structural pressure: preview may prevent backend entry. Nor does the constructed witness prove that every application slowdown comes from this P1.

New measurement must preserve real ingress, first-head, raw Tag probe, virtual preview decision, actual partition denial/admission, backend raw probe, relieve, detach and successor acceptance as separate boundaries. Repeated head cycles are not unique NEW arrivals.

## Actual new CPU execution

1. `test_mt_sector_counter.cc`: unchanged Source78 transactions/native D512 with reference payload port. Four T0/T1 x OFF/ON executions, two module NI pairs PASS. Original ten RO scenario functions also run. New assertions cover strict/new-sector/ready-other/ready-drain, duplicate failure exclusion, reuse protection, overflow invalidation. Counter sizeof88; 64 scalar instances5632 bytes.
2. `test_mt_geometry16.cc`: unchanged Source78 archive, real cache/subpartition, synthetic certificate, manual lower returns. Four controls PASS: T0 legal block/progress, T1 detach/old generation return, reordered sector merge, ReturnQ backpressure and full drain. Physical1168, normal MSHR128, D512, WAD128 and bankP1 assertions remain.
3. Initial four16-set controls failed at the inherited fixture's32/64-only scope assertion, before request execution. Preserve `GEOMETRY16_ATTEMPT1_CPU_EXECUTION.json` and all four logs. The private fixture extends the allowed set domain to16, preserves all protocol/data/resource assertions, checks actual requested geometry and uses MissQ128. Production Core is unchanged.
4. T0 pressure control has9 replies; T1 has10 because the original T1 test intentionally sends another revisit to verify old/new identity. Their118/65 fixture ticks are NOT a T speedup comparison. CPU controls contain no real DRAM timing and grant no application NI.

## Decision

Main should first disposition D's P1 and its scientific scope. Preserve the one-point Source78 Conv16x8 F-minus-T draft only as a test of legacy implemented T; it does not test corrected ordinary-request T coverage. Any D fix or production hook creates a new Source/ELF and requires fresh F-minus-T/F, never a cross-binary old F control. Both routes have zero start authorization.

For M, first collect successful-merge sector-ready categories and first reuse transition, not full-address reuse traces. Only implement a normal+RO simultaneous address union if a concrete resource decision requires it. For T, structural eligibility must be independent of the T flag and cover ordinary as well as RO requests. Full application NI remains missing.

## Preserved harness correction

The first four module executions passed assertions but used macro-renamed original `main` as an ordinary int helper without an explicit return, producing a compiler warning and undefined return behavior. These are preserved in MODULE_ATTEMPT1_CPU_EXECUTION.json, build receipt and module_attempt1 logs; they are NOT used as final NI evidence. A private copy of the reference fixture adds explicit return0 and an absolute include, with no protocol assertion changes. Final rebuild is warning-free, all four module runs passed again. Total module executions8, final authoritative executions4. No model runs occurred.

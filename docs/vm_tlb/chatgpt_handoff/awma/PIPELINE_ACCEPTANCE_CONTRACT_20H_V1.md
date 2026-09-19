# AWMA 20h Pipeline Acceptance Contract V1

Date: 2026-09-19

Status: ACTIVE AFTER USER LAUNCH

## 1. Global rule

Scientific acceptance requires exact:
- source/branch/commit;
- input/model/context identity;
- runtime/tool/binary identity;
- target identity;
- measurement semantics;
- artifact size/hash/provenance;
- node164 ACK for large outputs;
- scoped claim.

Exit code 0, file existence, kernel-name match, rsync success, page-footprint change, or a restored tensor
checkpoint are not sufficient by themselves.

## 2. Repair authority accepted for requalification

Independent review binds:

execution branch:
`hrl/awma-vm-per-access-coverage-repair-174new-v1`

commit:
`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

parent:
`be82faf264e93396b4b7d4fd72078c7e4491e3e4`

decision:
`PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_QUALIFIED_FOR_REQUALIFICATION`

Direct legacy proof:
- P34 downstream admissions = 3,090,304
- untranslated/unobserved admissions = 2,313,638

Repaired proof:
- admissions = 3,090,304
- translated = 3,090,304
- untranslated = 0
- unobserved = 0
- post-ready retranslation attempts = 0

P34 target completion cycles:
- legacy = 871,835
- repaired = 1,619,068

This is a material scientific change.
The repaired runtime is NOT automatically promoted to final research baseline.

## 3. Repair caveats that MUST close in 174-M0

The review pack does not bind a durable repaired simulator binary SHA in Git.

Also, auxiliary impact counters appear to mix target-scoped and whole-prefix scope:
the repair impact table reports walk_starts=499 while historical P34 target-only evidence used a different
target-scoped walk count.

Therefore 174-M0 must:
1. materialize the exact accepted repair semantics from the repair authority;
2. rebuild a clean repaired runtime;
3. record source tree identity + binary SHA256;
4. reproduce P34 coverage/cycle sanity;
5. implement/read target-boundary delta telemetry so every requalification metric has an explicit scope;
6. close GLOBAL/LOCAL/PARAM_LOCAL eligible/admission/translated accounting separately where source permits.

Do not reinterpret 499 as Q05 target-only walks unless target-boundary delta proves it.

## 4. Repaired runtime semantic acceptance

Required:
- exact current accessq_back must be translated before L1D/ICNT admission;
- untranslated access remains queued;
- existing VM helper is used on the next memory-cycle path;
- no TLB/cache config change;
- no address/coalescing/scheduler change;
- zero untranslated downstream admissions;
- zero post-ready retranslation attempts.

The source-level repair may reduce downstream issue when the existing translation model cannot qualify
multiple newly exposed accesses in one cycle. This is accepted as restoring the pre-existing VM gate semantics,
not as a new architecture optimization.

## 5. 174-M1 acceptance

Required identities/status:

- FORMAL_ISOLATED_REPAIRED_R0
- FORMAL_ISOLATED_REPAIRED_I0
- P34_REPAIRED_R0
- P34_REPAIRED_Q05_ONLY_I0
- P8_REPAIRED_R0
- bounded target-scoped timeline/translation sanity

A matching repair-qualification P34 run may be reused only for metrics whose exact scope and binary identity are
reconciled; otherwise rerun.

For each target report:
- full target cycles;
- instruction/CTA completion;
- target-scoped VM eligible accesses by class;
- coverage invariants;
- L1/L2 TLB hit/miss;
- MSHR alloc/merge/HWM/full;
- walk start/complete;
- PWC/PTE;
- requester-latency components;
- L2 data;
- DRAM.

REQUEST invocation counts are not unique memory requests.

### I0

P34 Q05-only I0:
- all predecessors = repaired natural R0;
- only Q05 = ideal identity translation;
- I0 applies per eligible access;
- SimVA -> same SimPA;
- no legacy undercoverage.

If exact target-I0 cannot close: `REPAIRED_TARGET_I0_DEFERRED`, no approximation.

## 6. Legacy claim classification

174 must produce:
`LEGACY_CLAIM_REQUALIFICATION.md`

Each major old translation claim:
- RETAINED_WITH_NEW_VALUES
- QUALITATIVELY_RETAINED
- MATERIALLY_REVISED
- RETIRED
- NOT_YET_REQUALIFIED

Old numeric values are not preserved merely because direction matches.

## 7. 174-C1 non-Attention screen

Only if explicitly gated after M1.

Preferred:
`PREFILL_GEMM_PRIMARY_OCC0` from accepted 109 V1 producer authority.

Accepted producer campaign:
`8f49ba3b9228b5f8a9163e961225ffd415107734`

If no qualified SIM_INPUT exists, Codex may perform the standard consumer admission from that exact immutable
producer bundle using the accepted validator/consumer contract. No recapture and no semantic weakening.

Then at most one complete pair:
- PREFILL_GEMM_REPAIRED_R0
- PREFILL_GEMM_REPAIRED_I0

If no matched predecessor context exists: label `ISOLATED_SCREEN_ONLY`.

## 8. 109-M0 acceptance

Targets:
- Q05 Prefill Flash;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1.

Reuse accepted evidence before new profiling.

Each row requires:
- semantic/function/shape/occurrence identity;
- uninstrumented timing authority or explicit absence;
- profiler version;
- replay/cache-control/pass count;
- compute/warp/occupancy + L2/DRAM resource evidence where available;
- COUNTER_UNAVAILABLE rather than invented zero.

## 9. E1 acceptance

Core:
`{down_proj,q_proj} x {M1,M256} x {raw,AWQ} = 8`

Each point:
- exact raw/AWQ model revision;
- operator/layer;
- weight/qweight/qzeros/scales identity;
- activation-pool hash;
- tensor rank/shape/stride/dtype;
- backend/kernel sequence;
- native timing samples;
- numeric status;
- provenance.

Each raw/AWQ pair:
`SEMANTIC_PAIR_QUALIFIED` or `IMPLEMENTATION_LEVEL_ONLY`.

If execution dtype differs materially:
`NOT_REQUIRED`, `REQUIRED_AND_COMPLETE`, or `REQUIRED_BUT_SCIENTIFICALLY_BLOCKED`.

No requirement exists for AWQ to be faster.
No-effect/opposite-effect is valid.

## 10. E3 acceptance

First-wave:
- N natural;
- P histogram-preserving joint permutation;
- U-active balancing within natural active-expert set.

P requires inverse-permutation output equivalence.
U-active is explicitly SYNTHETIC_ROUTING.

Same:
- M/E/k/total assignments;
- expert backend;
- weight residency/loading policy;
- input pool;
- timing boundary.

No detailed trace is required for E3 light acceptance.

## 11. Opportunity acceptance

### G1
New scenario identity, exact tokens/input, native timing, lightweight census.
No silent reuse of S2 label.

### G2
Same quantized-weight authority, trustworthy pre-existing reference execution path, explicit dequant timing boundary.
No new backend development.

### G3
Same target + metric set, exact NCU replay/cache-control settings.
Claim = profiler-protocol sensitivity, not TLB cold/hot.

### G4
Exact Llama binding, pre-frozen operators, M1/M256 native timing/fingerprint.
Claim = raw shape trend only.

## 12. Detailed capture

Optional.

Before capture:
- selector rule frozen;
- effect exceeds measured noise or uniquely discriminates an explanation;
- exact semantic/kernel identity;
- enough transfer/finalization budget.

Default new detailed raw cap: 16 GiB total, subject to stricter existing per-target limits.

Partial remains `PARTIAL_NOT_ADMITTED`.

## 13. Holdout

A holdout remains independent only if its result was not used for selector/threshold tuning.

## 14. Final deliverable

109 and 174 each produce:
- exact execution branch/SHA/parent;
- task matrix: reused/new/accepted/partial/skipped/stopped;
- run receipts;
- raw/node164 index;
- SHA256SUMS;
- clean-worktree confirmation;
- lock release for 109;
- next-stage proposal only.

Campaign success does not require every opportunity task to run.

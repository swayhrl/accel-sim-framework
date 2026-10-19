# ROB1 R6 preparation while final F is unavailable

Status: SOURCE_ONLY_PREPARED; NOT_DISPATCH_REGISTRATION. No UUID, build,
fixture execution, input-body read, resource observation, import or simulation
is introduced by this delivery. Only this ROB1 pack is changed.

The coordinator reports that AG6 AE_GEMM started, then stopped at
16:58:14Z on sustained cgroup IO PSI >25 (UTC date was not independently
established by this source-only intake). It reports one consumed
start, zero accepted points, three unstarted points frozen, and no live or
pending owned instances after cleanup. These are parent-reported observations,
not independently sampled here. The stopped cohort cannot resume or replace
its failed arm under this preparation. F remains
`PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN`, not final O. No result from the
incomplete optimization screen selects AE or AD.

## Immutable source and evidence basis

- Framework `46df82670a56a4498b6d6e23ad57859eb7c36945`,
  `docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/ROB1_GOAL.md`,
  `MASTER_PLAN.md` sections 3, 6 and 8, and `PLAN_CONTRACT.json`: R<=6,
  shared reserve<=4, total BA<=32, one global F and fixed GEMM/BICG service.
- Framework `f81ca1c5054a78ed2c09f316bac0501c3bbc9322`,
  `docs/dtc_l1/iscas2027/parallel_ag_ba_20261019_v1/`:
  `LANE_BA_V2_CONTINUE_AND_DISPATCH.md`, `MASTER_COORDINATION_V2.md`, and
  `AG6_AUTHORIZATION_V2.json`: AG6's separate four-start cap is not BA32;
  incomplete discovery retains provisional O. Its historical 10GiB wording
  is superseded only by the later explicit >5GiB output-mount policy.
- Diagnostic Core `b1077667f7a2bcc72260733f88f5798f167346d1`, tree
  `0a462efb9a48409064259735108b88dad127a53c`, parent
  `c8090115bd57512b1b23fca7d925301fa620c751`: inspected actual quota resolver,
  option registration, LDST constructors and actual LDST fixture source.
- Parent Framework snapshot `62323c40df0add726cae52a96ca946e589f00343`,
  `docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/`:
  `rob1_fixture_static_intake_v1/{STATIC_FREEZE,COMPILE_RECIPES}.json`,
  `rob1_fixture_runtime_prepared_v1/PARENT_INTAKE.json`, and
  `cpu_real_roles_v2_actual_intake_attempt4/controller_receipts/rob1/build.receipt.json`.
  This is an immutable evidence snapshot, not a claim about later activity.
- COV1 `385bfe375f091337443245424214d43d6d1ad067`,
  `docs/dtc_l1/review_packs/DTC_COV1_INPUTS_V1/{INPUT_COVERAGE,REUSE_MATRIX}.tsv`:
  historical complete input/control candidates, not automatic family admission.

## Conditional R matrix; caps are not targets

| Candidate scope | Service requirement | Additional necessary controls | New R starts ceiling |
|---|---|---|---|
| F still unknown, current state | Prepare GEMM/BICG quota1 only; no final-F dispatch | None selected | No starts released here |
| Independently registered provisional-O diagnostic | Same two inputs, O fixed, quota4→1; label all conclusions provisional-O only | No AE/AD fairness work | At most the two service rows; consume BA R slots, never an extra allowance |
| Final F=O | GEMM and BICG quota1 | No other R points | 2 |
| Final F=AE | GEMM and BICG quota1 at AE1/AD0 | C+ hash ON for each; missing DTC hash OFF for each. DTC ON and C+ OFF come from qualified P/reuse | <=6 including the two service starts |
| Final F=AD | GEMM and BICG quota1 at AE0/AD1 | Missing O OFF for BICG/DWT2D only; AD ON from qualified P/reuse | <=4 including service; unused capacity stays unused |

The provisional-O row requires the coordinator's explicit independent scope
and denominator admission; it does not silently convert waiting final-F
experiments into completed F experiments. It is not automatically repeated
after F changes. The coordinator must reconcile any such consumed R slots
before releasing later points. No slots or UUIDs are allocated here.

AE fair ratios are `H_D=D_OFF/D_ON`, `H_C=C_OFF/C_ON`, and `C_ON/D_ON`, using
cycles. If controls/budget are missing, prioritize one complete four-way input
and disclose the other incomplete; partial grids cannot support these ratios.
Do not implement C+ hash until AE is selected. Its accepted whole-line source
is separate from DTC; preserve its own sets/ways/bank bits/capacity/latencies.
AD statistics require the same admitted/all-return→collect/retire boundaries;
absent OFF fields are UNAVAILABLE, not zero or a difference of incompatible
post-ready means. No AE+AD, geometry/downstream scan, K1, new input, or budget
fill is included. P16/N6/R6/reserve4 remain one BA32 ledger; failed full starts
consume their slot. AG6's frozen one consumed start belongs only to AG6.

## Exact diagnostic intervention

`-gpgpu_dtc_l1_collection_quota 0` retains the original width4 path.
Omission also defaults to0. Literal `4` is unsupported: the only nonzero
supported value is `1`, finite PAPER_OO (mode3). The new option is an unsigned
config scalar, registered in gpu-sim.cc and resolved before actual LDST init.
Nonzero assigns only `m_dtc_service_collect`; zero leaves the original `{4}`.
The external-cache constructor rejects nonzero rather than silently accepting
a different path. This changes config layout, so header/library ABI matching
is required even for zero.

The quota is requested **32B collection sectors per absolute core cycle per
LDST service quota**, not references per cycle, Tag banks, returned sectors or
whole 128B lines. Data returns, waiter/select behavior, one-cycle ready edge,
WB arbitration, `cycle > collect_done_cycle`, Ref lifetime and fences stay on
their original paths. A quota1 result is a service sensitivity, not equal-area
fairness or evidence of a free timing implementation.

## What the actual CPU evidence proves

The already executed seven-negative helper has a limited quota/service_entry
PASS. Do not rerun it or call its synthetic rejection actual RF/WB integration.
The real LDST target and matching whole libcudart were subsequently built
successfully (build receipt SHA256
`7cad272e1239b6c7f23cf897b44d455760e1308cb06bd6639bb06bdee39345d1`).
Static freeze records fixture SHA256
`978b6e605f045808ee410e3b8d51934b74a621e17614a6f7f50a872aef2b9312`
and whole libcudart SHA256
`22963c70368489f930ae73a2383520d1da30996c6503fe565b5edd5c3770faf1`.
That freeze explicitly says STATIC_ONLY_NO_TARGET_EXECUTION_NO_LIVE_MAPPING_CLAIM.
At the inspected parent snapshot the six-case runtime intake still says
SOURCE_ONLY_NOT_EXECUTED. Actual six-case PASS is therefore NOT_PROVEN here.

The prepared cases are omitted, explicit0, quota1, badwidth2, badmode2 and
nonfinite. Their source exercises actual parser/constructor, four returned
sectors in order0/2/1/3 with three requested collection sectors, strict ready
edge, shared absolute-cycle quota, one real RF-bank WB denial, retained Ref
and completion/retirement. Expected width4 trace is ready11/start12/done12/
retire14; width1 done14/retire16, sectors3, denied1, finalRef0 and closedledger1.
Negative mode/width/finite rejection requires the exact quota diagnostic plus
the real SIGABRT handler signature and exit1; arbitrary nonzero is not PASS.
The fixture forces AE0/AD0. Even a future six-case PASS would not by itself
qualify quota1 combined with selected AE or AD, application values, a final
scoreboard-empty assertion, or whole-binary OFF equivalence.

The original c809 reference fixture has not been executed in this evidence.
Its future omitted-only reference must compile against c809's own headers and
matching old whole library, separately registered; never b107 headers with an
old library. Agreement between b107 omitted/0 is local component agreement,
not a measured c809-vs-b107 whole-trace equivalence. Preserve this distinction
even if all six new cases pass.

## Closure required before formal service results

1. Keep b107 diagnostic source isolated. Freeze all652 Core leaves, actual
   matching build headers/generated files/toolchain/compile and link recipes,
   and the exact Framework trace frontend source (accepted baseline frontend
   `8e43c75a5e2eb60a8466084602b7df8117111e89` unless separately reviewed).
   A **matching b107 trace accel-sim ELF is not established by the CPU build**.
   A future exact build role must build/freeze that ELF and matching whole
   libcudart together; record actual build options/version bytes. Do not use
   the old c809 trace ELF plus the b107 library or the reverse. Rebuilding may
   produce a different whole-library hash; freeze the resulting tuple rather
   than pretending the CPU fixture tuple proves a future trace build.
2. Freeze PT_INTERP, DT_NEEDED/RPATH resolution, loader, ld cache, transitive
   runtime ELF dependencies, current stat+SHA and permitted mapping closure
   for the **trace target**. The CPU fixture's seven-ELF static dependency
   closure is not a substitute for the trace frontend's actual closure.
3. Consume a qualified selected-F receipt, or separately label/register
   provisional-O scope. Freeze all ordered config-file bytes and full command
   vectors, the original complete same-input trace list and every member's
   known SHA/stat binding. Use COV1 immutable coverage and SEM1 support scope;
   no fresh large trace-body hashing is proposed here. Missing provenance
   blocks the affected input. GEMM's historical target is 1kernel/1024CTA/
   739246080 active instructions; BICG is 2kernels/16+16CTA/145666048. These
   are full existing inputs, not enlarged N inputs or native-value proof.
4. For the matched accepted c809 runtime, the complete effective option
   dictionary is270 entries. For an otherwise matching b107 trace frontend,
   expect271: all270 selected-F/input options plus exactly the new quota.
   Reconcile actual registration/echo before release; counts alone do not
   prove identity. Within a b107 service pair, the complete effective
   dictionaries must differ only quota0→1. For c809 control reuse, remove only
   quota0 to compare scientific options; source/ABI/build differences still
   require independent OFF-equivalence eligibility. Old267-option controls
   cannot be silently equated to270 or271. Copying AG6 strict expected-source
   strings unchanged would falsely reject or misidentify the new diagnostic.
5. Establish necessary actual LDST qualification and source/binary identity,
   then establish the required original-vs-diagnostic OFF control bridge. An
   admitted existing same-input control may be reused only with its immutable
   per-input dossier. If full default0 calibration is needed, charge it to
   remaining **shared CAL_OR_ENGINEERING<=4**, not free R or AG6. A qualified
   b107 quota0 full calibration may provide the service denominator. Do not
   add two fresh quota0 controls to the six R slots without reconciling the
   original service-two plan and reserve ledger. If calibration cannot fit,
   hold the affected comparison; no R7/BA33/fifth AG6 start.
6. Parent alone freezes fresh UUIDs, attempt/output estimates, unchanged
   production authority/observer roles and strict contracts, then publishes
   and independently reads back before any fork. Full strict requires complete
   kernels/CTAs/instructions, exact options/config/input/source/ELF/mapping,
   successful terminal and cleanup/authority, positive integral cycles, and
   applicable conservation/Ref/ledger counters. Quota1 collection timing may
   differ; do not require cycles equal quota0 or discard a reverse result.
   Native values and unsupported semantics remain separately scoped by SEM1.
7. Freeze a common pair timeout before either result (7200s default; any
   input-specific adjustment preregistered). No ROI/kernel truncation. Each
   fresh admission and runtime monitor preserves both host+cgroup R2:
   >=10.1s complete pair, 32GiB host+cgroup headroom, memory-full<=1,
   IO-full<=25, no new OOM, independent exact authority/roles. Actual output
   mount must remain strictly >5GiB; startup also covers the task's expected
   write footprint above that floor. No generic10GiB requirement is restored.
   Resource/science/identity/authority failure preserves consumed starts and
   follows the newly frozen family's stop policy; negative accepted speedup
   is a valid result. No background retry or reuse of the stopped AG6 UUID.

Ordinary preparation now: this conditional matrix, source delta accounting,
non-executable config/strict placeholders, immutable CPU evidence intake and
future exact build/runtime requests. The parent may separately release finite
CPU fixture work after current R2. Final-F flags/fairness branch, trace build
execution, OFF calibration, denominator admission, actual UUID allocation and
formal forks remain gated. Nothing here changes the parent's live49-source
closure, dispatcher, AG6 files, Core, commands or resource thresholds.

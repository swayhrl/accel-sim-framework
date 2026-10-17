"""Materialize complete four-cell STOP disclosure; no values imputed, no launches."""
from common import *
from decimal import Decimal,localcontext
from fractions import Fraction

def md(name,content):
    p=PACK/name
    with p.open('x') as f:f.write(content.strip()+'\n')

def main():
    observer='K1_ONLY_EVENT_TELEMETRY_ACCEPTED_AS_NONCOMPARATIVE_DIAGNOSTIC'
    md('OBSERVER_SUPPLEMENT_V1.md','''# AA3 observer supplement V1

Contract ID: AA3_OBSERVER_SUPPLEMENT_V1. User acceptance: **K1_ONLY_EVENT_TELEMETRY_ACCEPTED_AS_NONCOMPARATIVE_DIAGNOSTIC**. This is a new AA3 supplement; AA/AA2 observer-HOLD reports remain unchanged. Publication by commit/push/fetch-back precedes any new full performance; AA3 actual starts are zero.

All four cells bind the single Core c0a5e2c31e407c57e3a4af3ce529c921e8059a05, trace executable SHA 2cd45b1b91985b19255ff5c9db3b49a3ee46b5a479272eacd2a42fb2bf9ac9ae and libcudart SHA 06957c897f8248fa2b08a5c18823207db8dda954c218337ba399ba70e7f97b56. No second Core or option retune is allowed. Shared cycles, finite, lower, occupancy and traffic fields may be compared only under the same definitions, paths and populations, after strict acceptance and both K0 calibrations.

The source observer is guarded by K=1. Its request, origin, mapping-change, retained/reclaimed and ordinary-commit summaries are **K1-only noncomparative diagnostics**. K0 absence is UNAVAILABLE, never measured zero; no K1-minus-K0 event delta, event main effect or event interaction is permitted. Both K1 cells retain their actual values, without using event count differences as a controlled cause or normalizing away repeated idle calls.

Hook: source_invalidation_observer::request at ldst_unit::invalidate(source), before ordinary.invalidate request. Preserve original idle-cluster/config/MEMBAR predicates, selected SMs and repeated requests. Print each SM lifetime cumulative DTC_INVALIDATE_V1_SUMMARY at existing statistics boundaries. Use the last corresponding snapshot for each of 64 SMs, never sum kernel snapshots. Detailed request AND ordinary-commit records share -gpgpu_dtc_l1_debug_event_limit; fixed default=0 suppresses detail, not summary counters. First/last UINT64_MAX means UNDEFINED_NO_EVENT. pending_first/last are request sequence IDs, not cycles. Ordinary commits can coalesce requests and do not count actual changed ordinary tags.

K1 atomically revokes lookup mappings at the existing source request with zero added **simulated** cycles. This is a model assumption, not proof of zero hardware cost, bandwidth, lookup ports, area or timing. Host wall time is solely an execution-resource measure and must not be presented as GPU speed. K1-specific printing does not justify altering public metrics, K0 equivalence or strict conservation requirements.

Physical conservation uses new_misses = physical_allocated + immediate_reclaims + final_ref_reclaims + R, where K1 R is same-boundary sum of reclaimed_at_event. K0 R=0 is a structural OFF semantic term, not an invented observation of an absent counter. Event-retained allocations that later lose their final Ref are counted only through final_ref_reclaims; do not subtract retained again.

This supplement resolves the observer scientific clause only. It does not release an execution authority, replace full executable pre-registration, waive Y2's bounded scope or turn W's unavailable address scan into evidence.
''')
    md('SCIENTIFIC_SCOPE.md','''# AA3 scope and terminal STOP

Goal DTC_LANE_AA3_K1_GAUSSIAN_CONVERGENCE_174_V1, original huangrulin-174/root container. Independent Framework worktree and branch hrl/iscas2027-dtc-lane-aa3-gaussian-convergence-174-v1, raw /workspace/dtc-lane-aa3-gaussian-174-v1. AA c381b6e4 and AA2 fa7bd9ee remain frozen. Their four reserved UUIDs and shared total budget of four actual full starts are inherited; actual starts across AA/AA2/AA3 remain 0/4.

**STOP_LEGAL_EXECUTION_AUTHORITY_NOT_CLOSED**. The user-authorized single Core41 watcher was retired with one pidfd-bound SIGTERM after a fresh exact identity/task audit. Its inherited timer ended naturally and the original FLOCK inode has no remaining holders. No other process received a signal, no old file or lock was deleted, and no old execution lock was acquired. A different live deferred dispatcher, PID3291777/start_ticks550530984, still has a future seven-row BICG/GESUMMV launch path. Its present old-Core gate fails; that is not scientific retirement, release of authority or permanent inability to dispatch. Historical R1 is superseded/nonformal. Its disposition is outside the one-watcher signal authorization. Do not silently exempt it as a collector or seize shared execution rights.

The 10.17-second all-project resource audit also observed one page of new host swap-in (pswpin 3731549→3731550; pswpout unchanged10993148), so inherited zero-new-swap admission did not pass. This observation is not proof of memory-pressure causality. Host/cgroup memory, disk, memory/IO PSI and no-new-OOM checks passed; numerical headroom does not waive authority. All visible external EP_L2 work, helpers and RSS/I/O were counted. No actual AA3 authority or simulator was started.

Four fixed cells remain K0_32x4, K0_64x8, K1_32x4, K1_64x8. Same new functional Core/binary/library/input/runtime, OO PIB128, physical640×128B, ordinary16KiB, shared96KiB, 64SM, four Tag banks, finiteV1, lower cap32768, 1410MHz and flush_l1=1. Only K option and logical sets/ways vary across all267 effective fields. The original Gaussian manifest has510 members and513 commands (3HtoD+510 kernels),283685120 active-thread instructions and65790 CTAs. The T combined Gaussian+GEMM count511 is not Gaussian membership. Fresh member SHA hashes and exact option parser receipts are CPU-only preparation.

K1 uses Lane V eager source-request semantics, not per-kernel broadcasting or global quiescent drain. Revoke query mappings; preserve physical/generation, oldRefs, inflight UID/sector masks, late responses, PIB, waiters, credits and collection/WB ownership. Ordinary delayed Tag commit remains unchanged. New observer supplement is accepted as noncomparative diagnostic. Source/X/Y2/Z2/U frozen commits are independently fetched and bound. Y2 PASS_K1_OO_MODEL_SCOPE is bounded OO structural/model/API/production-LDST evidence, not all eight contracts PASS, architectural load-value proof, full ISA correctness, IO K1, coherence, NoC/DRAM validation or PPA proof. IO K1 remains STOP. Its partial/failed categories and gaps are preserved in the copied gate.

W's full address scan remains UNAVAILABLE and is an attribution gap, not an extra four-cell admission gate. No exact cross-kernel retained-mapping causal fraction can be assigned without direct line+generation evidence. Actual Gaussian source E, mapping invalidation, liveRef-after-E and new full K0 equivalence are UNAVAILABLE because no full run occurred; source applicability is not misreported as an observed event count or a null performance result.

PRE_REGISTRATION.tsv and four specs are fully identified CPU design drafts marked STOP, **not a released executable registration**. The production runner is UNAVAILABLE, and execution_guard exits nonzero unconditionally. Authority STOP occurred before runner release and performance. A future separately admitted continuation would still have to publish the complete immutable runner/strict/resources/spec registration and fetch it back before starting; this pack does not grant that continuation, create a fifth attempt, reset a deadline or reserve shared execution rights.

The fixed intended sequence remains two new K0 controls, each once and strict against the full original input, ordered instructions/CTA/cycles/common traffic/mechanisms/conservation, then only if both calibrate exactly3798174 and3278356 cycles the two K1 points once. Material discrepancy stops K1 with no tuning/retry. Timeout7200s per actual start, one simulator at a time; timeout/deadlock/negative results preserved. All four cells and all missing values are disclosed. No old result substitutes for new K0.

No T2, new Tag, third input, new Core, IO K1, modern DTC or K2 starts. No original44/GM12/A/M/T/U/AA/AA2/v0.13 main data edits. Recommendations are review-only. This terminal STOP leaves no AA3 dispatcher to wake later.
''')
    md('EXECUTION_CONTRACT.md','''# Unreleased execution contract

Maximum aggregate AA+AA2+AA3 actual full Gaussian starts=4, one per inherited UUID, no reset/retry. Fixed intended order: K0_32x4,K0_64x8,K1_32x4,K1_64x8. Parallel cap1. No actual authority acquired. Any matching historical RUN_START/PID attempt identity blocks duplicate initiation. Failures remain in the matrix. Wrapper repair cannot create another simulator start or reset the original7200s deadline.

Before future release: exact fixed source/X/V/Y2/Z2/U and binary/library/ldd+actual maps, full267-option echo,510 member hashes/order/CTA/instructions/full list/ROI, accepted observer supplement, immutable runner+strict SHA/specs/metric dictionary/formulas/resources and an independently fetched publication are mandatory. A guard is not a runner. No default launch command is released here.

Fresh all-project admission requires original174 identity, no conflicting/unresolved DTC authority or execution FLOCK, hostMemAvailable≥32GiB, cgroupheadroom≥32GiB, diskfree≥10GiB, memoryfullPSI avg10≤1, IOfullPSI avg10≤25, ≥10s probe, no pswpin/out increase and no new OOM/oom_kill. Include external projects, totalRSS, actual cgroup use/swap, perprocessI/O, CPUquota/affinity/load/PSI and diskstats. Frozen CPU probe shows broad spare capacity but gives no authority waiver. No termination of foreign jobs, deletion of their files or retuning of service options.

Natural exit0, single actual start, full510-kernel ordered instruction/CTA identity, all effective options, correct loaded runtime,64SM, OO/PIB/physical/ordinary/Tag/pool/sector/Ref/generation/lower-credit/finite conservation are required. Preserve unavailable fields as typed UNAVAILABLE, not PASS. K1-specific checks use actual event summaries and corrected event-reclaim accounting. Both K0 full comparisons with frozen old controls must pass before any K1. This pack records NOT_RUN for all such run gates.
''')
    md('K0_EQUIVALENCE.md','''# K0 evidence boundary

Independent Y2 d085f98c proves four bounded omitted/0/frozen-Core OO LDST pairings with identical per-cycle state and103 public fields, including finite11. AA3's fresh production option-parser CPU receipts show defaultOFF and omitted=explicit0 for both Tag profiles. Source runtime/Framework registration identities and267 effective fields are bound. None is a new full Gaussian result.

Full K0_32x4 and K0_64x8 are both NOT_RUN. Their historical calibration cycles are3798174 and3278356 respectively; new cycles/instructions/traffic/mechanism equivalence is UNAVAILABLE. No K1 was started. The old numbers do not populate either new K0 cell or any factorial denominator.
''')
    md('PAPER_V013_RECOMMENDATIONS.md','''# v0.13 review recommendations — no paper/data edits

AA3 has no new GPU performance evidence. Do not add K1 speedups, null effects, interaction estimates, a new GM, equal-area claims or a main-configuration promotion. Keep original44/GM12 and A/M/T/U/v0.13 data unchanged. These are section-level proposals based on the bound source/Y2/Z2 evidence, not line edits to an identified canonical v0.13 manuscript.

Methods/model assumptions: distinguish original source-request selection from kernel-done; define K1 as immediate query-mapping withdrawal while preserving old owners and ordinary delayed Tag commit. State zero added simulated cycles as an assumed atomic operation, with hardware latency/bandwidth/PPA unproved. Identify the precise new Core and bounded OO support; retain IO STOP, ISA/load-value/coherence gaps.

Metrics/reproducibility: document public comparable metrics separately from K1-only diagnostics. Missing K0 event counters are UNAVAILABLE. Specify accepted128B-reference and retired-warp denominators, all64SM cycle integrals,32B L2 sectors and DRAM atom byte accounting. Separate source requests, changed mappings, event-retained/reclaimed and ordinary commit invocations; repeated idle calls and coalescing prohibit equating them.

Results/discussion: existing T/U Tag-capacity findings remain separate from invalidation policy. Z2's frozen paper notes retain discovery versus holdout labels, BICG T1-C slower than C+ and post-ready counterevidence; do not reinterpret existing capacity gains as measured K1 effects or a precise retained-mapping causal share. AA3 execution STOP is a provenance limitation, not a negative K1 mechanism finding. A four-cell performance subsection is unavailable until new qualified paired controls/results exist.

Threats to validity: disclose W address-scan absence, no line+generation cross-kernel attribution, changing conditional map-loss populations, fixed lookup timing despite Tag metadata growth, bounded Y2 fixtures/ABI scope and no statistical repetition. Host wall time is not GPU performance. Record AA3 zero actual starts and execution authority/resource limits in an artifact appendix if useful.
''')
    md('FOLLOWUP_MINIMAL_EXPERIMENTS.md','''# Minimal follow-up recommendations — no automatic execution

| Category | Minimal action | Value / limit |
|---|---|---|
| Existing evidence can close | Read frozen V/X/Y2 and AA3 supplement to correct request-versus-ordinary-commit wording and bounded OO scope | No new sim; no general coherence/value proof |
| Existing evidence can close | Use Z2 typed T/U evidence for capacity-only descriptions and counterevidence | No new GM, main-data replacement or K1 causal claim |
| Operational prerequisite, not a scientific experiment | Resolve the separately identified deferred dispatcher's ownership/retirement through its own authority; then fresh all-project resource audit | No unilateral signal permission is inferred here; no new start budget |
| Already bounded four-cell study with paper value | Only after all admission/release requirements close, complete the inherited four Gaussian controls/treatments once, with K0-first exact calibration and same single Core | Reuses total4 budget, not an additional experiment set; current Goal terminates STOP |
| Potential new attribution study requiring new scientific approval | If qualified four-cell results exist and attribution matters, obtain minimal same-SM line+generation/owner linkage around actual source requests using existing immutable outputs when present; otherwise propose one separately qualified observation plan | Would distinguish retained mappings from mere capacity; address-only reuse is insufficient; no automatic added sim or secondCore |
| Stop branch under current evidence | T2/newTags/extra inputs/BICG-DWT2D reruns/IO K1/modern DTC/K2 or forcing new events to show a gain | Outside authorization or unresolved model scope; no launch |

No extra full canary, fifth cell, repetition or tuning is proposed as an automatic recovery for weak/negative results. No fullrun result exists in AA3, so do not select follow-ups from an invented effect size.
''')
    # Source identities, original-vs-new file-level changes and unchanged ordinary source.
    paths=git(CORE_REPO,'diff','--name-only',BASE_CORE,CANDIDATE_CORE).splitlines()
    source=[]
    for path in paths:
        a=subprocess.run(['git','-C',str(CORE_REPO),'show',BASE_CORE+':'+path],capture_output=True).stdout
        b=blob(CORE_REPO,CANDIDATE_CORE,path)
        source.append(dict(path=path,base_sha256=hashlib.sha256(a).hexdigest(),K1_sha256=hashlib.sha256(b).hexdigest(),K1_blob=git(CORE_REPO,'rev-parse',CANDIDATE_CORE+':'+path)))
    patch=subprocess.check_output(['git','-C',str(CORE_REPO),'diff','--binary','--unified=0',BASE_CORE,CANDIDATE_CORE])
    (PACK/'CORE_DELTA_U0.patch').write_bytes(patch)
    ordinary=[]
    for path in ['src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h']:
        a=blob(CORE_REPO,BASE_CORE,path);b=blob(CORE_REPO,CANDIDATE_CORE,path);assert a==b
        ordinary.append(dict(path=path,base_and_K1_sha256=hashlib.sha256(a).hexdigest(),byte_identical=True))
    write(PACK/'CORE_SOURCE_DELTA.json',dict(base=BASE_CORE,K1=CANDIDATE_CORE,changed_paths=source,ordinary_cache_sources=ordinary,patch_sha256=sha(PACK/'CORE_DELTA_U0.patch'),apply_contract='git apply --unidiff-zero; no production Core edit performed'))
    # Update the new dictionary only; original AA2 dictionary is immutable.
    p=PACK/'METRIC_DICTIONARY.tsv'
    with p.open() as f:metrics=list(csv.DictReader(f,delimiter='\t'))
    for row in metrics:row['comparability_class']='K1_ONLY_NONCOMPARATIVE_DIAGNOSTIC' if row['field'].startswith('DTC_INVALIDATE_V1_SUMMARY.') else 'PUBLIC_SAME_DEFINITION_ONLY_AFTER_STRICT';row['AA3_actual_availability']='UNAVAILABLE_NO_NEW_RUN'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(metrics[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(metrics)
    rows=[]
    for point,uid,k,sets,ways,cal in POINTS:
        spec=json.loads((PACK/'specs'/f'{point}.json').read_text())
        # Dictionary changed explicitly by the newly accepted observer contract.
        spec['source_event_metric_dictionary_sha256']=sha(p)
        (PACK/'specs'/f'{point}.json').write_text(json.dumps(spec,indent=2)+'\n')
        rr=PACK/'run_receipts'/uid
        write(rr/'STRICT.json',dict(status='STOP_NOT_RUN',point=point,attempt_uuid=uid,actual_starts=0,natural_exit='UNAVAILABLE',cycles='UNAVAILABLE',all_510_kernel_strict='NOT_RUN',source_events='UNAVAILABLE',new_K0_calibration='NOT_RUN' if k==0 else 'BLOCKED_BY_UNRUN_K0_AND_AUTHORITY',loaded_library_maps='UNAVAILABLE_NO_PROCESS',run_checks_passed=False,scope='NO_PERFORMANCE_RESULT; CPU preparation and bounded upstream proofs are not a full-run receipt'))
        table(rr/'RAW_SHA256.tsv',[dict(path='NO_RUN_DIRECTORY_OR_RUN_START_CREATED',sha256='UNAVAILABLE',status='NOT_RUN')])
        rows.append(dict(point=point,uuid=uid,K=k,tag_sets=sets,tag_ways=ways,status='STOP_AUTHORITY_NOT_CLOSED',actual_starts=0,cycles='UNAVAILABLE',kernels='UNAVAILABLE',active_instructions='UNAVAILABLE',CTAs='UNAVAILABLE',source_requests='UNAVAILABLE',mapping_changed='UNAVAILABLE',strict='STOP_NOT_RUN',calibration_reference_cycles=cal,calibration_reference_role='HISTORICAL_ONLY_NOT_NEW_PERFORMANCE',raw_run_directory='UNAVAILABLE_NOT_CREATED',strict_receipt_sha256=sha(rr/'STRICT.json')))
    table(PACK/'FULL_MATRIX.tsv',rows)
    table(PACK/'TERMINAL_MECHANISM_COMPARISON.tsv',[dict(field=r['field'],unit=r['typed_unit'],numerator=r['numerator'],denominator=r['denominator'],comparability=r['comparability_class'],**{point:'UNAVAILABLE_NO_RUN' for point,*_ in POINTS}) for r in metrics])
    table(PACK/'SOURCE_EVENT_ORDINARY_COMPARISON.tsv',[dict(point=point,source_request_cycle='UNAVAILABLE',source_requests='UNAVAILABLE',mapping_changed='UNAVAILABLE',retained_at_event='UNAVAILABLE',reclaimed_at_event='UNAVAILABLE',ordinary_commit_cycle='UNAVAILABLE',ordinary_commits='UNAVAILABLE',scope='K1_ONLY_NONCOMPARATIVE_DIAGNOSTIC' if k else 'K0_MISSING_DIAGNOSTICS_UNAVAILABLE_NOT_ZERO') for point,uid,k,*_ in POINTS])
    write(PACK/'ATTEMPT_BUDGET.json',dict(total_actual_start_limit=4,AA_actual_starts=0,AA2_actual_starts=0,AA3_actual_starts=0,total_actual_starts=0,budget_reset=False,reserved_UUIDs={p:u for p,u,*_ in POINTS},AA3_canary_or_other_full_inputs=0))
    # Independent algebra only: explicitly synthetic fixture cannot enter results.
    a,b,c,d=map(Fraction,[10,8,12,9]);q32=c/a;q64=d/b;t0=b/a;t1=d/c;i=a*d/(b*c)
    assert i==q64/q32==t1/t0 and (d-b)-(c-a)==a+d-b-c
    quantities=[('Q32','c/a','a'),('Q64','d/b','b'),('T0','b/a','a'),('T1','d/c','c'),('I','a*d/(b*c)','b*c'),('logI','ln(a)+ln(d)-ln(b)-ln(c)','positive cycles'),('Delta','a+d-b-c','1'),('K_main','((c-a)+(d-b))/2','2'),('Tag_main','((b-a)+(d-c))/2','2')]
    table(PACK/'FACTORIAL_EFFECTS.tsv',[dict(quantity=n,formula=f,exact_denominator=den,status='UNAVAILABLE_MISSING_ALL_FOUR_NEW_ACCEPTED_CYCLES',value='UNAVAILABLE') for n,f,den in quantities])
    write(PACK/'Z2_INDEPENDENT_RECALCULATION.json',dict(status='FORMULA_IDENTITY_CHECKED_OBSERVED_RECALCULATION_UNAVAILABLE',a='UNAVAILABLE',b='UNAVAILABLE',c='UNAVAILABLE',d='UNAVAILABLE',historical_controls_not_substituted=True,synthetic_algebra_fixture_only=dict(a=10,b=8,c=12,d=9,Q32=str(q32),Q64=str(q64),T0=str(t0),T1=str(t1),I=str(i),Delta=str(a+d-b-c)),actual_effects='UNAVAILABLE',no_logI_or_ratio_from_missing_cells=True))
    write(PACK/'STOP_RECORD.json',dict(utc=now(),status='STOP_LEGAL_EXECUTION_AUTHORITY_NOT_CLOSED',primary_reason='Different live deferred dispatcher PID3291777/start_ticks550530984 has future launch path; ownership/release not closed and outside specified watcher SIGTERM permission',additional_current_resource_gate='10.17s probe pswpin increased one page, zero-new-swap check failed',retired_watch=dict(pid=1425986,start_ticks=584741606,single_SIGTERM=True,lock_released=True),actual_starts=0,full_executable_registration_released=False,production_runner='UNAVAILABLE_NOT_RELEASED',pending_AA3_dispatcher=False,scientific_performance_null_claim=False))
    write(PACK/'STRICT_AUDIT.json',dict(status='STOP_NOT_A_FULL_RUN_PASS',cpu_source_identity='PASS',CPU_input_identity_510='PASS',CPU_267_effective_profile='PASS_ONLY_K_SETS_WAYS_DIFFER',Y2_gate='PASS_K1_OO_MODEL_SCOPE_BOUNDED',observer_contract=observer,watcher_retirement='PASS_EXACT_PARENT_ONLY_FLOCK_RELEASED',other_DTC_authority='STOP_UNRESOLVED_DIFFERENT_DEFERRED_DISPATCHER',resource_admission='FAIL_NO_NEW_SWAP_CHECK',full_executable_registration='NOT_RELEASED',all_four_strict='NOT_RUN',K0_full_equivalence='NOT_RUN',K1_actual_correctness_or_effect='UNAVAILABLE',actual_starts=0,run_receipts={r['point']:r['strict_receipt_sha256'] for r in rows}))
    # Refresh the CPU draft index after the explicit metric supplement update.
    pp=PACK/'PRE_REGISTRATION.tsv'
    with pp.open() as f:reg=list(csv.DictReader(f,delimiter='\t'))
    for r in reg:r['spec_sha256']=sha(PACK/'specs'/f"{r['point']}.json")
    with pp.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(reg[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(reg)
    md('LATEST_REPORT.md','''# AA3 convergence: terminal scientific/execution STOP, 0/4 actual starts

**STOP_LEGAL_EXECUTION_AUTHORITY_NOT_CLOSED**. Original174/root. No full simulator or canary started. All four inherited UUID cells are disclosed as STOP/NOT_RUN; new cycles, event counts and factorial effects remain UNAVAILABLE. Historical3798174/3278356 are calibration references only. This is not a measured null or negative K1 result.

The specifically authorized Core41 watcher PID1425986/start_ticks584741606 was revalidated against argv, script/helper hashes, actual descendants/tasks, logs, target paths and fdinfo/FLOCK. A single pidfd-bound SIGTERM was sent to the parent only. It exited; sleep120 inherited its fd and later ended naturally. The original lock device156/inode37920070 and file were preserved, with no remaining fdinfo FLOCK holder. No other process was signaled and no lock was deleted/acquired. See WATCHER_RELEASE_RECEIPT.json and raw pre/signal receipts.

A separate live deferred dispatcher PID3291777/start_ticks550530984 still waits to launch seven old BICG/GESUMMV points. Its current Core41 HEAD does not match its requiredbbcbb5e7, and its old R1 path is superseded/nonformal. Those facts do not retire it or release its execution rights. It is not a read-only collector and is outside the one specified watcher signal permission. AA3 therefore cannot claim exclusive legitimate execution authority or acquire shared execution rights. OTHER_AUTHORITY_REVIEW.json retains the source, PID/start, wait conditions and future path. Upstream AB retirement audit was also reviewed; it explicitly did not approve stopping the other controls.

All-project≥10s resources were measured: memory/headroom/disk/PSI/no-new-OOM passed, CPU idle fraction≈99.17%; pswpin increased3731549→3731550 (one page), pswpout unchanged10993148. Thus zero-new-swap admission also failed; allocated swap alone is not blamed as pressure. EXECUTION_RESOURCES.tsv and raw snapshots retain all visible projects, EP_L2 sim and helper RSS/I/O/cgroup/CPU accounting. No resource observation overrides the authority STOP.

Frozen Core/X/V/Y2/Z2/U commits were independently fetched and exact-matched. The real X executable/library SHA and loader resolution were rechecked. Y2 finald085f98c bounded OO PASS and its partial/failed/unproven scopes remain intact. Gaussian510 member identities were freshly rehashed against acceptedT manifest;510 ordered kernels,283685120 active-thread instructions,65790CTAs and original513-command list were bound. Fresh production CPU parser checks prove defaultOFF and omitted=explicit0;267 effective fields differ only in K/logicalsets/logicalways.

OBSERVER_SUPPLEMENT_V1.md records the user's newly accepted K1-only noncomparative telemetry contract without a second Core. K0 missing event fields remain UNAVAILABLE; host wall time is not GPU performance, and zero added simulated invalidation cycles is an explicit model assumption. W address scan remains an attribution gap, not a new hard gate. CORE_SOURCE_DELTA.json and PHYSICAL_CONSERVATION_DELTA.md retain source/ordinary identity and event-release accounting.

PRE_REGISTRATION.tsv and four specs are identified CPU drafts marked STOP, not a complete executable release: no production runner or launch authority was released. The fail-closed guard cannot run a simulator. No new performance appeared before this publication. FULL_MATRIX.tsv, per-UUID strict/raw receipts, typed mechanism and source/ordinary tables, Z2 algebra/UNAVAILABLE recalculation, SCIENTIFIC_SCOPE.md and paper/minimal-follow-up recommendations are included. A CPU preparation whitelist typo was corrected deterministically without changing any scientific option or rerunning a simulator; the failure is preserved in ENGINEERING_CORRECTIONS.json/raw.

No original44/GM12/A/M/T/U/AA/AA2 or v0.13 main data was changed. No T2, newTag, otherinput, secondCore, IO K1, modern DTC or K2 run. No AA3 pending dispatcher remains. Final HEAD/tree/push/fetch-back/per-file verification/clean receipt is external at /workspace/dtc-lane-aa3-gaussian-174-v1/FINAL_FETCH_BACK.json to avoid self-reference. Goal ends at this authorized STOP; there is no automatic continuation.
''')
    # Archive only small raw receipts, not raw simulator data or binaries.
    for name in ['WATCHER_PRE_SIGNAL_REVIEW.json','WATCHER_PRE_SIGNAL_REVIEW_V2.json','WATCHER_SIGTERM.json','WATCHER_PARENT_EXIT.json']:
        shutil.copy2(ROOT/name,PACK/name)
    print('Four-cell terminal STOP package written. No performance values or starts.')

if __name__=='__main__':main()

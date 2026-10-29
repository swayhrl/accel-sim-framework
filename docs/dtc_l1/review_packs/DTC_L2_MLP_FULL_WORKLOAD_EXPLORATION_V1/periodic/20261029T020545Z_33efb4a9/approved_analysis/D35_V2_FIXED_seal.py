"""Seal versioned fail-closed fix, preserving every V1 byte."""
import pathlib,json
import derived35_consumer as d
D=pathlib.Path(__file__).parent;V1=D.parent/'derived35_analysis_consumer_v1';O=D/'DRY_20261028T235418795934Z'
def put(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
old=d.read(V1/'DRY_20261028T234226933840Z/EVIDENCE.json');new=d.read(O/'EVIDENCE.json');qa=d.read(D/'CPU_QUALIFICATION.json')
assert qa['consumer_sha256']==new['consumer_sha256']==d.sha(D/'derived35_consumer.py')and qa['status']=='PASS'
projection=lambda v:[(r['original_cohort'],r['selected']['cohort']if r['selected']else None,r['selected']['RESULT_sha256']if r['selected']else None)for r in v['rows']]
assert projection(old)==projection(new)and old['summary']==new['summary']and new['summary']['formal_GM_generated']is False
put(D/'NORMAL_PATH_COVERAGE_EQUIVALENCE.json',dict(previous_source_sha256=d.sha(V1/'derived35_consumer.py'),new_source_sha256=d.sha(D/'derived35_consumer.py'),previous_dry_path=str(V1/'DRY_20261028T234226933840Z/EVIDENCE.json'),previous_dry_sha256=d.sha(V1/'DRY_20261028T234226933840Z/EVIDENCE.json'),new_dry_path=str(O/'EVIDENCE.json'),new_dry_sha256=d.sha(O/'EVIDENCE.json'),all350_selected_source_SHA_projections_equal=True,coverage_population_summaries_equal=True,original_valid=323,separate_R2_reference=1,IR_accepted=0,missing=26,formal_GM_generated=False))
interface=d.read(V1/'INTERFACE.json');interface.update(module=str(D/'derived35_consumer.py'),module_sha256=d.sha(D/'derived35_consumer.py'),version=2,publication_receipt_not_yet_provided=True)
interface['publication_receipt']['files']={str(d.CONTRACT):d.CONTRACT_SHA,str((D/'derived35_consumer.py').resolve()):d.sha(D/'derived35_consumer.py'),str((D/'CPU_QUALIFICATION.json').resolve()):d.sha(D/'CPU_QUALIFICATION.json')}
put(D/'INTERFACE.json',interface)
report='''# Derived35 readonly consumer V2

V2 fixes the independently confirmed V1/c9 source-flow defect before formal release. The frozen c9 source, all V1 reports/QA and the A independent counterexample remain unchanged.

`measure` now reads an existing RESULT marker **before** identity/role checks. A read/race/unknown-state failure carries explicit acceptance uncertainty. Failed identity/role verification also blocks substitution. `choose_reference` retains a valid original first, then HOLDs any apparent accepted/uncertain/identity-invalid original instead of treating it as an eligible negative gap. The exact twelve negative-lineage links and all scientific/strict/publication rules remain unchanged.

Eleven focused CPU delta checks reproduce the old defect through the real frozen `measure` → `choose_reference` functions with a private apparent-PASS file and bad canonical role, then prove V2 HOLD for PASS, REUSE, wrong ROI, unreadable JSON, unknown state and bad-role negative. A genuinely absent original scan result with valid identity can still use its exact, already qualified R2 reference. No production file is altered. An AST comparison establishes that only `measure` and `choose_reference` changed; the prior30 source-bound qualification checks apply to the unchanged identity/strict/archive/math/publication code. These are 11 new delta checks plus inherited30 coverage, not41 independent new tests.

The new actual dry validation is source-for-source identical on all350 selections to the frozen normal V1 snapshot: **323 original accepted + one separately identified scan R2 = 324/350 references; 26 remain missing; IR11 have no accepted source at this snapshot**. Available/common/suite/fourway coverage is unchanged. Six ratified downstream P0 proof objects omit suite/profile display fields; the precise V1 field-presence artifact remains the source for that disclosure, while full input/binding/build/all270/ROI equality remains mandatory.

Formal GM remains disabled. Main must publish this V2 source and its exact QA, then provide the complete source-bound receipt described in INTERFACE. A contract-only or old-c9 publication cannot release V2. No legacy roles/unionFalse/summary/adaptive/runtime-parent membership or English v0.23 changed. Full raw/archive/native acceptance is reused from source-bound receipts; no new large raw replay or full native restore was performed by this reader.

This delivery implements analysis only. It starts0 models, grants0 starts and changes0 production functions. Scope/registrar/runtime/adoption integration is not installed or authorized by it.
'''
with(D/'REPORT.md').open('x')as f:f.write(report)
files=[D/x for x in ['derived35_consumer.py','qualify_delta.py','run_dry.py','seal.py','CPU_QUALIFICATION.json','EXACT_DIFF_FROM_C9.patch','NORMAL_PATH_COVERAGE_EQUIVALENCE.json','INTERFACE.json','REPORT.md']]+[O/'EVIDENCE.json',O/'REPORT.json']
external=[V1/'derived35_consumer.py',V1/'CPU_QUALIFICATION_FROZEN.json',V1/'MANIFEST_FINAL.json',V1/'RATIFIED_P0_LABEL_FIELD_PRESENCE.json',d.A/'agents/A/derived35_consumer_independent_review_v1/REVIEW.json',d.A/'agents/A/derived35_consumer_independent_review_v1/BRANCH_COUNTEREXAMPLE.json',d.A/'agents/A/derived35_consumer_independent_review_v1/MANIFEST.json']
put(D/'MANIFEST.json',dict(schema='DTC_DERIVED35_READONLY_CONSUMER_DELIVERY_V2',status='FAILCLOSED_FIX_CPU_QUALIFIED_DRY_VALIDATED_AWAITING_PUBLIC_RELEASE',consumer_sha256=d.sha(D/'derived35_consumer.py'),CPU_QA_sha256=d.sha(D/'CPU_QUALIFICATION.json'),contract_sha256=d.CONTRACT_SHA,files=[dict(path=str(p),relative_path=str(p.relative_to(D)),sha256=d.sha(p),bytes=p.stat().st_size)for p in files],external_source_pins=[dict(path=str(p),sha256=d.sha(p))for p in external],formal_GM_generated=False,models_started=0,new_grants=0,production_changes=0))
print(json.dumps(dict(directory=str(D),manifest_sha256=d.sha(D/'MANIFEST.json'),source_sha256=d.sha(D/'derived35_consumer.py'),QA_sha256=d.sha(D/'CPU_QUALIFICATION.json'),report_sha256=d.sha(D/'REPORT.md'))))

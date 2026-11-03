"""Seal this independent delivery; never modifies source experiments."""
import json,pathlib,datetime
import derived35_consumer as d
D=pathlib.Path(__file__).parent;O=D/'DRY_20261028T234226933840Z';v=d.read(O/'EVIDENCE.json');s=v['summary'];qa=d.read(D/'CPU_QUALIFICATION_FROZEN.json')
assert v['consumer_sha256']==qa['consumer_sha256']==d.sha(D/'derived35_consumer.py')
assert qa['status']=='PASS' and qa['count']==30 and s['formal_GM_generated'] is False
def put(p,value):
    with p.open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def text(p,value):
    with p.open('x')as f:f.write(value.rstrip()+'\n')
refs=[r['original']for r in v['rows']if r['original'].get('evidence',{}).get('ratified_P0_reference')]
labels=[dict(cohort=r['cohort'],input_digest=r['input_digest'],input_binding_sha256=r['input_binding_sha256'],RESULT_sha256=r['RESULT_sha256'],**{k:r['evidence'][k]for k in ['source_suite_display','frozen35_suite_display','source_profile_display','frozen35_profile','reference_result_path','reference_result_sha256']})for r in refs]
assert len(labels)==6
put(D/'RATIFIED_P0_PRESENTATION_LABELS.json',dict(note='Only these six immutable ratified references retain legacy suite/profile display strings. Full input/binding/build/270-options/ROI equality remains mandatory; P0 parameter identity is established by all270 equality, not the legacy profile label.',rows=labels))
coverage=[]
for p in d.read(d.CONTRACT)['profiles']:
    groups=s['aggregates'][p]
    coverage.append(dict(profile=p,DH_available=groups['ALL']['DH_speedup']['available']['n'],DH_all_profile_common=groups['ALL']['DH_speedup']['all_profile_common']['n'],CH_available=groups['ALL']['CH_speedup']['available']['n'],relative_fourway=groups['ALL']['relative_DTC_improvement']['available']['n'],suites={k:dict(expected=x['DH_speedup']['available']['expected_n'],DH_available=x['DH_speedup']['available']['n'],DH_common=x['DH_speedup']['all_profile_common']['n'],relative_fourway=x['relative_DTC_improvement']['available']['n'])for k,x in groups.items()if k!='ALL'}))
put(D/'COVERAGE_ONLY.json',dict(UTC=v['UTC'],analysis_namespace=s['analysis_namespace'],formal_GM_generated=False,expected_inputs=35,original_valid=sum(r['original']['valid']for r in v['rows']),alternate_valid=sum(bool(r['alternate']and r['alternate']['valid'])for r in v['rows']),named_reference_cells=s['selected_measurement_references'],missing_cells=s['missing_slots'],profiles=coverage,missing=[dict(key=r['key'],original_cohort=r['original_cohort'],raw_state=r['original']['raw_state'],alternate_cohort=r['alternate']['cohort']if r['alternate']else None,reason=r['reason'])for r in v['rows']if r['selected']is None]))
interface=dict(schema='DTC_DERIVED35_READONLY_CONSUMER_INTERFACE_V1',module=str(D/'derived35_consumer.py'),module_sha256=d.sha(D/'derived35_consumer.py'),contract=dict(path=str(d.CONTRACT),sha256=d.CONTRACT_SHA),APIs=dict(dry='ReadonlyConsumer().run() -> source-bound coverage; all formal GM/value fields disabled',formal='ReadonlyConsumer().run(publication_receipt=absolute_path, qualification=absolute_CPU_QA_path) -> independently named statistics; never runtime adoption',pure_selection='choose_reference(original, alternate, fixed_link)',pure_statistics='summarize(frozen_points, validated_selected_measurements, profiles, formal=False); formal=True is used only in explicit synthetic CPU algebra fixtures unless called behind run publication_gate'),publication_receipt=dict(schema='DTC_DERIVED35_PUBLICATION_RECEIPT_V1',verified=True,qualification_only=False,commit='40-character immutable git commit; Main independently verifies public readback',files={str(d.CONTRACT):d.CONTRACT_SHA,str((D/'derived35_consumer.py').resolve()):d.sha(D/'derived35_consumer.py'),str((D/'CPU_QUALIFICATION_FROZEN.json').resolve()):d.sha(D/'CPU_QUALIFICATION_FROZEN.json')}),publication_receipt_not_yet_provided=True,exact_initial350_only=True,legacy_summary_parent_adaptive_or_source_roles_modified=False)
put(D/'INTERFACE.json',interface)
table='\n'.join('| '+r['profile']+' | '+str(r['DH_available'])+'/35 | '+str(r['DH_all_profile_common'])+'/35 | '+str(r['CH_available'])+'/35 | '+str(r['relative_fourway'])+'/35 |'for r in coverage)
label_table='\n'.join('| '+r['cohort']+' | '+str(r['source_suite_display'])+' → '+r['frozen35_suite_display']+' | '+str(r['source_profile_display'])+' → P0 |'for r in labels)
text(D/'REPORT.md',f'''# Independent Derived35 analysis consumer V1

The Main-approved contract ec62 is implemented as a new readonly named view. At {v['UTC']}, **323 original accepted measurements plus one separately identified scan R2 measurement supply 324/350 references; 26 remain missing**. All eleven IR measurements are pending/unaccepted at this snapshot. No original result, role, union flag, MATRIX, SCOPE, runtime parent or adaptive policy changed. This is not a claim that original350 has 324 accepted.

The consumer source is `{d.sha(D/'derived35_consumer.py')}`. Thirty new focused CPU checks pass (QA `{d.sha(D/'CPU_QUALIFICATION_FROZEN.json')}`). They cover original-source priority even when an alternate is faster, the exact twelve frozen links, rejected ROI/build/Hash changes, identical denominators, missing data, absent nonP0 CH, and fault-injected real R2 DONE/UUID/strict/archive critical-record joins. CPU synthetic ratios are not scientific results.

**Formal GM is disabled.** Contract publication alone does not release the consumer. Main must publish this exact consumer plus CPU QA and supply the source-bound public readback receipt described in `INTERFACE.json`. Pure algebra fixtures test calculations with synthetic data; the actual `ReadonlyConsumer.run` API enforces publication before real metric output. No full35 or candidate adoption is claimed.

| Profile | DH paired available | DH common across all profiles | CH paired available | Complete fourway |
|---|---:|---:|---:|---:|
{table}

Available, fixed all-profile common, suite and same-profile fourway populations are separately named and enumerated in `EVIDENCE.json`. Each metric is formed from matched source cells for the same input/build/ROI before aggregation. NonP0 CH is absent, so relative DTC improvement cannot currently be reported. No per-program best configuration is constructed. This contract covers the initial350 slots; future CH/combination matrices require an explicit named-contract extension instead of globbing extra results.

The source loader checks frozen350/12-link contract SHA, full input-binding bytes, same Core/FW/binary, same-design qualified generator vectors, all270 effective options, CTA/instruction/kernel ROI, performance scope, natural DONE==EXIT==authority receipt, UUID/INTENT/dispatch joins, original strict and additional strict sidecar SHA, full archive/native-restoration receipts and small critical source/restored file SHA. It deliberately **reuses prior full strict/archive/native acceptance**, and does not rescan giant raw streams, rehash archive chunks, or claim a new independent full native restoration. Every consulted small source is SHA-listed. Existing accepted originals/R2 must retain their previously frozen RESULT SHA. New IR results must also retain exact predeclared negative lineage and separate role/mirror/exclusion flags.

Six ratified P0 references use older display labels, listed below and in `RATIFIED_P0_PRESENTATION_LABELS.json`. Their input digest, input-binding SHA, build, complete270 physics and ROI remain exact. Legacy suite/profile text is not used to loosen input identity or select a workload; the frozen35 grouping and all270 P0 vector determine presentation/parameter identity.

| Ratified original slot | Legacy suite → frozen35 suite | Legacy profile → vector identity |
|---|---|---|
{label_table}

R2 remains `SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL`; IR remains `INCIDENT_RECOVERY_PERFORMANCE_TRIAL`. All original negative records stay negative. A reference is only a measurement source in `DTC_L2_MLP_DERIVED35_SAME_PHYSICS_V1`; no legacy accepted identity or ledger union is created. Pending or rejected sources remain missing, never 0 or 1. Runtime-parent/adoption integration is not authorized by this package. Source/binary/config/input semantics and English v0.23 are unchanged.

The frozen dry evidence is `DRY_20261028T234226933840Z/EVIDENCE.json`. Earlier development dry/QA files remain outside this final delivery manifest and are not final source qualification. Models started: 0; grants: 0; production mutations: 0; Git actions: 0.
''')
files=[D/x for x in ['derived35_consumer.py','qualify_consumer.py','run_dry.py','seal.py','CPU_QUALIFICATION_FROZEN.json','RATIFIED_P0_PRESENTATION_LABELS.json','COVERAGE_ONLY.json','INTERFACE.json','REPORT.md']]+[O/'EVIDENCE.json',O/'REPORT.json']
put(D/'MANIFEST.json',dict(schema='DTC_DERIVED35_READONLY_ANALYSIS_CONSUMER_DELIVERY_V1',status='CPU_QUALIFIED_DRY_VALIDATED_AWAITING_PUBLIC_CONSUMER_RELEASE',consumer_sha256=d.sha(D/'derived35_consumer.py'),CPU_QA_sha256=d.sha(D/'CPU_QUALIFICATION_FROZEN.json'),contract_sha256=d.CONTRACT_SHA,files=[dict(path=str(p),relative_path=str(p.relative_to(D)),sha256=d.sha(p),bytes=p.stat().st_size)for p in files],formal_GM_generated=False,actual_models_qualified_by_this_CPU_package=False,prior_accepted_receipts_reused=True,models_started=0,new_grants=0,production_changes=0))
print(json.dumps(dict(directory=str(D),manifest_sha256=d.sha(D/'MANIFEST.json'),report_sha256=d.sha(D/'REPORT.md'),source_sha256=d.sha(D/'derived35_consumer.py'),CPU_QA_sha256=d.sha(D/'CPU_QUALIFICATION_FROZEN.json'),coverage=coverage)))

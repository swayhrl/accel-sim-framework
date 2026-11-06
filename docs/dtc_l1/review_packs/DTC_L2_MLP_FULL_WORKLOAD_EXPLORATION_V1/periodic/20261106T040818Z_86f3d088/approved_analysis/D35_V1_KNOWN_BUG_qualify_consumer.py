"""Focused new consumer qualification. Synthetic math is CPU-only, not science.
Actual R2 joins reuse native/archive receipts; no raw-log or tar-chunk re-audit.
"""
import copy,datetime,json,pathlib,sys,math
sys.dont_write_bytecode=True
import derived35_consumer as d
def audit(event,args):
    if event=='subprocess.Popen' or event.startswith('os.exec') or event in ('os.system','os.kill','os.killpg'):raise AssertionError('CPU only: no processes/models/signals')
sys.addaudithook(audit)
checks=[]
def check(name,fn):
    fn();checks.append(dict(name=name,status='PASS'))
def reject(fn):
    try:fn()
    except (d.EvidenceHold,KeyError,ValueError):return
    raise AssertionError('negative unexpectedly admitted')
def eq(a,b):assert a==b,(a,b)
def mutated(v,path,x):
    v=copy.deepcopy(v);cur=v
    for k in path[:-1]:cur=cur[k]
    cur[path[-1]]=x;return v
c=d.ReadonlyConsumer();scope=c.scope['points'];link=next(iter(c.links.values()))
o=dict(cohort=link['original_cohort'],valid=True,cycles=100,apparent_accepted=True,scientific_role='ORIGINAL_PRIMARY_SLOT')
a=dict(cohort=link['alternate_cohort'],valid=True,cycles=1,scientific_role=link['alternate_role'])
check('faster alternate never replaces valid original',lambda:eq(d.choose_reference(o,a,link)['selected'],o))
missing=dict(o,valid=False,apparent_accepted=False,cycles=None)
check('only exact predeclared alternate can fill named reference',lambda:eq(d.choose_reference(missing,a,link)['selected'],a))
check('no link means no alternate even if faster and accepted',lambda:eq(d.choose_reference(missing,a,None)['selected'],None))
check('invalid apparent accepted original blocks alternate substitution',lambda:eq(d.choose_reference(dict(o,valid=False),a,link)['selected'],None))
check('wrong alternate role rejected',lambda:eq(d.choose_reference(missing,dict(a,scientific_role='CORRECTNESS_REPAIR'),link)['selected'],None))
check('pending and negative measurements remain missing',lambda:eq(d.choose_reference(missing,dict(a,valid=False,cycles=None),link)['selected'],None))
target=c.spec(link['original_cohort']);candidate=c.spec(link['alternate_cohort'])
check('wrong ROI rejects declared comparison',lambda:reject(lambda:d.assert_identity(mutated(candidate,['expected','CTA'],target['expected']['CTA']-1),target,c.science_keys)))
check('wrong Core rejects declared comparison',lambda:reject(lambda:d.assert_identity(dict(candidate,core_commit='0'*40),target,c.science_keys)))
hashkey=next(k for k in candidate['expected_options']if 'hash'in k.lower())
check('wrong Hash rejects declared comparison',lambda:reject(lambda:d.assert_identity(mutated(candidate,['expected_options',hashkey],['99']),target,c.science_keys)))
old='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1';new=c.links[old]['alternate_cohort'];spec=c.spec(new);value=c.get(d.R/'analysis'/(new+'.RESULT.json'));proof=value['proof']
check('strict actual wrong ROI rejected',lambda:reject(lambda:d.assert_proof(dict(proof,CTA=proof['CTA']+1),spec,value['cycles'])))
check('strict actual wrong binary rejected',lambda:reject(lambda:d.assert_proof(dict(proof,binary_sha256='0'*64),spec,value['cycles'])))
check('strict effective Hash mismatch rejected',lambda:reject(lambda:d.assert_proof(mutated(proof,['effective_options',hashkey],['99']),spec,value['cycles'])))
# Fixed 35-program synthetic table uses the real frozen slot identities. Its
# numbers exist only to test algebra/populations, never to generate paper data.
selections=[]
for p in scope:
    s=c.spec(p['cohort']);m=dict(cohort=p['cohort'],scientific_role='CPU_SYNTHETIC_ONLY',valid=True,cycles=100 if p['profile']=='P0'else 50,RESULT_sha256='qualification_only',expected_ROI=s['expected'],profile=p['profile'],**{k:s[k]for k in ('input_digest','input_binding_sha256','core_commit','framework_commit','binary_sha256','cell')})
    selections.append(dict(key={k:p[k]for k in ('input_digest','program','suite','cell','profile')},selected=m))
result=d.summarize(scope,selections,c.contract['profiles'],formal=True)
check('uniform35 matched DH factor GM and denominator',lambda:eq((math.isclose(result['aggregates']['E384']['ALL']['DH_speedup']['available']['GM'],2.0,rel_tol=1e-12),result['aggregates']['E384']['ALL']['DH_speedup']['available']['n']),(True,35)))
check('absent nonP0 CH forbids relative advantage',lambda:eq(result['aggregates']['E384']['ALL']['relative_DTC_improvement']['available']['n'],0))
partial=copy.deepcopy(selections);next(r for r in partial if r['key']['profile']=='E384')['selected']=None
pr=d.summarize(scope,partial,c.contract['profiles'],formal=True)
check('one missing stays34 and all-profile common34',lambda:eq((pr['aggregates']['E384']['ALL']['DH_speedup']['available']['n'],pr['aggregates']['M8']['ALL']['DH_speedup']['all_profile_common']['n']),(34,34)))
check('missing never filled with baseline1',lambda:eq(pr['aggregates']['E384']['ALL']['DH_speedup']['available']['missing_n'],1))
check('available versus common populations remain separate',lambda:eq(pr['aggregates']['M8']['ALL']['DH_speedup']['available']['n'],35))
check('suite expected denominator uses frozen membership',lambda:eq(sum(pr['aggregates']['E384'][s]['DH_speedup']['available']['expected_n']for s in {p['suite']for p in scope}),35))
cells={d.key(r['key']):r['selected']for r in selections};digest=scope[0]['input_digest'];wrong=copy.deepcopy(cells);wrong[(digest,'DH','E384')]['input_binding_sha256']='x'
check('different pair denominators/ROI identities rejected',lambda:reject(lambda:d.paired_metric(wrong,digest,'E384','DH_speedup')))
check('duplicate distribution identities rejected',lambda:reject(lambda:d.distribution([dict(input_digest='a',value=2),dict(input_digest='a',value=3)],['a'])))
check('zero ratio never imputed',lambda:reject(lambda:d.distribution([dict(input_digest='a',value=0)],['a'])))
check('formal publication absent fails closed',lambda:reject(lambda:d.publication_gate(None,None)))
def malformed_publication():
    # The two files are new E-owned CPU fixtures, not authority/publication files.
    root=d.P(__file__).parent/'PUBLICATION_NEGATIVE_CPU_FIXTURE';root.mkdir(exist_ok=False)
    qap=root/'qa.json';qap.write_text(json.dumps(dict(status='PASS',consumer_sha256=d.sha(d.__file__),contract_sha256=d.CONTRACT_SHA)))
    bp=root/'back.json';bp.write_text(json.dumps(dict(schema='DTC_DERIVED35_PUBLICATION_RECEIPT_V1',verified=True,commit='a'*40,qualification_only=False,files={str(d.CONTRACT):d.CONTRACT_SHA,str(d.P(d.__file__).resolve()):'0'*64,str(qap.resolve()):d.sha(qap)})))
    reject(lambda:d.publication_gate(bp,qap))
check('verified boolean and fake commit cannot override wrong source publication',malformed_publication)
dry=d.summarize(scope,selections,c.contract['profiles'],formal=False)
check('dry mode suppresses GM and all speedup values',lambda:eq((dry['aggregates']['E384']['ALL']['DH_speedup']['available']['GM'],dry['per_input']),(None,None)))
actual=c.measure(new,c.spec(old),'SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL')
check('actual R2 strict/build/options/ROI/DONE/q/archive/native critical joins',lambda:eq((actual['valid'],actual['cycles']),(True,6702538)))
# Fault injection overrides only reads in this private consumer instance; it
# never rewrites native files or q. Use the real R2 receipt schema and paths.
def fault(path,replace=None,modify_q=None):
    x=d.ReadonlyConsumer();original=x.get
    def get(p):
        v=original(p)
        return replace(copy.deepcopy(v))if d.P(p)==path else v
    x.get=get
    if modify_q:modify_q(x.q)
    r=x.measure(new,x.spec(old),'SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL');eq(r['valid'],False)
out=d.P(actual['evidence']['out'])
check('actual DONE/q execution mismatch fails closed',lambda:fault(out/'NATIVE_EXIT.json',lambda v:dict(v,uuid='foreign')))
check('actual non-natural stop cannot be measurement',lambda:fault(d.R/'control/qualification_ledger'/(new+'.DONE.json'),lambda v:dict(v,stop_reason='GUARD_STOP')))
check('actual strict/RESULT mismatch fails closed',lambda:fault(out/'L2_STRICT.json',lambda v:dict(v,cycles=v['cycles']+1)))
bundle=d.P(value['archive']['receipt']['target_mount_path'])
check('actual archive critical item missing fails closed',lambda:fault(bundle/'RESTORE_VERIFIED_NATIVE_TARGET.json',lambda v:dict(v,rows=[r for r in v['rows']if r['path']!='L2_STRICT.json'])))
check('actual consumedUUID mismatch fails closed',lambda:fault(None,modify_q=lambda q:q['consumed'][new].update(uuid='foreign')))
report=dict(schema='DTC_DERIVED35_CONSUMER_CPU_QUALIFICATION_V1',status='PASS',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),qualification_only=True,consumer_sha256=d.sha(d.__file__),contract_sha256=d.CONTRACT_SHA,driver_sha256=d.sha(__file__),checks=checks,count=len(checks),synthetic_metrics_are_not_scientific_results=True,actual_R2_source_sha256=actual['RESULT_sha256'],actual_R2_cycles=actual['cycles'],large_raw_or_archive_replay_performed=False,models_started=0,new_grants=0,production_changes=0)
path=d.P(__file__).parent/'CPU_QUALIFICATION_FROZEN.json'
with path.open('x')as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(dict(path=str(path),sha256=d.sha(path),count=len(checks),status='PASS')))

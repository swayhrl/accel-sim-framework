"""Independent read-only final structure32 gate. Import inert; no model/controller/registry mutations."""
from pathlib import Path
from fractions import Fraction
import json,hashlib,os,sys,types,stat,fcntl,math,gzip,argparse,datetime,copy
sys.dont_write_bytecode=True
P=Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1')
ROOTS={'4':P('/root/data/dtc_perf_first_parallel_exploration_20261104_v1'),'28':P('/root/data/dtc_perf_first_remaining28_20261104_v1')}
ARCHIVES={'4':A,'28':A/'remaining28'}
REQUESTS={'4':'DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1','28':'DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1'}
PLANS={'4':'f656a7a122ec270df1174ed12d6c669c85a329c0d1bd7fb2ebfe308c9d4220d4','28':'ace2f7ad9071d735e0e22f71dd252cbad13a17708158410d3d9edb67d78a3c70'}
CANDIDATES={'4':'3e513d48000bae1aa3a3561c0bcd8e79cf6efa0f1e4854e332de1b8fb4c54738','28':'13c8f519013b0f525c31f464e08e528ffbee680889f87a16c443b98f76395333'}
CORE='9eedb3131937748f0492fa83aad37d3691118d70';FW='02775fd795cde5aae1480d81cee6eb481d0a08f4';BINARY='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
AUTH=A/'control/INPUT_AUTHORITY.fixed.json';AUTH_SHA='0b9cd6dfe3c397e32ce286ef068717ac4dd563b65855dd245a4fceb08fdadfa1'
MATRIX=A/'agents/A_structure_config_v1/CANDIDATE_MATRIX48.json';MATRIX_SHA='7edc0554884cf735961e622b6fc2d83a16b12ee41eabc6979407442d0f805bb3'
TAG_MANIFEST=A/'C_contract_and_native_capability_v1/MANIFEST.json';TAG_SHA='6446219f207d3744c68be3d05d45dd0f29a27c904db7ef36636739ea24e0af54'
C069=A/'C_first4_terminal_gate_preparation_v1/first4_terminal_gate.py';C069_SHA='06996cc8f27ddbe67eb73e8979c98bcceb63e8993d98edfb3d7485076070d516'
B3=A/'agents/B_perf_results_consumer_v3';B3_SHA='7da8ddb8d9a89b0f526850ba1451389846c2e4470d632ee47a0b4947a5e26357'
PROVIDER=B3/'PUBLICATION_PROVIDER.json';N=P('/root/data/ep_l2_dtc_l1_native_v2');OUTPUT=A/'C_final_structure32_v1';SCHEMA='C_PERFFIRST_STRUCTURE32_FINAL_INDEPENDENT_AUDIT_V1'
VARIANTS=('PHYS768_TAG64x8','PHYS1024_TAG64x8','OO_PIB192','TAG4BANK_PERBANK2_TOTAL8')
TAG_VARIANTS={'TAG64x16_PHYS640','TAG128x8_PHYS640'}
PASS={k:'PASS_PERFFIRST'+k+'_DH_STRICT_ARCHIVE_NATIVE_RESTORE'for k in ROOTS};FAIL={k:'FAIL_PERFFIRST'+k+'_DH_ARCHIVED_NO_RETRY'for k in ROOTS};ROLES={'4':'PERFFIRST_FIRST4_AUTHORIZED_DH','28':'PERFFIRST_REMAINING28_AUTHORIZED_DH'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def js(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def put(p,v):
 with P(p).open('xb')as f:f.write(js(v));f.flush();os.fsync(f.fileno())
def ref(p):return dict(path=str(p),sha256=sha(p))
def load(p):
 m=types.ModuleType('C_structure32_readonly_private_'+P(p).stem);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def authority():
 with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as f:
  fcntl.flock(f,fcntl.LOCK_SH);p=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';r=read(p);e=read(N/'control/CURRENT_SCIENCE_EPOCH.json');assert sha(p)==e['native_registry_sha256']and e['epoch']==2
 return r,e

def baselines():
 assert sha(AUTH)==AUTH_SHA;auth=read(AUTH);out={};refs=[];aliases=0
 for inp in auth['inputs']:
  for r in inp['P0_references']:
   p=P(r['source_RESULT_path']);assert sha(p)==r['source_RESULT_sha256'];v=read(p);proof=v['proof'];assert r['accepted']is True and r['source_profile']=='P0'and proof['performance_accepted']is True and type(v['cycles'])is int and v['cycles']>0
   assert v['cycles']==r['cycles']==proof['cycles']and v['uuid']==r['source_uuid']and proof['input_digest']==r['input_digest']==inp['population']['input_digest']and proof['cell']==r['source_cell']and proof['effective_options']==r['effective_options']
   assert proof['core_commit']==CORE and proof['framework_commit']==FW and proof['binary_sha256']==BINARY
   alias=r['legal_prior_P0_alias'];bottom=p
   if alias:
    aliases+=1;bottom=P(alias['underlying_RESULT_path']);assert sha(bottom)==alias['underlying_RESULT_sha256'];b=read(bottom);assert b['uuid']==alias['underlying_execution_uuid']==v['uuid']and b['cohort']==alias['underlying_RESULT_declared_cohort']and b['cycles']==v['cycles']and b['proof']['input_digest']==r['input_digest']and b['proof']['cell']==r['source_cell']and b['proof']['raw_gzip_sha256']==proof['raw_gzip_sha256']
   out[r['program'],r['source_cell']]=r;refs.append(dict(program=r['program'],cell=r['source_cell'],cycles=v['cycles'],canonical=ref(p),actual_bottom=ref(bottom),legal_prior_P0_alias=alias,actual_uuid=v['uuid']))
 assert len(out)==len(refs)==16 and aliases==6;return out,refs

def validate_accounting(q,expected,budget):
 assert q['budget']==budget==len(q['admitted_specs'])and set(q['admitted_specs'])==set(expected)
 assert isinstance(q['consumed'],dict)and set(q['consumed'])<=set(expected)and q['remaining']==budget-len(q['consumed'])and q['model_automatic_retries']==0
 assert len({r['uuid']for r in q['consumed'].values()})==len(q['consumed'])
 unused=set(expected)-set(q['consumed']);holds=q.get('admission_holds',{});assert isinstance(holds,dict)and set(holds)==unused,'UNRESOLVED_UNUSED_OR_EXTRA_HOLD'
 if unused:
  assert budget==28 and q['state']=='STOP_UNACCEPTED';t=q['terminal_unused_family_HOLD'];assert set(t['cohorts'])==unused and len(t['cohorts'])==len(unused)and t['no_budget_refund']is True and t['no_spec_removal']is True and t['no_model_retries']is True
  for c in unused:
   h=holds[c];assert h['cohort']==c and h['state']=='UNUSED_FAMILY_HOLD'and h['uuid']is None and h['cycles']is None and h['consumed']is False and type(h['scientific_model_starts'])is int and h['scientific_model_starts']==0 and h['no_budget_refund']is True and h['no_model_retry']is True and h['reason']['state']=='FAILED'
 return unused

def source_context(reg):
 assert sha(MATRIX)==MATRIX_SHA and sha(TAG_MANIFEST)==TAG_SHA and sha(C069)==C069_SHA
 matrix=read(MATRIX)['candidates'];assert len(matrix)==48 and sum(x['variant']in TAG_VARIANTS for x in matrix)==16
 prior={(x['input_digest'],x['variant']):x for x in matrix if x['variant']not in TAG_VARIANTS};assert len(prior)==32
 contexts={};allco={};baseref,_=baselines()
 for k,R in ROOTS.items():
  assert sha(R/'control/EXECUTION_PLAN.json')==PLANS[k]and sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json')==CANDIDATES[k];plan=read(R/'control/EXECUTION_PLAN.json');q=reg['registered_future_requests'][REQUESTS[k]];candidate=read(R/'control/REGISTRY_REQUEST_CANDIDATE.json');
  for field in ['request','budget','admitted_specs','admitted_inputs','reserved_write_bytes','maximum_source_plus_restore_lifetime_bytes','model_automatic_retries','scientific_role','engine_sha256','strict_sha256','outbox_sha256','controller_sha256','execution_plan_sha256','owner_pid','owner_start_ticks']:assert q[field]==candidate[field],'REGISTERED_CONTRACT_DRIFT '+field
  ack=read(R/'control/PARENT_ADDON_ACK.json');assert ack['owner_pid']==1498278 and ack['owner_start_ticks']==977758783 and ack['new_request']==REQUESTS[k]and ack['plan_sha256']==PLANS[k]and ack['original_lock_handles_retained']is True
  expectedqual='5acd5239cac206cdf57b1b7958671dae8c7b5ea0d56ca7ddbaf14ead70270944'if k=='4'else'200286a07119dab3afc4d91114e316fd655481362fddeb88aafc55c2d75ea469'
  assert ack['CPU_qualification_sha256']==expectedqual==sha(R/'control/CPU_QUALIFICATION.json')
  points=read(R/'control/MATRIX.json')['points'];assert q['request']==REQUESTS[k]and q['execution_plan_sha256']==PLANS[k]
  for p in plan['source_pins']:assert sha(p['path'])==p['sha256'],'SOURCE_PIN_DRIFT '+p['path']
  for key,suffix in [('engine_sha256','native'),('strict_sha256','strict'),('outbox_sha256','outbox'),('controller_sha256','ops')]:assert q[key]==sha(R/'tools'/('perf'+k+'_'+suffix+'.py'))
  expected={p['cohort']:p for p in points};unused=validate_accounting(q,expected,int(k));assert len(points)==int(k)
  for c,p in expected.items():
   sp=R/'control/specs'/(c+'.json');s=read(sp);old=prior[s['input_digest'],s['profile']];assert sha(sp)==q['admitted_specs'][c]==sha(R/'control'/(c+'_SPEC.json'))and s['cohort']==c and s['request']==REQUESTS[k]
   assert s['expected_options']==old['expected_effective_options']and len(s['expected_options'])==270 and s['expected']==old['expected']and s['input_binding_sha256']==old['input_binding']['sha256']==sha(s['input_binding_path'])
   assert s['program']==p['program']==old['program']and s['suite']==p['suite']==old['suite']and s['cell']=='DH'and s['downstream_profile']=='P0'and s['structure_variant']==s['profile']==p['structure_variant']and s['host_cpu']is None
   assert s['core_commit']==CORE and s['framework_commit']==FW and s['binary_sha256']==BINARY
   assert [x['sha256']for x in s['configs']]==[x['sha256']for x in old['configs']]
   for x in s['configs']+s['runtime_files']:assert sha(x.get('path',x.get('actual_realpath')))==x['sha256']
   assert (s['input_digest'],s['profile'])not in allco;allco[s['input_digest'],s['profile']]=(k,c);p['C_spec']=s
  contexts[k]=dict(root=R,plan=plan,q=q,points=expected,unused=unused)
 assert set(allco)==set(prior)
 uuids=[v['uuid']for ctx in contexts.values()for v in ctx['q']['consumed'].values()];assert len(set(uuids))==len(uuids)
 other={row['uuid']for key,q in reg['registered_future_requests'].items()if key not in REQUESTS.values()and isinstance(q.get('consumed'),dict)for row in q['consumed'].values()if isinstance(row,dict)and'uuid'in row};assert not set(uuids)&other
 before=read(A/'C_remaining28_execution_qualification_v1/OLD_IDENTITIES_PRE_28_REGISTRATION.json')
 for key,old in before.items():
  q=reg['registered_future_requests'][key];assert q['budget']==old['budget']and q['remaining']==old['remaining']and ({c:r.get('uuid')for c,r in q['consumed'].items()}if isinstance(q['consumed'],dict)else q['consumed'])==old['UUIDs']
 # Rejoin the actual strong predecessor proof and exact runtime release hash; never run audit.
 r=load(ROOTS['28']/'tools/perf28_terminal_gate_receipt.py');r.verify(contexts['28']['plan'],reg,contexts['28']['q']['runtime_release_evidence'])
 return contexts,prior

def snapshot_metadata():
 assert sha(B3/'MANIFEST.json')==B3_SHA
 for x in read(B3/'MANIFEST.json')['files']:assert sha(B3/x['path'])==x['sha256']
 provider=read(PROVIDER);assert provider['schema']=='DTC_PERF_STRUCTURE48_READONLY_PUBLICATION_PROVIDER_V3';mp=P(provider['manifest']['path']);assert mp.resolve().is_relative_to((B3/'snapshots').resolve())and sha(mp)==provider['manifest']['sha256'];mf=read(mp)
 for x in mf['files']:assert P(x['path']).resolve().is_relative_to(mp.parent.resolve())and sha(x['path'])==x['sha256']
 snap=read(mp.parent/'SNAPSHOT.json');assert snap['schema']=='DTC_PERF_STRUCTURE48_CLOSED_READONLY_SNAPSHOT_V3'and len(snap['rows'])==48 and sum(r['route']=='TAG_SAFETY_HOLD'for r in snap['rows'])==16;summary=read(mp.parent/'SUMMARY.json');assert provider['summary']==summary==snap['summary']and provider['baseline_source_qualified']is True and provider['all_existing_closed_results_qualified']is True and provider['admission_hold_metadata_qualified']is True
 assert provider['all32_candidates_accounted_verified']is True and summary['family_hold_metadata_issues']==0,'B3_NOT_TERMINAL_ACCOUNTED'
 return snap,dict(provider=ref(PROVIDER),manifest=ref(mp),snapshot=ref(mp.parent/'SNAPSHOT.json'),summary=ref(mp.parent/'SUMMARY.json'))

def live_generation(packet):
 try:s=P('/proc',str(packet['pid']),'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==packet['start_ticks']and s[0]not in['Z','X']
 except FileNotFoundError:return False

def readiness():
 reg,epoch=authority();contexts,prior=source_context(reg);snap,brefs=snapshot_metadata();B={r['cohort']:r for r in snap['rows']if r.get('cohort')};assert len(B)==32
 for k,ctx in contexts.items():
  R=ctx['root'];q=ctx['q'];terminal=read(R/'analysis/EXECUTION_TERMINAL.json');assert terminal['status']in ['ALL4_STRICT_OR_ARCHIVED_NEGATIVE_TERMINAL','ALL28_STRICT_OR_ARCHIVED_NEGATIVE_TERMINAL','ALL_ACTUAL_MODELS_TERMINAL_WITH_UNUSED_FAMILY_HOLD']
  for c,point in ctx['points'].items():
   if c in ctx['unused']:
    assert k=='28'and B[c]['status']=='UNUSED_FAMILY_HOLD'and B[c]['accepted']is False and B[c]['cycles']is None and B[c]['uuid']is None
    assert not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(R/'control/qualification_ledger'/(c+'.DONE.json')).exists()and not(R/'analysis'/(c+'.RESULT.json')).exists();continue
   row=q['consumed'][c];i=read(R/'control/qualification_ledger'/(c+'.INTENT.json'));d=read(R/'control/qualification_ledger'/(c+'.DONE.json'));out=R/'DTC/run/results'/row['uuid'];rr=read(R/'analysis'/(c+'.RESULT.json'));assert i['uuid']==d['uuid']==rr['uuid']==row['uuid']and d==row['execution_receipt']==read(out/'NATIVE_EXIT.json')and row['charged']==i['consumed_before_launcher_fork']==1 and i['automatic_retry']is False
   assert rr['state']in[PASS[k],FAIL[k]]and rr['scientific_role']==ROLES[k]and rr['cohort']==c
   pid=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if pid.exists():assert not live_generation(read(pid)),'ACTUAL_MODEL_STILL_LIVE'
   else:assert d['native_simulator_observed']is False and rr['state']==FAIL[k],'UNRESOLVED_MODEL_GENERATION'
   assert B[c]['uuid']==row['uuid']and B[c]['cycles']==rr['cycles']and B[c]['accepted']==(rr['state']==PASS[k])
 return reg,contexts,prior,snap,brefs

def metric(values):
 if not values:return dict(n=0,GM=None,positive_exact=0,negative_exact=0,zero_exact=0,positive_tolerance=0,negative_tolerance=0,zero_within1e_minus12=0)
 return dict(n=len(values),GM=math.exp(math.fsum(math.log(float(x))for x in values)/len(values)),positive_exact=sum(x>1 for x in values),negative_exact=sum(x<1 for x in values),zero_exact=sum(x==1 for x in values),positive_tolerance=sum(float(x)>1+1e-12 for x in values),negative_tolerance=sum(float(x)<1-1e-12 for x in values),zero_within1e_minus12=sum(abs(float(x)-1)<=1e-12 for x in values))
def statistics(rows):
 accepted=[r for r in rows if r['accepted']];common=set.intersection(*[{r['input_digest']for r in accepted if r['variant']==v}for v in VARIANTS]);out=dict(variants={},common_inputs=sorted(common),common_n=len(common),accepted=len(accepted),archived_negative=sum(r['status']=='ARCHIVED_NEGATIVE_NO_PERFORMANCE'for r in rows),unused_family_HOLD=sum(r['status']=='UNUSED_FAMILY_HOLD'for r in rows),native_simulator_observed=sum(r.get('native_simulator_observed')is True for r in rows),planned_nonTag=32,Tag_safety_HOLD=16,programs=8,not_CORE32=True,no_best_stitching=True)
 for v in VARIANTS:
  selected=[r for r in accepted if r['variant']==v];same=[r for r in selected if r['input_digest']in common];out['variants'][v]=dict(accepted_n=len(selected),missing_or_negative_or_HOLD_n=8-len(selected),available={k:metric([Fraction(*r['ratios'][k])for r in selected])for k in ['S_DH','Rnew','Rold','I']},common={k:metric([Fraction(*r['ratios'][k])for r in same])for k in ['S_DH','Rnew','Rold','I']},by_suite={suite:{k:metric([Fraction(*r['ratios'][k])for r in selected if r['suite']==suite])for k in ['S_DH','Rnew','Rold','I']}for suite in sorted({r['suite']for r in rows if r['variant']==v})})
 out.update(all32_accounted=out['accepted']+out['archived_negative']+out['unused_family_HOLD']==32,all32_actual_closed=out['accepted']+out['archived_negative']==32,all32_accepted=out['accepted']==32);return out

def compare_B(rows,stats,snapshot):
 brow={r['cohort']:r for r in snapshot['rows']if r.get('cohort')};B=snapshot['summary'];assert len(rows)==len(brow)==32
 for r in rows:
  b=brow[r['cohort']];assert r['status']==b['status']and r['accepted']==b['accepted']and r['cycles']==b['cycles']and r['uuid']==b.get('uuid')and r['input_digest']==b['input_digest']and r['variant']==b['variant']
  if r['accepted']:
   for k,x in r['ratios'].items():assert abs(float(Fraction(*x))-b[k])<1e-13
  else:assert all(b[k]is None for k in ['S_DH','Rnew','I'])
 assert (stats['accepted'],stats['archived_negative'],stats['unused_family_HOLD'])==(B['accepted_new_points'],B['archived_negative_new_points'],B['unstarted_family_HOLD_points'])and stats['common_inputs']==B['common_nonTag_accepted_intersection']['ids']
 for v,values in stats['variants'].items():
  assert values['accepted_n']==B['variants'][v]['accepted_n']
  groups=[(values['available'],B['variants'][v]['available_set_metrics']),(values['common'],B['common_nonTag_accepted_intersection']['variants'][v])]+[(x,B['variants'][v]['by_suite_available_only'][suite])for suite,x in values['by_suite'].items()]
  for own,other in groups:
   for k,m in own.items():
    b=other[k];assert m['n']==b['n']and(m['GM']is None and b['GM']is None or m['GM']is not None and b['GM']is not None and abs(m['GM']-b['GM'])<1e-12)
    assert(m['positive_tolerance'],m['negative_tolerance'],m['zero_within1e_minus12'])==(b['positive'],b['negative'],b['zero_within1e_minus12'])
 assert stats['all32_actual_closed']==B['all32_nonTag_closed_verified']and stats['all32_accepted']==B['all32_scientific_success']and stats['all32_accounted']==B['all32_candidates_accounted_verified']

def verify_point(k,c,ctx,base,archive_template):
 R=ctx['root'];q=ctx['q'];point=ctx['points'][c];s=point['C_spec'];common=dict(cohort=c,program=s['program'],suite=s['suite'],input_digest=s['input_digest'],variant=s['profile'],accepted=False,cycles=None,uuid=None,ratios=None,request=REQUESTS[k])
 if c in ctx['unused']:
  h=q['admission_holds'][c];assert h['request']==REQUESTS[k]and h['input_digest']==h['full_input_digest']==s['input_digest']and h['program']==s['program']and h['suite']==s['suite']and h['profile']==h['structure_variant']==s['profile']and h['cell']=='DH'and h['downstream_profile']=='P0'and h['canonical_spec_sha256']==q['admitted_specs'][c]and h['source_ops_sha256']==sha(R/'tools/perf28_ops.py')
  return dict(common,status='UNUSED_FAMILY_HOLD',explicit_admission_hold=h,native_simulator_observed=False,actual_model_consumed=False,scientific_negative=False)
 row=q['consumed'][c];out=R/'DTC/run/results'/row['uuid'];ip=R/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');rrp=R/'analysis'/(c+'.RESULT.json');rr=read(rrp);i=read(ip);d=read(dp);assert sha(ip)==row['intent_sha256']and i['spec_sha256']==q['admitted_specs'][c]and rr['input_digest']==s['input_digest']and rr['profile']==rr['structure_variant']==s['profile']and rr['downstream_profile']=='P0'and rr['cell']=='DH'and rr['new_contract_only']is True and rr['original_or_repair_results_replaced']is False
 assert sha(out/'DOWNSTREAM_FROZEN_SPEC.json')==q['admitted_specs'][c];dbp=R/'control/dispatch_bindings'/(c+'.json');db=read(dbp);assert sha(out/'DISPATCH_BINDING.json')==sha(dbp)==i['dispatch_binding_sha256']and db['canonical_spec_sha256']==q['admitted_specs'][c]and type(db['host_cpu'])is int and db['resolved_spec_sha256']==hashlib.sha256(js(dict(s,host_cpu=db['host_cpu']))).hexdigest();engine=load(R/'tools'/('perf'+k+'_native.py'));assert i['l2_mlp_execution_binding']==engine.binding();assert sha(out/'raw.log.gz')==d['raw_sha256'];assert rr['validated_union_authorized']is False
 if rr['state']==PASS[k]:
  proof=load(R/'tools'/('perf'+k+'_strict.py')).terminal(c);assert proof==rr['proof']==read(out/'L2_STRICT.json')and proof['performance_accepted']is True and proof['cycles']==rr['cycles']and type(rr['cycles'])is int and rr['cycles']>0
  qual=read(R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json'));assert qual['uuid']==row['uuid']and qual['cohort']==c and qual['strict_sha256']==sha(out/'L2_STRICT.json')and qual['status']==proof['status'];assert d['stop_reason']is None and type(d['launcher_wait_returncode'])is int and d['launcher_wait_returncode']==0 and d['native_simulator_observed']is True
  status='ACCEPTED_STRICT_ARCHIVE_RESTORE';cycles=rr['cycles'];ratios={'S_DH':Fraction(base[s['program'],'DH']['cycles'],cycles),'Rnew':Fraction(base[s['program'],'CH']['cycles'],cycles),'Rold':Fraction(base[s['program'],'CH']['cycles'],base[s['program'],'DH']['cycles'])};ratios['I']=ratios['Rnew']/ratios['Rold'];assert ratios['I']==ratios['S_DH'];ratios={key:[v.numerator,v.denominator]for key,v in ratios.items()}
 else:
  assert rr['cycles']is None and rr['proof']['performance_accepted']is False and rr['proof']['accepted_cycles']is None;assert rr['proof']['stop_reason']==d['stop_reason']and rr['proof']['returncode']==d['launcher_wait_returncode']and rr['proof']['raw_sha256']==d['raw_sha256'];h=hashlib.sha256();size=0
  with gzip.open(out/'raw.log.gz','rb')as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
  assert h.hexdigest()==d['raw_uncompressed_sha256']and size==d['raw_uncompressed_bytes'];status='ARCHIVED_NEGATIVE_NO_PERFORMANCE';cycles=None;ratios=None
 # Every archive chunk and native/source typed member is independently rehashed; no new copy/archive is made.
 env=dict(archive_template.__dict__,R=R,A=ARCHIVES[k]);verify=types.FunctionType(archive_template.verify_archive.__code__,env,'verify_archive',archive_template.verify_archive.__defaults__);archive=verify(c,row,rr);ap=OUTPUT/(c+'.ARCHIVE_SOURCE_NATIVE_PROOF.json');put(ap,archive)
 receipt=rr['archive']['receipt'];assert receipt['scientific_status']==(rr['proof']['status']if rr['state']==PASS[k]else'STOP_UNACCEPTED')and receipt['source_disposition']=='SOURCE_KEEP'and receipt['source_release_bytes']==0 and rr['archive']['archive_overlay_sha256']==q['outbox_sha256']
 files=[rrp,ip,dp,out/'NATIVE_EXIT.json',R/'control'/(c+'_ARCHIVE_RECEIPT.json'),R/'control/specs'/(c+'.json')];events=[ref(p)for p in sorted((R/'analysis').glob(c+'.POSTPROCESS_ENGINEERING.*.json'))]
 return dict(common,status=status,accepted=rr['state']==PASS[k],cycles=cycles,uuid=row['uuid'],ratios=ratios,native_simulator_observed=d['native_simulator_observed'],actual_model_consumed=True,native_generation_nonlive_verified=(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').exists(),strict_reexecuted=rr['state']==PASS[k],closed_file_sha256={str(p):sha(p)for p in files},full_archive_native_proof=ref(ap),archive_typed_entry_count=archive['typed_entry_count'],engineering_event_refs=events,source_validated_union_authorized=rr['validated_union_authorized'],raw_display_union_scope=rr.get('union_scope'),scope_defined_by_actual_request_spec_role_not_legacy_display=True)

def run():
 reg,contexts,prior,B,brefs=readiness();assert not OUTPUT.exists(),'NO_BLIND_FINAL_AUDIT_RETRY';OUTPUT.mkdir();put(OUTPUT/'ATTEMPT_ONCE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(__file__),model_actions=0))
 try:
  base,baseline_refs=baselines();template=load(C069);rows=[]
  for k,ctx in contexts.items():
   for c in ctx['points']:rows.append(verify_point(k,c,ctx,base,template))
  stats=statistics(rows);compare_B(rows,stats,B);fresh,_=authority()
  for k,ctx in contexts.items():assert fresh['registered_future_requests'][REQUESTS[k]]==ctx['q'],'SCOPE_CHANGED_DURING_FINAL_AUDIT'
  source_context(fresh)
  for name,v in [('ROWS.json',rows),('STATISTICS.json',stats),('BASELINE_REFERENCES.json',baseline_refs),('B_FINAL_SNAPSHOT_REFERENCE.json',brefs)]:put(OUTPUT/name,v)
  report=dict(schema=SCHEMA,status='PASS',independent_verification_passed=True,all32_candidates_accounted_verified=stats['all32_accounted'],Root_signoff=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scientific_scope='8fixed_inputs_x4_nonTag_structures_plus16Tag_safetyHOLD_NOT_CORE32',consumed=sum(len(ctx['q']['consumed'])for ctx in contexts.values()),unspent_family_HOLD=stats['unused_family_HOLD'],accepted=stats['accepted'],archived_negative=stats['archived_negative'],native_simulator_observed=stats['native_simulator_observed'],all32_candidates_accounted=stats['all32_accounted'],all32_actual_closed=stats['all32_actual_closed'],all32_accepted=stats['all32_accepted'],source_path=str(P(__file__).resolve()),source_sha256=sha(__file__),plans=PLANS,candidates=CANDIDATES,source_A_matrix_sha256=MATRIX_SHA,Tag16_manifest_sha256=TAG_SHA,B3_manifest_sha256=B3_SHA,independent_strict_and_full_archive_rehash=True,integer_exact_sign_and_same_input_GM=True,baseline_references=16,legal_P0_aliases=6,no_perprogram_best_stitching=True,remaining28_legacy_union_scope_is_display_label_only=True,English_v023_modified=False,model_starts=0,registry_writes=0,owner_actions=0,automatic_Git_publication=False,automatic_total_Goal_complete=False,old_Goal_completion=False,manuscript_signoff=False,numerical_or_coherence_validated=False,new_scope_authorized=False)
  encoded=js(report);members=[dict(relative_path=p.name,size_bytes=p.stat().st_size,sha256=sha(p))for p in sorted(OUTPUT.iterdir())if p.is_file()and p.name!='MANIFEST.json'];members.append(dict(relative_path='FINAL_REVIEW.json',size_bytes=len(encoded),sha256=hashlib.sha256(encoded).hexdigest()));put(OUTPUT/'MANIFEST.json',dict(schema='C_PERFFIRST_STRUCTURE32_FINAL_MANIFEST_V1',files=members));put(OUTPUT/'FINAL_REVIEW.json',report);return report
 except BaseException as e:put(OUTPUT/'HOLD_NO_AUTOMATIC_RETRY.json',dict(status='HOLD',error=repr(e),no_new_models=True));raise

def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--check-readiness',action='store_true');g.add_argument('--audit',action='store_true');args=ap.parse_args()
 if args.check_readiness:
  try:readiness();print(json.dumps(dict(ready=True,metadata_only=True,not_final_audit=True)));return 0
  except(OSError,ValueError,KeyError,TypeError,AssertionError)as e:print(json.dumps(dict(ready=False,metadata_only=True,no_live_raw_read=True,reason=repr(e))));return 2
 r=run();print(json.dumps(dict(status=r['status'],review_path=str(OUTPUT/'FINAL_REVIEW.json'),manifest_sha256=sha(OUTPUT/'MANIFEST.json'))));return 0
if __name__=='__main__':raise SystemExit(main())




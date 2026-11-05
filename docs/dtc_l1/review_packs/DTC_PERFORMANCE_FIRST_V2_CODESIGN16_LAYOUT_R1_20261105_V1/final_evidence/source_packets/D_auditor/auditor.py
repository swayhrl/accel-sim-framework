#!/usr/bin/env python3
"""One-shot independent closed Codesign16 audit. Never registers/runs/restores a model."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,math,os,sys,types,uuid,gzip,re,fcntl
sys.dont_write_bytecode=True
P=Path
def digest(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def require(v,reason):
 if not v:raise ValueError(reason)
def pin(p):return {'path':str(p),'sha256':digest(p)}
def load(name,p):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def checked(ref):
 b=P(ref['path']).read_bytes();require(hashlib.sha256(b).hexdigest()==ref['sha256'],'SOURCE_SHA_DRIFT:'+ref['path']);return json.loads(b)
def stable_registry(c):
 r=P(c['registry']);ep=P(c['epoch'])
 for _ in range(20):
  b=r.read_bytes();e=read(ep)
  if hashlib.sha256(b).hexdigest()==e['native_registry_sha256']:return json.loads(b),e,{'path':str(r),'sha256':hashlib.sha256(b).hexdigest()}
 raise ValueError('EPOCH_REGISTRY_NOT_STABLE_NO_AUDIT')
def source_context(c):
 R=P(c['root']);plan=read(R/'control/EXECUTION_PLAN.json');require(digest(R/'control/EXECUTION_PLAN.json')==c['execution_plan_sha256'],'FINAL_PLAN_DRIFT');require(digest(R/'control/MATRIX.fixed.json')==c['runtime_matrix_sha256'],'FINAL_MATRIX_DRIFT')
 for x in plan['source_pins']:require(digest(x['path'])==x['sha256'],'REGISTERED_SOURCE_PIN_DRIFT:'+x['path'])
 require(plan['request']==c['request']and plan['expected_new_starts']==plan['initial_finite_budget']==16,'FINAL_PLAN_SCOPE')
 for key,name in [('engine_sha256','perf16r1_native.py'),('strict_sha256','perf16r1_strict.py'),('outbox_sha256','perf16r1_outbox.py'),('controller_sha256','perf16r1_ops.py')]:require(digest(R/'tools'/name)==c[key],'CURRENT_SOURCE_DRIFT:'+name)
 published=checked(c['approved_matrix']);cs=published['candidates'];require(len(cs)==16 and len({r['input_digest']for r in cs})==8 and len({r['profile']for r in cs})==2,'APPROVED_FIXED16_REQUIRED')
 recovered=checked(c['approved_recovery_plan']);mapping={r['proposed_new_cohort']:r for r in recovered['rows']};require(recovered['proposed_request']==c['request']and len(mapping)==16 and set(mapping)=={r['proposed_native_cohort']for r in cs},'APPROVED_NEW16_RECOVERY_SCOPE')
 for r in cs:
  a=mapping[r['proposed_native_cohort']];require(r['input_digest']==a['input_digest']and r['profile']==a['profile']and r['expected_effective_options']==a['expected_effective_options']and [x['sha256']for x in r['configs']]==a['config_sha256_vector'],'RECOVERY_SCOPE_INPUT_CONFIG_270')
 reg,ep,rp=stable_registry(c);q=reg['registered_future_requests'].get(c['request']);require(q is not None,'NOT_REGISTERED');require(q['budget']==16 and q['remaining']==16-len(q['consumed'])and set(q['admitted_specs'])=={r['proposed_native_cohort']for r in cs},'REGISTERED_FIXED16_ACCOUNTING')
 require(q['execution_plan_sha256']==c['execution_plan_sha256']and all(q[k]==c[k]for k in ['engine_sha256','strict_sha256','outbox_sha256','controller_sha256']),'REGISTERED_SOURCE_VERSION_MISMATCH')
 require(q.get('model_automatic_retries')==0,'MODEL_RETRY_NOT_AUTHORIZED')
 return R,plan,reg,q,published,cs,rp
def publication(provider,c):
 pr=read(provider);require(pr['schema']=='DTC_PERFV2_CODESIGN16_LAYOUT_R1_PUBLICATION_PROVIDER_V1'and pr['report_only']is True and pr['new_models']==pr['native_writes']==0,'REVIEWED_R1_PROVIDER_REQUIRED');mf=checked(pr['manifest']);require(mf['files']==pr['files'],'PROVIDER_MANIFEST_DISAGREES')
 for x in pr['files']:require(digest(x['path'])==x['sha256']and P(x['path']).stat().st_size==x['bytes'],'PROVIDER_MEMBER_SHA_SIZE:'+x['name'])
 snap=read(P(pr['snapshot'])/'SNAPSHOT.json');require(snap['schema']=='DTC_PERFV2_CODESIGN16_LAYOUT_R1_READONLY_SNAPSHOT_V1'and snap['authority_commit']==c['authority_commit'],'SNAPSHOT_SCOPE');require(len(snap['rows'])==16,'SNAPSHOT_EXACT16')
 for x in snap['consumer_sources']:require(digest(x['path'])==x['sha256'],'B_CONSUMER_SOURCE_DRIFT')
 require(digest(P(c['B_package'])/'MANIFEST.json')==c['B_manifest_sha256'],'REVIEWED_B_PACKAGE_DRIFT')
 return pr,snap
def live(out):
 p=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 if not p.exists():return False
 v=read(p)
 try:
  s=P('/proc',str(v['pid']),'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==v['start_ticks']and s[0]not in ['Z','X']
 except(FileNotFoundError,ProcessLookupError):return False
def readiness(c,provider):
 try:
  R,plan,reg,q,published,cs,rp=source_context(c);pr,snap=publication(provider,c);reasons=[]
  if not pr.get('runtime_source_qualified'):reasons.append('B_RUNTIME_SOURCE_NOT_QUALIFIED')
  if not pr.get('all16_candidates_accounted_verified'):reasons.append('B16_NOT_TERMINAL_ACCOUNTED')
  rows={r['cohort']:r for r in snap['rows']};require(set(rows)==set(q['admitted_specs']),'B16_MEMBERSHIP_DIFFERS')
  for co,row in q['consumed'].items():
   out=R/'DTC/run/results'/row['uuid'];ip=R/'control/qualification_ledger'/(co+'.INTENT.json');dp=ip.with_name(co+'.DONE.json');rr=R/'analysis'/(co+'.RESULT.json')
   if not row.get('execution_receipt')or not dp.exists()or not rr.exists():reasons.append('AWAIT_CLOSED_STRICT_ARCHIVE:'+co);continue
   require(read(dp)==read(out/'NATIVE_EXIT.json')==row['execution_receipt'],'DONE_EXIT_REGISTRY_JOIN:'+co)
   if live(out):reasons.append('ACTUAL_MODEL_STILL_LIVE:'+co)
   if rows[co]['status']not in ['ACCEPTED_STRICT_ARCHIVE_RESTORE','ARCHIVED_NEGATIVE_NO_PERFORMANCE']:reasons.append('B_CONSUMED_RESULT_NOT_TERMINAL:'+co)
  for co in set(q['admitted_specs'])-set(q['consumed']):
   if rows[co]['status']!='UNUSED_SAFETY_HOLD':reasons.append('UNUSED_POINT_NOT_TYPED_SAFETY_HOLD:'+co)
  tp=R/'analysis/EXECUTION_TERMINAL.json'
  if not tp.exists():reasons.append('AWAIT_ORIGINAL_OPS_EXECUTION_TERMINAL')
  else:
   terminal=read(tp);require(set(terminal['states'])==set(q['admitted_specs']),'TERMINAL_FIXED16_MEMBERSHIP')
  return {'ready':not reasons,'status':'READY'if not reasons else'WAIT_CLOSED_EVIDENCE','reasons':reasons,'consumed':len(q['consumed']),'remaining':q['remaining'],'B_summary':snap['summary'],'registry_read':rp,'new_models':0,'active_raw_reads':0}
 except Exception as error:return {'ready':False,'status':'HOLD_METADATA_OR_SOURCE_VERIFICATION','error':repr(error),'new_models':0,'active_raw_reads':0}
def retained_source_tree(aw,manifest,out):
 for e in manifest['entries']:
  p=aw.exact_safe(out,e['path']);require(p.lstat().st_dev==2128,'SOURCE_NOT_NATIVE_DEVICE')
  if e['type']=='file':require(p.is_file()and not p.is_symlink()and p.stat().st_size==e['size']and digest(p)==e['sha256'],'SOURCE_KEEP_FILE_SHA:'+e['path'])
  elif e['type']=='directory':require(p.is_dir()and not p.is_symlink(),'SOURCE_KEEP_DIRECTORY:'+e['path'])
  elif e['type']=='symlink':require(p.is_symlink()and os.readlink(p)==e['target'],'SOURCE_KEEP_SYMLINK:'+e['path'])
  else:raise ValueError('UNSUPPORTED_SOURCE_TYPE')
 return len(manifest['entries'])
def reference(ref):
 p=P(ref['source_RESULT_path']);require(digest(p)==ref['source_RESULT_sha256'],'P0_REFERENCE_SHA');r=read(p);proof=r['proof'];require(ref['accepted']is True and proof['performance_accepted']is True and type(r['cycles'])is int and r['cycles']==ref['cycles']>0,'P0_ACCEPTED_INTEGER_CYCLES');require(proof['input_digest']==ref['input_digest']and proof['cell']==ref['source_cell']and proof['effective_options']==ref['effective_options'],'P0_IDENTITY_OR_OPTIONS');seen=[]
 while 'reference_result_path'in r:
  require(str(p)not in seen and len(seen)<10,'P0_ALIAS_CYCLE');seen.append(str(p));p=P(r['reference_result_path']);require(digest(p)==r['reference_result_sha256'],'P0_LEGAL_ALIAS_SHA');r=read(p);require(r['cycles']==ref['cycles']and r['proof']['performance_accepted']is True,'P0_ALIAS_CYCLE_IDENTITY')
 return {'canonical':{'path':ref['source_RESULT_path'],'sha256':ref['source_RESULT_sha256']},'bottom':pin(p),'cycles':ref['cycles'],'proof':proof,'legal_prior_alias':ref['legal_prior_P0_alias']}
def component(comp,spec,dh,variant):
 if comp.get('accepted')is not True:return None,{'status':comp.get('status'),'reason':'NO_QUALIFIED_SINGLE_FACTOR_IN_FROZEN_B_SNAPSHOT'}
 r=checked(comp['source_RESULT']);p=r['proof'];expect=copy.deepcopy(dh['proof']['effective_options']);key='-gpgpu_dtc_l1_oo_pib_entries'if variant=='OO_PIB192'else'-gpgpu_dtc_l1_physical_lines';expect[key]=['192'if variant=='OO_PIB192'else'768'if variant=='PHYS768_TAG64x8'else'1024'];require(p['performance_accepted']is True and p['input_digest']==spec['input_digest']and p['cell']=='DH'and p['profile']==variant and p['downstream_profile']=='P0'and p['effective_options']==expect,'SINGLE_FACTOR_SOURCE_IDENTITY');require(type(r['cycles'])is int and r['cycles']==comp['cycles']>0,'SINGLE_FACTOR_CYCLES');require(all(p[k]==spec[k]for k in ['core_commit','framework_commit','binary_sha256']),'SINGLE_FACTOR_BUILD')
 return r['cycles'],{'RESULT':comp['source_RESULT'],'cycles':r['cycles'],'variant':variant,'scientific_role':r.get('scientific_role')}
def stats(rows,metric):
 xs=[r for r in rows if r[metric]is not None]
 def sg(r):
  if metric in ['S_combo','I']:a,b=r['DH_P0_cycles'],r['cycles']
  elif metric=='R_combo':a,b=r['CH_P0_cycles'],r['cycles']
  else:a,b=r['physical_cycles']*r['PIB_cycles'],r['DH_P0_cycles']*r['cycles']
  return(a>b)-(a<b)
 return {'n':len(xs),'GM':math.exp(sum(math.log(r[metric])for r in xs)/len(xs))if xs else None,'positive_exact':sum(sg(r)>0 for r in xs),'negative_exact':sum(sg(r)<0 for r in xs),'zero_exact_arithmetic':sum(sg(r)==0 for r in xs),'missing':len(rows)-len(xs)}
def summary(rows):
 ps=sorted({r['profile']for r in rows});metrics=['S_combo','R_combo','I','J'];out={'profiles':{}}
 for p in ps:
  rr=[r for r in rows if r['profile']==p];out['profiles'][p]={'metrics':{k:stats(rr,k)for k in metrics},'by_suite':{s:{k:stats([r for r in rr if r['suite']==s],k)for k in metrics}for s in sorted({r['suite']for r in rr})}}
 common=set.intersection(*[{r['input_digest']for r in rows if r['profile']==p and r['accepted']}for p in ps]);jc=set.intersection(*[{r['input_digest']for r in rows if r['profile']==p and r['J']is not None}for p in ps]);out['common_combo_accepted_inputs']={'ids':sorted(common),'n':len(common),'profiles':{p:{k:stats([r for r in rows if r['profile']==p and r['input_digest']in common],k)for k in metrics}for p in ps}};out['common_J_complete_terms_inputs']={'ids':sorted(jc),'n':len(jc),'profiles':{p:{k:stats([r for r in rows if r['profile']==p and r['input_digest']in jc],k)for k in metrics}for p in ps}};return out
def compare_stats(own,b):
 for profile,d in own['profiles'].items():
  for k,v in d['metrics'].items():
   w=b['profiles'][profile]['available_set'][k];require(all(v[x]==w[x]for x in ['n','positive_exact','negative_exact','zero_exact_arithmetic','missing']),'INDEPENDENT_METRIC_COUNT_DISAGREES');require((v['GM']is None and w['GM']is None)or math.isclose(v['GM'],w['GM'],rel_tol=1e-12),'INDEPENDENT_GM_DISAGREES')
 for name in ['common_combo_accepted_inputs','common_J_complete_terms_inputs']:
  require(own[name]['ids']==b[name]['ids']and own[name]['n']==b[name]['n'],'INDEPENDENT_COMMON_INTERSECTION_DIFFERS')
  for profile,d in own[name]['profiles'].items():
   for k,v in d.items():
    w=b[name]['profiles'][profile][k];require(all(v[x]==w[x]for x in ['n','positive_exact','negative_exact','zero_exact_arithmetic','missing']),'INDEPENDENT_COMMON_COUNT_DISAGREES');require((v['GM']is None and w['GM']is None)or math.isclose(v['GM'],w['GM'],rel_tol=1e-12),'INDEPENDENT_COMMON_GM_DISAGREES')
def natural(done):
 return done['stop_reason']is None and done['launcher_wait_returncode']==0 and done['native_simulator_observed']is True

def prior_science(c,reg):
 baseline=checked(c['old_science_baseline'])
 for name,old in baseline['old_scientific_immutable_baseline'].items():
  q=reg['registered_future_requests'][name];actual=dict(budget=q['budget'],remaining=q['remaining'],specs=q.get('specs'),admitted_specs=q.get('admitted_specs'),consumed={co:{k:v.get(k)for k in ['uuid','intent','intent_sha256','charged']}for co,v in q['consumed'].items()})
  require(actual==old,'PRIOR_SCIENCE_IDENTITY_BUDGET_CHANGED:'+name)

def closed_strict_rederive(c,co,spec,intent,done,out,result,q,plan):
 """Read closed source once, rederive population/cycles and replay all binding,
 progress and guard joins. Frozen runtime binding is read once per point, not
 recalculated for every historical resource record. No production strict edit.
 """
 require(natural(done)and not live(out),'NATURAL_OBSERVED_CLOSED_REQUIRED')
 proof=read(out/'L2_STRICT.json');require(proof==result['proof']and proof['schema']==c['strict_schema']and proof['status']==c['strict_status']and proof['performance_accepted']is True,'SOURCE_STRICT_IDENTITY')
 require(type(result['cycles'])is int and result['cycles']>0 and result['cycles']==proof['cycles'],'ACCEPTED_INTEGER_CYCLES')
 require(digest(out/'raw.log.gz')==done['raw_sha256'],'CLOSED_RAW_GZIP_SHA');raw=gzip.decompress((out/'raw.log.gz').read_bytes());require(len(raw)==done['raw_uncompressed_bytes']and hashlib.sha256(raw).hexdigest()==done['raw_uncompressed_sha256'],'CLOSED_RAW_FULL_SHA_SIZE');text=raw.decode()
 binding=read(Root(c)/'control/dispatch_bindings'/(co+'.json'));require(read(out/'DISPATCH_BINDING.json')==binding and binding['cohort']==co and binding['canonical_spec_sha256']==digest(Root(c)/'control/specs'/(co+'.json')),'DISPATCH_BINDING_SPEC');resolved=dict(spec,host_cpu=binding['host_cpu']);require(binding['resolved_spec_sha256']==hashlib.sha256(js(resolved)).hexdigest()and intent['dispatch_binding_sha256']==digest(out/'DISPATCH_BINDING.json'),'DISPATCH_RESOLVED_SHA')
 e=load('D_CLOSED_SOURCE_ONLY_ENGINE',Root(c)/'tools/perf16r1_native.py');frozen=e.binding()
 launch=read(out/'NATIVE_LAUNCH.json');pm=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 for p in [intent,launch,pm]:require(p['l2_mlp_execution_binding']==frozen and p['observer_exit_race_binding']==intent['observer_exit_race_binding']and p['dispatch_binding_sha256']==digest(out/'DISPATCH_BINDING.json'),'ACTUAL_RUNTIME_BINDING')
 obs=plan['observer_overlay'];observer=load('D_FROZEN_EXIT_OBSERVER_PURE',obs['path']);transformed,counts=observer.transformed(P(c['base_native_path']).read_text());ob=intent['observer_exit_race_binding'];require(ob['adapter_sha256']==obs['sha256']==digest(obs['path'])and ob['transformed_run_native_source_sha256']==hashlib.sha256(transformed.encode()).hexdigest()and ob['transformation_counts']==counts and not ob['identity_snapshots_synthesized'],'ACTUAL_EXIT_OBSERVER_SOURCE_BINDING')
 require(launch['argv'][-len(spec['native_simulator_argv']):]==spec['native_simulator_argv']and spec['native_simulator_argv'][0]in pm['maps']and pm['mnt_namespace']==spec['execution_mnt_namespace']and pm['host_cpu_affinity_actual']==[binding['host_cpu']],'ACTUAL_MODEL_ARGV_MAPS_CPU_NAMESPACE')
 require(launch['effective_RLIMIT_AS_bytes']==spec['limits']['max_process_tree_vms_bytes'],'ACTUAL_AS_CAP');limits=re.findall(r'^Max address space\s+(\S+)\s+(\S+)\s+bytes\s*$',pm['actual_process_limits_text'],re.M);require(limits==[(str(spec['limits']['max_process_tree_vms_bytes']),)*2],'ACTUAL_PROCESS_LIMITS')
 for name,src in [('DOWNSTREAM_FROZEN_SPEC.json',Root(c)/'control/specs'/(co+'.json')),('DOWNSTREAM_INTENT.json',Root(c)/'control/qualification_ledger'/(co+'.INTENT.json')),('DOWNSTREAM_PLAN.json',Root(c)/'control/EXECUTION_PLAN.json'),('DOWNSTREAM_REQUEST.json',Root(c)/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('DOWNSTREAM_PROFILE.json',Root(c)/'control/BUILD_PROFILE.json')]:require(digest(out/name)==digest(src),'DOWNSTREAM_FROZEN_SOURCE:'+name)
 domain=read(spec['input_binding_path']);require(digest(spec['input_binding_path'])==spec['input_binding_sha256'],'INPUT_BINDING_SHA');trace=(out/'actual_file_process_network.log').read_text();require('connect('not in trace and '"/usr/bin/ssh"'not in trace and '"/bin/ssh"'not in trace and all(x['path']in trace for x in domain['qualification']['rows']),'ACTUAL_TRACE_FILE_ACCESS_NO_NETWORK');require(spec['framework_commit']in text and spec['core_commit'][:7]in text,'ACTUAL_BUILD_ECHO')
 cap=load('D_QUALIFIED_PURE_POPULATION_ADAPTER',Root(c)/'tools/perf16r1_capacity_strict.py');cap.validate_spec(spec);population,shape=cap.population_from_verified_closed_text(text,spec,domain['qualification']);require(all(proof[k]==v for k,v in population.items()),'RAW_REDERIVED_POPULATION_CYCLES_COUNTERS');require(shape==proof['physical_capacity_parser_binding'],'PHYSICAL_CAPACITY_SOURCE_BINDING')
 for ref in spec['runtime_files']:require((Root(c)/ref['target']).resolve(strict=True)==P(ref['actual_realpath']).resolve(strict=True)and digest(ref['actual_realpath'])==ref['sha256'],'FROZEN_RUNTIME_TARGET_BYTES')
 diagnostic={k:int(v)for k,v in re.findall(r'^\s*(avg_mrq_latency|averagemflatency|avg_icnt2mem_latency|avg_icnt2sh_latency)\s*=\s*(\d+)\s*$',text,re.M)};require(proof['latency_counters']==diagnostic,'DIAGNOSTIC_COUNTER_REDERIVATION')
 seq=0;last=None
 with gzip.open(out/'progress.jsonl.gz','rt')as stream:
  for line in stream:
   v=json.loads(line);seq+=1;require(v['seq']==seq and(v['pid'],v['start_ticks'],v['generation'])==(pm['pid'],pm['start_ticks'],done['uuid'])and v['input']==spec['input_digest']and v['roi']==spec['original_environment']['DTC_AG7_ROI_SHA'],'AUTHENTICATED_WHOLE_ROI_PROGRESS');require(last is None or(v['mono_ns']>last['mono_ns']and v['completed']>=last['completed']),'MONOTONE_PROGRESS');last=v
 require(last is not None and last['end']=='NATURAL'and last['completed']==spec['expected']['instructions']and seq==proof['progress_records'],'NATURAL_COMPLETE_INPUT_PROGRESS')
 ba=rs=0;previous=None
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt')as stream:
  for line in stream:
   v=json.loads(line)
   if 'DTC_exact_original_policy'in v:
    item=v['DTC_exact_original_policy'];b=item['runtime_policy_binding'];require(item['decision']['decision']!='STOP'and b['schema']=='DTC_PERFV2_CODESIGN16_LAYOUT_R1_ADMISSION_PRESSURE_ONLY_RUNTIME_V1'and b['guard_sha256']==frozen['runtime_guard_sha256']and b['policy_sha256']==frozen['runtime_guard_policy_sha256']and b['telemetry_receiver_sha256']=='f523975b9780b498b988e2b3145ba5b4aebdef4d0e9b0146392d3a31a99a4ec1','ACTUAL_GUARD_BINDING_OR_STOP');stamp=item['sample']['monotonic_ns'];require(previous is None or 0<stamp-previous<=30*10**9,'ACTUAL_GUARD_SAMPLE_CADENCE');previous=stamp;ba+=1
   if 'physical_RAM_pass'in v:require(v['physical_RAM_pass']and v['physical_disk_pass']and v['process_tree_observed_rss_bytes']<=spec['limits']['max_process_tree_rss_bytes'],'ACTUAL_RUNTIME_RESOURCE_CAP');rs+=1
 require(ba==proof['BA_decisions']and rs==proof['resource_samples']and ba>0 and rs>0,'ACTUAL_GUARD_RESOURCE_COUNTS')
 require(proof['effective_options']==spec['expected_options']and proof['input_digest']==spec['input_digest']and all(proof[k]==spec[k]for k in['core_commit','framework_commit','binary_sha256','profile','cell','downstream_profile','cohort']),'PROOF_FROZEN_SCIENCE_IDENTITY')
 qual=read(Root(c)/'DTC/control'/('SCIENCE_QUALIFICATION_'+co+'.json'));require(qual['uuid']==done['uuid']and qual['cohort']==co and qual['status']==c['strict_status']and qual['strict_sha256']==digest(out/'L2_STRICT.json'),'EXACT_SCIENCE_QUALIFICATION')
 return proof

def Root(c):return P(c['root'])

def audit(c,provider,output):
 gate=readiness(c,provider);require(gate['ready'],'AUDIT_REQUIRES_ALL16_ACCOUNTED_CLOSED_NO_LIVE_RAW');R,plan,reg,q,published,cs,rp=source_context(c);pr,snap=publication(provider,c);rows_by={r['cohort']:r for r in snap['rows']};sys.path.insert(0,c['B_package']);import archive_witness as aw;import safety_hold_overlay as ho
 output=P(output).resolve();base=P(c['output_parent']).resolve();require(output.is_relative_to(base)and not output.exists(),'EXCLUSIVE_OWN_D_OUTPUT_REQUIRED');output.mkdir(parents=True);(output/'AUDIT_INVOKED.json').write_bytes(js({'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'provider':pin(provider),'contract_scope':c['request'],'one_shot':True,'new_models':0}));rows=[];proofs=[];checks=[]
 def ck(name,v):require(v,name);checks.append(name)
 try:
  strict=load('D_READONLY_PERF16_TERMINAL',R/'tools/perf16r1_strict.py');ctx={'root':str(R),'request':c['request'],'q':q,'source_pins':plan['source_pins'],'source_qualified':True};uuids=[];foreign={v['uuid']for key,qq in reg['registered_future_requests'].items()if key!=c['request']and isinstance(qq.get('consumed'),dict)for v in qq['consumed'].values()if isinstance(v,dict)and v.get('uuid')};retired=set(c['retired_pre_INTENT_UUIDs'])
  prior_science(c,reg);ck('PRIOR_SCIENCE_IDENTITY_BUDGET_PRESERVED',True)
  for approved in cs:
   co=approved['proposed_native_cohort'];bp=rows_by[co];sp=R/'control/specs'/(co+'.json');spec=read(sp);ck('SPEC_IDENTITY:'+co,digest(sp)==q['admitted_specs'][co]and spec['expected_options']==approved['expected_effective_options']and spec['input_digest']==approved['input_digest']);dh=reference(approved['DH_P0_reference']);ch=reference(approved['CH_P0_reference']);phy,pe=component(bp['V1_physical'],spec,dh,'PHYS768_TAG64x8'if approved['physical_lines']==768 else'PHYS1024_TAG64x8');pib,pie=component(bp['V1_PIB'],spec,dh,'OO_PIB192');row={'cohort':co,'profile':spec['profile'],'program':spec['program'],'suite':spec['suite'],'input_digest':spec['input_digest'],'accepted':False,'cycles':None,'status':bp['status'],'DH_P0_cycles':dh['cycles'],'CH_P0_cycles':ch['cycles'],'physical_cycles':phy,'PIB_cycles':pib,'S_combo':None,'R_combo':None,'I':None,'J':None,'kernel_changes':[]}
   if co not in q['consumed']:
    h=ho.validate_unstarted(bp,spec,cs,ctx);ck('UNUSED_TYPED_NO_SCIENCE:'+co,h is not None and bp['status']=='UNUSED_SAFETY_HOLD');row['unused_safety_HOLD']=h;row['uuid']=None
   else:
    entry=q['consumed'][co];u=entry['uuid'];uuid.UUID(u);ck('UNIQUE_NEW_ONCE_UUID:'+co,u not in uuids and u not in foreign and u not in retired and entry['charged']==1);uuids.append(u);ip=R/'control/qualification_ledger'/(co+'.INTENT.json');intent=read(ip);done=read(ip.with_name(co+'.DONE.json'));out=R/'DTC/run/results'/u;resultp=R/'analysis'/(co+'.RESULT.json');result=read(resultp);ck('EXACT_LIFECYCLE_JOIN:'+co,digest(ip)==entry['intent_sha256']and done==entry['execution_receipt']==read(out/'NATIVE_EXIT.json')and intent['uuid']==done['uuid']==result['uuid']==u and intent['cohort']==done['cohort']==result['cohort']==co and not live(out));ck('SOURCE_OWNER_INTENT:'+co,intent['batch_lease_pid']==1498278 and intent['batch_lease_start_ticks']==977758783);ck('NEW_ROLE_ONLY:'+co,result['scientific_role']=='PERFV2_CODESIGN16_LAYOUT_R1_AUTHORIZED_DH'and result['original_or_repair_results_replaced']is False and result['validated_union_authorized']is False);accepted=result['state']=='PASS_PERFV2_CODESIGN16_LAYOUT_R1_DH_STRICT_ARCHIVE_NATIVE_RESTORE';failed=result['state']=='FAIL_PERFV2_CODESIGN16_LAYOUT_R1_DH_ARCHIVED_NO_RETRY';ck('QUALIFIED_OR_HONEST_ARCHIVED_NEGATIVE:'+co,accepted or failed)
    if accepted:
     proof=closed_strict_rederive(c,co,spec,intent,done,out,result,q,plan);ck('INDEPENDENT_CLOSED_RAW_STRICT_REDERIVATION_EQUALS_SOURCE:'+co,proof==result['proof']and proof['performance_accepted']is True and type(result['cycles'])is int and result['cycles']==proof['cycles']>0);row.update(accepted=True,cycles=result['cycles']);row['traffic']=proof.get('traffic',{});row['metrics_mixed_scope_not_perkernel']=proof.get('metrics',{});ck('NATURAL_SUCCESS:'+co,done['stop_reason']is None and done['launcher_wait_returncode']==0 and done['native_simulator_observed'])
     domain=read(spec['input_binding_path'])['qualification']['rows'];ks=proof['kernels'];dk=dh['proof']['kernels'];ckk=ch['proof']['kernels'];ck('KERNEL_ORDER_AND_COMPLETE_SCOPE:'+co,len(ks)==len(domain)==len(dk)==len(ckk)==spec['expected']['kernels'])
     for i,(x,d,z,qual)in enumerate(zip(ks,dk,ckk,domain),1):ck('KERNEL_SYMBOL_INSTRUCTIONS:'+co+str(i),x['kernel']==d['kernel']==z['kernel']==qual['kernel']and x.get('active_instructions',x.get('instructions'))==qual['active_thread_instructions']);row['kernel_changes'].append({'ordinal':i,'kernel':x['kernel'],'DH_P0_cycles':d['cycles'],'CH_P0_cycles':z['cycles'],'combo_cycles':x['cycles'],'within_DH_cycle_delta':x['cycles']-d['cycles']})
     ck('KERNEL_CYCLE_SUM:'+co,sum(x['combo_cycles']for x in row['kernel_changes'])==row['cycles'])
    else:ck('NEGATIVE_NEVER_PERFORMANCE:'+co,(not natural(done))and result['cycles']is None and result['proof']['performance_accepted']is False)
    refs,witness=aw.verify_for(R,P(c['archive_results_root']),c['strict_status'],co,result,out,done,accepted,c['outbox_sha256'],check_mount=True);manifest=read(witness['source_manifest']['path']);ck('FULL_SOURCE_KEEP_TYPED_TREE:'+co,retained_source_tree(aw,manifest,out)==len(manifest['entries']));restore=P(result['archive']['receipt']['native_restore']);ck('RESTORE_ROOT_NOT_SYMLINK_OR_ESCAPE:'+co,not restore.is_symlink()and restore.resolve().is_relative_to((R/'DTC/run/recovery').resolve()));row['uuid']=u;row['actual_model_observed']=done['native_simulator_observed'];row['archive_witness']=witness;row['RESULT']=pin(resultp);proofs.append({'cohort':co,'RESULT':pin(resultp),'INTENT':pin(ip),'DONE':pin(ip.with_name(co+'.DONE.json')),'archive_witness':witness,'scientific_acceptance':accepted})
   if row['accepted']:
    row.update(S_combo=dh['cycles']/row['cycles'],R_combo=ch['cycles']/row['cycles'],I=dh['cycles']/row['cycles']);row['J']=phy*pib/(dh['cycles']*row['cycles'])if phy is not None and pib is not None else None
   for name in ['S_combo','R_combo','I','J']:ck('INDEPENDENT_CYCLE_METRIC:'+co+name,(row[name]is None and bp[name]is None)or(row[name]is not None and bp[name]is not None and math.isclose(row[name],bp[name],rel_tol=1e-12)))
   row['P0_references']={'CH':{k:v for k,v in ch.items()if k!='proof'},'DH':{k:v for k,v in dh.items()if k!='proof'}};row['single_factor_sources']={'physical':pe,'PIB':pie};rows.append(row)
  accounted=ho.accounting(snap['rows'],ctx);ck('ALL16_ACCOUNTED_HONESTLY',accounted['all16_candidates_accounted_verified']);own=summary(rows);compare_stats(own,snap['summary']);ck('B_PROFILE_AND_COMMON_STATS_INDEPENDENT_MATCH',True)
  fresh,_,_=stable_registry(c);prior_science(c,fresh);fq=fresh['registered_future_requests'][c['request']];ck('OWN_SCIENTIFIC_LEDGER_STABLE_DURING_AUDIT',fq['budget']==q['budget']and fq['remaining']==q['remaining']and fq['admitted_specs']==q['admitted_specs']and fq['consumed']==q['consumed']);require(digest(R/'control/EXECUTION_PLAN.json')==c['execution_plan_sha256'],'PLAN_CHANGED_DURING_AUDIT'); [require(digest(x['path'])==x['sha256'],'FINAL_SOURCE_PIN_DRIFT:'+x['path']) for x in plan['source_pins']]
  report={'schema':'DTC_PERFV2_CODESIGN16_LAYOUT_R1_D_FINAL_INDEPENDENT_SCIENTIFIC_REVIEW_V1','status':'PASS','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authority_commit':c['authority_commit'],'request':c['request'],'independent_verification_passed':True,'all16_candidates_accounted_verified':True,'all16_actual_scientific_closed':accounted['all16_actual_scientific_closed'],'accepted':sum(r['accepted']for r in rows),'archived_negative':sum(r['status']=='ARCHIVED_NEGATIVE_NO_PERFORMANCE'for r in rows),'unused_safety_HOLD':sum(r['status']=='UNUSED_SAFETY_HOLD'for r in rows),'fixed_program_inputs':8,'not_CORE32_or_35':True,'rows':rows,'independent_summary':own,'accounting':accounted,'checks':checks,'provider_used':pin(provider),'frozen_snapshot_manifest':pr['manifest'],'actual_registry_read':rp,'new_scientific_models_by_auditor':0,'native_mutation_or_restore_actions':0,'active_raw_reads':0,'Root_scientific_narrative_or_visual_signoff':False,'manuscript_v023_modified_or_promoted':False,'hardware_boundary':'128B nominal identity accounting80/96/128KiB;512Tag mappings fixed;PIB+lowercreate192 each+50%; no payloadSRAM/area/port/timing/PPA equivalence','causal_boundary':'Per-kernel cycles verified; mixed final counters/occupancy/retry/endpoint gauges do not establish critical-path time; missing neverzero; HtoD/captureELF/fullapplication numeric and coherence remain unproven.'};(output/'FINAL_REVIEW.json').write_bytes(js(report));(output/'MATRIX_RESULTS.json').write_bytes(js(rows));(output/'INDEPENDENT_STATISTICS.json').write_bytes(js(own));(output/'SOURCE_PROOFS.json').write_bytes(js(proofs));(output/'README.md').write_text('Independent closed Codesign16 one-shot review. Core/input/config/source identity, natural strict and every new archive chunk/native restored and retained source entry checked. All8x2 statuses retained; actual16closed differs from16accounted with unused credits. No new model/restore/registry/Goal/manuscript action. Root narrative and visual signoff remain separate.\n');members=[{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)}for p in sorted(output.iterdir())if p.is_file()];(output/'MANIFEST.json').write_bytes(js({'schema':'DTC_PERFV2_CODESIGN16_LAYOUT_R1_D_FINAL_AUDIT_MANIFEST_V1','status':'PASS','files':members,'new_models':0}));return {'status':'PASS','output':str(output),'FINAL_REVIEW':pin(output/'FINAL_REVIEW.json'),'manifest':pin(output/'MANIFEST.json'),'accepted':report['accepted'],'negative':report['archived_negative'],'unusedHOLD':report['unused_safety_HOLD']}
 except BaseException as error:
  (output/'HOLD_NO_AUTOMATIC_RETRY.json').write_bytes(js({'status':'HOLD_ROOT_DIAGNOSIS_REQUIRED','error':repr(error),'checks_completed':checks,'new_models':0,'no_model_retry':True}));raise
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',required=True,type=P);ap.add_argument('--contract-sha256',required=True);ap.add_argument('--provider',required=True,type=P);ap.add_argument('--check-readiness',action='store_true');ap.add_argument('--audit',action='store_true');ap.add_argument('--output-dir',type=P);args=ap.parse_args();require(digest(args.contract)==args.contract_sha256,'AUDIT_CONTRACT_SHA');c=read(args.contract);require(c['schema']=='DTC_CODESIGN16_LAYOUT_R1_D_FINAL_READONLY_AUDIT_CONTRACT_V1','AUDIT_CONTRACT_SCHEMA');require(digest(__file__)==c['auditor_source_sha256'],'AUDITOR_SOURCE_SHA');os.nice(19)
 if args.check_readiness:print(json.dumps(readiness(c,args.provider)));return
 require(args.audit and args.output_dir is not None,'EXPLICIT_AUDIT_AND_EXCLUSIVE_OUTPUT_REQUIRED');require(not(args.check_readiness and args.audit),'ONE_MODE_ONLY');require(readiness(c,args.provider)['ready'],'ALL16_TERMINAL_REQUIRED_BEFORE_ONESHOT_MARKER');res=load('D_AUDIT_READONLY_CPU_SAMPLE',P(c['root'])/'tools/perf16r1_resources.py');sample=res.sample_system();require(bool(sample['cpu_allowed']),'NO_SAFE_READONLY_CPU_AVAILABLE');os.sched_setaffinity(0,{sample['cpu_allowed'][0]});state=P(c['one_shot_state_dir']);state.mkdir(parents=True,exist_ok=True)
 with(state/('AUDIT_'+args.contract_sha256[:16]+'.lock')).open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);marker=state/('AUDIT_'+args.contract_sha256[:16]+'.INVOKED.json');require(not marker.exists(),'EXISTING_AUDIT_ATTEMPT_NO_AUTOMATIC_RETRY')
  with marker.open('xb')as f:f.write(js(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),contract=pin(args.contract),provider=pin(args.provider),output=str(args.output_dir),new_models=0,one_shot=True)));f.flush();os.fsync(f.fileno())
  print(json.dumps(audit(c,args.provider,args.output_dir)))
if __name__=='__main__':main()




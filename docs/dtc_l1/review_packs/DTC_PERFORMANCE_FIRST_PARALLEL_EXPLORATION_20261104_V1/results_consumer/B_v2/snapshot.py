"""Repeatable read-only closed RESULT snapshot. No model/registry/service writes."""
from pathlib import Path
import argparse,ast,csv,datetime,hashlib,json,math,uuid,copy
import archive_witness as aw
D=Path(__file__).resolve().parent
require=aw.require;sha=aw.sha;get=aw.get
read=lambda p:json.loads(Path(p).read_bytes())
js=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def fixed_inputs():
 f=read(D/'FIXED_INPUTS.json')
 for x in f['pins']:require(sha(x['path'])==x['sha256'],'FIXED_INPUT_SHA:'+x['path'])
 a=read(f['input_authority']);v=read(f['variant_authority'])['variants'];require(len(a['inputs'])==8,'NOT_FIXED8');return f,a,{x['variant']:x for x in v}
def baselines(auth):
 rows={};evidence=[]
 for inp in auth['inputs']:
  for ref in inp['P0_references']:
   p=Path(ref['source_RESULT_path']);v,vr=get(p);q=v['proof'];require(ref['accepted']and q['performance_accepted']and q.get('profile',q.get('downstream_profile'))=='P0','BASELINE_NOT_P0');require(v['cycles']==ref['cycles']and q['input_digest']==ref['input_digest']and q['cell']==ref['source_cell']and q['effective_options']==ref['effective_options'],'BASELINE_IDENTITY_OPTIONS')
   for k in ['core_commit','framework_commit','binary_sha256']:require(q[k]==ref['build'][k],'BASELINE_BUILD')
   bp=Path(v.get('reference_result_path',str(p)));b,br=get(bp);require(b['uuid']==v['uuid']and b['cycles']==v['cycles']and b['proof']['raw_gzip_sha256']==q['raw_gzip_sha256'],'BASELINE_ALIAS_BOTTOM');r=copy.deepcopy(ref);r.update(actual_bottom_RESULT=br,actual_bottom_cohort=b['cohort'],canonical_RESULT=vr,suite=inp['population']['suite']);
   if ref['source_cell']=='DH':
    sp=p.parents[1]/'control/specs'/(v['cohort']+'.json');bs=read(sp);require(bs['expected_options']==ref['effective_options']and bs['binary_sha256']==ref['build']['binary_sha256'],'BASELINE_SPEC_IDENTITY');r['baseline_runtime_files']=bs['runtime_files'];r['baseline_spec']={'path':str(sp),'sha256':sha(sp)}
   rows[ref['program'],ref['source_cell']]=r;evidence.append(r)
 require(len(rows)==16,'BASELINE16');return rows,evidence

def expected_rows(f,auth,variants):
 rows=[]
 for inp in auth['inputs']:
  p=inp['population'];n=p['program'];d=p['input_digest']
  for v in variants.values():
   r=dict(program=n,suite=p['suite'],input_digest=d,variant=v['variant'],design='DH',downstream_profile='P0',accepted=False,cycles=None,S_DH=None,Rnew=None,Rold=None,I=None)
   if v['status']=='CPU_PROGRESS_NEGATIVE_HOLD':r.update(route='TAG_SAFETY_HOLD',cohort=None,status='SAFETY_HOLD_CPU_PROGRESS_NEGATIVE',reason='Fixed1024Tag/pool640 CPU progress counterexample; no substitution')
   else:
    first=n in f['first4_programs']and v['variant']=='PHYS768_TAG64x8';k='4'if first else'28';token=f['variant_tokens'][v['variant']];c='E2-DTCPF4-'+d[:16]+'-DH-PHYS768-V1'if first else'E2-DTCPF28-'+d[:16]+'-DH-'+token+'-V1';r.update(route='FIRST4'if first else'REMAINING28',route_key=k,cohort=c,request=f['request'+k],status='AWAIT_ACTUAL_REGISTRY_GRANT')
   rows.append(r)
 require(len(rows)==48 and sum(r['route']=='TAG_SAFETY_HOLD'for r in rows)==16 and sum(r['route']=='FIRST4'for r in rows)==4,'PLAN48_PARTITION');return rows

def strict_literals(p):
 tree=ast.parse(Path(p).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='terminal');out={}
 for n in ast.walk(fn):
  if isinstance(n,ast.Return)and isinstance(n.value,ast.Call):
   for kw in n.value.keywords:
    if kw.arg in ['schema','status']and isinstance(kw.value,ast.Constant)and isinstance(kw.value.value,str):out[kw.arg]=kw.value.value
 require(set(out)=={'schema','status'},'STRICT_STATUS_SCHEMA_NOT_STATIC');return out

def runtime_context(f,k,expected,registry=None,epoch=None):
 R=Path(f['root'+k]);budget=4 if k=='4'else 28;req=f['request'+k];ctx=dict(root=str(R),archive=f['archive'+k],request=req,budget=budget,registration_granted=False,source_qualified=False,status='AWAIT_ACTUAL_REGISTRY_GRANT')
 if registry is None:registry,rr=get(f['registry']);epoch,er=get(f['epoch'])
 else:rr={'path':'CPU_ONLY_IN_MEMORY_REGISTRY','sha256':epoch['native_registry_sha256']};er={'path':'CPU_ONLY_IN_MEMORY_EPOCH','sha256':'0'*64}
 require(epoch['native_registry_sha256']==rr['sha256'],'REGISTRY_EPOCH_PAIR_CHANGED');q=registry.get('registered_future_requests',{}).get(req)
 if q is None:return ctx
 require(q['request']==req and q['budget']==budget and q.get('model_automatic_retries')==0,'GRANT_SCOPE_OR_RETRY');cs={r['cohort']for r in expected if r.get('route_key')==k};require(set(q['admitted_specs'])==cs and q['remaining']==budget-len(q['consumed'])and set(q['consumed'])<=cs,'GRANT_MEMBERSHIP_ACCOUNTING');plan,pr=get(R/'control/EXECUTION_PLAN.json');require(pr['sha256']==q['execution_plan_sha256'],'REGISTERED_PLAN_SHA')
 for x in plan['source_pins']:require(sha(x['path'])==x['sha256'],'SOURCE_PIN:'+x['path'])
 prefix='perf4'if k=='4'else'perf28';paths={key:R/'tools'/(prefix+'_'+name+'.py')for key,name in [('engine_sha256','native'),('strict_sha256','strict'),('outbox_sha256','outbox')]}
 for key,p in paths.items():require(sha(p)==q[key],'REGISTERED_SOURCE_DRIFT:'+key)
 m=read(R/'control/MATRIX.json');require({p['cohort']for p in m['points']}==cs,'ACTUAL_MATRIX_MEMBERSHIP');lit=strict_literals(paths['strict_sha256']);ctx.update(registration_granted=True,source_qualified=True,status='ACTUAL_REGISTERED_SOURCE_QUALIFIED',registry=rr,epoch=er,execution_plan=pr,registered_consumed_n=len(q['consumed']),registered_remaining=q['remaining'],registry_state=q.get('state'),strict_schema=lit['schema'],strict_status=lit['status'],outbox_sha256=q['outbox_sha256'],q=q);return ctx

def validate_exit_policy(done,accepted):
 # Only acceptedperformance requires naturalexit0. A legitimate archived
 # strict/ROI negative may have naturalexit0 and remains nonperformance.
 if accepted:require(done.get('stop_reason')is None and type(done.get('launcher_wait_returncode'))is int and done['launcher_wait_returncode']==0,'ACCEPTED_NOT_NATURAL_EXIT0')

def qualify_closed(row,f,variant,base,ctx):
 R=Path(ctx['root']);c=row['cohort'];rp=R/'analysis'/(c+'.RESULT.json')
 if not rp.exists():return dict(row,status='AWAIT_CLOSED_RESULT')
 v,vr=get(rp);k=row['route_key'];ok=v.get('state')==f['PASS'+k];negative=v.get('state')==f['FAIL'+k];require(ok or negative,'UNDECLARED_RESULT_STATE');require(v.get('scientific_role')==f['role'+k]and v.get('new_contract_only')is True and v.get('original_or_repair_results_replaced')is False,'RESULT_ROLE_BOUNDARY')
 for key,val in [('cohort',c),('input_digest',row['input_digest']),('cell','DH'),('profile',row['variant']),('structure_variant',row['variant']),('downstream_profile','P0')]:require(v.get(key)==val,'RESULT_IDENTITY:'+key)
 sp=R/'control/specs'/(c+'.json');s,sr=get(sp);q=ctx['q'];require(sr['sha256']==q['admitted_specs'][c]==sha(R/'control'/(c+'_SPEC.json')),'SPEC_SHA');dh=base[row['program'],'DH'];ch=base[row['program'],'CH'];options=copy.deepcopy(dh['effective_options'])
 for key,val in variant['delta'].items():require(options.get(key)==val['from'],'BASELINE_DELTA_FROM');options[key]=val['to']
 require(len(options)==270 and s['expected_options']==options,'FULL270_CONFIG_DELTA')
 for key,val in [('cohort',c),('request',row['request']),('cell','DH'),('profile',row['variant']),('structure_variant',row['variant']),('downstream_profile','P0'),('host_cpu',None),('input_digest',row['input_digest']),('expected',dh['expected'])]:require(s.get(key)==val,'SPEC_IDENTITY:'+key)
 for key in ['core_commit','framework_commit','binary_sha256']:require(s[key]==dh['build'][key],'BUILD_CHANGED')
 require(s['input_binding_sha256']==dh['input_binding']['sha256']==sha(s['input_binding_path']),'BINDING_SHA');require([x['sha256']for x in s['configs']]==[x['sha256']for x in variant['configs']],'A_CONFIG_VECTOR')
 for x in s['configs']:require(sha(x['path'])==x['sha256'],'CONFIG_BYTES')
 require(s['runtime_files']==dh['baseline_runtime_files'],'RUNTIME_BINARY_LIBRARY_CONTRACT_CHANGED')
 for x in s['runtime_files']:require(sha(x['actual_realpath'])==x['sha256'],'RUNTIME_FILE')
 require(any(x['sha256']==s['binary_sha256']for x in s['runtime_files']),'BINARY_UNPINNED');ip=R/'control/qualification_ledger'/(c+'.INTENT.json');i,ir=get(ip);d,dr=get(ip.with_name(c+'.DONE.json'));cons=q['consumed'][c];uid=v['uuid'];out=R/'DTC/run/results'/uid;exitv,er=get(out/'NATIVE_EXIT.json');require(cons['uuid']==uid==i['uuid']==d['uuid']and i['output']==str(out),'RUN_UUID');require(cons['intent_sha256']==ir['sha256']and cons['execution_receipt']==d==exitv,'DONE_GRANT_EXIT');validate_exit_policy(d,ok);require(sha(out/'DOWNSTREAM_FROZEN_SPEC.json')==sr['sha256'],'RUN_SPEC');db,dbr=get(R/'control/dispatch_bindings'/(c+'.json'));require(db['canonical_spec_sha256']==sr['sha256']and sha(out/'DISPATCH_BINDING.json')==dbr['sha256']==i['dispatch_binding_sha256'],'DISPATCH_BINDING');require(type(db['host_cpu'])is int,'DYNAMIC_CPU');require(hashlib.sha256(js(dict(s,host_cpu=db['host_cpu']))).hexdigest()==db['resolved_spec_sha256'],'RESOLVED_SPEC');_,av=aw.verify_for(R,f['archive'+k],ctx['strict_status'],c,v,out,d,ok,ctx['outbox_sha256'])
 common=dict(row,source_RESULT=vr,source_SPEC=sr,source_INTENT=ir,source_DONE=dr,native_EXIT=er,uuid=uid,source_scientific_role=v['scientific_role'],source_validated_union_authorized=v.get('validated_union_authorized'),source_union_scope=v.get('union_scope'),archive_witness=av,baseline_DH_P0=dh['canonical_RESULT'],baseline_DH_bottom=dh['actual_bottom_RESULT'],baseline_CH_P0=ch['canonical_RESULT'],baseline_CH_bottom=ch['actual_bottom_RESULT'])
 if negative:require(v.get('cycles')is None and v['proof'].get('performance_accepted')is False,'NEGATIVE_PERFORMANCE');return dict(common,status='ARCHIVED_NEGATIVE_NO_PERFORMANCE',reason=v['proof'])
 proof=v['proof'];strict,strref=get(out/'L2_STRICT.json');require(strict==proof and proof['schema']==ctx['strict_schema']and proof['status']==ctx['strict_status']and proof['performance_accepted']is True,'STRICT_IDENTITY');cycles=v['cycles'];require(type(cycles)is int and cycles>0 and cycles==proof['cycles']and d.get('native_simulator_observed')is True,'CYCLES_OR_ACTUAL_MODEL')
 for key,val in [('cohort',c),('uuid',uid),('input_digest',row['input_digest']),('cell','DH'),('profile',row['variant']),('structure_variant',row['variant']),('downstream_profile','P0'),('effective_options',options)]+[(key,dh['build'][key])for key in ['core_commit','framework_commit','binary_sha256']]:require(proof.get(key)==val,'STRICT_EXPECTED:'+key)
 for key,val in [('CTA',dh['expected']['CTA']),('instructions',dh['expected']['instructions']),('kernel_count',dh['expected']['kernels'])]:require(proof[key]==val,'ROI:'+key)
 require(proof['raw_gzip_sha256']==d['raw_sha256']and proof['raw_uncompressed_sha256']==d['raw_uncompressed_sha256']and proof['dispatch_binding_sha256']==dbr['sha256'],'STRICT_RUN_WITNESS');qual,qr=get(R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json'));require(qual['status']==ctx['strict_status']and qual['cohort']==c and qual['uuid']==uid and qual['strict_sha256']==strref['sha256'],'SCIENCE_QUALIFICATION');sd=dh['cycles']/cycles;rn=ch['cycles']/cycles;ro=ch['cycles']/dh['cycles'];return dict(common,status='ACCEPTED_STRICT_ARCHIVE_RESTORE',accepted=True,cycles=cycles,S_DH=sd,Rnew=rn,Rold=ro,I=sd,STRICT=strref,science_qualification=qr,kernels=proof.get('kernels'),traffic=proof.get('traffic'),metrics_mixed_scope=proof.get('metrics'),latency_counters_diagnostic=proof.get('latency_counters'),actual_effective_options=options,counter_scope='Additive final cumulative typed events; gpu_sim_cycle is finalkernel. Missing!=0; no mean/gauge/peak differences; numerical/coherence unproven.')

def gm(xs):return math.exp(sum(math.log(x)for x in xs)/len(xs))if xs else None
def metric_stats(rows):
 result={}
 for k in ['S_DH','Rnew','Rold','I']:
  xs=[r[k]for r in rows];result[k]={'n':len(xs),'GM':gm(xs),'positive':sum(x>1+1e-12 for x in xs),'negative':sum(x<1-1e-12 for x in xs),'zero_within1e_minus12':sum(abs(x-1)<=1e-12 for x in xs)}
 return result

def summarize(rows,f):
 out=dict(planned_total=48,nonTag_planned=32,Tag_safety_HOLD=16,fixed_input_n=8,new_models=0,native_writes=0,CORE32_population=False,status_counts={},variants={});accepted=[r for r in rows if r['accepted']]
 for r in rows:out['status_counts'][r['status']]=out['status_counts'].get(r['status'],0)+1
 ids=list(f['variant_tokens'])
 for v in ids:
  allv=[r for r in rows if r['variant']==v];got=[r for r in allv if r['accepted']];out['variants'][v]={'planned_n':8,'accepted_n':len(got),'missing_or_negative_or_HOLD_n':8-len(got),'available_set_metrics':metric_stats(got),'by_suite_available_only':{s:metric_stats([r for r in got if r['suite']==s])for s in sorted(set(r['suite']for r in allv))},'not_direct_GM_comparable_without_same_intersection':True}
 common=set.intersection(*[{r['input_digest']for r in accepted if r['variant']==v}for v in ids]);out['common_nonTag_accepted_intersection']={'n':len(common),'ids':sorted(common),'variants':{v:metric_stats([r for r in accepted if r['variant']==v and r['input_digest']in common])for v in ids},'no_best_stitching':True};out['accepted_new_points']=len(accepted);out['archived_negative_new_points']=sum(r['status']=='ARCHIVED_NEGATIVE_NO_PERFORMANCE'for r in rows);out['verification_HOLD_points']=sum(r['status']in ['VERIFICATION_HOLD','RUNTIME_VERIFICATION_HOLD']for r in rows);out['pending_nonTag_points']=32-out['accepted_new_points']-out['archived_negative_new_points'];out['all32_nonTag_closed_verified']=out['pending_nonTag_points']==0 and out['verification_HOLD_points']==0;out['first4_accepted']=sum(r['accepted']and r['route']=='FIRST4'for r in rows);out['remaining28_accepted']=sum(r['accepted']and r['route']=='REMAINING28'for r in rows);return out

def collect():
 f,a,variants=fixed_inputs();base,brefs=baselines(a);rows=expected_rows(f,a,variants);contexts={}
 for k in ['4','28']:
  try:contexts[k]=runtime_context(f,k,rows)
  except Exception as e:contexts[k]={'registration_granted':False,'source_qualified':False,'status':'RUNTIME_VERIFICATION_HOLD','error':repr(e),'request':f['request'+k]}
 out=[]
 for r in rows:
  r['Rold']=base[r['program'],'CH']['cycles']/base[r['program'],'DH']['cycles']
  if r['route']=='TAG_SAFETY_HOLD':out.append(r);continue
  c=contexts[r['route_key']]
  if not c['registration_granted']:out.append(dict(r,status=c['status'],reason=c.get('error')));continue
  try:out.append(qualify_closed(r,f,variants[r['variant']],base,c))
  except Exception as e:out.append(dict(r,status='VERIFICATION_HOLD',verification_error=repr(e)))
 return dict(schema='DTC_PERF_STRUCTURE48_CLOSED_READONLY_SNAPSHOT_V1',observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_baselines_qualified=True,report_scope='Fixed8x4nonTag plus16TagHOLD; notCORE32 or oldledger union',runtime_context={k:{x:y for x,y in c.items()if x!='q'}for k,c in contexts.items()},baseline_sources=brefs,rows=out,summary=summarize(out,f),no_model_registry_or_native_writes=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path);a=ap.parse_args();out=a.output_dir.resolve()if a.output_dir else D/'snapshots'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]);require(out.resolve().is_relative_to(D.resolve())and out.resolve().is_relative_to((D/'snapshots').resolve()),'OUTPUT_OWN_SNAPSHOT_ONLY');require(not out.exists(),'NO_OVERWRITE');snapshot=collect();out.mkdir(parents=True,exist_ok=False)
 for n,x in [('SNAPSHOT.json',snapshot),('SUMMARY.json',snapshot['summary'])]:(out/n).write_bytes(js(x))
 fields=['program','suite','input_digest','variant','route','status','accepted','cycles','S_DH','Rnew','Rold','I','cohort']
 with(out/'RESULTS.csv').open('w',newline='')as h:
  w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k)for k in fields}for r in snapshot['rows'])
 (out/'README.md').write_text('Read-only fixed8 structural snapshot:32nonTagplanned+16safetyHOLD, notCORE32. Only actual strict/natural/archive/native-restored closedRESULTs havecycles; other rowsnull. AvailableGM/commonintersection explicit; no perprogrambest. Sourceflags preserved; missingcounter!=0. No rawdecompression/model/controller action.\n')
 files=[{'name':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.iterdir())if p.is_file()];require(all(x['bytes']<8*1024**2 for x in files),'OVERSIZE');(out/'MANIFEST.json').write_bytes(js(dict(schema='DTC_PERF_STRUCTURE48_SNAPSHOT_MANIFEST_V1',observed_utc=snapshot['observed_utc'],files=files,new_models=0,native_writes=0,readonly_consumer_source_sha256=sha(__file__))));provider=dict(schema='DTC_PERF_STRUCTURE48_READONLY_PUBLICATION_PROVIDER_V1',observed_utc=snapshot['observed_utc'],snapshot=str(out),manifest={'path':str(out/'MANIFEST.json'),'sha256':sha(out/'MANIFEST.json')},files=files,summary=snapshot['summary'],report_only=True,baseline_source_qualified=snapshot['source_baselines_qualified'],all_existing_closed_results_qualified=snapshot['summary']['verification_HOLD_points']==0,all32_nonTag_closed_verified=snapshot['summary']['all32_nonTag_closed_verified'],new_models=0,native_writes=0);tmp=D/('PUBLICATION_PROVIDER.'+uuid.uuid4().hex+'.tmp');tmp.write_bytes(js(provider));tmp.replace(D/'PUBLICATION_PROVIDER.json');print(json.dumps({'status':'READONLY_SNAPSHOT_COMPLETE','manifest':provider['manifest'],'status_counts':snapshot['summary']['status_counts']}))
if __name__=='__main__':main()

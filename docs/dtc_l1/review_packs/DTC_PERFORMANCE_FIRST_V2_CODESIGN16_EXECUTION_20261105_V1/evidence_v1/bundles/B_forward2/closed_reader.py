from pathlib import Path
import ast,hashlib,json,copy
import archive_witness as aw
require=aw.require;sha=aw.sha;get=aw.get
read=lambda p:json.loads(Path(p).read_bytes())
js=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
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

def strict_literals(p):
 tree=ast.parse(Path(p).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='terminal');out={}
 for n in ast.walk(fn):
  if isinstance(n,ast.Return)and isinstance(n.value,ast.Call):
   for kw in n.value.keywords:
    if kw.arg in ['schema','status']and isinstance(kw.value,ast.Constant)and isinstance(kw.value.value,str):out[kw.arg]=kw.value.value
 require(set(out)=={'schema','status'},'STRICT_STATUS_SCHEMA_NOT_STATIC');return out

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

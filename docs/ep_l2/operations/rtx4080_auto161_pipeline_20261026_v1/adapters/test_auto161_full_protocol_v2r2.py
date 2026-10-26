#!/usr/bin/env python3
"""Full CLI-core synthetic protocol replay; production161 is never executed."""
import pathlib,json,hashlib,importlib.util,copy,types,os
D=pathlib.Path(__file__).resolve().parent
# Reuse fixture factory without executing its test suite or writing production inputs.
text=(D/'test_auto161_metadata_adapter_v2r2.py').read_text()
prefix=text[:text.index('tests=[]')]
prefix=prefix.replace("T=D/'synthetic_fixtures_v2r2'","T=D/'synthetic_protocol_v2r2'")
ns={'__file__':str(D/'test_auto161_metadata_adapter_v2r2.py'),'__name__':'synthetic_factory'}
exec(compile(prefix,'synthetic_factory','exec'),ns)
a=ns['a'];T=ns['T'];ref=ns['ref']
row,projection,job,idx=ns['fixture']('ISA_PROFILE_SPECIALIST_PREPARATION_REQUIRED',True)
rows=[]
for i in range(161):
 r=copy.deepcopy(row);r['queue_id']='SYNTHETIC_SCOPE_ONLY_'+str(i);rows.append(r)
rows[0]=row
scope={'rows':rows};sp=T/'SYNTHETIC_SCOPE.json';sp.write_text(json.dumps(scope))
projection_ref=ref(projection,'row_projection')
index=dict(idx,rows=[{'queue_id':row['queue_id'],'frozen_row_sha256':a.digest(row),'projection_ref':projection_ref}])
ip=T/'FROZEN_AUTHORITY_INDEX_V2.json';ip.write_text(json.dumps(index))
source=T/'synthetic_protocol_source.py';source.write_bytes((D/'auto161_metadata_adapter_v2.py').read_bytes())
# Isolated in-memory pin substitution only. The actual source and production authorities stay unchanged.
a.SCOPE_SHA=hashlib.sha256(sp.read_bytes()).hexdigest()
ba=a.Reader().refobj(idx['root_binary_attestation']);ba['scope_sha256']=a.SCOPE_SHA
idx['root_binary_attestation']=ref(ba,'synthetic_binary_attestation')
index.update(idx);ip.write_text(json.dumps(index));a.INDEX_SHA=hashlib.sha256(ip.read_bytes()).hexdigest();a.__file__=str(source)
attempt=T/'attempt';attempt.mkdir()
ctx={'schema':'AUTO161_CONTEXT_V1','attempt_id':'SYNTHETIC_PROTOCOL_ONLY','nonce':'SYNTHETIC_NOT_A_REAL_LAUNCH_NONCE','queue_id':row['queue_id'],'row_index':0,'stage':'METADATA_IDENTITY_STATIC','scope_sha256':a.SCOPE_SHA,'frozen_row_sha256':a.digest(row),'admission_sha256':'0'*64,'input_fingerprint':'1'*64,'adapter_id':a.ADAPTER_ID,'adapter_profile':a.PROFILE,'adapter_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dependency_artifacts':[],'attempt_directory':str(attempt),'output_path':str(attempt/'RESULT.json')}
cp=attempt/'CONTEXT.json';cp.write_text(json.dumps(ctx))
args=types.SimpleNamespace(context_json=str(cp),scope_json=str(sp),row_index=0,output=str(attempt/'RESULT.json'))
out=a.run(args);assert out['status']=='HOLD'and out['stage_execution_complete']and out['attempt_id']==ctx['attempt_id']and out['nonce']==ctx['nonce']
assert all(out[x]is False for x in ['qualification_granted','historical_queue_mutated','gpu_executed','simulation_executed'])
assert any(x['path']==str(cp)for x in out['inputs'])and any(x['path']==str(sp)for x in out['inputs'])
tests=[{'case':'full_protocol_raw_io_real_RESULT_write','status':'PASS','scope':'SYNTHETIC_ONLY_NOT_PRODUCTION161','read_files':len(out['inputs'])}]
for name,key,value in [('wrong_adapter_profile','adapter_profile','UNKNOWN'),('wrong_scope_sha','scope_sha256','0'*64),('wrong_frozen_row','frozen_row_sha256','0'*64),('wrong_output','output_path',str(attempt/'FORBIDDEN.json'))]:
 bad=dict(ctx);bad[key]=value;cp.write_text(json.dumps(bad))
 try:a.run(args)
 except ValueError as e:tests.append({'case':name,'status':'REJECTED','reason':str(e)})
 else:raise AssertionError('negative accepted '+name)
result={'schema':'AUTO161_SYNTHETIC_FULL_PROTOCOL_FIXTURE_V1','status':'PASS','tests':tests,'test_count':len(tests),'production161_run':False,'production_adapter_or_authority_mutated':False,'GPU_or_simulation':False,'nonce_output_to_stdout':False}
(T/'PROTOCOL_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','tests':len(tests),'production161_run':False}))

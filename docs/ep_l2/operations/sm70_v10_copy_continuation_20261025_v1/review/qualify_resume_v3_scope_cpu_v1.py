"""CPU-only exact-AST scope branch and inheritance proof; no engine import/main/Source/driver/production lock."""
from pathlib import Path
import ast,json,hashlib,types
N=Path('/root/data/closed_audit_offload_independent_review_20261025_v1');W=N/'resume_v3_scope_cpu_A1';W.mkdir(exist_ok=False);T=Path('/root/data/shared_sm70_trace_library_20261024_v1/tools');v2=(T/'resume_archive_copy_only_v2.py').read_text();v3=(T/'resume_archive_copy_only_v3.py').read_text()
def defs(s):return{n.name:ast.get_source_segment(s,n)for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
a,b=defs(v2),defs(v3);assert all(a[k]==b[k]for k in a if k!='main');node=next(n for n in ast.walk(ast.parse(v3))if isinstance(n,ast.FunctionDef)and n.name=='preflight')
R=W/'synthetic_R';(R/'tools').mkdir(parents=True);(R/'control').mkdir();eh=hashlib.sha256(b'engine-fixture').hexdigest();dh=hashlib.sha256(b'driver-fixture').hexdigest();(R/'tools/library_copy_v10.py').write_bytes(b'engine-fixture');(R/'tools/transfer_batches_v10.py').write_bytes(b'driver-fixture');(R/'control/ENGINE_V10_PROMOTION.json').write_text(json.dumps({'status':'PASS_ROOT_APPROVED_COPY_ONLY_V10_AT_CLOSED_BATCH_BOUNDARY','engine_sha256':eh}))
old={'source_backend':'archive','source_host':'174','archive_path':'DO_NOT_TOUCH_OLD174_SOURCE','archive_identity':{}};new={'source_backend':'archive','source_host':'174-new','archive_path':'synthetic_pending_native_archive','archive_identity':{'fixture':1}}
for key,d in [('old',old),('new',new)]:(W/(key+'.json')).write_text(json.dumps(d))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();batches=[{'id':'89eb4fdd795fad40be6c','manifest':str(W/'old.json'),'sha256':sha(W/'old.json')},{'id':'2dcf6422136b02adcc6d','manifest':str(W/'new.json'),'sha256':sha(W/'new.json')}];manifest_list=W/'batches.json';manifest_list.write_text(json.dumps(batches));(R/'control/BATCH_89eb4fdd795fad40be6c.json').write_text('{}');called=[];validated=[]
def identity(path):
 assert path=='synthetic_pending_native_archive','old Source was touched';called.append(path);return{'fixture':1}
def need(x,msg):
 if not x:raise RuntimeError(msg)
scope=dict(R=R,STOP_REQUESTED=False,sha=sha,manifest_list=manifest_list,list_sha=sha(manifest_list),EXPECTED_ENGINE=eh,EXPECTED_DRIVER=dh,json=json,Path=Path,need=need,guard=lambda force:{'SSD_free_bytes':1000*2**30,'required_SSD_bytes':10*2**30},engine=types.SimpleNamespace(identity=identity,same_source=lambda x,y:x==y),validate_one_batch=lambda batch,m:validated.append(batch['id']))
exec(compile(ast.Module([node],type_ignores=[]),'exact_nested_preflight','exec'),scope);scope['preflight']();assert called==['synthetic_pending_native_archive']and validated==['89eb4fdd795fad40be6c']
out={'status':'PASS_EXACT_AST_PENDING_AND_HISTORICAL_SCOPE_ONLY','resume_sha256':sha(T/'resume_archive_copy_only_v3.py'),'all_V2_top_level_functions_except_main_byte_identical':[k for k in a if k!='main'],'old174_identity_calls':0,'pending_native_identity_calls':1,'completed_chain_validator_calls':validated,'old_batch_validator_is_injected_boundary_not_actualNAS_proof':True,'Source_driver_or_main_started':False,'production_lock_used':False};p=W/'QUALIFICATION.json';p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'path':str(p),'sha256':sha(p)}))

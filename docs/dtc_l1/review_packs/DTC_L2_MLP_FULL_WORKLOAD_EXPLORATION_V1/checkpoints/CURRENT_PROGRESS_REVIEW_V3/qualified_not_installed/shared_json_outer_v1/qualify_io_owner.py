from pathlib import Path as P
import importlib.util,json,hashlib,types,tempfile,sys,copy
B=P(__file__).parent;REAL=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
report=read(B/'NATIVE_PREFIX_PADDING.json');fixture=P(report['fixture']);intent=read(next((fixture/'control/qualification_ledger').glob('*.INTENT.json')));out=P(intent['output']);snapshot=read(out/'SHARED_JSON_IO_SNAPSHOT.json');cfg=snapshot['config'];q=dict(additional_operational_overlays={'SHARED_JSON_IO_OUTER_V1':snapshot['operational_overlay_record']});front=load('cpu_owner_outer',B/'io_frontend.py');owner=load('cpu_owner_adapter',B/'io_owner.py');res=load('cpu_owner_real_resource',REAL/'tools/l2_resources.py');consumer=load('cpu_owner_real_consumer',REAL/'tools/l2_results.py');proof=read(out/'PADDING_EXTRA_STRICT.json');oldproof=dict(performance_accepted=True,additional_padding_admission_strict=dict(proof,sidecar_path=str(out/'PADDING_EXTRA_STRICT.json'),sidecar_sha256=sha(out/'PADDING_EXTRA_STRICT.json')))
# Real original consumer module/put; previous strict loader is an explicit CPU
# double for the preexisting base+B5 AND result, never scientific acceptance.
oldload=consumer.load
consumer.load=lambda name,file:types.SimpleNamespace(__file__=str(REAL/'tools/l2_strict.py'),terminal=lambda c:copy.deepcopy(oldproof))if P(file).name=='l2_strict.py'else oldload(name,file)
real_owner_load=owner.load
def fixture_owner_load(name,path):
 m=real_owner_load(name,path)
 if name=='owner_io_extra_strict':m.R=fixture
 return m
owner.load=fixture_owner_load;claims={};pool=object();frame=types.SimpleNamespace(f_locals=dict(engine=types.SimpleNamespace(registered=lambda:(None,None,q,None)),res=res,consumer=consumer,pool=pool,claims=claims));checks=[]
def ck(n,v):assert v,n;checks.append(n)
def denied(fn):
 try:fn()
 except (AssertionError,KeyError,ValueError):return True
 return False
installed=owner.install_on_frame(frame,cfg,fixture=True);ck('existing_owner_instances_pool_claims_preserved',installed['pool_object_id']==id(pool)and installed['claims_object_id']==id(claims)and hasattr(res,'_SHARED_JSON_PUBLICATION_V1')and hasattr(consumer,'_SHARED_JSON_PUBLICATION_V1'))
with tempfile.TemporaryDirectory()as tmp:
 p=P(tmp)/'result.json';value={'payload':'x'*30000};consumer.put(p,value,True)
 try:consumer.put(p,{'wrong':1},True);exclusive=False
 except FileExistsError:exclusive=True
 ck('real_consumer_exclusive_put_atomic_noreplace_same_bytes',exclusive and p.read_bytes()==(json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
 consumer.put(p,{'v':1},False);consumer.put(p,{'v':2},False);ck('real_consumer_nonexclusive_put_original_behavior',read(p)=={'v':2})
mod=consumer.load('strict','l2_strict.py');combined=mod.terminal(intent['cohort']);ck('consumer_original_B5_IO_AND_returns_IO_sidecar',combined['additional_shared_json_io_strict']['status']=='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT');oldproof['performance_accepted']=False;ck('consumer_never_promotes_original_strict_false',denied(lambda:mod.terminal(intent['cohort'])))
base=['experiment','prepare','E2-DTCL2MLP-CPU-DH-P0-V1','--project','DTC_L1'];positive=front.parse(base)[1]is False and front.parse(base+['--padding-only-admission-v1'])[1]is True
bad=[base+['--unknown'],base+['--padding-only-admission-v1']*2,['experiment','prepare','E2-EP-CPU','--project','DTC_L1'],base[:-1]+['EP_L2']];ck('CLI_padding_noflag_exact_routes_unknown_EP_duplicate_rejected',positive and all(denied(lambda a=a:front.parse(a))for a in bad))
old_front_load=front.load;archive_args=['result','archive','E2-DTCL2MLP-CPU-ARCHIVE'];front.load=lambda name,path:types.SimpleNamespace(main=lambda args:dict(delegated_unchanged=args));ck('legacy_result_archive_delegates_unchanged_even_new_admission_held',front.main(archive_args)['delegated_unchanged']==archive_args);front.load=old_front_load
badcfg=copy.deepcopy(cfg);badcfg['status']='HOLD';badq=copy.deepcopy(q);badq['additional_operational_overlays']['SHARED_JSON_IO_OUTER_V1']['source_sha256']='0'*64;ck('HOLD_or_registry_pin_mismatch_rejects',denied(lambda:front.validate(badcfg,q))and denied(lambda:front.validate(cfg,badq)))
qa=dict(status='PASS',checks=checks,passed=len(checks),qualified_sources=report['qualified_sources'],expected_pins=report['expected_pins'],production_mutations=0,model_starts=0,model_signals=0,synthetic_previous_base_B5_terminal_proof=True)
(B/'OWNER_QUALIFICATION.json').write_text(json.dumps(qa,sort_keys=True,indent=2)+'\n');print(json.dumps(qa))

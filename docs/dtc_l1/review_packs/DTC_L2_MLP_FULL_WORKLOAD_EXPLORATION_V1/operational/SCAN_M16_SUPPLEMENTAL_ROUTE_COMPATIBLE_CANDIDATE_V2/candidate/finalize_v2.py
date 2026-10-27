import datetime,hashlib,json,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent;V1=HERE.with_name('supplemental_scan_m16_v1')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):P(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
old_manifest=read(V1/'DELIVERY_MANIFEST.json');assert sha(V1/'DELIVERY_MANIFEST.json')=='cb8ca331cd8db43cfec01f4ba816d6eb9e6d0961433bf957414f6587dcbaa077'
for name,pin in old_manifest['files'].items():assert sha(V1/name)==pin['sha256'],'V1 sealed bytes changed '+name
all_v1={str(p.relative_to(V1)):sha(p)for p in V1.rglob('*')if p.is_file()}
old=read(V1/'CANDIDATE_PLAN.json');new=read(HERE/'CANDIDATE_PLAN.json');diff=[]
def compare(a,b,path=''):
 if type(a)is not type(b):diff.append(dict(path=path,old_type=type(a).__name__,new_type=type(b).__name__));return
 if isinstance(a,dict):
  for key in sorted(set(a)|set(b)):
   if key not in a or key not in b:diff.append(dict(path=path+'/'+key,change='ADDED'if key not in a else'REMOVED'))
   else:compare(a[key],b[key],path+'/'+key)
 elif isinstance(a,list):
  if a!=b:diff.append(dict(path=path,change='LIST_CHANGED',old_length=len(a),new_length=len(b)))
 elif a!=b:diff.append(dict(path=path,old=a,new=b))
compare(old,new)
import supplemental_trial as module
assert sha(HERE/'supplemental_trial.py')==sha(V1/'supplemental_trial.py')=='b39fb919f4bb706d05bf10f44250c82a1b34e0701e009f78563e1e0680379127'
assert module.scientific(old['new_spec'])==module.scientific(new['new_spec'])and old['scientific_identity_sha256']==new['scientific_identity_sha256']
oldpins={p['path']:p['sha256']for p in old['source_and_evidence_pins']};newpins={p['path']:p['sha256']for p in new['source_and_evidence_pins']}
pd=dict(changed=[dict(path=p,old=oldpins[p],new=newpins[p])for p in sorted(oldpins.keys()&newpins.keys())if oldpins[p]!=newpins[p]],
 removed=[dict(path=p,sha256=oldpins[p])for p in sorted(oldpins.keys()-newpins.keys())],added=[dict(path=p,sha256=newpins[p])for p in sorted(newpins.keys()-oldpins.keys())])
exact=dict(schema='SUPPLEMENTAL_SCAN_M16_CANDIDATE_V1_TO_V2_DIFF',plan_changes=diff,source_pin_changes=pd,
 unchanged_transaction_module_sha256=sha(HERE/'supplemental_trial.py'),scientific_identity_unchanged=True,
 scientific_identity_sha256=new['scientific_identity_sha256'],all270_options_and_configs_unchanged=True,
 V1_manifest_sha256=sha(V1/'DELIVERY_MANIFEST.json'),V1_sealed_files_preserved=True,V1_all_file_byte_seal=all_v1)
put(HERE/'PRECISE_DIFF.json',exact)
cpu=read(HERE/'CPU_QUALIFICATION.json');route=read(HERE/'ROUTE_CPU_QUALIFICATION.json');actual=read(HERE/'READONLY_INTEGRATION.json')
assert cpu['status']=='PASS'and cpu['count']==26 and cpu['source_sha256']==sha(HERE/'supplemental_trial.py')
assert route['status']=='PASS'and route['checks']==4 and route['source_sha256']==sha(HERE/'route_qualification.py')
assert actual['status']=='PASS_REAL_READONLY_SUPPLEMENTAL_INTERFACE_CHAIN'and actual['plan_sha256']==sha(HERE/'CANDIDATE_PLAN.json')
for pin in new['source_and_evidence_pins']:assert sha(pin['path'])==pin['sha256']
assert all(sha(V1/name)==value for name,value in all_v1.items())
files={p.name:dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in HERE.iterdir()if p.is_file()and p.name!='DELIVERY_MANIFEST.json'}
out=dict(schema='DTC_L2_MLP_SUPPLEMENTAL_SCAN_M16_ROUTE_COMPATIBLE_V2_DELIVERY',status='CPU26_ROUTE4_AND_REAL_READONLY_QUALIFIED_NOT_REGISTERED',
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,plan_sha256=sha(HERE/'CANDIDATE_PLAN.json'),
 module_sha256=sha(HERE/'supplemental_trial.py'),native_entry_sha256=route['current_route']['native_entry_sha256'],
 proposed_cohort=new['new_cohort'],existing_grants=344,proposed_new_grants=1,primary_cells=350,
 registration_callback='route_qualification.route_lineage_verifier',V1_all_sealed_files_preserved=True,
 automatic_union=False,primary_results_replaced=False,production_registered=False,production_installed=False,
 model_starts=0,signals=0,production_mutations=0)
put(HERE/'DELIVERY_MANIFEST.json',out)
print(json.dumps(dict(status=out['status'],manifest_sha256=sha(HERE/'DELIVERY_MANIFEST.json'),plan_sha256=out['plan_sha256'],
 module_sha256=out['module_sha256'],route_qa_sha256=sha(HERE/'ROUTE_CPU_QUALIFICATION.json'),diff_sha256=sha(HERE/'PRECISE_DIFF.json'))))

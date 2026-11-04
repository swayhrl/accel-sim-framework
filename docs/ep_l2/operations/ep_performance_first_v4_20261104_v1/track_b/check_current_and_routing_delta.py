"""Final current dependency reopen, routing delta, and stage gates; no model starts."""
from pathlib import Path
import json,hashlib,sys,os,subprocess,copy,importlib.util,ast,difflib
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');O=Path(__file__).resolve().parent;R=O/'private_runtime';V=P/'research/performance_first_v3_20261104_v1/activation_20261104_v1';H=V/'agent_b_formal/runtime';F=O/'routing_stage_delta';F.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def put(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def mod(n,p):sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
sys.path.insert(0,str(R));engine=mod('final_delta_engine',R/'ep_perf_native_wv_modes_draft.py');w=read(O/'proposal/specs/W_ONLY.json');wv=read(O/'proposal/specs/WV_ZERO_RO.json')
# Reopen every exact runtime pin and explicit source/config/qualification ref; Trace bodies never rehashed.
pins={};skip=[]
def gather(x):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str)and x.get('sha256'):
   if x['path'].startswith('/root/share/mnt164/')and Path(x['path']).name!='kernelslist.g':skip.append(dict(path=x['path'],sha256=x['sha256'],reason='large Trace body preserved; stat-only'))
   else:pins[x['path']]=x['sha256']
  for z in x.values():gather(z)
 elif isinstance(x,list):
  for z in x:gather(z)
for s in [w,wv]:
 pins.update(s['pinned_files']);gather(s);pins[s['binary_path']]=s['source_identity']['binary_sha256'];pins[s['static_library_path']]=s['source_identity']['archive_sha256']
for x in read(O/'SOURCEKEEP_PREIMAGES.json')['untouched_refs']:pins[x['path']]=x['sha256']
rows=[dict(path=p,expected_sha256=h,actual_sha256=sha(p),resolved_path=str(Path(p).resolve()),bytes=Path(p).stat().st_size)for p,h in sorted(pins.items())]
for x in rows:x['PASS']=x['expected_sha256']==x['actual_sha256']
source=[]
for k,c in [('core','core_source_commit'),('framework','framework_source_commit')]:
 repo=w['source_worktrees'][k];head=subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip();dirty=subprocess.check_output(['git','-C',repo,'status','--porcelain','--untracked-files=no'],text=True).strip();source.append(dict(role=k,path=repo,HEAD=head,expected=w['source_identity'][c],tracked_dirty=bool(dirty),PASS=head==w['source_identity'][c]and not dirty))
input_binding=read(w['input_binding_ref']['path']);stats=[]
for m in input_binding['members']:
 st=Path(m['path']).stat();stats.append(dict(path=m['path'],size=st.st_size,mtime_ns=st.st_mtime_ns,resolved_path=str(Path(m['path']).resolve()),PASS=st.st_size==m['size']and st.st_mtime_ns==m['mtime_ns']and str(Path(m['path']).resolve())==m['resolved_path'],body_rehashed=False))
proof=dict(status='PASS'if all(x['PASS']for x in rows+source+stats)else'FAIL',exact_reopened_pin_count=len(rows),rows=rows,source=source,input_stat_only=stats,large_Trace_rehash=False,domain=dict(native_boot_id=w['native_boot_id'],native_mount_namespace=w['native_mount_namespace'],current_boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),current_mount=os.readlink('/proc/self/ns/mnt')),Core_ELF_hardware282_unchanged=True)
put(O/'CURRENT_EXACT_DEPENDENCY_REOPEN.json',proof);assert proof['status']=='PASS'
# Actual private guard retains all original safe-core protections; only exact namespace differs.
g=mod('private_v4_route_guard',R/'native_route_guard_v3.py');oldg=(V/'agent_d_execution/native_route_guard_v3.py').read_text();assert (R/'native_route_guard_v3.py').read_text()==oldg.replace('EP_PERF_PFV3_','EP_PERF_PFV4_');assert sha(R/'safe_native_core_v3.py')==sha(V/'agent_d_execution/safe_native_core_v3.py')
route=read(P/'execution_vector1700_decomposition_v3_20261104_v1/vector1700/control/NATIVE_ENTRY_ROUTE_V3.json');route.update(TEST_ONLY=True,scope='PRIVATE_READ_ONLY_ROUTE_FIXTURE_NOT_INSTALLATION',goal=engine.GOAL,entry_ref=ref(R/'native_vector1700_v4'),frontend_ref=ref(R/'ep_perf_frontend.py'),guard_module_ref=ref(R/'native_route_guard_v3.py'),exact_cohorts=sorted([w['cohort'],wv['cohort']]),owned_runtime_pins=[ref(p)for p in R.rglob('*')if p.is_file()and '__pycache__'not in p.parts]);p=F/'SYNTHETIC_PRIVATE_ROUTE_NO_SCIENCE_AUTHORITY.json';put(p,route);route_proof=g.validate_current(p)
wrong=copy.deepcopy(route);wrong['exact_cohorts']=['EP_PERF_PFV3_VECTOR4M_W_ONLY_1700_V1'];put(F/'WRONG_NAMESPACE_ROUTE.json',wrong)
try:g.validate_current(F/'WRONG_NAMESPACE_ROUTE.json');raise AssertionError('wrong namespace accepted')
except Exception as e:wrong_proof=dict(status='PASS',rejected=str(e))
# Call actual executable entry: absent fresh registration must reject before model launch.
entry=subprocess.run([str(R/'native_vector1700_v4'),'experiment','prepare',w['cohort'],'--project','EP_L2'],capture_output=True,text=True)
assert entry.returncode==2 and 'HOLD'in entry.stderr
put(F/'ROUTING_DELTA_RECEIPT.json',dict(status='PASS',route_guard_positive=route_proof,wrong_namespace=wrong_proof,actual_entry_unauthorized_rejected=dict(returncode=entry.returncode,stderr=entry.stderr),shared_native_writes=0,registry_writes=0,model_starts=0,safe_core_byte_identical=True,guard_only_change='exact V4 cohort prefix in private copy'))
# Reuse unchanged accepted_cell to enforce W_ONLY acceptance/archive/two restores before WV.
engine.spec_path=lambda c:O/'proposal/specs'/('W_ONLY.json'if c==w['cohort']else'WV_ZERO_RO.json')
point=dict(TEST_ONLY=True,status='EP_FULL_PERF_APPLICATION_ACCEPTED',hardware_drained=True,cohort=w['cohort'],mode=w['mode'],uuid='CPU_ROUTE_GATE_FIXTURE_ONLY',source_identity=w['source_identity'],input_identity_sha256=w['input_identity_sha256'],cycles=1,spec_ref=ref(engine.spec_path(w['cohort'])))
put(F/'SYNTHETIC_ACCEPTED_POINT.json',point)
archive=dict(TEST_ONLY=True,status='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS',cohort=w['cohort'],uuid=point['uuid'],source_keep=True,archive_ref=dict(path='/root/share/mnt164/TEST_ONLY_NO_ARCHIVE_BODY',sha256='0'*64),native_restores=[dict(status='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS',archive_sha256='0'*64,restore_label=n,target='/root/data/TEST_ONLY_'+n)for n in ['FIRST','INDEPENDENT']]);put(F/'SYNTHETIC_ARCHIVE_RECEIPT.json',archive)
row=dict(state='CLOSED_ACCEPTED',uuid=point['uuid'],accepted_point_ref=ref(F/'SYNTHETIC_ACCEPTED_POINT.json'),archive_receipt_ref=ref(F/'SYNTHETIC_ARCHIVE_RECEIPT.json'));q=dict(admitted_specs={w['cohort']:sha(engine.spec_path(w['cohort']))},consumed={w['cohort']:row});stage=[]
for label in ['unaccepted','one_restore','wrong_archive_SHA','missing_full_SHA','same_restore_target','PASS']:
 qq=copy.deepcopy(q);aa=copy.deepcopy(archive)
 if label=='unaccepted':qq['consumed'][w['cohort']]['state']='CLOSED_UNACCEPTED'
 if label=='one_restore':aa['native_restores']=aa['native_restores'][:1]
 if label=='wrong_archive_SHA':aa['native_restores'][1]['archive_sha256']='1'*64
 if label=='missing_full_SHA':
  aa['archive_ref']['sha256']=None
  for rr in aa['native_restores']:rr['archive_sha256']=None
 if label=='same_restore_target':aa['native_restores'][1]['target']=aa['native_restores'][0]['target']
 put(F/'SYNTHETIC_STAGE_RECEIPT.json',aa);qq['consumed'][w['cohort']]['archive_receipt_ref']=ref(F/'SYNTHETIC_STAGE_RECEIPT.json')
 try:engine.staged_w_only_archive_release(wv,qq);assert label=='PASS';stage.append(dict(case=label,status='PASS',accepted=True))
 except RuntimeError as e:assert label!='PASS';stage.append(dict(case=label,status='PASS',accepted=False,reason=str(e)))
put(F/'STAGED_RELEASE_DELTA_RECEIPT.json',dict(status='PASS',synthetic_fixture_only=True,tests=stage,actual_model_starts=0,stage_gate_in_engine="if s['mode']=='WV_ZERO_RO': accepted_cell(W_ONLY,s,q)",no_application_acceptance_claim=True))
changes=[]
for src,dst in [(H/n,R/n)for n in ['ep_perf_native_wv_modes_draft.py','ep_perf_common_v2.py','mode_contract.py','ep_perf_frontend.py','ep_perf_archive.py']]+[(V/'agent_d_execution/native_route_guard_v3.py',R/'native_route_guard_v3.py'),(V/'native/native_v3.py',R/'native_v4.py'),(V/'agent_c_resources/resources_vector1700.py',R/'resources_vector1700_v4.py')]:changes.append(''.join(difflib.unified_diff(src.read_text().splitlines(True),dst.read_text().splitlines(True),fromfile=str(src),tofile=str(dst))))
(O/'PRIVATE_RUNTIME_EXACT_DIFF.patch').write_text('\n'.join(changes))
print(json.dumps(dict(status='PASS',current_pins=len(rows),source_heads=source,route_guard=route_proof['status'],actual_entry_unauthorized=entry.returncode,stage_tests=stage)))

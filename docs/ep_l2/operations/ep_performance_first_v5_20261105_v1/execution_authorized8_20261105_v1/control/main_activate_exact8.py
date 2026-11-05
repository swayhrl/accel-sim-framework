"""Main only: register exact A3+B2+D3 and additive Native. Never forks a model."""
import pathlib,json,hashlib,copy,os,fcntl,subprocess,datetime,uuid,argparse
P=pathlib.Path;C=P(__file__).resolve().parent;V=C.parent.parent;J=V.parent.parent
N=P('/root/data/ep_l2_dtc_l1_native_v2');REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
ROOTS={'A':V/'track_a_wv/host_private_candidate_v1/main_materialized/37e5a2db776190ee3f74/execution','B':V/'track_b_fullf/host_private_candidate_v1/execution','D':V/'track_d_workloads/three_mm/execution'}
BUDGET={'A':3,'B':2,'D':3};WALL={'A':28800,'B':7200,'D':259200}
def need(x,m):
 if not x:raise ValueError(m)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def pin(r):need(sha(r['path'])==r['sha256'],'reference drift '+r['path']);return read(r['path'])
def put(p,x,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
 t=p if exclusive else p.with_name('.'+p.name+'.'+str(uuid.uuid4()))
 with t.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 if not exclusive:os.replace(t,p)
 d=os.open(p.parent,os.O_RDONLY);os.fsync(d);os.close(d);return ref(p)
def pre(p):
 p=P(p)
 if not p.exists():return
 dst=C/'FORMAL_PREIMAGES'/sha(p)/p.name;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():dst.write_bytes(p.read_bytes())
def left(q):
 if 'remaining'in q:return q['remaining']
 x=q.get('consumed',0);return max(0,q.get('budget',0)-(x if type(x)is int else len(x)))
def main(apply):
 auth=read(C/'USER_AUTHORIZATION.json');fam={f['name']:f for f in auth['families']}
 need(auth['explicit_user_approval']and auth['approved_total_launches']==8 and auth['all_eight_independently_released'],'user exact8')
 need(set(fam)==set(ROOTS)and {g:f['approved_launches']for g,f in fam.items()}==BUDGET,'budgets')
 allspec={}
 for g,root in ROOTS.items():
  specs=[read(p)for p in sorted(root.glob('cases/*/control/FROZEN_SPEC.json'))];need(len(specs)==BUDGET[g],'point count')
  for s in specs:
   need(s['source_identity']==fam[g]['Source5']and s['science_request_id']==fam[g]['request'],'identity')
   need(s['limits']['wall_seconds']==WALL[g]and len(s['expected_effective_options'])==(282 if g=='D'else 283),'Host/schema delta not applied')
   need(s['limits']['RSS_bytes']==(10 if g=='D'else 2)*(1<<30)and s['limits']['AS_bytes']==(24 if g=='D'else 10)*(1<<30),'RAM limits changed')
   need(s['native_boot_id']==P('/proc/sys/kernel/random/boot_id').read_text().strip()and s['native_mount_namespace']==os.readlink('/proc/self/ns/mnt'),'native domain')
   for p,h in s['pinned_files'].items():need(sha(p)==h,'dependency drift '+p)
   a=pin(s['Main_scientific_launch_authorization']);need(a['explicit_user_approval']and a['approved_launches']==BUDGET[g]and a['allowed_cohorts']==fam[g]['allowed_cohorts']and a['Source5']==s['source_identity'],'family approval')
   need(a['user_request_ref']==ref(root/'control/USER_REQUEST.txt'),'private user request identity')
  allspec[g]=specs
 if not apply:print(json.dumps(dict(status='MAIN_EXACT8_PREFLIGHT_NO_WRITES',points=8,starts=0)));return
 need(not(C/'MAIN_FORMAL_NATIVE_INSTALLATION_RECEIPT.json').exists(),'no repeated activation')
 locks=[J/'execution_v2_20261103_v1/control/GLOBAL_MAIN_SUCCESSOR_OWNERSHIP.lock',J/'execution_performance_first_20261103_v1/control/ADMISSION.lock',N/'control/science_authority/REGISTRY_UPDATE.lock',N/'control/science_authority/NATIVE_ROUTE_UPDATE.lock']
 handles=[]
 try:
  for p in locks:
   h=p.open('a+b');handles.append(h);fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
  reg=read(REG);epoch=read(EPOCH);need(sha(REG)==epoch['native_registry_sha256']and epoch['state']=='NATIVE_SCIENCE_ACTIVE','unstable authority');before=copy.deepcopy(reg)
  need(all(f['request']not in reg['registered_future_requests']for f in fam.values()),'request already registered')
  old=(N/'bin/native').read_bytes();nativepre=C/'CURRENT_NATIVE_PREIMAGE.sh';need(not nativepre.exists(),'retained partial activation requires diagnosis');nativepre.write_bytes(old)
  prefix=['#!/bin/sh','set -eu','# EP-MAIN authorized V5 exact8; all previous bytes follow unchanged.']
  for g in ['B','A','D']:
   entry=ROOTS[g].parent/'runtime'/('native_b1'if g=='B'else'native_request3')
   patterns='|'.join(op+':'+c for c in fam[g]['allowed_cohorts']for op in ['experiment','result'])
   interp='/bin/sh'if entry.read_bytes().startswith(b'#!/bin/sh\n')else'/usr/bin/python3 -B'
   prefix+=['if [ "$#" -ge 3 ]; then',' case "$1:$3" in','  '+patterns+')','   exec '+interp+' '+str(entry)+' "$@"','   ;;',' esac','fi']
  candidate=C/'GLOBAL_NATIVE_EXACT8_WITH_ALL_PRIOR_BYTES.sh';candidate.write_bytes(('\n'.join(prefix)+'\n').encode()+old)
  z=subprocess.run(['/bin/sh','-n',str(candidate)],capture_output=True,text=True);need(z.returncode==0,'Native shell syntax '+z.stderr);need(candidate.read_bytes().endswith(old),'prior bytes')
  groups={};points=[];diffs=[]
  for g,root in ROOTS.items():
   rt=root.parent/'runtime';f=fam[g];contract=C/('SHARED_ROUTE_CONTRACT_'+g+'_V5.json')
   put(contract,dict(schema='EP_MAIN_PFV5_B1_SHARED_ROUTE_CONTRACT_V1'if g=='B'else'EP_MAIN_V3_SHARED_ROUTE_CONTRACT_V1',installed_baseline_ref=ref(candidate),reviewed_foreign_insertions=[],Main_authorization_ref=ref(C/'USER_AUTHORIZATION.json'),current_foreign_preimage_ref=ref(nativepre)))
   specs=[];admitted={}
   for s0 in allspec[g]:
    s=copy.deepcopy(s0);cohort=s['cohort'];sp=root/'cases'/cohort/'control/FROZEN_SPEC.json';pre(sp)
    s.update(status='USER_APPROVED_MAIN_BOUND_FRESH_V5_EXACT8',scientific_scope_activated=True,scientific_launch_permission=True,launch_permission=True,Main_review_status='MAIN_REVIEWED_USER_AUTHORIZED_EXACT8',parent_scientific_authorization_ref=ref(C/'USER_AUTHORIZATION.json'))
    changed=[k for k in s if s.get(k)!=s0.get(k)];need(set(changed)<=set(['status','scientific_scope_activated','scientific_launch_permission','launch_permission','Main_review_status','parent_scientific_authorization_ref']),'only activation metadata')
    check='import json,sys;sys.path.insert(0,sys.argv[1]);import ep_perf_native_wv_modes_draft as e;e.validate_spec_contract(json.load(sys.stdin));print(1)'
    z=subprocess.run(['/usr/bin/python3','-B','-c',check,str(rt)],input=json.dumps(s),text=True,capture_output=True,timeout=90);need(z.returncode==0,'final schema '+z.stderr[-2000:])
    put(sp,s);admitted[cohort]=sha(sp);specs.append(s);diffs.append(dict(cohort=cohort,fields=changed,science_identity_unchanged=True))
    points.append(dict(group=g,cohort=cohort,mode=s['mode'],priority=10 if g=='B' else 20 if g=='A' else 30,spec_ref=ref(sp),host_limits=s['limits'],estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],independent_release=True))
   s=specs[0];rp=root/'control'/('NATIVE_ENTRY_ROUTE_V3.json'if g=='B'else'NATIVE_ENTRY_ROUTE_V4.json');route=read(rp)if rp.exists()else {};pre(rp)
   owned={}
   for r in route.get('owned_runtime_pins',[]):need(sha(r['path'])==r['sha256'],'owned drift '+r['path']);owned[r['path']]=ref(r['path'])
   for t in specs:
    for path,h in t['pinned_files'].items():
     need(sha(path)==h,'full owned frozen dependency drift '+path);owned[path]=dict(path=path,sha256=h)
   for p in list(rt.glob('*.py'))+[rt/('native_b1'if g=='B'else'native_request3')]:owned[str(p)]=ref(p)
   for t in specs:
    for k in ['host_qualification_ref','host_engine_ref','host_common_ref','resource_module_ref','native_route_guard_ref','Main_scientific_launch_authorization']:owned[t[k]['path']]=t[k]
   route.update(goal=f['request'],status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',approved_by='EP-MAIN',scientific_scope_activated=True,install_authorization=True,Main_user_authorization_ref=s['Main_scientific_launch_authorization'],entry_ref=s['native_entry_ref'],frontend_ref=ref(rt/'ep_perf_frontend.py'),guard_module_ref=s['native_route_guard_ref'],global_shared_native_ref=dict(path=str(N/'bin/native'),sha256=sha(candidate)),shared_route_contract_ref=ref(contract),exact_cohorts=f['allowed_cohorts'],owned_runtime_pins=list(owned.values()));put(rp,route)
   q=dict(request=f['request'],request_id=f['request'],owner='EP-MAIN',project='EP_L2',budget=BUDGET[g],remaining=BUDGET[g],consumed={},admitted_specs=admitted,runtime_versions={s['host_engine_ref']['sha256']:dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref'])},authorization_ref=s['Main_scientific_launch_authorization'],parent_authorization_ref=ref(C/'USER_AUTHORIZATION.json'),source_identity=s['source_identity'],allowed_cohorts=f['allowed_cohorts'],native_entry_ref=s['native_entry_ref'],native_qualification_ref=ref(rp),state='ARMED',reserved_write_bytes=0,source_keep=True,automatic_retry=False,refund=False,independent_release=True,resource_group_id=f['request'],global_model_concurrency_authorized=10,global_model_concurrency_qualified=10,registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
   groups[g]=dict(request_id=f['request'],budget=BUDGET[g],data_root=str(root),runtime_root=str(rt),native_entry_ref=s['native_entry_ref'],route_ref=ref(rp),route_file=rp.name,registry_row=q)
   cp=root/'control/DISPATCH_CLAIMS.json'
   if cp.exists():need(read(cp)==dict(claims={}),'old claims')
   else:put(cp,dict(claims={}))
  payload=dict(schema='EP_MAIN_PFV5_EXACT8_ACTIVATION_PAYLOAD_V1',user_authorization_ref=ref(C/'USER_AUTHORIZATION.json'),groups=groups,points=points,global_native_candidate_ref=ref(candidate),scientific_starts=0,all_eight_independent=True)
  put(C/'EXACT8_ACTIVATION_PAYLOAD.json',payload,True);put(C/'MAIN_FINAL_SPEC_ACTIVATION_DIFFERENCES.json',dict(differences=diffs,starts=0),True)
  for p in [REG,EPOCH,N/'bin/native']:pre(p)
  for p in [REG,EPOCH]:
   d=N/'control/science_authority/request_history'/(p.stem+'.'+sha(p)+'.json')
   if not d.exists():d.write_bytes(p.read_bytes())
  need((N/'bin/native').read_bytes()==old,'Native CAS moved')
  t=N/'bin'/('.native.PFV5.'+str(uuid.uuid4()))
  with t.open('xb')as z:z.write(candidate.read_bytes());z.flush();os.fsync(z.fileno())
  t.chmod((N/'bin/native').stat().st_mode&0o777);need((N/'bin/native').read_bytes()==old,'Native CAS moved before replace');os.replace(t,N/'bin/native');fd=os.open(N/'bin',os.O_RDONLY);os.fsync(fd);os.close(fd)
  for g,q in groups.items():reg['registered_future_requests'][q['request_id']]=q['registry_row']
  need(all(reg['registered_future_requests'][k]==q for k,q in before['registered_future_requests'].items()),'previous row changed')
  need({k:x for k,x in reg.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']}=={k:x for k,x in before.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']},'old history changed')
  reg['new_scientific_budget_remaining']=sum(left(q)for q in reg['registered_future_requests'].values());put(REG,reg)
  epoch.update(native_registry_sha256=sha(REG),new_budget_remaining=reg['new_scientific_budget_remaining'],request_revision=dict(request_id=[f['request']for f in fam.values()],operation='EP_MAIN_USER_APPROVED_V5_REGISTER_3_2_3_EXACT8_ADDITIVE_NATIVE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));put(EPOCH,epoch)
  put(C/'MAIN_FORMAL_NATIVE_INSTALLATION_RECEIPT.json',dict(status='EXACT8_THREE_INDEPENDENT_SCOPES_REGISTERED_AND_NATIVE_INSTALLED',payload_ref=ref(C/'EXACT8_ACTIVATION_PAYLOAD.json'),registry_ref=ref(REG),epoch_ref=ref(EPOCH),native_ref=ref(N/'bin/native'),all_prior_rows_exact_preserved=True,all_prior_native_bytes_exact_suffix=True,scientific_starts=0),True)
 finally:
  for h in reversed(handles):h.close()
 print(json.dumps(dict(status='EXACT8_ARMED_NO_MODEL_START',payload_ref=ref(C/'EXACT8_ACTIVATION_PAYLOAD.json'))))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');o=a.parse_args();main(o.apply)

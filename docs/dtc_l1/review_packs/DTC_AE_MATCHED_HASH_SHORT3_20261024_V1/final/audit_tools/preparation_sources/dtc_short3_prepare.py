import pathlib,json,hashlib,csv,subprocess,os,time
P=pathlib.Path
T=P('/root/data/dtc_main_short3_20261024_v1'); A=P('/root/data/dtc_main_20261023_v1/ae_fair_v1'); N=P('/root/data/ep_l2_dtc_l1_native_v2')
F=P('/root/data/dtc_main_20261023_v1/accel-sim-framework')
REQUEST='DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1'
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(p,o):
 p=P(p)
 with p.open('x') as f:json.dump(o,f,indent=2,ensure_ascii=False);f.write('\n')
T.mkdir(exist_ok=False)
for d in ['control','tools','analysis','DTC/bin','DTC/env','DTC/control','DTC/run/results','DTC/run/recovery','DTC/run/tmp','DTC/run/cache']: (T/d).mkdir(parents=True,exist_ok=True)
subprocess.run(['git','-C',str(F),'worktree','add','-b','hrl/dtc-aefair-short3-174new-20261024-v1',str(T/'docs-worktree'),'HEAD'],check=True,stdout=subprocess.DEVNULL)
for name,target in [('core',A/'core'),('framework',A/'framework'),('common-lib',N/'common-lib'),('tools/bin',A/'tools/bin'),('tools/lib',A/'tools/lib'),('DTC/env/lib',A/'DTC/env/lib')]: (T/name).symlink_to(target,target_is_directory=True)
os.link(A/'DTC/bin/accel-sim.out',T/'DTC/bin/accel-sim.out')
ledger=N/'control/qualification_ledger'/REQUEST;ledger.mkdir(exist_ok=False)
(ledger/'NATIVE_QUALIFICATION.lock').symlink_to(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')
(T/'control/qualification_ledger').symlink_to(ledger,target_is_directory=True)
(T/'control/CURRENT_SCIENCE_EPOCH.json').symlink_to(N/'control/CURRENT_SCIENCE_EPOCH.json')
for name in ['NATIVE_SCIENCE_REGISTRY.json']:(T/'control'/('PREIMAGE_'+name)).write_bytes((N/'control/science_authority'/name).read_bytes())
(T/'control/PREIMAGE_CURRENT_SCIENCE_EPOCH.json').write_bytes((N/'control/CURRENT_SCIENCE_EPOCH.json').read_bytes())
(T/'control/NATIVE_ENTRY_PREIMAGE').write_bytes((N/'bin/native').read_bytes())
audit=F/'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/trace_body_v1/KERNEL_BODY_AUDIT.tsv'
rows=list(csv.DictReader(audit.open(),delimiter='\t'))
catalog=P('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json')
assets=json.loads(catalog.read_text())['assets']
oldrows=json.loads((F/'docs/dtc_l1/review_packs/DTC_MAIN_NATIVE_ONBOARDING_20261023_V1/ORIGINAL44_ROW_INTAKE.json').read_text())['rows']
selected={}; proofs=[]
for w,asset in [('NN','DTC_LEGACY_NN'),('DWT2D','DTC_DWT2D'),('MRI-Q','DTC_MRI_Q')]:
 a=next(a for a in assets if a['asset_id']==asset);rs=sorted([r for r in rows if r['workload'].lower()==w.lower()],key=lambda r:int(r['ordinal']))
 assert len(rs)==len(a['ordered_kernel_members'])>0
 assert [P(r['path']).name for r in rs]==a['ordered_kernel_members']
 assert all(r['coverage']=='ALL_DECLARED_WARPS_AND_FULL_GRID_WITH_TERMINAL_EXIT' and r['binary_version']=='70' for r in rs)
 mp={r['relative_path']:r for r in a['members']};members=[]
 assert P(a['source_root']).resolve()==P(a['mount_tree']).resolve()
 for r in rs:assert r['sha256']==mp[P(r['path']).name]['sha256']
 for m in a['members']:
  p=P(a['source_root'])/m['relative_path'];st=p.stat();assert [st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns]==m['verified_tree_identity']
  start=time.monotonic();h=sha(p);assert h==m['sha256']
  members.append({'path':str(p),'sha256':h,'identity':[st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns]})
  print('HASH_VERIFIED',w,m['relative_path'],st.st_size,round(time.monotonic()-start,3),flush=True)
 commands=(P(a['source_root'])/a['entry_name']).read_text().splitlines()
 prior=[r for r in oldrows if r['workload']==w]
 insns=sum(int(r['active_thread_instructions']) for r in rs);ctas=sum(int(r['complete_ctas']) for r in rs)
 assert set(r['instructions'] for r in prior)=={str(insns)}
 spec={'workload':w,'asset_id':asset,'asset':a,'rows':rs,'expected_commands':commands,'expected_instructions':insns,'expected_CTA':ctas,'expected_kernels':len(rs),'members':members,'historical_rows':prior,'input_shape':'NOT_INFERRED_FROM_FILENAME','capture_native_values':'UNPROVEN'}
 selected[w]=spec
 print('INPUT_FULL_IDENTITY_PASS',w,insns,ctas,len(rs),flush=True)
put(T/'control/INPUT_IDENTITIES.json',selected)
put(T/'control/INPUT_PREFLIGHT.json',{'status':'THREE_FULL_INPUTS_SHA_AND_ORIGINAL_BODY_AUDIT_JOIN_PASS','body_audit_path':str(audit),'body_audit_sha256':sha(audit),'asset_catalog_path':str(catalog),'asset_catalog_sha256':sha(catalog),'selection_basis':'Three lowest original OO cycles among the eight original workloads without input-interpretation HOLD, excluding GEMM already studied; full inputs, no truncation','model_starts':0,'selected':list(selected)})
print('PREPARATION_COMPLETE',str(T),flush=True)

from pathlib import Path
import json,hashlib,shutil,datetime
V=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1')
DOC=V/'review/docs/ep_l2/operations/ep_performance_first_v3_20261104_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=Path(p).stat().st_size)
def exact(r):assert sha(r['path'])==r['sha256'],r['path'];return read(r['path'])
MANIFESTS={'agent_a_mid_tag':'BUNDLE_MANIFEST.json','agent_b_vector_modes':'DELIVERY_MANIFEST.json','agent_c_victim_quota':'DELIVERY_MANIFEST.json','agent_d_native_queue':'MANIFEST.json'}
packets={}; copied=[]
for agent,manifest in MANIFESTS.items():
 root=V/agent;mf=read(root/manifest);packets[agent]=ref(root/manifest)
 rows=mf.get('files',mf.get('reports_and_small_evidence',[]));assert rows
 for item in rows:
  p=Path(item['path']) if 'path' in item else root/item['name']
  rel=p.relative_to(root);assert p.resolve().is_relative_to(root.resolve()) and p.is_file() and not p.is_symlink()
  assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],str(p)
  assert p.stat().st_size<8*1024*1024 and p.suffix not in ['.pyc','.a','.out'],str(p)
  dest=DOC/agent/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  copied.append(dict(member=str(Path(agent)/rel),sha256=item['sha256'],bytes=item['bytes']))
 for name in [manifest,'GIT_INCLUDE_FILES.txt','SHA256SUMS']:
  p=root/name
  if p.is_file():
   dest=DOC/agent/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
   if not any(r['member']==str(Path(agent)/name) for r in copied):copied.append(dict(member=str(Path(agent)/name),sha256=sha(p),bytes=p.stat().st_size))
old=V.parent/'performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/concurrency10_20261104_v1'
accepted=read(old/'closeout_20261104_v1/FINAL_RESULTS.json')['points']
registry=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']
A=read(V/'agent_a_mid_tag/MID_TAG_FAMILY_SCOPE.json');B=read(V/'agent_b_vector_modes/DELIVERY_MANIFEST.json');C=read(V/'agent_c_victim_quota/VICTIM_QUOTA_PERFORMANCE_FAMILY_V1.json')
assert len(A['points'])==8 and len(B['candidate_specs'])==2 and len(C['points'])==6
assert A['request_id'] not in registry and B['request_id'] not in registry
cases=set();review=[]
for group,items in [('A',[p['spec_ref'] for p in A['points']]),('B',list(B['candidate_specs'].values())),('C',[p['ref'] for p in C['points']])]:
 for r in items:
  s=exact(r);assert s['cohort'] not in cases;cases.add(s['cohort']);o=s['expected_effective_options']
  assert s.get('approved_launches') in [None,0] and s.get('launch_permission') in [None,False]
  assert s.get('Main_scientific_launch_authorization') is None
  assert 'CANDIDATE' in s['status'] and s.get('source_keep',s.get('Source_KEEP')) is True
  assert s.get('M',False) is False and s.get('T',False) is False
  assert str(s['trace_entry']).startswith('/root/share/mnt164/')
  assert all(o[k]=='1' for k in ['-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats'])
  assert o['-dram_latency']=='100' and o['-gpgpu_frfcfs_dram_sched_queue_size']=='128'
  if group=='A':
   assert s['science_request_id']==A['request_id'] and s['source_identity']==A['source_identity']
   assert s['mode'] in ['S','WV_ZERO_RO'] and (s['geometry']['sets'],s['geometry']['ways']) in [(32,16),(64,8)]
   base=exact(s['absolute_REF850_spec_ref']);diff={k for k in o if o[k]!=base['expected_effective_options'][k]};assert diff=={'-gpgpu_cache:dl2'},diff
   assert len(o)==282 and o['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'
   assert s['input_identity_sha256']==base['input_identity_sha256']
  elif group=='B':
   assert s['science_request_id']==B['request_id'] and s['source_identity']==B['Source5']
   assert s['mode'] in ['W_ONLY','WV_ZERO_RO']
   ctrl=next(p for p in accepted if p['cohort']=='EP_PERF_CC_CAM_VECTOR4M_S_1700_V1');base=exact(ctrl['spec_ref'])
   diff={k for k in o if o[k]!=base['expected_effective_options'][k]}
   expected={'-gpgpu_ep_l2_ft_mode'}|({'-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty'} if s['mode']=='WV_ZERO_RO' else set());assert diff==expected,diff
   assert len(o)==282 and o['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:1700.0'
   assert s['input_identity_sha256']==base['input_identity_sha256']
  else:
   assert s['source_identity']['core_source_commit']=='bf4e48447136b990bd2db15e2972a4394e37d21f'
   assert len(o)==283 and o['-gpgpu_ep_l2_tvd_clean_limit'] in ['0','64','128'] and s['mode']=='WV_ZERO_RO'
   assert o['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'
  for q in s['ordered_configs']:assert sha(q['path'])==q['sha256']
  assert not any(s['cohort'] in row.get('consumed',{}) for row in registry.values() if isinstance(row.get('consumed'),(dict,list)))
  ledger=Path('/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger')
  assert not (ledger/(s['cohort']+'.INTENT.json')).exists() and not (ledger/(s['cohort']+'.DONE.json')).exists()
  review.append(dict(family=group,cohort=s['cohort'],candidate_spec_ref=r,source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],option_count=len(o),options_sha256=hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest(),PASS=True))
result=dict(schema='EP_MAIN_V3_INDEPENDENT_MANIFEST_AND_SCOPE_REVIEW_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS_CANDIDATE_ENGINEERING_ONLY',agent_manifests=packets,verified_and_staged_file_count=len(copied),verified_and_staged_bytes=sum(p['bytes'] for p in copied),specs_reviewed=review,models_started=0,new_budget_registered=False,old_budget_reused=False,Trace_body_read_or_rehashed=False,production_activation=False)
(V/'main/MAIN_INDEPENDENT_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
(V/'main/STAGED_AGENT_FILE_INDEX.json').write_text(json.dumps(dict(files=copied),indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='specs_reviewed'},indent=2))

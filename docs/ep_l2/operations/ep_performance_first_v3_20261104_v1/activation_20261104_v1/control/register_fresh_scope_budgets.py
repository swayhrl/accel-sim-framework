from pathlib import Path
import json,hashlib,copy,datetime,fcntl,os,uuid
N=Path('/root/data/ep_l2_dtc_l1_native_v2');V=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1');C=V/'activation_20261104_v1/control';REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def put(p,x):
 data=(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode();tmp=p.with_name('.'+p.name+'.'+str(uuid.uuid4()))
 with tmp.open('xb') as h:h.write(data);h.flush();os.fsync(h.fileno())
 os.replace(tmp,p)
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
 return ref(p)
def rem(row):
 if 'remaining'in row:return row['remaining']
 spent=row.get('consumed',0);return max(0,row.get('budget',0)-(spent if type(spent)is int else len(spent)))
a=read(C/'USER_AUTHORIZATION.json');assert a['explicit_user_approval']and a['total_new_start_budget']==10 and a['global_EP_model_cap']==10
with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 r=read(REG);e=read(EPOCH);assert sha(REG)==e['native_registry_sha256'] and e['state']=='NATIVE_SCIENCE_ACTIVE' and e['holder']==os.uname().nodename
 previous=copy.deepcopy(r);before=dict(registry=ref(REG),epoch=ref(EPOCH));protected_epoch=copy.deepcopy(e)
 for p in [REG,EPOCH]:
  archive=N/'control/science_authority/request_history'/(p.stem+'.'+sha(p)+'.json')
  if not archive.exists():archive.write_bytes(p.read_bytes())
 added={}
 for f in a['families']:
  q=f['request_id'];assert q not in r['registered_future_requests'],'already registered; inspect, never duplicate budget'
  root=Path(f['data_root']);scope=read(root/'control/USER_AUTHORIZATION.json')
  assert scope['goal']==q and scope['approved_launches']==f['budget'] and scope['parent_authorization_ref']==ref(C/'USER_AUTHORIZATION.json')
  assert scope['allowed_cohorts']==f['allowed_cohorts'] and scope['Source5']==f['Source5']
  row=dict(request=q,project='EP_L2',owner='EP-MAIN',budget=f['budget'],remaining=f['budget'],consumed={},admitted_specs={},state='REGISTERED_HOLD_FORMAL_BINDING',authorization_ref=ref(root/'control/USER_AUTHORIZATION.json'),parent_authorization_ref=ref(C/'USER_AUTHORIZATION.json'),source_identity=f['Source5'],source_keep=True,automatic_retry=False,refund=False,reserved_write_bytes=0,resource_group_id=q,runtime_versions={},native_entry_ref=None,native_qualification_ref=None,global_model_concurrency_authorized=10,temporary_qualified_cap2_allowed=True,allowed_cohorts=f['allowed_cohorts'],registered_utc=now(),Main_activation_control_root=str(C))
  r['registered_future_requests'][q]=row;added[q]=copy.deepcopy(row)
 for k,row in previous['registered_future_requests'].items():assert r['registered_future_requests'][k]==row,'existing request changed'
 assert {k:x for k,x in r.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']}=={k:x for k,x in previous.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']}
 r['new_scientific_budget_remaining']=sum(rem(row)for row in r['registered_future_requests'].values());assert r['new_scientific_budget_remaining']==previous['new_scientific_budget_remaining']+10
 put(REG,r);e['native_registry_sha256']=sha(REG);e['new_budget_remaining']=r['new_scientific_budget_remaining'];e['request_revision']=dict(request_id=list(added),operation='MAIN_REGISTER_FRESH_V3_EXACT_8_PLUS_2_HOLD_BINDING',utc=now(),previous_registry_sha256=before['registry']['sha256'])
 assert {k:x for k,x in e.items()if k not in ['native_registry_sha256','new_budget_remaining','request_revision']}=={k:x for k,x in protected_epoch.items()if k not in ['native_registry_sha256','new_budget_remaining','request_revision']}
 put(EPOCH,e)
 receipt=dict(schema='EP_MAIN_V3_FRESH_BUDGET_REGISTRATION_V1',utc=now(),status='REGISTERED_FRESH8_AND2_HOLD_FORMAL_BINDING',before=before,after=dict(registry=ref(REG),epoch=ref(EPOCH)),added_requests=added,existing_requests_and_history_preserved=True,old_remaining_untouched=True,formal_model_starts=0,consumed=0,global_cap_authorized=10)
 put(C/'NEW_BUDGET_REGISTRATION_RECEIPT.json',receipt);print(json.dumps(dict(status=receipt['status'],request_budgets={q:row['budget']for q,row in added.items()},registry_sha256=sha(REG)),indent=2))

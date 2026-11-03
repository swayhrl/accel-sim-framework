"""EP-MAIN explicit approved fresh scopes registration. Zero application starts."""
import pathlib,json,hashlib,fcntl,os,datetime,copy,uuid
P=pathlib.Path;E=P(__file__).resolve().parents[1];N=P('/root/data/ep_l2_dtc_l1_native_v2');REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EP=N/'control/CURRENT_SCIENCE_EPOCH.json'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode();tmp=p.with_name('.'+p.name+'.'+str(uuid.uuid4()))
 with tmp.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def remaining(v):
 if 'remaining' in v:return v['remaining']
 c=v.get('consumed',0);return max(0,v.get('budget',0)-(c if type(c)is int else len(c)))
def main():
 assert not(E/'control/FRESH_REGISTRATION_RECEIPT.json').exists(),'already registered; never reset'
 m=read(E/'control/EXACT_EXECUTION_MANIFEST.json');assert len(m['points'])==8 and m['budgets']=={'wv':2,'t3':6}
 assert read(E/'control/MAIN_SCOPED_NATIVE_QUALIFICATION.json')['status']=='MAIN_REVIEWED_SCOPED_NATIVE_EXTENSION_QUALIFIED'
 assert ref(m['native_entry_ref']['path'])==m['native_entry_ref']
 assert ref(m['shared_native_ref']['path'])==m['shared_native_ref']
 with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b') as f:
  fcntl.flock(f,fcntl.LOCK_EX);r=read(REG);e=read(EP);assert sha(REG)==e['native_registry_sha256'] and e['epoch']==2 and e['state']=='NATIVE_SCIENCE_ACTIVE' and e['holder']==os.uname().nodename
  before=copy.deepcopy(r);ebefore=copy.deepcopy(e);prior=dict(registry_ref=ref(REG),epoch_ref=ref(EP));oldrows=copy.deepcopy(r['registered_future_requests']);created={}
  for group in ('wv','t3'):
   points=[x for x in m['points'] if x['group']==group];qid=points[0]['science_request_id'];assert qid not in r['registered_future_requests'];assert len(points)==m['budgets'][group]
   a=E/group/'control/USER_AUTHORIZATION.json';auth=read(a);assert auth['budget']==len(points) and set(auth['exact_cohorts'])==set(x['cohort'] for x in points) and auth['goal']==qid and auth['user_request_ref']==ref(E/group/'control/USER_REQUEST.txt')
   specs={}
   for x in points:
    assert ref(x['spec_ref']['path'])==x['spec_ref'];s=read(x['spec_ref']['path']);assert s['science_request_id']==qid and s['cohort']==x['cohort'];specs[x['cohort']]=x['spec_ref']['sha256']
   engine=s['host_engine_ref'];common=s['host_common_ref']
   q=dict(request=qid,owner='EP-MAIN',project='EP_L2',budget=len(points),remaining=len(points),consumed={},admitted_specs=specs,authorization_ref=ref(a),runtime_versions={engine['sha256']:dict(engine_ref=engine,common_ref=common)},native_entry_ref=m['native_entry_ref'],shared_native_unmodified_ref=m['shared_native_ref'],native_qualification_ref=ref(E/'control/MAIN_SCOPED_NATIVE_QUALIFICATION.json'),state='REGISTERED_NOT_STARTED',automatic_retry=False,refund=False,source_keep=True,resource_group_id=qid,reserved_write_bytes=0,source_identity=s['source_identity'],Main_manifest_ref=ref(E/'control/EXACT_EXECUTION_MANIFEST.json'))
   r['registered_future_requests'][qid]=q;created[qid]=q
  assert {k:r['registered_future_requests'][k] for k in oldrows}==oldrows
  for k,v in before.items():
   if k not in ('registered_future_requests','new_scientific_budget_remaining'):assert r[k]==v
  hist=N/'control/science_authority/request_history';hist.mkdir(exist_ok=True)
  for p in (REG,EP):
   dest=hist/(p.stem+'.'+sha(p)+'.json')
   if not dest.exists():
    with dest.open('xb') as disk:disk.write(p.read_bytes());disk.flush();os.fsync(disk.fileno())
  r['new_scientific_budget_remaining']=sum(remaining(v) for v in r['registered_future_requests'].values());assert r['new_scientific_budget_remaining']==before['new_scientific_budget_remaining']+8
  put(REG,r);e['native_registry_sha256']=sha(REG);e['new_budget_remaining']=r['new_scientific_budget_remaining'];e['request_revision']=dict(request_ids=list(created),operation='MAIN_REGISTER_USER_APPROVED_FRESH_W2_T6_SCOPED_NATIVE_EXTENSION_NO_START',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_registry_sha256=prior['registry_ref']['sha256'],prior_current_epoch_sha256=prior['epoch_ref']['sha256']);put(EP,e)
  assert read(REG)==r and sha(REG)==read(EP)['native_registry_sha256']
  receipt=dict(schema='EP_MAIN_FRESH_W2_T6_REGISTRATION_RECEIPT_V1',status='REGISTERED_FRESH_EXACT_W2_T6_NO_APPLICATION_STARTED',approved_by='EP-MAIN',prior=prior,new_registry_ref=ref(REG),new_epoch_ref=ref(EP),request_ids=list(created),budgets={k:v['budget'] for k,v in created.items()},prior_all_requests_preserved=True,foreign_rows_preserved=True,old_budget_reuse=False,shared_native_unmodified_ref=ref(N/'bin/native'),scoped_native_entry_ref=m['native_entry_ref'],scientific_starts=0)
  put(E/'control/FRESH_REGISTRATION_RECEIPT.json',receipt);print(json.dumps(receipt))
if __name__=='__main__':main()

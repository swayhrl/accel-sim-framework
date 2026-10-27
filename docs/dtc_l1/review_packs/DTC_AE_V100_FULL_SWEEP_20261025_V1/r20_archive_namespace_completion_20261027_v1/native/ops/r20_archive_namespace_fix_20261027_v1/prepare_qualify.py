import pathlib,json,hashlib,importlib.util,types,copy,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/r20_archive_namespace_fix_20261027_v1';R=F/'validation_storage_recovery12_v1';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('namespace_fix_candidate',D/'namespace_fix.py');reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=reg['registered_future_requests'][m.REQ];ops=load('namespace_fix_frozen_worker',R/'tools/recovery12_ops_v1.py');ob=load('namespace_fix_frozen_outbox',R/'tools/recovery12_outbox_v1.py');policy=F/'control/R20_RESOURCE_ACCOUNTING_POLICY_V1.json';lease=read(T/'control/BATCH_LEASE.json');points={}
for c,row in q['consumed'].items():
 rp=R/'analysis'/(c+'.RESULT.json');dp=R/'control/qualification_ledger'/(c+'.DONE.json')
 if not rp.exists()or not dp.exists():continue
 old=read(rp);d=read(dp)
 if old.get('state')!='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS':continue
 assert old['error']=="RuntimeError('COPY namespace not the pinned namespace')"and d['stop_reason']is None and d['launcher_wait_returncode']==0;points[c]=dict(uuid=row['uuid'],old_RESULT_sha256=sha(rp),DONE_sha256=sha(dp))
assert len(points)==6;p=dict(schema='R20_EXACT_NAMESPACE_RECONCILIATION_METADATA_PLAN_V1',source_sha256=sha(D/'namespace_fix.py'),parent_pid=lease['pid'],parent_start_ticks=lease['start_ticks'],parent_sha256=lease['controller_sha256'],policy_path=str(policy),policy_sha256=sha(policy),ops_sha256=sha(R/'tools/recovery12_ops_v1.py'),expected_ops_loader=m.identity(ops.load),outbox_path=str(R/'tools/recovery12_outbox_v1.py'),outbox_sha256=sha(R/'tools/recovery12_outbox_v1.py'),frozen_outbox_NAS=str(ob.NAS),pinned_policy_NAS=read(policy)['copy_namespaces'][m.REQ],points=points,all12_future_archive_route_corrected=True,old_scientific_source_and_ledger_unchanged=True);assert not(D/'PLAN.json').exists();m.write(D/'PLAN.json',p);checks=[]
def rejected(fn):
 try:fn()
 except(RuntimeError,AssertionError):return
 raise AssertionError('expected rejection')
for c in sorted(q['admitted_specs']):
 private=m.corrected_outbox(load('namespace_cpu_'+c,P(p['outbox_path'])),p);base=private.adapted(c);assert str(base.NAS)==p['pinned_policy_NAS']and base.ROOT==R and c in base.COHORTS and base._R20_PRIVATE_COPY_GATE_BINDING['owner_request']==m.REQ;checks.append('actual full outbox+gate composition '+c)
bad=load('namespace_old_reproduction',P(p['outbox_path']));rejected(lambda:bad.adapted(next(iter(points))));checks.append('old real namespace mismatch reproduces before COPY')
obj=types.SimpleNamespace(__file__=p['outbox_path'],NAS=P('/unknown/destination'));rejected(lambda:m.corrected_outbox(obj,p));checks.append('unknown namespace rejected')
obj=types.SimpleNamespace(__file__='/wrong/source.py',NAS=P(p['frozen_outbox_NAS']));rejected(lambda:m.corrected_outbox(obj,p));checks.append('wrong module rejected')
sentinel=object();obj=types.SimpleNamespace(__file__=p['outbox_path'],NAS=P(p['frozen_outbox_NAS']),KEEP=sentinel);loader=m.make_loader(lambda name,file:obj,p);assert loader('CPU','other.py')is obj and str(obj.NAS)==p['frozen_outbox_NAS'];checks.append('other worker imports unchanged');assert loader('CPU','recovery12_outbox_v1.py')is obj and str(obj.NAS)==p['pinned_policy_NAS']and obj.KEEP is sentinel;checks.append('only namespace attribute changes');assert m.corrected_outbox(obj,p)is obj;checks.append('exact correction idempotent')
for c in points:
 proof=m.verify_one(c,p,False);assert proof['strict']['correctness_validation_passed']and proof['archive']is None;checks.append('real full strict replay and no archive '+c)
qual=dict(status='PASS',source_sha256=sha(D/'namespace_fix.py'),plan_sha256=sha(D/'PLAN.json'),driver_sha256=sha(__file__),check_count=len(checks),checks=checks,real_COPY_calls=0,scientific_model_starts=0,real_source_or_ledger_mutations=0,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());m.write(D/'CPU_QUALIFICATION.json',qual);print(json.dumps(dict(status='PASS',checks=len(checks),completed_points=len(points),source_sha256=qual['source_sha256'],plan_sha256=qual['plan_sha256'])))

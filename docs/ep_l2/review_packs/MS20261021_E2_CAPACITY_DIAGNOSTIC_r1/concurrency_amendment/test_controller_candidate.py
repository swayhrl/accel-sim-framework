"""Pure mocked scheduler controls: zero real pool threads/apps/central writes."""
from pathlib import Path
import ast,contextlib,copy,importlib.util,json,sys,tempfile,types,unittest
from unittest.mock import patch
P=Path(__file__).resolve().parent;R=P.parents[4]
sys.path.insert(0,str(R/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(P/'candidate'))
import coordinator as c
s=importlib.util.spec_from_file_location('controller_candidate',P/'candidate/controller.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
BASE=json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text())
class Future:
 def __init__(self,spec,done=False,status='COMPLETE_VALID'):self.spec=spec;self.finished=done;self.status=status
 def done(self):return self.finished
 def result(self):return dict(attempt_id='SYNTHETIC_'+self.spec['condition_id'],run_key=m.run_key(self.spec['identity']),status=self.status,detail='MOCK_NOT_APPLICATION')
class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='pure_controls_',dir=P);self.addCleanup(self.tmp.cleanup);self.d=Path(self.tmp.name)
  self.data=copy.deepcopy(BASE);self.data['runs']={};self.data['resource_leases']={};self.data[c.FIELD]['actual_starts']=38;self.actual=38;self.persist()
  self.submitted=[];self.waits=[];self.capacities=[];self.outcomes={};self.writes=[]
  self.coord=types.SimpleNamespace(registry=types.SimpleNamespace(root=self.d),handoff=self.d,snapshot=self.snapshot,unique_controller=lambda:contextlib.nullcontext())
  for name,value in [('tooling_binding',lambda:{}),('write_json',lambda p,v:self.writes.append((str(p),v))),('local_resources',lambda:dict(available_memory_bytes=256*c.GIB,disk_free_bytes=40*c.GIB,share_disk_free_bytes=44*c.GIB)),('output_usage',lambda:dict(old_bytes=13*c.GIB,new_bytes=6*c.GIB,total_bytes=19*c.GIB)),('resource_gate',self.gate),('roll_pairs',lambda *a:[])]:self.enterContext(patch.object(m,name,value))
  self.enterContext(patch.object(m.durable_exit,'controller_signals',lambda:contextlib.nullcontext()));self.enterContext(patch.object(m.durable_exit,'STOP',types.SimpleNamespace(is_set=lambda:False)))
 def persist(self):(self.d/'RUN_REGISTRY.json').write_text(json.dumps(self.data))
 def snapshot(self):
  x=copy.deepcopy(self.data[c.FIELD]);x.update(actual_starts=self.actual,remaining_start_capacity=46-self.actual);return x
 def spec(self,i,memory=8*c.GIB):
  x=copy.deepcopy(BASE[c.FIELD]['attempts'][0]['identity']);x['runtime_config_sha256']=f'{i:064x}'
  return dict(identity=x,condition_id=str(i),qualification_id='SYNTHETIC_'+str(i),budget_bucket='five_input_capacity_diagnostic_user_approved_20261021',memory_bytes=memory,maximum_result_bytes=384*2**20)
 def gate(self,data,kind,cpu,memory,growth,resources,usage,scan=False):
  rows=[x for x in data['runs'].values() if x['status'] in ('RESERVED','RUNNING')]
  if sum(x['cpu_units'] for x in rows)+cpu>8:raise ValueError('shared CPU quota full')
  if sum(x['memory_bytes'] for x in rows)+memory>32*c.GIB:raise ValueError('shared memory reservation quota full')
  if resources['disk_free_bytes']-sum(x.get('disk_growth_bytes',0)+x.get('monitor_reserve_bytes',0) for x in rows)-growth-2*c.GIB<5*c.GIB:raise ValueError('workspace floor plus existing/proposed output growth and monitor reserve')
 def pool(self,max_workers):
  owner=self;self.capacities.append(max_workers)
  class Pool:
   def __enter__(self):return self
   def __exit__(self,*a):return False
   def submit(self,fn,spec,coord):
    f=Future(spec,status=owner.outcomes.get(spec['condition_id'],'COMPLETE_VALID'));owner.submitted.append(f);return f
  return Pool()
 def wait(self,running,return_when):
  self.waits.append(len(running));f=next(iter(running));f.finished=True;self.actual+=1;return {f},set(running)-{f}
 def run_step(self,n):
  entries=[]
  for i in range(1,n+1):
   p=self.d/f'spec{i}.json';p.write_text(json.dumps(self.spec(i)));entries.append(dict(path=str(p),sha256=m.digest(p)))
  q=self.d/'QUEUE.json';q.write_text(json.dumps(dict(campaign_id=c.CAMPAIGN,prepared_by='E',authority_commit=c.AUTHORITY,input_and_profile_freeze_unix=1,specs=entries,pairs=[])))
  self.enterContext(patch.object(m,'ThreadPoolExecutor',self.pool));self.enterContext(patch.object(m,'wait',self.wait));return m.step(self.coord,q)
 def test_virtual_view_does_not_mutate_original(self):
  before=copy.deepcopy(self.data);f=Future(self.spec(1));v,keys=m.submitted_reservation_view(self.data,{f:f.spec});self.assertEqual(self.data,before);self.assertEqual(len(v['runs']),1);self.assertEqual(len(keys),1)
 def test_real_reserved_not_double_counted(self):
  f=Future(self.spec(1));self.data['runs'][m.run_key(f.spec['identity'])]=dict(status='RESERVED');v,keys=m.submitted_reservation_view(self.data,{f:f.spec});self.assertEqual(len(v['runs']),1);self.assertFalse(keys)
 def test_done_future_not_virtual_reserved(self):
  f=Future(self.spec(1),done=True);v,keys=m.submitted_reservation_view(self.data,{f:f.spec});self.assertFalse(v['runs']);self.assertFalse(keys)
 def test_fourth_fits_fifth_defers(self):
  fs={Future(self.spec(i)):self.spec(i) for i in range(1,4)};self.assertTrue(m.forecast(self.coord,self.spec(4),fs)['fits']);f=Future(self.spec(4));fs[f]=f.spec;self.assertFalse(m.forecast(self.coord,self.spec(5),fs)['fits'])
 def test_no_fixed_four_for_smaller_specs(self):
  fs={Future(self.spec(i,c.GIB)):self.spec(i,c.GIB) for i in range(1,6)};self.assertTrue(m.forecast(self.coord,self.spec(6,c.GIB),fs)['fits'])
 def test_eight_roll_at_four_resources_no_loss(self):
  r=self.run_step(8);self.assertEqual(self.capacities,[8]);self.assertEqual(len(self.submitted),8);self.assertEqual(max(self.waits),4);self.assertEqual(r['queue_remaining_count'],0);self.assertTrue(any(x['action']=='WAIT_OWN_FUTURE_COMPLETION' for x in r['resource_waits']))
 def test_no_running_no_fit_legal_stop_preserves_pending(self):
  def no(*a,**k):raise ValueError('shared memory reservation quota full')
  self.enterContext(patch.object(m,'resource_gate',no));r=self.run_step(8);self.assertFalse(self.submitted);self.assertFalse(self.waits);self.assertEqual(r['queue_remaining_count'],8);self.assertEqual(r['status'],'RESOURCE_ADMISSION_STOP_NO_OWN_FUTURE')
 def test_failed_stops_dispatch_drains_other_futures(self):
  self.outcomes={'1':'FAILED'};r=self.run_step(8);self.assertEqual(len(self.submitted),4);self.assertEqual(r['queue_remaining_count'],4);self.assertEqual(len(r['outcomes']),4);self.assertEqual(r['status'],'BLOCKED_EVENT_REQUIRED')
 def test_legacy_target_two_unchanged(self):
  self.data[c.FIELD].pop('formal_simulator_concurrency');self.data[c.FIELD]['target_simulators']=2;self.persist();r=self.run_step(3);self.assertEqual(self.capacities,[2]);self.assertEqual(max(self.waits),2);self.assertEqual(r['concurrency_mode'],'LEGACY_FINITE_TARGET')
 def test_exact_unreserved_resource_failure_can_defer(self):
  with patch.object(m,'forecast',return_value=dict(fits=False,reason='shared memory reservation quota full')):self.assertIsNotNone(m.deferred_prelaunch_resource(self.coord,self.spec(1),ValueError('shared memory reservation quota full'),{}))
 def test_identity_failure_not_reclassified(self):
  with patch.object(m,'forecast',return_value=dict(fits=False,reason='shared memory reservation quota full')):self.assertIsNone(m.deferred_prelaunch_resource(self.coord,self.spec(1),ValueError('binary changed'),{}))
 def test_existing_attempt_never_implicit_retry(self):
  spec=self.spec(1);self.data[c.FIELD]['attempts'].append(dict(run_key=m.run_key(spec['identity']),state='CANCELLED_BEFORE_START'));self.assertIsNone(m.deferred_prelaunch_resource(self.coord,spec,ValueError('shared memory reservation quota full'),{}))
 def test_AST_unique(self):
  t=ast.parse((P/'candidate/controller.py').read_text());names=[x.name for x in t.body if isinstance(x,ast.FunctionDef)];self.assertEqual(len(names),len(set(names)))
if __name__=='__main__':unittest.main()

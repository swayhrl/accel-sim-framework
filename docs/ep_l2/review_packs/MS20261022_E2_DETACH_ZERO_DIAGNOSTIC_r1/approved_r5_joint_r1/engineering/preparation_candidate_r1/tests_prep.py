"""Bounded SYNTHETIC engineering controls, not native/application qualification."""
import copy,hashlib,json,sys,unittest,ast
from pathlib import Path
sys.dont_write_bytecode=True
import r5_preparation as p
class PrepControls(unittest.TestCase):
 def setUp(self):
  self.d={'runs':{},'resource_leases':{}}
  self.i=dict(campaign_id=p.CAMPAIGN,t0_unix=1792414193,attempts=[{'id':n,'status':'COMPLETE_VALID'} for n in range(55)],actual_starts=55,uncertain_start_intents=0,remaining_start_capacity=0,controller={'state':'STOPPED'},workspace_disk_policy={'disk_floor_bytes':5*p.GIB,'monitor_reserve_bytes':2*p.GIB},qualifications={'old':{'q':'fixed'}},accepted_results={'old':{'r':'fixed'}},accepted_pairs={},input_selections={},scientific_holds={})
  self.m=dict(historical55_seal=p.seal55(self.d,self.i),approval_ref={'path':'SYNTHETIC','sha256':'a'*64},build_identity={'core':'NEW_SYNTHETIC'},output_directory=p.BUILD_PATH)
  self.old=p.authority;self.oldref=p.PREP_AUTHORITY_REF;p.authority=lambda:self.m;p.PREP_AUTHORITY_REF={'path':'SYNTHETIC','sha256':'b'*64}
 def tearDown(self):p.authority=self.old;p.PREP_AUTHORITY_REF=self.oldref
 def call(self,**kw):
  a=dict(data=self.d,item=self.i,role='E',kind='build',cpu=2,memory=8*p.GIB,growth=p.GIB,directory=p.BUILD_PATH,result_growth=0,disk_authorization_id=None,build_identity=self.m['build_identity']);a.update(kw);return p.authorize(**a)
 def row(self):return dict(experiment_id=p.CAMPAIGN,role='E',kind='MECHANISM_BUILD',owner='mechanism_E',output_directory=p.BUILD_PATH,cpu_units=2,memory_bytes=8*p.GIB,disk_growth_bytes=p.GIB,result_growth_bytes=0,status='RESERVED',disk_floor_bytes=5*p.GIB,monitor_reserve_bytes=2*p.GIB,**self.call())
 def test_exact_authorized(self):self.assertEqual(self.call()['build_owner'],'E2_R5_FORMAL_PRODUCER')
 def test_wrong_path(self):
  with self.assertRaises(ValueError):self.call(directory='/workspace/build/other')
 def test_old_or_wrong_source(self):
  with self.assertRaises(ValueError):self.call(build_identity={'core':p.BASE})
 def test_wrong_role(self):
  with self.assertRaises(ValueError):self.call(role='A')
 def test_named_A_exception_rejected(self):
  with self.assertRaises(ValueError):self.call(disk_authorization_id='oldA')
 def test_resource_bounds(self):
  for changes in ({'cpu':3},{'cpu':True},{'memory':9*p.GIB},{'growth':p.GIB+1},{'result_growth':1}):
   with self.subTest(changes=changes),self.assertRaises(ValueError):self.call(**changes)
 def test_no_science_namespace(self):
  self.i['NEW_NAMESPACE']={}
  with self.assertRaises(ValueError):self.call()
 def test_original_attempt_prefix(self):
  self.i['attempts'][0]['status']='NEW'
  with self.assertRaises(ValueError):self.call()
 def test_original_Q(self):
  self.i['qualifications']['old']['q']='NEW'
  with self.assertRaises(ValueError):self.call()
 def test_no_added_Q(self):
  self.i['qualifications']['new']={}
  with self.assertRaises(ValueError):self.call()
 def test_no_refund(self):
  self.i['actual_starts']=54
  with self.assertRaises(ValueError):self.call()
 def test_controller_stopped(self):
  self.i['controller']['state']='RUNNING'
  with self.assertRaises(ValueError):self.call()
 def test_active_E_lease(self):
  self.d['resource_leases']['busy']={'experiment_id':p.CAMPAIGN,'role':'E','status':'RUNNING'}
  with self.assertRaises(ValueError):self.call()
 def test_other_campaign_untouched(self):
  self.d['resource_leases']['other']={'experiment_id':'C16','role':'E','status':'RUNNING'};self.call()
 def test_actual_active_app(self):
  self.d['runs']['busy']={'experiment_id':p.CAMPAIGN,'status':'RUNNING'}
  with self.assertRaises(ValueError):self.call()
 def test_valid_row_release_history(self):
  self.d['resource_leases']['prep']=self.row();p.crosscheck(self.d,self.i);self.d['resource_leases']['prep']['status']='RELEASED';p.crosscheck(self.d,self.i)
 def test_markerless_rejected(self):
  r=self.row();r.pop('r5_preparation_authority_ref');self.d['resource_leases']['prep']=r
  with self.assertRaises(ValueError):p.crosscheck(self.d,self.i)
 def test_wrong_owner_rejected(self):
  r=self.row();r['build_owner']='A';self.d['resource_leases']['prep']=r
  with self.assertRaises(ValueError):p.crosscheck(self.d,self.i)
 def test_two_live_rejected(self):
  r=self.row();self.d['resource_leases'].update(one=r,two=copy.deepcopy(r))
  with self.assertRaises(ValueError):p.crosscheck(self.d,self.i)
 def test_unbound_rejected(self):
  r=self.row();self.d['resource_leases']['prep']=r;p.PREP_AUTHORITY_REF=None
  with self.assertRaises(ValueError):p.crosscheck(self.d,self.i)
 def test_guard_not_lowered(self):
  self.i['workspace_disk_policy']['disk_floor_bytes']=4*p.GIB
  with self.assertRaises(ValueError):self.call()
 def test_historical_canonical_integrity(self):
  self.d['runs']['old']={'experiment_id':p.CAMPAIGN,'status':'FAILED'};self.m['historical55_seal']=p.seal55(self.d,self.i);self.d['runs']['old']['status']='COMPLETE_VALID'
  with self.assertRaises(ValueError):self.call()
 def test_historical_E_integrity(self):
  self.d['resource_leases']['old']={'experiment_id':p.CAMPAIGN,'role':'E','status':'RELEASED'};self.m['historical55_seal']=p.seal55(self.d,self.i);self.d['resource_leases']['old']['status']='RESERVED'
  with self.assertRaises(ValueError):self.call()
 def test_guard_AST_unchanged(self):
  new=ast.parse(Path(__file__).with_name('coordinator.py').read_text());old=ast.parse(Path(__file__).with_name('coordinator_before_r5_prep.py').read_text())
  def node(tree,name):return next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
  for name in ('resource_gate','bind_work_process','release_work'):
   self.assertEqual(ast.dump(node(new,name)),ast.dump(node(old,name)),name)
if __name__=='__main__':unittest.main(verbosity=2)

"""Bounded pure synthetic route controls; no registry, native or app start."""
import ast,copy,hashlib,importlib.util,json,pathlib,sys,tempfile,types,unittest
P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(P/'candidate'))
import capacity_validation as cv, capacity_policy as policy

def require(ok,message):
 if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
# Execute only the new pure helper, never import production runner/controller.
r=ast.parse((P/'candidate/runner.py').read_text())
f=next(x for x in r.body if isinstance(x,ast.FunctionDef) and x.name=='validate_terminal_summary')
legacy_calls=[]
def legacy(summary,identity):legacy_calls.append((summary,identity));return {'legacy':'unchanged'}
ns=dict(require=require,digest=digest,capacity_policy=policy,capacity_validation=cv,validate_summary=legacy)
exec(compile(ast.Module(body=[f],type_ignores=[]),'<candidate-route>','exec'),ns)
route=ns['validate_terminal_summary']
example_source=P.parent/'acceptance_preparation/test_capacity_validation.py'
tree=ast.parse(example_source.read_text());ex=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='example')
g={'copy':copy,'AUTHORITY':cv.AUTHORITY,'SLICE_ZERO':cv.SLICE_ZERO};exec(compile(ast.Module(body=[ex],type_ignores=[]),'<synthetic-only-example>','exec'),g)

def normalize(master):
 s,i,q=g['example'](master);old=s['profile'];name=policy.ON if master else policy.OFF;s['profile']=name
 q['profiles'][name]=q['profiles'].pop(old)
 q['input_selection_id']='D_V1_convolutionSeparable';q['source_identity']['vendor_pybind11_commit']='5'*40
 q['expected_full_instructions']=714547200;s['instructions']=714547200
 for row in s['capacity_diagnostic']['slices'].values():
  for resource in row['resources'].values():resource.update(coverage_kind='EXACT_EVENT_HIGHWATER',refusal_semantics='SYNTHETIC_EXACT_REFUSALS')
 return s,i,q

def make_fixture(tmp):
 s,i,scope=normalize(1);off,_,oq=normalize(0);scope['profiles'].update(oq['profiles'])
 manifest={'synthetic_not_producer':True,'OFF':scope['profiles'][policy.OFF]['capacities'],'ON':scope['profiles'][policy.ON]['capacities']}
 mf=tmp/'manifest.json';mf.write_text(json.dumps(manifest));scope['capacity_manifest_sha256']=digest(mf)
 s['capacity_diagnostic']['capacity_manifest_sha256']=scope['capacity_manifest_sha256'];off['capacity_diagnostic']['capacity_manifest_sha256']=scope['capacity_manifest_sha256']
 zero_options={k:'0' for k in ('-gpgpu_ep_l2_diag_copy_free','-gpgpu_ep_l2_diag_l2_data_free','-gpgpu_ep_l2_ideal_meta','-gpgpu_ep_l2_ideal_read_hit','-gpgpu_ep_l2_ideal_wb','-gpgpu_ep_l2_mq2','-gpgpu_ep_l2_rg1','-gpgpu_ep_l2_feature_unified_payload','-gpgpu_ep_l2_feature_ro_pending_state','-gpgpu_ep_l2_feature_tvd','-gpgpu_ep_l2_feature_adaptive_policy','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_tvd_fixed_entries','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass','-gpgpu_ep_l2_static_s64','-gpgpu_ep_l2_wb_local_cap')}
 profiles={}
 for name,p in scope['profiles'].items():
  m=p['master'];profiles[name]={'research_switches':dict(W=0,V=0,T=0,M=0),'effective_options':{**zero_options,policy.MASTER:str(m),'-gpgpu_ep_l2_ft_mode':'1','-gpgpu_ep_l2_payload_mode':'2'},'comparison_variable_options':[policy.MASTER],'hardware_P1_throughput_eligible':1-m,'feature_vector':{'payload_capacity_per_slice':p['capacities']['payload_slots_total'],'wbuf_entries':p['capacities']['wb_payload_slots']},'ideal_vector':dict(copy_free=False,meta=False,read_hit=False,wb=False,mem_all_data=False,l2_data_free=bool(m)),'labels':dict(subset=False,oracle=False,diagnostic=bool(m))}
 q={'source_identity':scope['source_identity'],'input_selection_id':scope['input_selection_id'],'supported_profiles':profiles,'gates':{name:dict(status='PASS',production_driven=True,evidence_path=str(mf),evidence_sha256=digest(mf)) for name in policy.GATES},'capacity_diagnostic':dict(authority_commit=policy.AUTHORITY,master_option=policy.MASTER,common_capacity_vector=manifest,native_cache_geometry={name:{k:p['configuration'][k] for k in ('native_tag_sets','native_tag_ways','native_line_bytes')} for name,p in scope['profiles'].items()},validation_scope=scope,capacity_manifest=dict(path=str(mf),sha256=digest(mf)),normalized_capacity_profiles={name:{k:p[k] for k in ('capacities','configuration')} for name,p in scope['profiles'].items()})}
 qp=tmp/'synthetic_q.json';qp.write_text(json.dumps(q));qid=digest(qp)
 spec=dict(identity=i,budget_bucket=policy.BUCKET,qualification_id=qid,selection_id=scope['input_selection_id'])
 qrow=dict(qualification=q,path=str(qp),sha256=qid);audit=dict(qualification_sha256=qid,expected_full_instructions=scope['expected_full_instructions'])
 return s,i,q,spec,qrow,audit,off

class Controls(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='bounded-controls-',dir=P);self.fx=make_fixture(pathlib.Path(self.tmp.name));legacy_calls.clear()
 def tearDown(self):self.tmp.cleanup()
 def test_no_duplicate_candidate_top_level_definitions(self):
  # Guard against a generator inserting a second function/constants block that
  # Python silently replaces. Test actual final candidate bytes, not a mock.
  for path in (P/'candidate').glob('*.py'):
   tree=ast.parse(path.read_text());functions=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
   self.assertEqual(len(functions),len(set(functions)),str(path))
   constants=[]
   for node in tree.body:
    if isinstance(node,ast.Assign):
     for target in node.targets:
      if isinstance(target,ast.Name) and target.id.isupper():constants.append(target.id)
   self.assertEqual(len(constants),len(set(constants)),str(path))
  names=[n.name for n in ast.parse((P/'candidate/capacity_validation.py').read_text()).body if isinstance(n,ast.FunctionDef)]
  self.assertEqual(names.count('validate_scope'),1);self.assertEqual(names.count('capacity_label'),1)
 def test_new_on_route(self):
  s,i,q,spec,row,audit,off=self.fx;v=route(s,spec,row,audit);self.assertEqual(v['status'],'PASS');self.assertTrue(v['capacity_classification']['near_unbounded']);self.assertEqual(legacy_calls,[])
 def test_new_off_route(self):
  s,i,q,spec,row,audit,off=self.fx;spec['identity']['feature_vector']=q['supported_profiles'][policy.OFF]['feature_vector'];v=route(off,spec,row,audit);self.assertEqual(v['capacity_classification']['label'],'FINITE_OFF_BASELINE')
 def test_legacy_path_unchanged(self):
  s={'old':'unchanged'};i={'old':'identity'};self.assertEqual(route(s,dict(identity=i),{'qualification':{}},{}),{'legacy':'unchanged'});self.assertEqual(legacy_calls,[(s,i)])
 def test_capacity_bucket_no_scope_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;row['qualification']={}
  with self.assertRaises(ValueError):route(s,spec,row,audit)
 def test_missing_validation_scope_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;del q['capacity_diagnostic']['validation_scope']
  with self.assertRaises(ValueError):route(s,spec,row,audit)
 def test_main61_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;q['source_identity']['binary_sha256']=policy.MAIN61
  with self.assertRaises(ValueError):route(s,spec,row,audit)
 def test_no_registered_id_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;spec['qualification_id']='0'*64
  with self.assertRaises(ValueError):route(s,spec,row,audit)
 def test_legacy_bucket_cannot_route(self):
  s,i,q,spec,row,audit,off=self.fx;spec['budget_bucket']='main'
  with self.assertRaises(ValueError):route(s,spec,row,audit)
 def test_finite_negative_valid(self):
  s,i,q,spec,row,audit,off=self.fx;s['capacity_diagnostic']['slices']['0']['resources']['wad_entries']['capacity_refusals']=1
  self.assertEqual(route(s,spec,row,audit)['capacity_classification']['label'],'LARGE_FINITE')
 def test_unknown_observation_valid(self):
  s,i,q,spec,row,audit,off=self.fx;s['capacity_diagnostic']['slices']['0']['resources']['wad_entries']['counter_covered']=False
  self.assertEqual(route(s,spec,row,audit)['capacity_classification']['label'],'UNKNOWN')
 def test_wrong_input_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;audit['expected_full_instructions']-=1
  with self.assertRaises(ValueError):route(s,spec,row,audit)
 def test_nested_native_configuration_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;q['capacity_diagnostic']['validation_scope']['profiles'][policy.ON]['configuration']['native_tag_sets']={}
  with self.assertRaises(ValueError):policy.qualification(q,digest)
 def test_wrong_manifest_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;q['capacity_diagnostic']['capacity_manifest']['sha256']='0'*64
  with self.assertRaises(ValueError):policy.qualification(q,digest)
 def test_default_finite_unchanged(self):
  s,i,q,spec,row,audit,off=self.fx;q['capacity_diagnostic']['validation_scope']['profiles'][policy.OFF]['capacities']['descriptor_entries']*=2
  with self.assertRaises(ValueError):policy.qualification(q,digest)
 def test_wrong_authority_rejected(self):
  s,i,q,spec,row,audit,off=self.fx;q['capacity_diagnostic']['validation_scope']['authority_commit']='0'*40
  with self.assertRaises(ValueError):policy.qualification(q,digest)
 def test_conservative_bound_basis_preserved(self):
  s,i,q,spec,row,audit,off=self.fx
  for x in s['capacity_diagnostic']['slices'].values():x['resources']['tag_slots']['coverage_kind']='CONSERVATIVE_UPPER_BOUND'
  v=route(s,spec,row,audit)['capacity_classification'];self.assertTrue(v['near_unbounded']);self.assertEqual(v['evidence_basis'],'CONSERVATIVE_UPPER_BOUND_INCLUDED')
 def test_unknown_kind_cannot_claim_measured(self):
  s,i,q,spec,row,audit,off=self.fx;s['capacity_diagnostic']['slices']['0']['resources']['tag_slots']['coverage_kind']='UNKNOWN'
  self.assertEqual(route(s,spec,row,audit)['capacity_classification']['label'],'UNKNOWN')
 def test_non_applicable_s_bypass_not_required_as_observation(self):
  s,i,q,spec,row,audit,off=self.fx;p=q['capacity_diagnostic']['validation_scope']['profiles'][policy.ON]
  p['non_applicable_resources']={'bypass_payload_slots':'TRADITIONAL_S_NO_BYPASS_ALLOCATION'};p['enlarged_resources'].remove('bypass_payload_slots')
  for x in s['capacity_diagnostic']['slices'].values():x['resources']['bypass_payload_slots']['counter_covered']=False
  self.assertTrue(route(s,spec,row,audit)['capacity_classification']['near_unbounded'])
 def test_wad_cannot_be_exempted_as_na(self):
  s,i,q,spec,row,audit,off=self.fx;p=q['capacity_diagnostic']['validation_scope']['profiles'][policy.ON];p['non_applicable_resources']={'wad_entries':'TRADITIONAL_S_NO_BYPASS_ALLOCATION'};p['enlarged_resources'].remove('wad_entries')
  with self.assertRaises(ValueError):policy.qualification(q,digest)
 def test_capacity_failure_stops_admission_only(self):
  # Extract exactly the new guard; false for old FAILED, true for new FAILED;
  # no STOP.set()/signal/terminate calls are introduced in the controller patch.
  source=(P/'candidate/controller.py').read_text();tree=ast.parse(source)
  x=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test)=="result['status'] == 'FAILED' and capacity_policy.is_capacity_spec(spec)")
  guard=compile(ast.Expression(x.test),'<admission-guard>','eval')
  self.assertTrue(eval(guard,dict(result={'status':'FAILED'},spec={'budget_bucket':policy.BUCKET},capacity_policy=policy)))
  self.assertFalse(eval(guard,dict(result={'status':'FAILED'},spec={'budget_bucket':'main'},capacity_policy=policy)))
  self.assertEqual(ast.unparse(x.body[0]),'blocked = True');self.assertEqual(len(x.body),1)

if __name__=='__main__':unittest.main()

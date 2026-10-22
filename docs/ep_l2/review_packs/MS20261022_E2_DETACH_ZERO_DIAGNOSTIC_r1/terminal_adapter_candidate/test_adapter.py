"""SYNTHETIC adapter controls only; never actual native/application evidence."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import detach_validation as dv
sys.path.insert(0,'/tmp/e2_detach_runtime_decoder')
from decoder import Decoder
import test_decoder as wire

LEGACY=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/ft_lane5/validate.py')
spec=importlib.util.spec_from_file_location('original_bound_legacy_summary_for_synthetic_controls',LEGACY);vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)

def ref(path):return {'path':str(path),'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}
def write(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n');return ref(path)

class Fixture:
 def __init__(self,root):
  self.root=root;self.dir=root/'E_SYNTHETIC_NOT_AN_APPLICATION';self.dir.mkdir()
  self.raw=self.dir/'raw.log';self.raw.write_bytes(wire.encode(wire.rows(64)))
  self.source={'core_source_commit':'c'*40,'framework_source_commit':'d'*40,'vendor_pybind11_commit':'e'*40,'binary_sha256':'a'*64,'archive_sha256':'b'*64}
  features={'payload_capacity_per_slice':1168,'ops_per_bank_cycle':1,'wbuf_entries':16,'bank_count':4,'unified_wb':True,'tvd':True,'ro_tag_detach':True,'ro_line_mshr_bypass':True}
  ideal=dict.fromkeys(('copy_free','l2_data_free','mem_all_data','wb','meta','read_hit'),False)
  self.identity={k:self.source[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')};self.identity.update(feature_vector=features,ideal_vector=ideal,runtime_config_sha256='1'*64,trace_content_sha256='2'*64,epoch_range={'scope':'full_application','epochs':'all'},workload='SYNTHETIC_NOT_REAL_SGEMM',termination_contract={'all_kernels':True,'normal_exit':True,'hardware_drained':True,'kind':'FULL_APPLICATION_MECHANISM_V2','timeout_seconds':10800})
  self.profile={'research_switches':dict.fromkeys(('W','V','T','M'),1),'feature_vector':features,'ideal_vector':ideal,'effective_options':{'-gpgpu_ep_l2_ro_manifest_sha256':'3'*64,'-gpgpu_ep_l2_ro_scope':'TRACE_MODEL_CLOSED_WORLD'}}
  marker=root/'not_a_production_parser.py';marker.write_text('# synthetic callback marker only, never executed as real parser\n')
  schema=copy.deepcopy(wire.SCHEMA);schema['source_commit']=self.source['core_source_commit'];sref=write(root/'schema_synthetic.json',schema)
  self.binding={'schema':'E2_DETACH_TERMINAL_ADAPTER_BINDING_V1','status':'SYNTHETIC_NOT_DEPLOYABLE','synthetic_fixture':True,'E_independently_reviewed':True,'scientific_scope':dv.SCI_SCOPE,'pair':False,'source_identity':self.source,'legacy_parser':ref(marker),'legacy_validator':ref(LEGACY),'observer_decoder':ref('/tmp/e2_detach_runtime_decoder/decoder.py'),'observer_schema':sref}
  self.contract={'validation_scope':self.binding,'trace_content_sha256':self.identity['trace_content_sha256'],'runtime_config_sha256':self.identity['runtime_config_sha256'],'input_selection_id':'SYNTHETIC_SELECTION','termination_contract':self.identity['termination_contract'],'expected_full_instructions':1658916864}
  parser=ref(Path(__file__).parent/'parse_detach_terminal.py')
  q={'status':'INDEPENDENTLY_QUALIFIED','qualified_by':'E','scientific_scope':dv.SCI_SCOPE,'synthetic_fixture':True,'source_identity':self.source,'supported_profiles':{'F':self.profile},'terminal_parser':parser,'detach_observer_diagnostic':self.contract}
  qref=write(root/'Q_SYNTHETIC_NOT_QUALIFICATION.json',q);self.qrow={**qref,'qualification':q}
  self.spec={'qualification_id':qref['sha256'],'scientific_scope':dv.SCI_SCOPE,'profile':'F','profile_semantics':self.profile,'identity':self.identity,'vendor_pybind11_commit':self.source['vendor_pybind11_commit'],'selection_id':'SYNTHETIC_SELECTION','parser':parser,'environment':{'EPL2_DETACH_DIAG':'1'}}
  self.audit={'qualification_sha256':qref['sha256'],'expected_full_instructions':1658916864,'comparison_invariants_sha256':'4'*64}
  self.legacy={'diagnostic_scope':'MECHANISM_STUDY_LOCAL_SERVICE_V1','cycles':100,'instructions':1658916864,'slices':64,'unique_requesters':64,'responses':64,'live_descriptors':0,'live_line_mshrs':0,'live_wad':0,'pending_lower_reads':0,'pending_returns':0,'pending_responses':0,'wb_created':0,'wb_lower_accepted':0,'wb_completed':0,'payload_capacity':1168*64,'payload_free':1168*64,'payload_roles':{'RESIDENT_OR_FILL':0,'BYPASS':0,'WB_STAGED':0,'TVD_VALID':0},'transient_payloads':0,'hardware_drained':True,'workload_termination':self.identity['termination_contract'],'requester_exact_once_audit':True,'data_correctness_qualification':True,'raw_log_sha256':hashlib.sha256(self.raw.read_bytes()).hexdigest(),'mechanism_metrics':{'full_mechanism_records':{'readonly':{str(i):{'summary':{'live':0,'detached':0,'manifest':'3'*64,'scope':'TRACE_MODEL_CLOSED_WORLD'},'closure':{'epoch_closed':1,'ro_live':0,'shared_descriptor_used':0,'shared_line_used':0},'resource':{'oracle':'TRACE_MODEL_CLOSED_WORLD'}} for i in range(64)}}}}
  boot='SYNTHETIC_BOOT_NOT_HOST';controller={'pid':100,'start_ticks':1000,'boot_id':boot};guardian={'pid':200,'start_ticks':2000,'boot_id':boot};native={'pid':300,'start_ticks':3000,'boot_id':boot}
  binding={'attempt_id':self.dir.name,'run_key':dv.sha(self.identity),'identity':self.identity,'qualification_id':self.spec['qualification_id'],'comparison_invariants_sha256':self.audit['comparison_invariants_sha256']}
  command=[str(self.dir/'accel-sim.out'),'-trace','SYNTHETIC_NOT_A_REAL_TRACE']
  self.docs={'NATIVE_EXIT':{'schema':'E2_NATIVE_WAITPID_DURABLE_EXIT_V1','native_process':native,'guardian_process':guardian,'controller_process':controller,'native_ppid':200,'wait_status':0,'exit_code':0,'exited_normally':True,'signaled':False,'signal':None,'core_dumped':False,'binding':binding,'command':command,'released_to_native':True,'stop_reason':None,'collector_signals':[],'collection_method':'direct-parent os.wait4; child reaped before durable receipt'},'NATIVE_EXECUTION_REQUEST':{'controller_process':controller,'binding':binding,'command':command,'directory':str(self.dir)},'NATIVE_EXECUTION_READY':{'native_process':native,'guardian_process':guardian,'controller_process':controller,'native_ppid':200,'binding':binding,'command':command},'NATIVE_EXECUTION_RELEASE':{'native_process':native,'controller_process':controller,'central_start_committed':True}}
  self.flush()
  self.adapter=dv.Adapter(self.binding,fixture_mode=True,legacy_parse=lambda raw,spec,q:copy.deepcopy(self.legacy),legacy_validate=vm.validate_summary,decoder_factory=Decoder)
 def flush(self):
  for k,v in self.docs.items():write(self.dir/(k+'.json'),v)
 def parse(self):return self.adapter.parse(self.raw,self.spec,self.qrow,self.audit)
 def validate(self,s):return self.adapter.validate_summary(s,self.spec,self.qrow,self.audit)

class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='e2_detach_adapter_SYNTHETIC_');self.addCleanup(self.tmp.cleanup);self.f=Fixture(Path(self.tmp.name))
 def test_valid_synthetic_pipeline_never_app_PASS(self):
  s=self.f.parse();r=self.f.validate(s);self.assertEqual(r['status'],'SYNTHETIC_ADAPTER_CONTROL_ONLY');self.assertIs(r['pair'],False);self.assertFalse(dv.INDEPENDENT_SCHEMA_VALIDATION_READY)
 def test_json_roundtrip_integer_slice_keys_stable(self):
  self.f.legacy['mechanism_metrics']['full_mechanism_records']['readonly']={int(k):v for k,v in self.f.legacy['mechanism_metrics']['full_mechanism_records']['readonly'].items()};s=json.loads(json.dumps(self.f.parse()));self.assertEqual(self.f.validate(s)['status'],'SYNTHETIC_ADAPTER_CONTROL_ONLY')
 def test_default_global_module_failclosed(self):
  with self.assertRaisesRegex(ValueError,'NOT_SOURCE_SCHEMA_BOUND'):dv.validate_summary({},self.f.spec,self.f.qrow,self.f.audit)
 def test_synthetic_binding_cannot_set_production_ready(self):
  with self.assertRaises(ValueError):dv.configure_binding(self.f.binding)
  self.assertFalse(dv.INDEPENDENT_SCHEMA_VALIDATION_READY)
 def test_original_parser_failure_propagates(self):
  def fail(*args):raise ValueError('original_ROC1_gate_failed')
  self.f.adapter.legacy_parse=fail
  with self.assertRaisesRegex(ValueError,'original_ROC1_gate_failed'):self.f.parse()
 def test_original_64slice_validator_still_called(self):
  self.f.legacy['slices']=63
  with self.assertRaisesRegex(ValueError,'64 slices'):self.f.parse()
 def test_original_request_response_validator_still_called(self):
  self.f.legacy['responses']=63
  with self.assertRaisesRegex(ValueError,'requester/response'):self.f.parse()
 def test_incomplete_full_instructions(self):
  self.f.legacy['instructions']-=1
  with self.assertRaisesRegex(ValueError,'instruction'):self.f.parse()
 def test_missing_observer_records(self):
  self.f.raw.write_text('SYNTHETIC_NO_OBSERVER\n')
  with self.assertRaisesRegex(ValueError,'observer framing'):self.f.parse()
 def test_changed_bound_schema(self):
  Path(self.f.binding['observer_schema']['path']).write_text('{}')
  with self.assertRaisesRegex(ValueError,'bytes changed'):self.f.parse()
 def test_wrong_profile_not_borrowed_F(self):
  self.f.spec['profile']='S'
  with self.assertRaisesRegex(ValueError,'profile/scope'):self.f.parse()
 def test_old_main61_rejected(self):
  b=copy.deepcopy(self.f.binding);b['source_identity']['binary_sha256']=dv.LEGACY_MAIN61
  with self.assertRaisesRegex(ValueError,'old main61'):dv.Adapter(b,fixture_mode=True,legacy_parse=lambda *a:{},legacy_validate=vm.validate_summary,decoder_factory=Decoder)
 def test_missing_durable_exit_not_process_disappearance(self):
  (self.f.dir/'NATIVE_EXIT.json').unlink()
  with self.assertRaisesRegex(ValueError,'NATIVE_EXIT'):self.f.parse()
 def test_native_exit_minus15(self):
  self.f.docs['NATIVE_EXIT']['exit_code']=-15;self.f.flush()
  with self.assertRaisesRegex(ValueError,'wait/exit'):self.f.parse()
 def test_native_stop_reason_even_exit0(self):
  self.f.docs['NATIVE_EXIT']['stop_reason']={'kind':'RESOURCE_LIMIT'};self.f.flush()
  with self.assertRaisesRegex(ValueError,'stopped'):self.f.parse()
 def test_native_boot_mismatch(self):
  self.f.docs=copy.deepcopy(self.f.docs);self.f.docs['NATIVE_EXIT']['native_process']['boot_id']='OTHER_BOOT';self.f.flush()
  with self.assertRaises(ValueError):self.f.parse()
 def test_native_start_ticks_mismatch(self):
  self.f.docs['NATIVE_EXIT']['native_process']=copy.deepcopy(self.f.docs['NATIVE_EXIT']['native_process']);self.f.docs['NATIVE_EXIT']['native_process']['start_ticks']+=1;self.f.flush()
  with self.assertRaises(ValueError):self.f.parse()
 def test_release_without_central_charge_refused(self):
  self.f.docs['NATIVE_EXECUTION_RELEASE']['central_start_committed']=False;self.f.flush()
  with self.assertRaisesRegex(ValueError,'centrally charged'):self.f.parse()
 def test_changed_receipt_after_parsing(self):
  s=self.f.parse();self.f.docs['NATIVE_EXIT']['native_ppid']=999;self.f.flush()
  with self.assertRaises(ValueError):self.f.validate(s)
 def test_ROC1_drain_missing(self):
  self.f.legacy['mechanism_metrics']['full_mechanism_records']['readonly']['0']['closure']['ro_live']=1
  with self.assertRaisesRegex(ValueError,'ROC1 not drained'):self.f.parse()
 def test_ROC1_missing_slice(self):
  del self.f.legacy['mechanism_metrics']['full_mechanism_records']['readonly']['63']
  with self.assertRaisesRegex(ValueError,'ROC1 exact64'):self.f.parse()
 def test_old_new_detached_disagreement(self):
  self.f.legacy['mechanism_metrics']['full_mechanism_records']['readonly']['0']['summary']['detached']=1
  with self.assertRaisesRegex(ValueError,'detached'):self.f.parse()
 def test_oracle_identity_mismatch(self):
  self.f.legacy['mechanism_metrics']['full_mechanism_records']['readonly']['0']['summary']['manifest']='f'*64
  with self.assertRaisesRegex(ValueError,'oracle'):self.f.parse()
 def test_observer_report_mutation(self):
  s=self.f.parse();s['detach_observer_diagnostic']['observer']['final_cycle']=101
  with self.assertRaisesRegex(ValueError,'report changed'):self.f.validate(s)
 def test_legacy_summary_mutation(self):
  s=self.f.parse();s['cycles']=101
  with self.assertRaisesRegex(ValueError,'projection changed'):self.f.validate(s)
 def test_pair_disguised_as_diagnostic(self):
  s=self.f.parse();s['detach_observer_diagnostic']['pair']=True
  with self.assertRaisesRegex(ValueError,'schema/pair'):self.f.validate(s)
 def test_Qbody_changed_without_hash_change(self):
  self.f.qrow['qualification']['source_identity']=dict(self.f.source,binary_sha256='f'*64)
  with self.assertRaisesRegex(ValueError,'Q body differs'):self.f.parse()
 def test_observer_env_off_refused(self):
  self.f.spec['environment']['EPL2_DETACH_DIAG']='0'
  with self.assertRaisesRegex(ValueError,'environment'):self.f.parse()

if __name__=='__main__':unittest.main()

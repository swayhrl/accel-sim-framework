"""Original-runner terminal adapter candidate. No registry/process/control API.

Default unbound. Root explicitly configures source/schema/parser evidence after
E qualification. This module never treats old main61 qualification as new Q.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

SCI_SCOPE='DETACH_OBSERVER_DIAGNOSTIC_POINT_V1'
LEGACY_MAIN61='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
INDEPENDENT_SCHEMA_VALIDATION_READY=False
_BINDING=None
_ADAPTER=None
META_CAP=4*1024**2


def require(ok,message):
 if not ok:raise ValueError(message)

def canonical(obj):
 # Normalize integer record keys exactly as a JSON subprocess boundary does.
 normalized=json.loads(json.dumps(obj,ensure_ascii=False,allow_nan=False),object_pairs_hook=unique)
 return json.dumps(normalized,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(obj):return hashlib.sha256(canonical(obj)).hexdigest()
def unique(pairs):
 out={}
 for k,v in pairs:require(k not in out,'duplicate metadata JSON key');out[k]=v
 return out

def small_bytes(ref):
 require(type(ref) is dict and type(ref.get('path')) is str and type(ref.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}',ref['sha256']),'invalid bound metadata ref')
 p=Path(ref['path']);require(p.is_file() and p.stat().st_size<=META_CAP,'bound metadata absent/oversized')
 b=p.read_bytes();require(hashlib.sha256(b).hexdigest()==ref['sha256'],'bound metadata bytes changed: '+str(p));return b

def small_json(ref):return json.loads(small_bytes(ref),object_pairs_hook=unique)
def load(ref,tag):
 small_bytes(ref)
 spec=importlib.util.spec_from_file_location(tag,ref['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def validate_native_documents(documents,spec,audit,result_directory_name):
 """Reconcile original small collector files; no process-state inference."""
 e,r,ready,release=(documents[k] for k in ('NATIVE_EXIT','NATIVE_EXECUTION_REQUEST','NATIVE_EXECUTION_READY','NATIVE_EXECUTION_RELEASE'))
 require(e.get('schema')=='E2_NATIVE_WAITPID_DURABLE_EXIT_V1','missing durable direct-parent schema')
 require(type(e.get('wait_status')) is int and e['wait_status']==0 and type(e.get('exit_code')) is int and e['exit_code']==0,'actual native wait/exit must be0')
 require(e.get('exited_normally') is True and e.get('signaled') is False and e.get('signal') is None and e.get('core_dumped') is False,'native signal/core or missing normal-exit evidence')
 require(e.get('released_to_native') is True and e.get('stop_reason') is None and e.get('collector_signals')==[],'native not normally released or stopped by supervisor')
 require(e.get('collection_method')=='direct-parent os.wait4; child reaped before durable receipt','unreviewed native exit collector')
 binding=e['binding'];require(binding==r['binding']==ready['binding'],'collector binding changed')
 require(binding.get('attempt_id')==result_directory_name and binding.get('identity')==spec['identity'] and binding.get('qualification_id')==spec['qualification_id'],'collector attempt/source/Q differs')
 require(binding.get('run_key')==sha(spec['identity']) and binding.get('comparison_invariants_sha256')==audit['comparison_invariants_sha256'],'collector run/comparison differs')
 if spec.get('operational_limits_override') is not None:require(binding.get('operational_limits_override')==spec['operational_limits_override'],'collector operational limit override differs')
 require(e['command']==r['command']==ready['command'] and e['command'],'collector real command differs')
 require(Path(r['directory']).name==result_directory_name and e['command'][0]==str(Path(r['directory'])/'accel-sim.out'),'native command not original owned binary snapshot')
 for name in ('native_process','guardian_process','controller_process'):
  p=e[name];require(type(p) is dict and type(p.get('pid')) is int and p['pid']>0 and type(p.get('start_ticks')) is int and p['start_ticks']>0 and type(p.get('boot_id')) is str and p['boot_id'],'incomplete PID/start_ticks/boot identity')
  require(p==ready[name],'ready/exit process identity differs '+name)
 require(e['controller_process']==r['controller_process']==release['controller_process'],'request/release controller differs')
 require(e['native_process']==release['native_process'] and release.get('central_start_committed') is True,'native release differs or not centrally charged')
 require(len({e[k]['pid'] for k in ('native_process','guardian_process','controller_process')})==3,'collector/native/controller are not distinct')
 require(len({e[k]['boot_id'] for k in ('native_process','guardian_process','controller_process')})==1,'collector boot identity differs')
 require(e['native_ppid']==e['guardian_process']['pid']==ready['native_ppid'],'native direct parent changed')
 return {'status':'DURABLE_NATIVE_DOCUMENT_CLOSURE_PASS','native_process':copy.deepcopy(e['native_process']),
 'not_a_process_exit_inference':True,'original_runner_collector_remains_authoritative':True}


class Adapter:
 def __init__(self,binding,*,fixture_mode=False,legacy_parse=None,legacy_validate=None,decoder_factory=None):
  self.binding=copy.deepcopy(binding);self.fixture_mode=fixture_mode
  require(type(binding) is dict and binding.get('schema')=='E2_DETACH_TERMINAL_ADAPTER_BINDING_V1','missing exact source/schema binding')
  require(binding.get('scientific_scope')==SCI_SCOPE and binding.get('pair') is False,'adapter is one diagnostic point, not pair')
  require(binding.get('E_independently_reviewed') is True,'E independent adapter binding not sealed')
  if fixture_mode:require(binding.get('synthetic_fixture') is True,'fixture is explicitly synthetic')
  else:require(binding.get('synthetic_fixture') is False and binding.get('status')=='E_SOURCE_SCHEMA_ADAPTER_SEALED','real root seal required')
  self.source=binding['source_identity']
  for k,n in [('core_source_commit',40),('framework_source_commit',40),('vendor_pybind11_commit',40),('binary_sha256',64),('archive_sha256',64)]:
   require(type(self.source.get(k)) is str and re.fullmatch('[0-9a-f]{'+str(n)+'}',self.source[k]),'bad source identity '+k)
  require(self.source['binary_sha256']!=LEGACY_MAIN61,'old main61 cannot qualify new observer runtime')
  for key in ('legacy_parser','legacy_validator','observer_decoder','observer_schema'):
   small_bytes(binding[key])
  self.schema=small_json(binding['observer_schema'])
  require(self.schema.get('source_commit')==self.source['core_source_commit'],'observer schema not bound to actual Core')
  if not fixture_mode:require(all(fn is None for fn in (legacy_parse,legacy_validate,decoder_factory)),'production cannot inject arbitrary callbacks')
  self.legacy_parse=legacy_parse or load(binding['legacy_parser'],'_e_detach_bound_legacy_parser').parse
  self.legacy_validate=legacy_validate or load(binding['legacy_validator'],'_e_detach_bound_legacy_validator').validate_summary
  self.decoder_factory=decoder_factory or load(binding['observer_decoder'],'_e_detach_bound_observer_decoder').Decoder
 def check(self,spec,qrow,audit=None):
  b=self.binding
  for key in ('legacy_parser','legacy_validator','observer_decoder','observer_schema'):small_bytes(b[key])
  q=qrow['qualification'];qbytes=small_bytes({'path':qrow['path'],'sha256':qrow['sha256']})
  require(json.loads(qbytes,object_pairs_hook=unique)==q,'registered Q body differs from exact file')
  require(spec['qualification_id']==qrow['sha256'],'spec does not bind exact new Q')
  if audit is not None:require(audit['qualification_sha256']==qrow['sha256'],'runner input audit Q differs')
  require(q.get('status')=='INDEPENDENTLY_QUALIFIED' and q.get('qualified_by')=='E' and q.get('scientific_scope')==SCI_SCOPE,'new E diagnostic qualification missing')
  require(q.get('synthetic_fixture') is self.fixture_mode,'synthetic/real Q scope mismatch')
  require(q['source_identity']==self.source,'Q source differs from new observer producer')
  contract=q.get('detach_observer_diagnostic',{});require(contract.get('validation_scope')==b,'Q does not seal this exact adapter/source/schema binding')
  require(spec.get('scientific_scope')==SCI_SCOPE and spec.get('profile')=='F','wrong diagnostic profile/scope')
  require(not spec.get('pair_id') and spec.get('pairs',[])==[],'observer point cannot claim a pair')
  require(spec['profile_semantics']==q['supported_profiles']['F'],'new F profile not independently qualified')
  i=spec['identity'];require(all(i[k]==self.source[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')),'runtime source/binary differs')
  require(spec['vendor_pybind11_commit']==self.source['vendor_pybind11_commit'],'vendor differs')
  p=spec['profile_semantics'];require(p['research_switches']==dict.fromkeys(('W','V','T','M'),1),'fullF W/V/T/M not exact')
  require(i['feature_vector']==p['feature_vector'] and i['ideal_vector']==p['ideal_vector'],'profile feature/ideal identity differs')
  f=i['feature_vector'];require(f['payload_capacity_per_slice']==1168 and f['ops_per_bank_cycle']==1 and f['wbuf_entries']==16 and f['bank_count']==4 and f['unified_wb'] is True and f['tvd'] is True and f['ro_tag_detach'] is True and f['ro_line_mshr_bypass'] is True,'finite physical F organization differs')
  require(not any(i['ideal_vector'].values()),'idealized service forbidden in observer F')
  require(spec['environment'].get('EPL2_DETACH_DIAG')=='1','observer environment not enabled')
  require(i['trace_content_sha256']==contract['trace_content_sha256'] and i['runtime_config_sha256']==contract['runtime_config_sha256'],'new input/config identity differs')
  require(spec['selection_id']==contract['input_selection_id'] and i['termination_contract']==contract['termination_contract'],'whole input/termination differs')
  require(type(contract['expected_full_instructions']) is int and contract['expected_full_instructions']>0,'missing complete instruction denominator')
  require(spec['parser']==q['terminal_parser'],'runner parser differs from new Q')
  small_bytes(spec['parser'])
  if audit is not None:require(audit['expected_full_instructions']==contract['expected_full_instructions'],'runner complete instruction denominator differs')
  # No binary/raw/trace read here; original runner.inspect revalidates actual bytes.
  return contract
 def native_files(self,raw,spec,audit):
  parent=Path(raw).parent;docs={};refs={}
  for key in ('NATIVE_EXIT','NATIVE_EXECUTION_REQUEST','NATIVE_EXECUTION_READY','NATIVE_EXECUTION_RELEASE'):
   p=parent/(key+'.json');require(p.is_file() and p.stat().st_size<=META_CAP,'missing small native boundary receipt '+key)
   b=p.read_bytes();refs[key]={'path':str(p),'sha256':hashlib.sha256(b).hexdigest()};docs[key]=json.loads(b,object_pairs_hook=unique)
  closure=validate_native_documents(docs,spec,audit,parent.name)
  return {'documents':docs,'refs':refs,'closure':closure,'directory_name':parent.name}
 def parse(self,raw,spec,qrow,audit):
  self.check(spec,qrow,audit)
  # The exact original parser retains all applicable FT/B0/MS/TVD/RO/ROC1,
  # commandlist, structural/native gate checks. No compatibility bypass.
  legacy=self.legacy_parse(raw,spec,qrow['qualification'])
  require(self.legacy_validate(legacy,spec['identity'])['status']=='PASS','original global terminal validator failed')
  with Path(raw).open('rb') as stream:
   observer=self.decoder_factory(self.schema).decode(stream)
  require(observer.get('status')=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY','observer framing/terminal not valid')
  native=self.native_files(raw,spec,audit)
  result=copy.deepcopy(legacy);result['diagnostic_scope']=SCI_SCOPE
  result['detach_observer_diagnostic']={'schema':'E2_DETACH_NORMALIZED_TERMINAL_V1','source_identity':copy.deepcopy(self.source),
   'qualification_id':spec['qualification_id'],'pair':False,'binding_sha256':sha(self.binding),
   'legacy_summary_sha256':sha(legacy),'legacy_diagnostic_scope':legacy.get('diagnostic_scope'),'observer':observer,'native_boundary':native,
   'observer_sha256':sha(observer),'raw_log_sha256':legacy['raw_log_sha256']}
  self.validate_summary(result,spec,qrow,audit)
  return result
 def validate_summary(self,summary,spec,qrow,audit):
  contract=self.check(spec,qrow,audit)
  require(summary.get('diagnostic_scope')==SCI_SCOPE,'not an exact new observer terminal point')
  require(self.legacy_validate(summary,spec['identity'])['status']=='PASS','original64slice terminal validation failed')
  require(summary['instructions']==contract['expected_full_instructions'] and summary['instructions']==audit['expected_full_instructions'],'full instruction scope not complete')
  d=summary['detach_observer_diagnostic'];require(d['schema']=='E2_DETACH_NORMALIZED_TERMINAL_V1' and d['pair'] is False,'wrong observer point schema/pair')
  require(d['source_identity']==self.source and d['qualification_id']==spec['qualification_id'] and d['binding_sha256']==sha(self.binding),'observer source/Q/adapter binding differs')
  require(d['legacy_diagnostic_scope']=='MECHANISM_STUDY_LOCAL_SERVICE_V1','unreviewed legacy normalized scope')
  legacy=copy.deepcopy(summary);legacy.pop('detach_observer_diagnostic');legacy['diagnostic_scope']=d['legacy_diagnostic_scope']
  require(sha(legacy)==d['legacy_summary_sha256'],'original complete terminal projection changed')
  observer=d['observer'];require(observer['status']=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY' and observer.get('data_kind')=='REAL_UNACCEPTED','synthetic or unvalidated observer report')
  require(sha(observer)==d['observer_sha256'],'observer report changed')
  require(observer['expected_slice_count']==64 and observer['require_closed'] is True and observer['final_cycle']==summary['cycles'],'observer incomplete or native clock mismatch')
  require(observer['schema_counter_fields']==self.schema['counter_fields'],'observer decoded different schema')
  require(d['raw_log_sha256']==summary['raw_log_sha256'],'legacy/observer raw provenance differs')
  # Reuse original parser's already-normalized complete RO/ROC1 records, not
  # fabricated aggregate-only booleans. Missing records fail closed.
  ro=summary['mechanism_metrics']['full_mechanism_records']['readonly']
  require(set(ro)==set(range(64)) or set(ro)=={str(i) for i in range(64)},'original ROC1 exact64slice records missing')
  for sid in range(64):
   row=ro[sid] if sid in ro else ro[str(sid)];close=row['closure'];old=row['summary'];resource=row['resource']
   require(close['epoch_closed']==1 and close['ro_live']==close['shared_descriptor_used']==close['shared_line_used']==0,'original ROC1 not drained')
   require(old['live']==0 and old['detached']==observer['slice_counters'][str(sid)]['detach_success'],'old/new detached or RO live mismatch')
   require(old['manifest']==spec['profile_semantics']['effective_options']['-gpgpu_ep_l2_ro_manifest_sha256'] and old['scope']==resource['oracle']==spec['profile_semantics']['effective_options']['-gpgpu_ep_l2_ro_scope'],'exact positive oracle scope/hash mismatch')
  native=d['native_boundary']
  for key,ref in native['refs'].items():require(small_json(ref)==native['documents'][key],'native boundary receipt changed')
  validate_native_documents(native['documents'],spec,audit,native['directory_name'])
  return {'status':'SYNTHETIC_ADAPTER_CONTROL_ONLY' if self.fixture_mode else 'PASS',
   'scientific_scope':SCI_SCOPE,'pair':False,'qualification_id':spec['qualification_id'],
   'scope':'Original applicable full-app64slice/ROC1 closure plus exact observer schema and durable native boundary.',
   'not_validated_here':'Original runner.inspect actual source/main/config/input/lease/resource recheck remains mandatory; no numerical recapture or performance comparison inferred.'}


def configure_binding(binding):
 global _BINDING,_ADAPTER,INDEPENDENT_SCHEMA_VALIDATION_READY
 require(_ADAPTER is None,'observer adapter already bound')
 instance=Adapter(binding,fixture_mode=False)
 _BINDING=copy.deepcopy(binding);_ADAPTER=instance;INDEPENDENT_SCHEMA_VALIDATION_READY=True


def validate_summary(summary,spec,qrow,audit):
 require(INDEPENDENT_SCHEMA_VALIDATION_READY and _ADAPTER is not None,'DETACH_OBSERVER_VALIDATOR_NOT_SOURCE_SCHEMA_BOUND')
 return _ADAPTER.validate_summary(summary,spec,qrow,audit)

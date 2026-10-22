"""New r5 diagnostic adapter. Default unbound. No registry or execution authority.
Old212 syntax compatibility is not old-source qualification. All source/spec/Q
checks below bind the actual new producer, independently from frame base_core.
"""
import copy,hashlib,importlib.util,json,re,sys
from pathlib import Path
SCI_SCOPE='TAGPRESSURE_OBSERVER_DIAGNOSTIC_POINT_V1'
BASE='9243f769620653f2a9d4df5599e9581e9dae6067'
OLD647='647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4'
_BINDING=None;_ADAPTER=None;INDEPENDENT_SCHEMA_VALIDATION_READY=False
CAP=4*2**20
REF_KEYS=('legacy_parser','legacy_validator','legacy_model_helpers','observer_decoder','math_audit','fixed_r4_decoder','fixed_r4_syntax_schema','r4_syntax_compatibility_proof','observer_schema','producer_release','native_release','source_review')
def require(ok,message):
 if not ok:raise ValueError(message)
def unique(pairs):
 out={}
 for k,v in pairs:require(k not in out,'duplicate JSON key');out[k]=v
 return out
def canon(x):return json.dumps(json.loads(json.dumps(x,allow_nan=False)),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(x):return hashlib.sha256(canon(x)).hexdigest()
def small(ref):
 require(isinstance(ref,dict) and isinstance(ref.get('path'),str) and re.fullmatch('[0-9a-f]{64}',ref.get('sha256','')),'invalid metadata/source ref')
 p=Path(ref['path']);require(p.is_file() and p.stat().st_size<=CAP,'bound small file absent/oversized');b=p.read_bytes();require(hashlib.sha256(b).hexdigest()==ref['sha256'],'bound file changed '+str(p));return b
def jref(ref):return json.loads(small(ref),object_pairs_hook=unique)
def load(ref,name):
 small(ref);spec=importlib.util.spec_from_file_location(name,ref['path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Adapter:
 def __init__(self,binding):
  self.binding=copy.deepcopy(binding);b=self.binding
  require(b.get('schema')=='E2_TAGPRESSURE_TERMINAL_ADAPTER_BINDING_V1' and b.get('scientific_scope')==SCI_SCOPE,'new r5 binding schema/scope required')
  require(b.get('status')=='E_SOURCE_SCHEMA_ADAPTER_SEALED' and b.get('E_independently_reviewed') is True and b.get('synthetic_fixture') is False and b.get('pair') is False,'real independent E r5 seal missing')
  self.source=b['source_identity']
  for k,n in [('core_source_commit',40),('framework_source_commit',40),('vendor_pybind11_commit',40),('binary_sha256',64),('archive_sha256',64)]:require(isinstance(self.source.get(k),str) and re.fullmatch('[0-9a-f]{'+str(n)+'}',self.source[k]),'actual new source identity '+k)
  require(self.source['core_source_commit']!=BASE and self.source['binary_sha256'] not in ('d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13','61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'),'old r4/main61 cannot qualify newr5')
  for k in REF_KEYS:small(b[k])
  require(b['fixed_r4_decoder']['sha256']==OLD647,'fixed212 decoder changed')
  self.schema=jref(b['observer_schema']);require(self.schema['schema_id']=='EPL2_TAGPRESSURE_V1_R5' and self.schema['base_core']==BASE,'wire schema base is compatibility anchor only')
  self.compat_schema=jref(b['fixed_r4_syntax_schema']);require(self.compat_schema['source_commit']==BASE and len(self.compat_schema['counter_fields'])==212,'unchanged212 syntax schema only')
  proof=jref(b['r4_syntax_compatibility_proof'])
  require(proof.get('status')=='E_R5_OLD212_EMITTER_COMPATIBILITY_VERIFIED' and proof.get('source_identity')==self.source and proof.get('fixed_decoder_sha256')==OLD647 and proof.get('syntax_schema_source_commit')==BASE and proof.get('parser_role')=='UNCHANGED_212_SYNTAX_ONLY' and proof.get('old_212_emitter_unchanged') is True and proof.get('old_qualification_inherited') is False,'actual r5 source compatibility proof missing; no source projection')
  producer=jref(b['producer_release']);native=jref(b['native_release']);review=jref(b['source_review'])
  require(producer.get('source_identity')==self.source and producer.get('status')=='R5_PRODUCER_RELEASED_PENDING_E_APPLICATION_QUALIFICATION','actual r5 formal producer release missing')
  require(native.get('source_identity')==self.source and native.get('status')=='R5_TARGETED_NATIVE_PASS_NOT_FULL_APPLICATION','actual r5 targeted native evidence missing')
  require(review.get('source_identity')==self.source and review.get('status')=='E_R5_PASSIVE_SOURCE_REVIEW_PASS','actual r5 passive source review missing')
  self.helpers=load(b['legacy_model_helpers'],'_r5_original_native_helpers');self.legacy_parse=load(b['legacy_parser'],'_r5_original_model_parser').parse;self.legacy_validate=load(b['legacy_validator'],'_r5_original_model_validator').validate_summary
  # Dependency path is explicit, checked and source-bound; no production callback injection.
  ddir=str(Path(b['observer_decoder']['path']).parent);mathpath=Path(b['math_audit']['path']).resolve();require(mathpath.parent==Path(ddir).resolve(),'r5 decoder/math package split')
  if ddir not in sys.path:sys.path.insert(0,ddir)
  self.decoder=load(b['observer_decoder'],'_r5_bound_additive_decoder');require(self.decoder.SCHEMA_SHA256==b['observer_schema']['sha256'],'compiled r5 wire schema hash differs')
  mathmod=sys.modules.get('math_audit');require(mathmod is not None and Path(mathmod.__file__).resolve()==mathpath,'r5 math module path differs')
  require(hashlib.sha256(mathpath.read_bytes()).hexdigest()==b['math_audit']['sha256'],'r5 math dependency changed')
  self.fixed=load(b['fixed_r4_decoder'],'_r5_unchanged_212_syntax_decoder')
 def check(self,spec,qrow,audit=None):
  b=self.binding
  for k in REF_KEYS:small(b[k])
  q=qrow['qualification'];require(jref({'path':qrow['path'],'sha256':qrow['sha256']})==q,'exact registered r5 Q file differs')
  require(spec['qualification_id']==qrow['sha256'] and q.get('status')=='INDEPENDENTLY_QUALIFIED' and q.get('qualified_by')=='E' and q.get('scientific_scope')==SCI_SCOPE and q.get('synthetic_fixture') is False,'new E r5 Q missing')
  require(q['source_identity']==self.source,'new Q producer identity differs');c=q['detach_observer_diagnostic'];require(c['validation_scope']==b,'new Q exact validation scope differs')
  require(spec.get('scientific_scope')==SCI_SCOPE and spec.get('profile')=='F' and not spec.get('pair_id') and spec.get('pairs',[])==[],'new F diagnostic point only')
  i=spec['identity'];require(all(i[k]==self.source[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')) and spec['vendor_pybind11_commit']==self.source['vendor_pybind11_commit'],'actual new source/spec differs')
  p=spec['profile_semantics'];require(p==q['supported_profiles']['F'] and p['research_switches']==dict.fromkeys(('W','V','T','M'),1),'new F independently qualified profile differs')
  require(i['feature_vector']==p['feature_vector'] and i['ideal_vector']==p['ideal_vector'] and not any(i['ideal_vector'].values()),'new finite F feature identity differs')
  f=i['feature_vector'];require(f['payload_capacity_per_slice']==1168 and f['bank_count']==4 and f['ops_per_bank_cycle']==1 and f['wbuf_entries']==16 and all(f[k] is True for k in ('unified_wb','tvd','ro_tag_detach','ro_line_mshr_bypass')),'new F physical1168/P1 configuration differs')
  require(spec['environment'].get('EPL2_DETACH_DIAG')=='1' and spec['environment'].get('EPL2_TAGPRESSURE_DIAG')=='1','both independently enabled observers required')
  require(i['trace_content_sha256']==c['trace_content_sha256'] and i['runtime_config_sha256']==c['runtime_config_sha256'] and spec['selection_id']==c['input_selection_id'] and i['termination_contract']==c['termination_contract'],'exact input/config/selection/termination differs')
  require(type(c['expected_full_instructions']) is int and c['expected_full_instructions']>0 and isinstance(c['expected_kernel_uids'],list) and 0<len(c['expected_kernel_uids'])<=16,'full instruction/kernel denominator absent')
  require(all(type(uid) is int and 0<=uid<2**64 for uid in c['expected_kernel_uids']) and len(set(c['expected_kernel_uids']))==len(c['expected_kernel_uids']),'full kernel UID catalog malformed')
  require(spec['parser']==q['terminal_parser'],'new parser differs from Q');small(spec['parser'])
  if audit is not None:require(audit['qualification_sha256']==qrow['sha256'] and audit['expected_full_instructions']==c['expected_full_instructions'],'runner full input audit differs')
  return c
 def native_files(self,raw,spec,audit):
  docs={};refs={};parent=Path(raw).parent
  for key in ('NATIVE_EXIT','NATIVE_EXECUTION_REQUEST','NATIVE_EXECUTION_READY','NATIVE_EXECUTION_RELEASE'):
   p=parent/(key+'.json');require(p.is_file() and p.stat().st_size<=CAP,'native durable boundary absent '+key);refs[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};docs[key]=jref(refs[key])
  return {'documents':docs,'refs':refs,'directory_name':parent.name,'closure':self.helpers.validate_native_documents(docs,spec,audit,parent.name)}
 def parse(self,raw,spec,qrow,audit):
  c=self.check(spec,qrow,audit);legacy=self.legacy_parse(raw,spec,qrow['qualification']);require(self.legacy_validate(legacy,spec['identity'])['status']=='PASS','original fullmodel validator failed')
  feed=self.decoder.Feed(expected_slices=list(range(64)),registered_slice_count=64,expected_kernels=c['expected_kernel_uids'],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=self.source,old212_decoder_sha256=OLD647)
  with Path(raw).open('rb') as stream:old=self.fixed.Decoder(self.compat_schema).decode(self.decoder.TappingReader(stream,feed))
  new=feed.finish(old);require(new['status']=='VALID_R5_OBSERVER_DECLARATIONS_ONLY','r5 additive framing/math invalid: '+str(new.get('reason')))
  require(new['raw_log_sha256']==legacy['raw_log_sha256'],'same raw changed between model and observer passes')
  native=self.native_files(raw,spec,audit);out=copy.deepcopy(legacy);out['diagnostic_scope']=SCI_SCOPE
  d={'schema':'E2_TAGPRESSURE_NORMALIZED_TERMINAL_V1','source_identity':self.source,'qualification_id':spec['qualification_id'],'pair':False,'binding_sha256':sha(self.binding),'legacy_summary_sha256':sha(legacy),'legacy_diagnostic_scope':legacy.get('diagnostic_scope'),'r4_compat_observer':old,'r5_observer':new,'r4_compat_observer_sha256':sha(old),'r5_observer_sha256':sha(new),'native_boundary':native,'raw_log_sha256':legacy['raw_log_sha256']};out['tagpressure_observer_diagnostic']=d;self.validate_summary(out,spec,qrow,audit);return out
 def validate_summary(self,summary,spec,qrow,audit):
  c=self.check(spec,qrow,audit);require(summary.get('diagnostic_scope')==SCI_SCOPE,'wrong new diagnostic scope')
  require(self.legacy_validate(summary,spec['identity'])['status']=='PASS','original64/fullmodel terminal invalid')
  require(summary['instructions']==c['expected_full_instructions']==audit['expected_full_instructions'],'full instruction denominator differs')
  d=summary['tagpressure_observer_diagnostic'];require(d['schema']=='E2_TAGPRESSURE_NORMALIZED_TERMINAL_V1' and d['pair'] is False and d['source_identity']==self.source and d['qualification_id']==spec['qualification_id'] and d['binding_sha256']==sha(self.binding),'new normalized source/Q/binding differs')
  legacy=copy.deepcopy(summary);legacy.pop('tagpressure_observer_diagnostic');legacy['diagnostic_scope']=d['legacy_diagnostic_scope'];require(d['legacy_diagnostic_scope']=='MECHANISM_STUDY_LOCAL_SERVICE_V1' and sha(legacy)==d['legacy_summary_sha256'],'original fullmodel projection changed')
  old=d['r4_compat_observer'];new=d['r5_observer'];require(sha(old)==d['r4_compat_observer_sha256'] and sha(new)==d['r5_observer_sha256'],'normalized observer changed')
  require(old['status']=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY' and old['expected_slice_count']==64 and old['require_closed'] is True,'old212 compatibility did not fully decode64')
  require(new['status']=='VALID_R5_OBSERVER_DECLARATIONS_ONLY' and new['source_binding_external']==self.source and new['schema_sha256']==self.binding['observer_schema']['sha256'] and new['fixed_r4_decoder_sha256']==OLD647,'newr5 decode/source binding invalid')
  self.decoder.audit_normalized_result(new,old)
  require(new['full_application_mode'] is True and new['selected_slices']==list(range(64)) and new['registered_slice_count']==64 and new['global_closure_declared'] is True and new['global_epoch_closed_declared'] is True,'newr5 global64 not closed')
  require(old['final_cycle']==new['final_cycle']==summary['cycles'] and new['raw_log_sha256']==d['raw_log_sha256']==summary['raw_log_sha256'],'observer clock/raw identity differs')
  ro=summary['mechanism_metrics']['full_mechanism_records']['readonly'];require(set(map(str,ro))==set(map(str,range(64))),'ROC1 slice64 absent')
  for sid in range(64):
   row=ro[sid] if sid in ro else ro[str(sid)];cl=row['closure'];prior=row['summary'];res=row['resource'];require(cl['epoch_closed']==1 and cl['ro_live']==cl['shared_descriptor_used']==cl['shared_line_used']==prior['live']==0,'ROC1 not drained')
   require(prior['detached']==old['slice_counters'][str(sid)]['detach_success'],'newsource old212/authoritative detached differs')
   require(prior['manifest']==spec['profile_semantics']['effective_options']['-gpgpu_ep_l2_ro_manifest_sha256'] and prior['scope']==res['oracle']==spec['profile_semantics']['effective_options']['-gpgpu_ep_l2_ro_scope'],'oracle complete scope differs')
  for key,ref in d['native_boundary']['refs'].items():require(jref(ref)==d['native_boundary']['documents'][key],'durable boundary changed')
  self.helpers.validate_native_documents(d['native_boundary']['documents'],spec,audit,d['native_boundary']['directory_name'])
  return {'status':'PASS','scientific_scope':SCI_SCOPE,'qualification_id':spec['qualification_id'],'pair':False,'scope':'Actual newsource fullinput/model64/ROC1/native closure plus unchanged212 syntax and additive r5 truejoint; no old Q inherited.'}

def configure_binding(binding):
 global _BINDING,_ADAPTER,INDEPENDENT_SCHEMA_VALIDATION_READY
 require(_ADAPTER is None,'new r5 adapter already bound');instance=Adapter(binding);_BINDING=copy.deepcopy(binding);_ADAPTER=instance;INDEPENDENT_SCHEMA_VALIDATION_READY=True

def validate_summary(summary,spec,qrow,audit):
 require(INDEPENDENT_SCHEMA_VALIDATION_READY and _ADAPTER is not None,'R5_VALIDATOR_NOT_NEW_SOURCE_SCHEMA_BOUND');return _ADAPTER.validate_summary(summary,spec,qrow,audit)

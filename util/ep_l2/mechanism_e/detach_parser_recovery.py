"""Exact source-bound supplemental review; no run, retry, Q registration or rewrite.

Default unbound. Root seals the actual completed E051/parser-repair/full terminal
review metadata after independent review. Original execution receipts stay FAILED.
"""
import copy,hashlib,json,importlib.util
from pathlib import Path
FINAL_RECOVERY_REF={'path': '/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/parser_recovery/RECOVERY_MANIFEST.json', 'sha256': '2f3e647754fd5b9a3b5383f67d4af89bcc27a5e7009de1d207d32b9f3eb8353a'}
FIELD='detach_parser_engineering_revalidation'
SCOPE='DETACH_OBSERVER_DIAGNOSTIC_POINT_V1'
def require(ok,msg):
 if not ok:raise ValueError(msg)
def sha(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def content(ref):
 p=Path(ref['path']);require(p.stat().st_size<4*2**20,'metadata oversized')
 b=p.read_bytes();require(hashlib.sha256(b).hexdigest()==ref['sha256'],'recovery metadata changed')
 return b
def read(ref):return json.loads(content(ref))
def frozen(item):
 return dict(attempts_sha256=sha(item['attempts']),qualifications_sha256=sha(item['qualifications']),accepted_pairs_sha256=sha(item['accepted_pairs']),workload_batches_sha256=sha(item['workload_pipeline_batches']))
def manifest():
 require(FINAL_RECOVERY_REF is not None,'PARSER_RECOVERY_SOURCE_BINDING_UNAVAILABLE')
 m=read(FINAL_RECOVERY_REF)
 require(m['schema']=='E2_EXACT_E051_PARSER_ENGINEERING_RECOVERY_V1' and m['synthetic_fixture'] is False and m.get('status')=='E_SOURCE_BOUND_SUPPLEMENTAL_REVIEW_SEALED','real E parser recovery seal required')
 require(m['maximum_new_actual_starts']==0 and m['automatic_retry_authorized'] is False and m['pair'] is False,'recovery is metadata only')
 return m

def check(item,m):
 require(item['actual_starts']==len(item['attempts'])==51,'preserve51 charge')
 require(frozen(item)==m['frozen'],'original attempts/Q/pairs/workload changed')
 a=item['attempts'][-1]
 require(a['attempt_id']==m['attempt_id'] and a['state']=='FAILED' and a['actual_start'] is True,'original failed execution retained')
 require(a['run_key']==m['run_key'] and a['identity']==m['identity'] and a['qualification_id']==m['qualification_id'],'original run/source/Q changed')
 require(a['diagnostic_spec_sha256']==m['diagnostic_spec_sha256'] and a['receipt_sha256']==m['original_failed_receipt']['sha256'],'original spec/failed receipt changed')
 require(sha({k:v for k,v in item['accepted_results'].items() if k!=a['attempt_id']})==m['old_accepted_results_sha256'],'old accepted results changed')
 q=item['qualifications'][a['qualification_id']]
 require(q['sha256']==m['qualification']['sha256'] and q['path']==m['qualification']['path'],'no substitute Q')
 for r in [m['original_failed_receipt'],m['qualification'],m['original_spec'],m['native_exit'],*m['engineering_evidence']]:content(r)
 original=read(m['original_failed_receipt']);native=read(m['native_exit']);spec=read(m['original_spec'])
 require(original['status']=='FAILED' and original['attempt_id']==a['attempt_id'],'old failed status retained')
 require(native['exit_code']==native['wait_status']==0 and native['stop_reason'] is None and native['released_to_native'] is True,'actual durable exit0 required')
 require(native['native_process']==a['process'] and native['guardian_process']==a['exit_collector_process'],'original native/collector identity')
 require(native['binding']['identity']==a['identity'] and native['binding']['qualification_id']==a['qualification_id'] and native['binding']['attempt_id']==a['attempt_id'],'original durable input/Q binding')
 require(spec['identity']==a['identity'] and spec['qualification_id']==a['qualification_id'],'original spec Q/identity')
 require(sha({k:v for k,v in spec.items() if k!='input_audit'})==m['diagnostic_spec_sha256'],'original full spec semantic hash')
 require(original['raw_log_sha256']==m['raw_log_sha256'],'raw identity changed')
 return a

FIXED_DECODER_SHA256='647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4'
def stream_raw(path,expected_bytes,expected_sha):
 p=Path(path);require(type(expected_bytes) is int and 0<expected_bytes<=384*2**20,'bounded actual raw size required')
 require(p.stat().st_size==expected_bytes,'raw actual byte count changed')
 h=hashlib.sha256();count=0
 with p.open('rb') as f:
  while True:
   b=f.read(1024*1024)
   if not b:break
   count+=len(b);require(count<=384*2**20,'raw grew beyond endpoint cap');h.update(b)
 require(count==expected_bytes and h.hexdigest()==expected_sha,'actual raw stream digest mismatch')
def same_process(identity):
 try:
  stat=Path('/proc',str(identity['pid']),'stat').read_text()
  ticks=int(stat[stat.rfind(')')+2:].split()[19])
  boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
  return ticks==identity['start_ticks'] and boot==identity['boot_id']
 except (FileNotFoundError,ProcessLookupError):return False

def execution_checks(m,a):
 """Expensive execution truth checks occur once at append, never on snapshots."""
 directory=Path(a['result_directory']);raw=directory/'raw.log'
 require(m['raw_path']==str(raw),'original raw path only')
 stream_raw(raw,m['raw_bytes'],m['raw_log_sha256'])
 require(not same_process(a['process']) and not same_process(a['exit_collector_process']),'native/collector identity still alive')
 names={'NATIVE_EXIT':'NATIVE_EXIT.json','NATIVE_EXECUTION_REQUEST':'NATIVE_EXECUTION_REQUEST.json','NATIVE_EXECUTION_READY':'NATIVE_EXECUTION_READY.json','NATIVE_EXECUTION_RELEASE':'NATIVE_EXECUTION_RELEASE.json'}
 docs={}
 for key,name in names.items():
  ref=m['durable_documents'][key];require(ref['path']==str(directory/name),'original durable document path only');docs[key]=read(ref)
 require(m['durable_documents']['NATIVE_EXIT']==m['native_exit'],'exit receipt ref mismatch')
 spec=read(m['original_spec']);audit=spec['input_audit']
 # Root seals the original already-reviewed validator, not arbitrary callbacks.
 vr=m['engineering_bindings']['durable_validator'];require(vr['sha256']=='93466cb2379cb3c618299674403b747727ba98f840b6db1a17755d2c51d09fd8','original durable validator required');content(vr)
 module_spec=importlib.util.spec_from_file_location('_exact_e2_recovery_durable_validator',vr['path']);module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
 require(module.validate_native_documents(docs,spec,audit,directory.name)['status']=='DURABLE_NATIVE_DOCUMENT_CLOSURE_PASS','four-document native boundary failed')

def engineering_checks(m):
 b=m['engineering_bindings'];q=read(m['qualification']);old=q['detach_observer_diagnostic']['validation_scope']
 require(b['fixed_decoder']['sha256']==FIXED_DECODER_SHA256,'exact reviewed lifecycle decoder required')
 require(b['legacy_parser']==old['legacy_parser'] and b['observer_schema']==old['observer_schema'],'original parser/schema source semantics retained')
 for ref in b.values():content(ref)
 summary=read(b['terminal_summary']);validation=read(b['independent_validation']);schema=read(b['observer_schema'])
 require(validation.get('synthetic_fixture') is False and validation['status']=='PASS' and validation['validation']['status']=='PASS','actual E independent validation proof required')
 require(validation['identity']==m['identity'] and validation['qualification_id']==m['qualification_id'] and validation['raw_log_sha256']==m['raw_log_sha256'],'independent proof input/Q/raw mismatch')
 require(validation['terminal_summary_ref']==b['terminal_summary'] and validation['fixed_decoder_ref']==b['fixed_decoder'] and validation['legacy_parser_ref']==b['legacy_parser'],'independent proof exact decoder/parser/summary binding')
 require(summary['raw_log_sha256']==m['raw_log_sha256'] and summary['instructions']==1658916864 and type(summary['cycles']) is int and summary['cycles']>0,'complete actual SGEMM summary required')
 obs=summary['detach_observer_diagnostic']['observer'];fields=schema['counter_fields']
 require(obs['status']=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY' and obs['data_kind']=='REAL_UNACCEPTED' and obs['expected_slice_count']==64 and obs['require_closed'] is True,'real complete observer summary required')
 require(len(fields)==212 and obs['schema_counter_fields']==fields and obs['final_cycle']==summary['cycles'],'exact212 schema/native cycle required')
 slices=obs['slice_counters'];glob=obs['global_counters']
 require(set(slices)==set(map(str,range(64))) and set(glob)==set(fields),'exact64 counter membership required')
 for sid,row in slices.items():
  require(set(row)==set(fields) and all(type(v) is int and v>=0 for v in row.values()),'missing or invalid per-slice counters')
 for field in fields:
  require(type(glob[field]) is int and glob[field]>=0 and glob[field]==sum(row[field] for row in slices.values()),'global64 counter rollup failed')
 return validation

def accepted_record(m):
 return dict(path=m['supplemental_review']['path'],sha256=m['supplemental_review']['sha256'],run_key=m['run_key'],identity=m['identity'],qualification_id=m['qualification_id'],scientific_scope=SCOPE,acceptance_basis='PARSER_ENGINEERING_SUPPLEMENTAL_REVALIDATION',original_execution_status='FAILED',original_failed_receipt=m['original_failed_receipt'])

def allowed_revalidated_results(item):
 if FIELD not in item:return set()
 m=manifest();a=check(item,m)
 content(m['supplemental_review'])
 for ref in m['engineering_bindings'].values():content(ref)
 require(item[FIELD]==dict(manifest_ref=FINAL_RECOVERY_REF,supplemental_review=m['supplemental_review'],attempt_id=a['attempt_id'],status='ACCEPTED_SUPPLEMENTAL_DIAGNOSTIC'),'exact supplemental record changed')
 require(item['accepted_results'].get(a['attempt_id'])==accepted_record(m),'supplemental accepted pointer changed')
 require('qualification:'+a['qualification_id'] not in item.get('scientific_holds',{}),'unresolved qualification HOLD')
 return {a['attempt_id']}

def append(data,item):
 m=manifest();a=check(item,m)
 require(item['controller']['state']=='STOPPED','original controller must stop')
 run=data['runs'][a['run_key']]
 require(sha(run)==m['original_canonical_run_sha256'] and run['status']=='FAILED','original failed canonical row preserved')
 require('qualification:'+a['qualification_id'] not in item.get('scientific_holds',{}),'explicit original hold resolution required first')
 engineering_checks(m)
 execution_checks(m,a)
 review=read(m['supplemental_review'])
 require(review['reviewed_by']=='E' and review['status']=='COMPLETE_VALID_SUPPLEMENTAL_DIAGNOSTIC' and review['attempt_id']==a['attempt_id'],'exact E supplemental acceptance')
 require(review['identity']==a['identity'] and review['qualification_id']==a['qualification_id'] and review['raw_log_sha256']==m['raw_log_sha256'],'supplemental source/Q/raw mismatch')
 require(review['terminal_summary_ref']==m['engineering_bindings']['terminal_summary'] and review['independent_validation_ref']==m['engineering_bindings']['independent_validation'],'supplemental engineering proof binding')
 require(review['independent_acceptance']=='PASS' and review['complete_input_verified'] is True and review['validation']['status']=='PASS','complete independent terminal validation required')
 require(review['original_execution_status']=='FAILED' and review['new_application_starts']==0 and review['pair'] is False,'supplemental preserves failure; no science expansion')
 require(all(review['closure'][k] is True for k in ('normal_native_exit0','full_instructions','all_kernels','all_64_slices','hardware_drained','resources_retired','source_config_input_unchanged','positive_ro_scope_unchanged','fixed_decoder_source_bound','original_native_binding_validated')),'full terminal gates missing')
 rec=accepted_record(m);row=dict(manifest_ref=FINAL_RECOVERY_REF,supplemental_review=m['supplemental_review'],attempt_id=a['attempt_id'],status='ACCEPTED_SUPPLEMENTAL_DIAGNOSTIC')
 if FIELD in item:
  allowed_revalidated_results(item);return False
 require(a['attempt_id'] not in item['accepted_results'],'already accepted by another path')
 item[FIELD]=row;item['accepted_results'][a['attempt_id']]=rec
 item.setdefault('parser_engineering_revalidation_history',[]).append(copy.deepcopy(row))
 allowed_revalidated_results(item)
 return True

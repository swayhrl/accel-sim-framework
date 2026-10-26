#!/usr/bin/env python3
"""Pure new-source terminal/NI validator. Never launches, registers or writes acceptance."""
import sys
sys.dont_write_bytecode=True
import argparse,array,ast,copy,hashlib,importlib.util,json,pathlib,re
import lifetime_parser as life
P=pathlib.Path
ROOT=P('/root/data/ep_tag_reservation_lifetime_20261026_v1')
OLD=P('/root/data/ep_l2_main_vector_r5_20261023_v1')
NATIVE=P('/root/data/ep_l2_dtc_l1_native_v2')
SOURCEQ=P('/root/data/ep_tag_reservation_lifetime_20261026_v1/control/SOURCE_QUALIFICATION_V2.json')
SOURCEQ_SHA='8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814'
HEADER_SHA='d88efa5012f1bd24c0b55be42504c1b8e3727bcabdf46a2c96385ee61082b8e1'
IDENTITY={'archive_sha256': '685b497b50328deff4b96741c9a770b4b37e5d4bb2c8a1b5db90558b90be73c4', 'binary_sha256': '8d55f19bbe74c72e5da688f0ede6c2de1c3aa13040015475f23c9c6c521b9bef', 'core_source_commit': '11c02df1034112013523429894f1f931323adbef', 'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7', 'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'}
SOURCE_TAR_SHA='99b876285fef26539ef464b751cdee9bcd754e8101815f57df56e830fed37a17'
GOAL='EP_L2_TAG_RESERVATION_LIFETIME_CAUSAL_V1'
ROLES={'EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2': False, 'EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2': True}
COMMON=NATIVE/'EP/control/parse_main_terminal.py'
FT=NATIVE/'EP/src/owner-control/util/ep_l2/ft_lane5'
PINS={str(COMMON):'f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e',str(FT/'parse_unified_terminal.py'):'536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b',str(FT/'validate.py'):'08a7396a6e11893dbbcb982725765a6c9b12194b1e01e3f0dc70d337f85dd500',str(OLD/'control/HISTORICAL_VECTOR_SPEC.json'):'462d2f35368cfebceda39053df8e3b79246f2d5a3b40c81a0603f3182752c453',str(OLD/'sources/r5/decoder.py'):'65731a6df85e9821994e4efea84ea5473e482e6f1c2bb385c9b8abdf00aefcff',str(OLD/'sources/r5/math_audit.py'):'f55b4f911a321aae2f22fd2b017e5bcef270847adf24968d7d1e0791401d5ae0',str(OLD/'sources/r5/WIRE_CONTRACT.json'):'cb973b3bc462ce33895a0f8cc31b428f6bf14b63f8497e8895eb314ea0894db7',str(OLD/'sources/r4/decoder_samecycle_close.py'):'647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4',str(OLD/'sources/r4/SOURCE_BOUND_SCHEMA_r4.json'):'2c070214ed8d0f3738014f7c0a3a0386d0199defad3f4a2b2d4d3343b8707ba2'}
class InvalidEvidence(ValueError):pass
def need(ok,why):
 if not ok:raise InvalidEvidence(why)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_bytes(),parse_constant=lambda n:(_ for _ in ()).throw(InvalidEvidence('nonfinite JSON '+n)))
def _json_keys(obj):
 if isinstance(obj,dict):
  out={}
  for key,value in obj.items():
   need(type(key) in (str,int),'non-JSON semantic dictionary key')
   name=str(key);need(name not in out,'semantic key collision after JSON serialization');out[name]=_json_keys(value)
  return out
 if isinstance(obj,(list,tuple)):return [_json_keys(x) for x in obj]
 return obj

def canonical(obj):return json.dumps(_json_keys(obj),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def doc(value):return read(value) if isinstance(value,(str,P)) else copy.deepcopy(value)
def verify_pins():
 need(sha(life.__file__)=='7b3f119b019a93dda216f994a4b805a6c118f25619b3cb41b747d42773937abe','reviewed lifetime parser code changed')
 need(sha(P(__file__).resolve().parent/'wire_contract.json')=='ff13db1b2ff841e1f6358a0bdb0f9d93f68e6e932ec815adca2efff22de14bd2','reviewed lifetime contract changed')
 for path,h in PINS.items():need(sha(path)==h,'frozen parser/reference source changed: '+path)
def sourceq(path=SOURCEQ,expected_sha=SOURCEQ_SHA):
 need(str(P(path).resolve())==str(SOURCEQ.resolve()) and expected_sha==SOURCEQ_SHA,'unreviewed SourceQ path/SHA')
 need(P(path).is_file() and sha(path)==expected_sha,'SourceQ absent or SHA changed')
 q=read(path)
 need(q.get('schema')=='EP_L2_TAG_LIFETIME_SOURCE_QUALIFICATION_V1' and q.get('status')=='SOURCEQ_CPU_PASS_NOT_APPLICATION_ACCEPTED','explicit reviewed SourceQ status missing')
 need(q.get('goal')==GOAL and q.get('qualified_by')=='EP-MAIN' and q.get('source_identity')==IDENTITY and q.get('header_sha256')==HEADER_SHA,'SourceQ source/header/owner mismatch')
 need(q.get('source_tar_sha256')==SOURCE_TAR_SHA,'source tar identity missing; not staticlib archive identity')
 need(q.get('application_start_permission_issued_by_this_qualification') is False and q.get('scientific_acceptance_granted') is False and q.get('full_application_qualified') is False,'SourceQ must not impersonate app authority')
 refs=q.get('evidence_refs');need(type(refs) is dict and bool(refs),'SourceQ evidence references absent')
 for name,ref in refs.items():need(type(ref) is dict and P(ref['path']).is_file() and sha(ref['path'])==ref['sha256'],'SourceQ evidence changed: '+name)
 return q

def _function(text,name):
 tree=ast.parse(text);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
 return ''.join(text.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
def _assignment(text,name):
 for x in ast.parse(text).body:
  if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets):return ast.literal_eval(x.value)
 raise InvalidEvidence('missing frozen assignment '+name)
def numeric_parser():
 """Extract pure frozen functions; never import old coordinator/controller modules."""
 verify_pins();text=COMMON.read_text();original=_function(text,'parse')
 authority_marker="    require(qualification['campaign_id']"
 body_marker='    native={};final={};frames={}'
 need(original.count(authority_marker)==1 and original.count(body_marker)==1,'frozen function splice contract changed')
 prefix=original[:original.index(authority_marker)]
 oldcall='    policy_v2.combination_qualification(qualification,digest)\n'
 need(prefix.count(oldcall)==1,'frozen old authority call absent/ambiguous');prefix=prefix.replace(oldcall,'')
 body=original[original.index(body_marker):]
 patched=prefix+'    _new_authority(qualification,identity)\n'+body
 ns={'Path':P,'re':re,'require':need,'digest':sha,'_new_authority':lambda q,i:need(q['status']=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED' and q['qualified_by']=='EP-MAIN' and all(q['source_identity'][n]==i[n]==IDENTITY[n] for n in IDENTITY),'new exact native authority required')}
 for name in ['REASONS','PROFILES','EXEMPT']:ns[name]=_assignment(text,name)
 for x in ast.parse(text).body:
  if isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Attribute) and isinstance(x.value.func.value,ast.Name) and x.value.func.value.id=='PROFILES' and x.value.func.attr=='update':ns['PROFILES'].update(ast.literal_eval(x.value.args[0]))
 validator=(FT/'validate.py').read_text();ns['SUMMARY_FIELDS']=_assignment(validator,'SUMMARY_FIELDS');ns['integer']=lambda x:type(x) is int and x>=0
 exec(compile(_function(validator,'validate_summary'),'FROZEN_VALIDATE_SUMMARY','exec'),ns)
 exec(compile(_function((FT/'parse_unified_terminal.py').read_text(),'parse_structure'),'FROZEN_PARSE_STRUCTURE','exec'),ns)
 for name in ['numbers','full_numbers','validate_full_records']:exec(compile(_function(text,name),'FROZEN_'+name,'exec'),ns)
 exec(compile(patched,'NEW_EP_LIFETIME_AUTHORITY_UNCHANGED_NUMERIC_BODY','exec'),ns)
 return ns['parse'],{'frozen_parser_sha256':PINS[str(COMMON)],'unchanged_numeric_body_sha256':hashlib.sha256(body.encode()).hexdigest(),'original_parse_function_sha256':hashlib.sha256(original.encode()).hexdigest(),'new_authority_parse_sha256':hashlib.sha256(patched.encode()).hexdigest(),'change':'old E authority preamble replaced explicitly; full numeric body retained byte-for-byte','old_E_qualification_inherited':False,'controller_imported':False}

def rebound_history(s):
 """Actual fresh hist must already be rebound; guard scientific fields, then set all5."""
 h=read(s['historical_spec_path']);old=read(OLD/'control/HISTORICAL_VECTOR_SPEC.json')
 need(h['profile']==old['profile']=='F' and h['profile_semantics']==old['profile_semantics'],'unqualified profile/scientific options changed')
 oldscience={k:v for k,v in old['identity'].items() if k not in IDENTITY};newscience={k:v for k,v in h['identity'].items() if k not in IDENTITY}
 need(newscience==oldscience,'historical scientific feature/input/config/termination changed')
 need(all(h['identity'].get(n)==v for n,v in IDENTITY.items()),'fresh hist.identity must completely rebind all5 source fields')
 need(h.get('vendor_pybind11_commit')==IDENTITY['vendor_pybind11_commit'],'fresh history vendor missing')
 if isinstance(h.get('binary'),dict):need(h['binary'].get('sha256',h['binary'].get('binary_sha256'))==IDENTITY['binary_sha256'],'fresh history binary field stale')
 elif isinstance(h.get('binary'),str):need(P(h['binary']).resolve()==P(s['binary_path']).resolve() and sha(h['binary'])==IDENTITY['binary_sha256'],'fresh history string binary path/digest stale')
 else:need(False,'fresh history binary field missing')
 h=copy.deepcopy(h);h['identity'].update(IDENTITY)
 return h

def printed(raw):
 options={}
 for line in P(raw).open(errors='replace'):
  if line.startswith(('launching ','EPL2ROV1|COMMANDLIST_BEGIN')):break
  m=re.match(r'^(-[^\s]+)\s+(.*?)\s+#',line)
  if m:
   k,v=m.groups();v=' '.join(v.split());need(k not in options or options[k]==v,'conflicting printed option');options[k]=v
 need(len(options)==282,'actual282 printed options required');return options

def _module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def r4r5(raw):
 math=_module(OLD/'sources/r5/math_audit.py','_ep_life_frozen_math');prior=sys.modules.get('math_audit');sys.modules['math_audit']=math
 try:r5=_module(OLD/'sources/r5/decoder.py','_ep_life_frozen_r5')
 finally:
  if prior is None:sys.modules.pop('math_audit',None)
  else:sys.modules['math_audit']=prior
 r4=_module(OLD/'sources/r4/decoder_samecycle_close.py','_ep_life_frozen_r4');schema=read(OLD/'sources/r4/SOURCE_BOUND_SCHEMA_r4.json')
 feed=r5.Feed(expected_slices=list(range(64)),registered_slice_count=64,expected_kernels=[1],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=IDENTITY,old212_decoder_sha256=r5.FIXED_R4_SHA256)
 with P(raw).open('rb') as stream:old=r4.Decoder(schema).decode(r5.TappingReader(stream,feed))
 need(old['status']=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY','invalid fixed r4 terminal')
 new=feed.finish(old);need(new['status']=='VALID_R5_OBSERVER_DECLARATIONS_ONLY','invalid fixed r5 terminal');r5.audit_normalized_result(new,old)
 return old,new

class NullCSV:
 def write(self,text):return len(text)

def lifetime(raw,enabled):
 k=read(P(__file__).resolve().parent/'wire_contract.json');need(k['header_sha256']==HEADER_SHA and sha(P(__file__).resolve().parent/k['header_snapshot'])==HEADER_SHA,'lifetime contract/header changed')
 p=life.Parser(k,NullCSV(),NullCSV(),64) if enabled else None
 delta=array.array('i',[0])*4096;minimum=array.array('i',[0])*4096;maximum=array.array('i',[0])*4096;found=False;h=hashlib.sha256()
 with P(raw).open('rb') as f:
  for lineno,line in enumerate(f,1):
   h.update(line)
   if not line.startswith(b'EPL2LIFEV1|'):continue
   found=True;need(enabled,'observer OFF emitted lifetime data');kind,d=life.record(line,k);p.consume(kind,d,len(line))
   if kind=='WINDOW_SET':
    slot=int(d['slice'])*64+int(d['set']);v=life.vec(d['c'],15);next_delta=delta[slot]+v[0]-v[1];need(-16<=next_delta<=16,'window reservation delta outside associativity');delta[slot]=next_delta;minimum[slot]=min(minimum[slot],delta[slot]);maximum[slot]=max(maximum[slot],delta[slot])
   elif kind=='SET':
    slot=int(d['slice'])*64+int(d['set']);v=life.vec(d['c'],55);left=v[k['counters'].index('LEFT')];right=v[k['counters'].index('RIGHT')]
    need(0<=left+minimum[slot] and left+maximum[slot]<=16 and left+delta[slot]==right,'window carry bounds/endpoint fail')
 if not enabled:need(not found,'OFF lifetime absence');return {'status':'OFF_NO_LIFETIME_RECORDS','raw_sha256':h.hexdigest(),'scientific_acceptance_granted':False}
 need(found,'ON lifetime absent');out=p.finish();out.update(raw_sha256=h.hexdigest(),header_sha256=HEADER_SHA,observer_enabled=True,strict_expected_slices=64,window_carry_checked=True,synthetic_fixture=False);return out

SCOPED={'EPL2B0V1':('slice',64),'EPL2M0AV1':('slice',64),'EPL2DRAMV1':('channel',32),'EPL2L1V1':('scope',1)}
SCALARS={'gpu_tot_sim_cycle','gpu_tot_sim_insn','gpu_tot_issued_cta','gpgpu_n_tot_thrd_icount','gpgpu_n_tot_w_icount','gpgpu_n_mem_read_global','gpgpu_n_mem_write_global','gpgpu_n_load_insn','gpgpu_n_store_insn','gpgpu_n_stall_shd_mem','gpgpu_n_l1cache_bkconflict','gpu_stall_dramfull','gpu_stall_icnt2sh','L1D_total_cache_accesses','L1D_total_cache_misses','L1D_total_cache_reservation_fails','L2_total_cache_accesses','L2_total_cache_misses','L2_total_cache_reservation_fails','icnt_total_pkts_simt_to_mem','icnt_total_pkts_mem_to_simt'}

def scoped_projection(raw,cycles):
 groups={x:{} for x in SCOPED};scalars={};kernels=[];printed_kernel_uids=[]
 for line in P(raw).open(errors='replace'):
  m=re.fullmatch(r'\s*([A-Za-z0-9_]+)\s*=\s*([0-9]+)\s*',line)
  if m and m[1] in SCALARS:scalars[m[1]]=int(m[2])
  m=re.fullmatch(r'kernel_name\s*=\s*(\S+)\s*',line)
  if m:kernels.append(m[1])
  m=re.fullmatch(r'kernel_launch_uid\s*=\s*(\d+)\s*',line)
  if m:printed_kernel_uids.append(int(m[1]))
  prefix=line.split('|',1)[0]
  if prefix not in groups or '|scope=application|' not in line:continue
  row={}
  for field in line.strip().split('|')[1:]:
   need(field.count('=')==1,'bad scoped field');key,value=field.split('=',1);need(key not in row,'duplicate scoped field');row[key]=value
  key=SCOPED[prefix][0];owner=int(row[key]) if key!='scope' else 0;groups[prefix][str(owner)]=row
 need(set(scalars)==SCALARS,'complete terminal/cache/request scalar set required')
 need(scalars['gpu_tot_sim_cycle']==cycles and scalars['gpu_tot_sim_insn']==56000000 and scalars['gpu_tot_issued_cta']==15625,'full actual instruction/CTA/cycle mismatch')
 need(kernels==['_Z6VecAddPKfS0_Pfi'] and printed_kernel_uids==[1],'exact kernel1 source events required')
 for prefix,(owner,count) in SCOPED.items():
  need(set(groups[prefix])=={str(i) for i in range(count)},'missing exact scoped population '+prefix)
  if prefix in ['EPL2B0V1','EPL2M0AV1']:
   need(all(int(row['completion_cycle'])==cycles for row in groups[prefix].values()),'scoped final clock mismatch '+prefix)
 return {'terminal_scalars':scalars,'scoped_application_records':groups,'kernel_names':kernels,'kernel_uids':printed_kernel_uids}

def _without_raw(value):
 out=dict(value) # Read-only nested data shared; remove top-level provenance only.
 for key in ['raw_log_sha256','input_bytes','line_number']:out.pop(key,None)
 return out

def validate_case(raw,spec,qualification,sourceq_path=SOURCEQ,sourceq_sha=SOURCEQ_SHA):
 """Return pending validation bundle only. Engine must first prove natural DONE/native identity."""
 sq=sourceq(sourceq_path,sourceq_sha);verify_pins();s=doc(spec);q=doc(qualification)
 need(s['cohort'] in ROLES and s['source_identity']==IDENTITY,'unqualified exact cohort/source')
 enabled=ROLES[s['cohort']];expected={'EPL2_DETACH_DIAG':'1','EPL2_TAGPRESSURE_DIAG':'1','EPL2_TAG_LIFETIME':'1' if enabled else '0'}
 need(s.get('observer_env')==expected,'only lifetime OFF/ON env is permitted')
 need(s.get('source_qualification_sha256')==SOURCEQ_SHA and P(s.get('source_qualification_path','')).resolve()==SOURCEQ.resolve(),'spec SourceQ binding')
 sp=P(spec) if isinstance(spec,(str,P)) else ROOT/'cases'/s['cohort']/'control/FROZEN_SPEC.json'
 need(sp.is_file() and read(sp)==s,'exact frozen spec path/content required')
 need(q.get('status')=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED' and q.get('qualified_by')=='EP-MAIN' and q.get('cohort')==s['cohort'] and q.get('spec_sha256')==sha(sp) and q.get('source_identity')==IDENTITY,'new exact prelaunch qualification required')
 need(sha(s['binary_path'])==IDENTITY['binary_sha256'],'new main ELF changed')
 for path,h in s['env_hashes'].items():need(sha(path)==h,'env/source input changed '+path)
 configs=sorted(P(path).name for path in s['env_hashes'] if P(path).name.startswith('config-'))
 need(configs==['config-0.config','config-1.config','config-2.config','config-3.config'],'exact four configs, no config4')
 for i in range(4):
  path=next(P(x) for x in s['env_hashes'] if P(x).name==f'config-{i}.config');need(path.read_bytes()==(OLD/'env'/path.name).read_bytes(),'old scientific config byte drift')
 need(s['input_trace_composite_sha256']=='138f33b61fffe99c5e9c31a5943a96edcab180e6aaaa5ed4714021249c0d2940','input composite changed')
 h=rebound_history(s);opts=printed(raw);oldopts=printed(OLD/'run/results/a6b61f77-2ff6-45ad-897c-df0812d01ae8/raw.log');need(opts==oldopts,'actual282 options changed from scientific baseline')
 for option,value in h['profile_semantics']['effective_options'].items():need(opts.get(option)==' '.join(str(value).split()),'profile option mismatch '+option)
 head=P(raw).open(errors='replace').read(32768);need('gpgpu-sim_git-commit-11c02df' in head and 'accelsim-commit-9dd1ee57' in head,'actual producer header missing/wrong')
 parser,authority=numeric_parser();model=parser(P(raw),h,q);need(model['instructions']==56000000 and model['slices']==64 and model['hardware_drained'] is True,'full model closure required')
 old,new=r4r5(raw);need(model['cycles']==old['final_cycle']==new['final_cycle'],'model/r4/r5 clocks disagree')
 need(model['raw_log_sha256']==new['raw_log_sha256']==sha(raw),'closed raw hash mismatch')
 for sid in range(64):
  row=model['mechanism_metrics']['full_mechanism_records']['readonly'][sid];summary=row['summary'];close=row['closure']
  need(close['epoch_closed']==1 and summary['live']==close['ro_live']==close['shared_descriptor_used']==close['shared_line_used']==0,'explicit all64 RO/shared closure join failed')
  need(summary['detached']==old['slice_counters'][str(sid)]['detach_success'],'RO/r4 detach_success all64 join failed')
 need(new['global_record']['kernel_catalog']==[1],'r5 kernel catalog must beUID1')
 wire=lifetime(raw,enabled);need(wire['raw_sha256']==model['raw_log_sha256'],'lifetime/model raw mismatch')
 common=scoped_projection(raw,model['cycles'])
 model['source_map']['mechanism']='Frozen MSV1/MSV2/TVD/RO format numeric decoder; actual producing Core11c/main0090 is bound by fresh SourceQ, not the legacy descriptor text'
 model['source_map']['data']='New EP-MAIN exact SourceQ65147 and prelaunch authority; trace-model conditional correctness, no old E/native acceptance or numeric SASS validation inherited'
 authority.update(source_qualification_path=str(SOURCEQ),source_qualification_sha256=SOURCEQ_SHA,source_identity=copy.deepcopy(IDENTITY),source_tar_sha256=SOURCE_TAR_SHA,archive_identity='libgpgpusim.a static library; source tar separate',hist_identity_fully_rebound=True)
 semantic={'model':_without_raw(model),'R4':_without_raw(old),'R5':_without_raw(new),'application_scopes':common}
 return {'status':'NEW_SOURCE_APPLICATION_VALIDATED_PENDING_MAIN_ACCEPTANCE','scientific_acceptance_granted_by_C':False,'cohort':s['cohort'],'cycles':model['cycles'],'instructions':model['instructions'],'CTA':15625,'slices':64,'kernel_count':1,'hardware_drained':True,'raw_sha256':model['raw_log_sha256'],'source_identity':copy.deepcopy(IDENTITY),'observer_enabled':enabled,'observer_header_sha256':HEADER_SHA,'clock_domains_MHz':opts['-gpgpu_clock_domains'],'semantic_config_sha256':hashlib.sha256(canonical(opts)).hexdigest(),'semantic_config_scope':'all282 normalized actual printed options','source_qualification_sha256':SOURCEQ_SHA,'spec_sha256':sha(sp),'model':model,'R4':old,'R5':new,'LIFE':wire,'authority':authority,'semantic_projection':semantic,'semantic_projection_sha256':hashlib.sha256(canonical(semantic)).hexdigest(),'numeric_SASS_output_validation':'UNKNOWN'}

def require_semantic_equivalence(left,right):
 need(canonical(left)==canonical(right),'full scoped production semantics differ; no last-slice fallback')

def compare_pair(off,on):
 need(off['status']==on['status']=='NEW_SOURCE_APPLICATION_VALIDATED_PENDING_MAIN_ACCEPTANCE' and off['observer_enabled'] is False and on['observer_enabled'] is True,'validated exact OFF/ON required')
 need(off['source_identity']==on['source_identity']==IDENTITY and off['source_qualification_sha256']==on['source_qualification_sha256']==SOURCEQ_SHA,'same new source/authority required')
 require_semantic_equivalence(off['semantic_projection'],on['semantic_projection'])
 common=on['semantic_projection']['application_scopes'];pipeline_scalar_keys={'gpu_tot_sim_cycle','gpu_tot_sim_insn','gpu_tot_issued_cta','gpgpu_n_mem_read_global','gpgpu_n_mem_write_global','icnt_total_pkts_simt_to_mem','icnt_total_pkts_mem_to_simt','L1D_total_cache_accesses','L1D_total_cache_misses','L1D_total_cache_reservation_fails','L2_total_cache_accesses','L2_total_cache_misses','L2_total_cache_reservation_fails','gpu_stall_dramfull','gpu_stall_icnt2sh'};metrics={'terminal_scalars':{k:v for k,v in common['terminal_scalars'].items() if k in pipeline_scalar_keys},'requests_responses':{'unique_requesters':on['model']['unique_requesters'],'responses':on['model']['responses'],'RO_all64':on['model']['mechanism_metrics']['full_mechanism_records']['readonly']},'cache_behavior':{'full_application_scopes':common,'model':on['semantic_projection']['model'],'R4_all64_and_phases':on['semantic_projection']['R4'],'R5_all64_and_phases':on['semantic_projection']['R5']},'queue_behavior':common['scoped_application_records']}
 snapshots={role:{'schema':'EP_L2_LIFETIME_PRODUCTION_SEMANTIC_SNAPSHOT_V1','raw_sha256':item['raw_sha256'],'source_identity':copy.deepcopy(IDENTITY),'normalizer_sha256':sha(__file__),'metrics':metrics} for role,item in [('OFF',off),('ON',on)]}
 receipt={'status':'PASS_COMPLETE_OFF_ON_NONINTERFERENCE','goal':GOAL,'source_identity':copy.deepcopy(IDENTITY),'raw_sha256':{'OFF':off['raw_sha256'],'ON':on['raw_sha256']},'checks':{k:True for k in ['cycles','instructions','CTA','slices','drain','requests_responses','cache_queue_behavior','observer_switch_only']},'scope':'entire frozen numeric model plus all64r4/r5 phases and all64B0/M0,32DRAM,globalL1; not last overwritten scalar','source_qualification_sha256':SOURCEQ_SHA,'normalizer_code':{'path':str(P(__file__).resolve()),'sha256':sha(__file__)},'scientific_acceptance_granted_by_C':False,'engine_still_must_bind_native_DONE_and_write_accepted_receipts':True}
 return {'noninterference':receipt,'normalized_snapshots':snapshots,'normalized_snapshot_references_pending_engine_write':True,'scientific_acceptance_granted_by_C':False}

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--raw');a.add_argument('--spec');a.add_argument('--qualification');a.add_argument('--inspect-sourceq',action='store_true');z=a.parse_args()
 try:
  if z.inspect_sourceq:sourceq();result={'status':'SOURCEQ_CHECKED_ONLY_NOT_LAUNCH_OR_APPLICATION_AUTHORITY','source_qualification_sha256':SOURCEQ_SHA,'scientific_acceptance_granted_by_C':False}
  else:need(z.raw and z.spec and z.qualification,'raw/spec/qualification required');result=validate_case(z.raw,z.spec,z.qualification)
  print(json.dumps(result,sort_keys=True,indent=2))
 except (InvalidEvidence,life.InvalidWire,OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({'status':'HOLD_NOT_ACCEPTED','reason':str(e),'scientific_acceptance_granted_by_C':False}),file=sys.stderr);sys.exit(2)

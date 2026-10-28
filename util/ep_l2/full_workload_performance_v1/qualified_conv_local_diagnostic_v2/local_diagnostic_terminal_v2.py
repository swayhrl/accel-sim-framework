"""Pure bounded Source78 Conv diagnostic adapter; no actor or acceptance authority.
Existing frozen numeric body and rolling structural math are unchanged.
"""
import ast,copy,hashlib,importlib.util,json,pathlib,sys
sys.dont_write_bytecode=True
P=pathlib.Path;ROOT=P(__file__).resolve().parent
G_PATH=P('/root/data/ep_l2_full_workload_performance_20261027_v1/tools/qualified_geometry_queue_v1/geometry_queue_terminal.py')
G_SHA='a9d11c3f1e04ceb26849a8f083e2725ef0a4aa648916776d2d6ee353752000b9'
PARENT_SHA='2f23e6cb8125db87d51044b0ff94741fc4ea01eb9b7146827962d789b8538356'
FLAG={'COPY_FREE':'-gpgpu_ep_l2_diag_copy_free','L2_DATA_FREE':'-gpgpu_ep_l2_diag_l2_data_free'}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def exact(ref):
 need(sha(ref['path'])==ref['sha256'],'immutable evidence drift '+ref['path']);return read(ref['path'])
def load_g():
 need(sha(G_PATH)==G_SHA,'frozen G math dependency drift');sp=importlib.util.spec_from_file_location('isolated_local_diagnostic_G',G_PATH);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.verify_pins();return m
def parents():
 p=ROOT/'PARENT_BINDINGS.json';need(sha(p)==PARENT_SHA,'exact accepted parent bindings drift');return read(p)
def normalized(s):
 s=copy.deepcopy(s);s['expected_effective_options']['-gpgpu_ep_l2_diag_copy_free']='0';s['expected_effective_options']['-gpgpu_ep_l2_diag_l2_data_free']='0';return s

def qualify_history_spec(s):
 mode=s.get('mode');diag=s.get('local_diagnostic');need((mode,diag)in[('S','COPY_FREE'),('F','L2_DATA_FREE')],'only two selected Conv diagnostic points; no automatic matrix')
 parent=parents()[mode];ps=exact(parent['spec_ref']);point=exact(parent['accepted_point_ref']);bundle=exact(parent['bundle_ref'])
 need(point['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED'and point['validation_ref']==parent['bundle_ref'],'parent accepted point/bundle identity')
 need(point['source_identity']==ps['source_identity']==bundle['source_identity'],'parent source identity mismatch')
 need(s.get('diagnostic_parent_ref')==parent['accepted_point_ref'],'exact accepted own-mode mother point required')
 need(s['cohort']!=ps['cohort'],'new diagnostic cannot reuse mother cohort')
 for key in ['source_identity','mode','T','M','geometry','trace_entry','input_identity_sha256','expected_CTA','expected_instructions','expected_kernel_launches','binary_path','static_library_path','input_binding_ref']:
  need(s[key]==ps[key],'diagnostic parent background/input/source mismatch '+key)
 o=s['expected_effective_options'];base=ps['expected_effective_options'];need(len(o)==282 and set(o)==set(base)and all(type(v)is str for v in o.values()),'complete typed exact282')
 desired=dict(base);desired[FLAG[diag]]='1';need(o==desired,'only selected diagnostic flag may change from accepted own-mode parent')
 need(all(s['observer_env'].get(k)=='0'for k in ['EPL2_DETACH_DIAG','EPL2_TAGPRESSURE_DIAG','EPL2_TAG_LIFETIME','EP_L2_EVENT_TIMELINE']),'all4optionalOFF remains exact')
 g=load_g();physical=g.qualify_history_spec(normalized(s))
 return dict(schema='EP_SOURCE78_CONV_LOCAL_DIAGNOSTIC_MATH_BINDING_V1',mode=mode,diagnostic=diag,parent_accepted_ref=parent['accepted_point_ref'],parent_bundle_ref=parent['bundle_ref'],exact282_delta={FLAG[diag]:{'before':'0','after':'1'}},physical=physical,hardware_P1_throughput_eligible=False,diagnostic_app_positive='UNKNOWN_NOT_EXECUTED',numeric_body_changed=False,scientific_acceptance_granted=False)

def history_for(s):
 binding=qualify_history_spec(s);g=load_g();h=g.history_for(normalized(s));h['profile']='S_COPY_FREE'if binding['diagnostic']=='COPY_FREE'else'F_L2_DATA_FREE';h['profile_semantics']['effective_options']=s['expected_effective_options'];return h

def configured_base():
 g=load_g();base=g.configured_base();factory=base.frozen_c
 def new_factory():
  c=factory();c.history_for=history_for;return c
 base.frozen_c=new_factory
 return base

def numeric_math():return configured_base().numeric_math()

def strict_final_terminal_closure(raw):
 import gzip,re
 with P(raw).open('rb')as probe:compressed=probe.read(2)==b'\x1f\x8b'
 opener=gzip.open if compressed else open
 current=None;rows={}
 with opener(raw,'rt',errors='strict')as f:
  for line in f:
   m=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
   if m:
    clock=int(m[1]);need(current is None or clock>=current,'native clock regressed in closure join')
    if clock!=current:rows={}
    current=clock
   if line.startswith('EPL2FTV1|TERMINAL|'):
    need(current is not None,'terminal without native cycle');r={}
    for item in line.strip().split('|')[2:]:
     k,v=item.split('=',1);need(k not in r and v.isdigit(),'terminal duplicated/noninteger field');r[k]=int(v)
    sid=r['slice'];need(0<=sid<64,'terminal slice range');need(sid not in rows or rows[sid]==r,'same-final terminal conflict');rows[sid]=r
 need(current is not None and set(rows)==set(range(64)),'exact final64slice terminal closure join')
 for sid,r in rows.items():
  need(all(r[k]==0 for k in ['requester_live','pending_lower_reads','pending_returns','pending_responses']),'raw terminal live counter contradicts drain at slice '+str(sid))
  need(r['unique_requesters']==r['responses'] and r['requester_exact_once']==r['hardware_drained']==1,'raw requester equality/flags contradict source closure at slice '+str(sid))
 return {'final_cycle':current,'slices':64,'live_requesters':0,'all_pending_queues':0,'requester_unique_equals_responses':True,'source_evidence':'Source78 l2cache.cc2497-2504','separate_consistency_join_original_numeric_unchanged':True}

def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 s=read(spec)if isinstance(spec,(str,P))else copy.deepcopy(spec);binding=qualify_history_spec(s);base=configured_base();result=base.validate_case(raw,s,qualification,sourceq_path,sourceq_sha)
 closure=strict_final_terminal_closure(raw);need(closure['final_cycle']==result['cycles'],'raw closure/native cycle mismatch');result['raw_terminal_consistency_join']=closure
 m=result['model'];need(m['mechanism_metrics']['local_service']['physical_throughput_eligible']is False,'diagnostic may not claim hardware P1 result')
 flags=m['mechanism_metrics']['trigger']['diagnostic_flags'];need(flags=={'copy_free':s['local_diagnostic']=='COPY_FREE','l2_data_free':s['local_diagnostic']=='L2_DATA_FREE'},'actual diagnostic profile mismatch')
 result['local_diagnostic_math_binding']=binding;result['local_diagnostic_provenance']={'entry_sha256':sha(__file__),'frozen_geometry_queue_math_sha256':G_SHA,'parent_bindings_sha256':PARENT_SHA,'original_numeric_body_sha256':result['math_binding']['numeric_body_sha256'],'original_rolling_suffix_sha256':result['math_binding']['frozen_final_suffix_sha256'],'ownership_descriptor_RO_drain_math_unchanged':True,'physical_hardware_performance_result':False,'all_outer_native_and_archive_joins_still_required':True}
 need(result['scientific_acceptance_granted']is False,'pure math cannot accept application');return result

def local_component_checker():
 """Exact local flag/paid/exempt fragment from frozen numeric body; component only."""
 g=load_g();p=g.ROOT/'host_scaling/frozen_math/parse_main_terminal.py';need(sha(p)=='f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e','original numeric source drift');text=p.read_text();a="        require(o['enabled']==enabled and d['copy_free']==copy_free and d['l2_data_free']==data_free,'actual observer/diagnostic flags mismatch')";b='        if enabled:';start=text.index(a);end=text.index(b,start);fragment=text[start:end];fn='def check(o,d,enabled,copy_free,data_free):\n'+''.join('    '+line[8:]+'\n'for line in fragment.splitlines());ns={'require':need,'EXEMPT':('response','fill','lower_wb','frontend','copy_read','copy_write')};exec(compile(fn,'EXACT_FROZEN_LOCAL_DIAGNOSTIC_FRAGMENT','exec'),ns);return ns['check'],hashlib.sha256(fragment.encode()).hexdigest()

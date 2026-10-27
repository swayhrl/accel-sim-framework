"""Pure G/queue-only physical math adapter. No model/actor/acceptance authority.
All frozen physical mathsuffixes remain original bytes; actual option+geometry
mapping is qualified before the private history_for guard is replaced.
"""
import ast,hashlib,importlib.util,json,math,pathlib,re
P=pathlib.Path;ROOT=P(__file__).resolve().parent
PINS={'evidence/GEOMETRY_MAPPING_PROOF.json': '1a673e3d6154abdb0d56b66adcf6394f5119f1db3bec71586067dcbcd77f4de0', 'evidence/REFERENCE_282_BY_MODE.json': '8aef95b36823b3a52ab6aaaff2b3a01b3b4e193b21a8a91e7cfd241940e2a03d', 'evidence/SOURCE78_ACTUAL_CONSTRUCTOR_RESULT.json': '928e9185a2331cae661a6013043d77d540fe566d4271588084651c0580030c99', 'host_scaling/dynamic_observation_scaled.py': '4db737bf5bdc09532480e401001e39bc0de414c0b692c666542e8665a011ab25', 'host_scaling/lowcost_terminal_scaled.py': 'fdcaab0aef93363148a81257e548dd1cc58cc1369986cbfc809366ff83cd1df1', 'host_scaling/rolling_structure_core.py': 'b8f09af83cf2eb50933b46216f825593eb218c2a304a61ec7a624fc22f3f2066', 'host_scaling/PACKAGE_MANIFEST.json': '83a0ac96f6f26f0788a46cde210277e22222476157e74352d9ed41f0ae1be2c1', 'host_scaling/frozen_math/parse_main_terminal.py': 'f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e', 'host_scaling/frozen_math/lowcost_terminal_v2.py': 'cba193d8ec810219f58bbe55870814b70604082f4f6683a236a418e80b9da35c', 'host_scaling/frozen_math/ft_lane5/validate.py': '08a7396a6e11893dbbcb982725765a6c9b12194b1e01e3f0dc70d337f85dd500', 'host_scaling/frozen_math/ft_lane5/parse_unified_terminal.py': '536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b'}
VARIABLE_INPUT={'-trace','-gpgpu_ep_l2_ro_manifest','-gpgpu_ep_l2_ro_manifest_sha256','-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_ranges_sha256','-gpgpu_ep_l2_ro_scope'}
KNOBS={'-gpgpu_cache:dl1','-gpgpu_cache:dl2','-gpgpu_dram_partition_queues','-gpgpu_frfcfs_dram_sched_queue_size','-gpgpu_dram_return_queue_size','-dram_latency','-gpgpu_clock_domains','-icnt_in_buffer_limit','-icnt_out_buffer_limit'}

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def verify_pins():
 for rel,digest in PINS.items():need(sha(ROOT/rel)==digest,'geometry package drift '+rel)
 return {rel:{'path':str(ROOT/rel),'sha256':digest}for rel,digest in PINS.items()}
def load(rel,name):
 need(rel in PINS and sha(ROOT/rel)==PINS[rel],'unbound module')
 s=importlib.util.spec_from_file_location(name,ROOT/rel);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def qualify_history_spec(s):
 verify_pins();o=s['expected_effective_options'];g=s['geometry'];mode=s['mode'];need(mode in('S','F','WV_ZERO_RO'),'unreviewed mode')
 need(s.get('T')is(mode=='F')and s.get('M')is(mode=='F'),'formalT/Mdeclaredbool mismatch')
 proof=read(ROOT/'evidence/GEOMETRY_MAPPING_PROOF.json');cpu=read(ROOT/'evidence/SOURCE78_ACTUAL_CONSTRUCTOR_RESULT.json')
 need(s['source_identity']==proof['source_identity']==cpu['source_identity'],'constructor/mapping Source5 mismatch')
 need(cpu['status']=='ACTUAL_CONSTRUCTOR_CPU_CHECKS_PASS_NOT_APPLICATION_QUALIFICATION'and all(t['PASS']for t in cpu['tests']),'actualconstructor evidence notPASS')
 for rel,r in proof['source_file_refs'].items():need(sha(r['path'])==r['sha256'],'actualmappingSource bytes drift '+rel)
 need(set(g)=={'slices','sets','ways','line_bytes'}and all(type(v)is int for v in g.values()),'exacttyped geometry fields')
 need(g['slices']==64 and g['sets']in(32,64)and g['ways']in(8,16)and g['line_bytes']==128,'unqualified geometry')
 need(len(o)==282 and all(type(k)is str and type(v)is str for k,v in o.items()),'complete282 string options')
 reference=read(ROOT/'evidence/REFERENCE_282_BY_MODE.json')['S'if mode=='S'else'F']
 if mode=='WV_ZERO_RO':reference=dict(reference,**{'-gpgpu_ep_l2_ro_tag_detach':'0','-gpgpu_ep_l2_ro_line_mshr_bypass':'0'})
 need(set(o)==set(reference),'exact282 option keyset changed')
 for k,v in reference.items():
  if k not in VARIABLE_INPUT|KNOBS:need(o[k]==v,'undeclaredphysical/service/background option '+k)
 need(all(o[k]=='1'for k in('-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats')),'first matched lowcost statsprofile muststay1')
 need(all(s['observer_env'].get(k)=='0'for k in('EPL2_DETACH_DIAG','EPL2_TAGPRESSURE_DIAG','EPL2_TAG_LIFETIME','EP_L2_EVENT_TIMELINE')),'matched heavy-observer fourOFF profile')
 need(o['-trace']==s['trace_entry'],'input trace/actual option mismatch')
 l2=o['-gpgpu_cache:dl2'].split(',');need(len(l2)==5,'L2 tuple grammar')
 need(l2[0]==f"S:{g['sets']}:128:{g['ways']}"and l2[1]=='L:B:m:L:P'and l2[2]=='A:128:1'and l2[3]in('128:0','256:0')and l2[4]=='32','actualL2geometry/hash/policy/MSHR/MQ mismatch')
 l1=o['-gpgpu_cache:dl1'].split(',');need(len(l1)==5 and l1[:3]==['S:4:128:128','L:T:m:L:L','A:512:8']and l1[3]in('16:0','32:0')and l1[4]=='32','unqualified L1 geometry/MSHR/MQ')
 need(o['-gpgpu_n_mem']=='32'and o['-gpgpu_n_sub_partition_per_mchannel']=='2','actual32channels*2subparts mismatch')
 need(o['-gpgpu_dram_partition_queues']in('64:128:64:64','64:256:64:64'),'unqualifiedFIFO geometry')
 need(o['-gpgpu_frfcfs_dram_sched_queue_size']in('128','256')and o['-gpgpu_dram_return_queue_size']in('192','384'),'finite scheduler/return domain')
 need(o['-dram_latency']in('50','100','200'),'qualifiedfixed-delay domain')
 clocks=o['-gpgpu_clock_domains'].split(':');need(len(clocks)==4,'clockdomain tuple')
 values=[float(x)for x in clocks];need(all(math.isfinite(x)and x>0 for x in values),'finitepositive clockdomains')
 need(values[0]==values[2]==1132.0 and values[1]in(1132.0,1358.4)and values[3]in(850.0,935.0,1020.0),'CORE/L2 equality or qualifiedICNT/DRAMclock domain changed')
 need(o['-icnt_in_buffer_limit']==o['-icnt_out_buffer_limit']and o['-icnt_in_buffer_limit']in('512','1024'),'qualifiedpairedICNTpacket buffers')
 cases={t['case']:t for t in cpu['tests']};ctor=cases[f"G{g['sets']}W{g['ways']}_{'S'if mode=='S'else'F'}"]
 need(ctor['expected_success']is True and ctor['returncode']==0,'actualgeometryctor missing')
 for row in ctor['actual_fields']['L2']:
  need(row['sets']==str(g['sets'])and row['ways']==str(g['ways'])and row['all_sets_reached']=='1'and row['physical_payload_line_slots']=='1168'and row['MSHR']=='128'and row['descriptor']=='512'and row['WAD']=='128'and row['bank_ops_per_CORE_cycle']=='1','actualinitialproducergetter/map evidence mismatch')
 binding={'schema':'EP_FULL_PERF_G_QUEUE_PHYSICAL_MATH_BINDING_V1','geometry':g,'logical_tags_per_slice':g['sets']*g['ways'],'Tag_data_address_coverage_bytes_GPU':g['sets']*g['ways']*128*64,'modeled_physical_payload_line_slots_per_slice':1168,'modeled_physical_payload_data_bytes_GPU':1168*128*64,'resident_nominal':1024,'descriptor_capacity':512,'line_MSHR':128,'WAD':128,'banks':4,'bank_ops_per_CORE_cycle':1,'copy_latch_bytes_per_slice':128,'L1_MissQ':int(l1[3].split(':')[0]),'L2_MissQ':int(l2[3].split(':')[0]),'lower_FIFO':int(o['-gpgpu_dram_partition_queues'].split(':')[1]),'FRFCFS':int(o['-gpgpu_frfcfs_dram_sched_queue_size']),'DRAM_return':int(o['-gpgpu_dram_return_queue_size']),'general_shared_credit_per_channel':int(o['-gpgpu_frfcfs_dram_sched_queue_size'])+int(o['-gpgpu_dram_return_queue_size'])-1,'private_credit_per_channel':2,'separate_WB_progress_credit_per_channel':1,'clock_domains_MHz':values,'fixed_delay_CORE_cycles':int(o['-dram_latency']),'ICNT_packet_buffer_limits':int(o['-icnt_in_buffer_limit']),'Source5':s['source_identity'],'CPU_geometry_ctor_case':ctor['case'],'CPU_proof_SHA':PINS['evidence/SOURCE78_ACTUAL_CONSTRUCTOR_RESULT.json'],'mapping_proof_SHA':PINS['evidence/GEOMETRY_MAPPING_PROOF.json'],'queuecombinations':'constructor/source compositional math support; no application/performance acceptance','frequency_clock_initialization_executed_by_CPUfixture':False,'fixed_final_math_suffix_changed':False,'heavy_observer_opportunity':'ALL4_OFF_NOT_MEASURED_NOT_ZERO'}
 return binding

def private_history(c):
 text=(ROOT/'host_scaling/frozen_math/lowcost_terminal_v2.py').read_text();source=c.function(text,'history_for')
 marker="need(s['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128),'first physical geometry qualified only')"
 need(source.count(marker)==1,'frozenhistory geometry marker drift')
 adapted=source.replace(marker,'qualify_history_spec(s)')
 ns=dict(c.__dict__,qualify_history_spec=qualify_history_spec);exec(compile(adapted,'STRICT_GEOMETRY_JOIN_WITH_UNCHANGED_PHYSICAL_HISTORY','exec'),ns)
 return ns['history_for'],hashlib.sha256(source.encode()).hexdigest(),hashlib.sha256(adapted.encode()).hexdigest()

def configured_base():
 base=load('host_scaling/lowcost_terminal_scaled.py','isolated_scaled_base');factory=base.frozen_c
 def c_factory():
  c=factory();c.history_for=private_history(c)[0];return c
 base.frozen_c=c_factory
 return base

def history_for(s):
 binding=qualify_history_spec(s);base=configured_base();c=base.frozen_c();h=c.history_for(s);h['actual_tag_geometry']=binding['geometry'];return h

def numeric_math():return configured_base().numeric_math()

def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 s=read(spec)if isinstance(spec,(str,P))else dict(spec);binding=qualify_history_spec(s);base=configured_base();result=base.validate_case(raw,spec,qualification,sourceq_path,sourceq_sha)
 result['geometry_queue_math_binding']=binding
 result['geometry_queue_adapter_provenance']={'entry_sha256':sha(__file__),'dependencies':verify_pins(),'numeric_body_sha256':result['math_binding']['numeric_body_sha256'],'final_suffix_sha256':result['math_binding']['frozen_final_suffix_sha256'],'defaultphysicalhistory_math_unchanged':True,'actual282_and_Tag_mapping_prejoin':True,'original_C2_geometry_guard_replaced_only_after_strict_join':True,'scientific_acceptance_granted':False}
 need(result['scientific_acceptance_granted']is False,'puremathmaynotaccept')
 return result

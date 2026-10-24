"""Independent exact native case8 admission; does not launch an application."""
from pathlib import Path
import json,sys,time,subprocess,os,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
A=Path('/root/data/ada_native_extensions_stage4_20261024_v1');B=Path('/root/data/ep_l2_main_ada_tex37_ada9_compat_20261024_v1')
D=Path('/root/data/ada9_parent_cold_review_20261024_v1');T=Path('/root/data/ada_linear_texture_consumer_v9_20261024_v1')
specsha='7ec0074f3286b3d13fc846c2bc9a6d4c799fb0423fca7eb96565d543646a4596';qsha='83a948a665c2a183b28068b464cf911b918a990e5045115ff91d7aef2a3b2357'
assert e.hash_file(B/'control/FROZEN_SPEC.json',rate=0)==specsha and e.hash_file(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json',rate=0)==qsha
s=e.read(B/'control/FROZEN_SPEC.json');q=e.read(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json')
assert q['status']=='PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED'and q['spec_sha256']==specsha
assert e.hash_file(B/'ada_runtime.py',rate=0)=='3899d524e6fc9a43bc2dcac1fef47304f6584a1d13d7b369229045d73470487f'
assert s['maximum_application_attempts']==1 and not s['automatic_retry']and len(s['cases'])==1
assert s['limits']['memory_cap_bytes']==4*e.GIB and s['limits']['output_cap_bytes']==128*e.MIB and s['limits']['wall_seconds']==120
assert not s['hardware_performance_qualification']and not s['changes_frozen_EP_runtime']
assert s['request']=='EP_ADA_TRACE_COMPAT_TEX37_ADA9_20261024_V1'and list(s['cases'])==['tex37_ada9_v1']
assert subprocess.check_output(['git','-C',str(A/'core'),'rev-parse','HEAD'],text=True).strip()=='e5942d5bdeb9848327dbaaf63d155ca6970904f4'
assert not subprocess.check_output(['git','-C',str(A/'core'),'status','--porcelain','--untracked-files=no'],text=True).strip()
assert len(s['pinned_files'])==174
pins=[]
for name,want in s['pinned_files'].items():
 p=Path(name);assert e.hash_file(p,rate=0)==want,'pin drift '+name
 pins.append({'path':name,'sha256':want,'bytes':p.stat().st_size})
assert s['pinned_files'][s['binary']]=='c98850c09c3f0729d6dd06136d083f411158829313a351b8765ecf7e03d5988f'
assert s['pinned_files'][str(A/'core/lib/gcc-11.4.0/cuda-12040/release/libcudart.so')]=='f4c0e5014fe601e624c9b7e7131ea4a65a4459c0d3987b26ee673f75e28d106c'
assert e.hash_file(A/'native_maps_observer_v2.py',rate=0)=='3f187edf034f0d6d9f79f410ed6bbcdc0572df9a13db0c8b87cf62307d4a7c21'
assert e.hash_file(A/'native_process_status_v1.py',rate=0)=='22ad2df8b69fbee913f2b41abc03181bcd789f6194a9721966e21af2c45064e1'
parent=e.read(D/'PARENT_INDEPENDENT_SOURCE_TRACE_REVIEW.json');assert parent['predicted_total_lane_instructions']==666 and parent['predicted_TEX_requests']==6
case=s['cases']['tex37_ada9_v1'];assert case['source_active_lane_instances']==481 and case['expected_aux_active_lane_instances']==185 and case['expected_total_sim_active_lane_uop_instances']==666
assert case['ctas']==1 and case['warps']==2 and case['physical_EXIT_lanes']==37 and case['expected_const_lane_instances']==222
assert case['texture_lane_accesses']==37 and case['global_load_lane_accesses']==74 and case['global_store_lane_accesses']==37
assert case['actual_loaded_cubin_sha256']=='83f26c01fbf4ccfd580e6f1aab5f036cf0b988378ecd739a548aefea4eafb255'
probe=(T/'ACTUAL_CORE_PROBE_RUN_A1.log').read_text()
assert 'total_model_lane_uops=666'in probe and 'tex_requests=6'in probe and 'tex_enum=9'in probe
probe_source=(T/'ada9_actual_core_probe_v1.cc').read_text()
assert 'req.get_type()==TEXTURE_ACC_R&&req.get_size()==128'in probe_source
assert 'req.get_type()==CONST_ACC_R&&req.get_size()==64'in probe_source
assert str(T/'ada9_actual_core_probe_v1.cc')in s['pinned_files']
reg=e.read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');assert s['request']not in reg['registered_future_requests']
consumed=sum(reg['registered_future_requests'].get(k,{}).get('consumed',0)for k in s['campaign']['request_ids']);assert consumed==7 and s['campaign']['application_attempt_ceiling']==8
helptext=(B/'control/ELF_HELP_R2.log').read_text();assert ('usage'in helptext.lower()or'option'in helptext.lower())and 'gpu_tot_sim_insn'not in helptext
approval={'schema':'EP_MAIN_PARENT_TEX37_ADA9_EXACT_REVIEW_V1','approved_for_registration':True,'request':s['request'],'spec_sha256':specsha,'native_qualification_sha256':qsha,'entry_sha256':e.hash_file(B/'ada_runtime.py',rate=0),'one_exact_application_attempt':True,'maximum_application_attempts':1,'automatic_retry':False,'campaign_consumed_before_registration':7,'campaign_ceiling':8,'failed_attempts_never_refunded':True,'pins_checked_independently':pins,'resource_admission_before':e.Resources()(True),'reviewed_semantics':['Full original source9d5/actual loaded83f26/producerf4c693/raw87a86 identity and complete typed/CBANK map; no observer conversion','Every actual37 texture address is API LINEAR U32 backing plus actual signed index; entireAPI handle<=UINT32, not a GPU VA','Actual raw26 plus embedded10 width-preserving constant aux records;481+185=666; directULDC8 remains original load, no word splitting','Actual C++ parser/decoder/Core probe includes all26 source records, all8B CONST byte masks, actual TEX space/128B TEXTURE_ACC_R4+2 requests; independent parent raw/typed/address join and two corrupted actual-raw negatives pass','New private consumer OP_TLD explicitly LOAD_OP/memory_load/TEX/tex_space/L1T; zero-mask no memory or destination write; unsupported sampler variants rejected','Native entry differs from reviewed legacyR2 only in request/root/case identity; epoch2 shared authority lock/CAS, fresh exact budget before fork, frozen old ledger preserved','First actual issue and stopped post-simulation maps sampling; recursive main-thread child-list scope, not all transientDSO/allTID coverage','No hardware texture layout/latency/overlap, broad graphics, bulk, or EP scientific qualification'],'expected_total_active_lane_uops':666,'expected_CPU_Core_TEX_requests':6,'post_run_required':'Independent full raw/source/decoded/issued counts, actual TEXTURE_ACC_R/L1T effects, all mapped pinned path hashes, process terminal status; exit0 alone insufficient. Full true164 archive plus independent native cold readback before reservation retirement.','scientific_or_hardware_performance_qualification':False,'observed_unix':time.time()}
p=B/'control/PARENT_APPROVED_FOR_REGISTRATION.json';assert not p.exists()
with p.open('x')as f:json.dump(approval,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
proof={'status':'PARENT_APPROVED_EXACT_CASE8_NOT_YET_REGISTERED_OR_CONSUMED','root':str(B),'request':s['request'],'case':'tex37_ada9_v1','approval_sha256':e.hash_file(p,rate=0),'spec_sha256':specsha,'qualification_sha256':qsha,'campaign_before':7,'maximum_after_one':8,'campaign_ceiling':8,'observed_unix':time.time()}
(R/'control/ADA_TEX37_ADA9_PARENT_PRELAUNCH_REVIEW.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

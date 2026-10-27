"""Pure Source92 P1/P2 math candidate. No actor, registry or acceptance writes."""
import ast,hashlib,importlib.util,json,re
from pathlib import Path as P
ROOT=P(__file__).resolve().parent
GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
SID={'core_source_commit':'92ed2c4c1c2d682b33f2f7ce4d6b56571a889480','framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7','vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b','binary_sha256':'67315b875a0fa80d2886cb142f3fc4a5b044325ce2b5f901eca675a9abb0e53f','archive_sha256':'b1b501fcc413f7dd3149c026b6c19764351e9f30632d7f79f9577834f4cc19ab'}
HEAVY={k:'0'for k in('EPL2_DETACH_DIAG','EPL2_TAGPRESSURE_DIAG','EPL2_TAG_LIFETIME','EP_L2_EVENT_TIMELINE')}
ENV={**HEAVY,'EPL2_LIFE_WIRE':'SUMMARY_STAGE'}
PERF_PROFILE={'heavy_env':HEAVY,'inactive_LIFE_wire_mode':'SUMMARY_STAGE','options':{'-gpgpu_ep_l2_ms_observer':'1','-gpgpu_ep_l2_b0_stats':'1','-gpgpu_ep_l2_m0a_stats':'1'}}
OLD_BODY_SHA='7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817'
FINAL_SUFFIX_SHA='bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432'
OLD_ELIGIBILITY="require(d['hardware_P1_throughput_eligible']==int(not(copy_free or data_free)),\n                'diagnostic service mislabeled normal physical P1 throughput')"
NEW_ELIGIBILITY="require(d['hardware_P1_throughput_eligible']==int(identity['feature_vector']['ops_per_bank_cycle']==1 and not(copy_free or data_free)),\n                'P1 eligibility must match exact bank_ops; independent P2_POLICY validation required')"
PINS={'evidence/SOURCE92_MAPPING_AND_GUARD_SOURCE.json': '8cd560a9ec4f970363ce3ca481c83915dc239de857c1deeb06ec11a9cfa51694', 'evidence/REFERENCE_282_BY_MODE.json': '8aef95b36823b3a52ab6aaaff2b3a01b3b4e193b21a8a91e7cfd241940e2a03d', 'evidence/SOURCE92_DELIVERY.json': '3a6ee13a036a37af5e48ec1565a8ef5b502baa2d3c577b42e92d7d232b228006', 'evidence/SOURCE92_CONSTRUCTOR_LOADER.json': '592fd2ca7ec78222b0c5551933f40c325e9d6305303b9ea572cf5b6101fe859f', 'evidence/SOURCE92_FULL_BUILD.json': '3c461e37cd3d1a3c880cb4afefcf2deb64bf689425166c3e195677acff4940a0', 'evidence/SOURCE92_P2_POLICY.json': 'bba5238de07903cfd7282265b98a40b06f24ac22f2c09898613b567c2334a842', 'host_scaling/dynamic_observation_scaled.py': '4db737bf5bdc09532480e401001e39bc0de414c0b692c666542e8665a011ab25', 'host_scaling/lowcost_terminal_scaled.py': 'fdcaab0aef93363148a81257e548dd1cc58cc1369986cbfc809366ff83cd1df1', 'host_scaling/rolling_structure_core.py': 'b8f09af83cf2eb50933b46216f825593eb218c2a304a61ec7a624fc22f3f2066', 'host_scaling/frozen_math/parse_main_terminal.py': 'f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e', 'host_scaling/frozen_math/lowcost_terminal_v2.py': 'cba193d8ec810219f58bbe55870814b70604082f4f6683a236a418e80b9da35c', 'host_scaling/frozen_math/ft_lane5/validate.py': '08a7396a6e11893dbbcb982725765a6c9b12194b1e01e3f0dc70d337f85dd500', 'host_scaling/frozen_math/ft_lane5/parse_unified_terminal.py': '536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b', 'p2_policy_wire.py': '928b20a030c6fb4e69443efdc4708d9100607e53b1162214960543319d895236', 'evidence/SOURCE92_PRODUCTION_ASSERTION_STATE.json': 'a209215bc88ee3ea64257abf8094b99331a5cb3f2fa7afd2365d9308d7a5cfdc'}
VARIABLE_INPUT={'-trace','-gpgpu_ep_l2_ro_manifest','-gpgpu_ep_l2_ro_manifest_sha256','-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_ranges_sha256','-gpgpu_ep_l2_ro_scope'}
REQUIRED_CPU_SHA={'production_assertion_state':'a209215bc88ee3ea64257abf8094b99331a5cb3f2fa7afd2365d9308d7a5cfdc','p2_engineering_delivery':'3a6ee13a036a37af5e48ec1565a8ef5b502baa2d3c577b42e92d7d232b228006','full_build':'3c461e37cd3d1a3c880cb4afefcf2deb64bf689425166c3e195677acff4940a0','production_cpu_NI':'15e6713a4930616544079ebceda9755056218da56380c073dbc7764c280fbbab','actual_constructor_loader':'592fd2ca7ec78222b0c5551933f40c325e9d6305303b9ea572cf5b6101fe859f','default_S_P1_regression':'e4bbbad93f0d489af6009c7879c08e4c95a8da0c1e013dbb4f760404964885fc','MS_observer_NI':'c4308041336a2960cc1445b9ca43217108f41943a83049258af694a5af79f6fc'}
def need(x,msg):
 if not x:raise ValueError(msg)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def doc(v):
 if isinstance(v,dict):return v
 def pairs(items):
  out={}
  for k,x in items:need(k not in out,'duplicate JSON key');out[k]=x
  return out
 return json.loads(P(v).read_bytes(),object_pairs_hook=pairs,parse_constant=lambda v:need(False,'nonfinite JSON'))
def ref(p):return dict(path=str(p),sha256=sha(p))
def exact(r):
 need(type(r)is dict and set(r)>={'path','sha256'}and sha(r['path'])==r['sha256'],'evidence ref SHA drift')
 return doc(r['path'])
def verify_pins():
 for rel,d in PINS.items():need(sha(ROOT/rel)==d,'Source92 package dependency drift '+rel)
 return {rel:ref(ROOT/rel)for rel in PINS}
def load(rel,name):
 need(rel in PINS and sha(ROOT/rel)==PINS[rel],'unbound new-source math module')
 s=importlib.util.spec_from_file_location(name,ROOT/rel);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def qualify_history_spec(s):
 verify_pins();need(s.get('goal')==GOAL and s.get('source_identity')==SID,'exact new Source92/ELF/archive5 required')
 mode=s['mode'];need(mode in('S','F'),'only explicit Source92 S/F performance modes')
 need(s.get('T')is(mode=='F')and s.get('M')is(mode=='F'),'formal native T/M bool mismatch')
 o=s['expected_effective_options'];need(len(o)==282 and all(type(k)is str and type(v)is str for k,v in o.items()),'exact complete282 strings')
 g=s['geometry'];need(set(g)=={'slices','sets','ways','line_bytes'}and all(type(v)is int for v in g.values()),'typed exact geometry')
 need(g['slices']==64 and g['sets']in(32,64)and g['ways']in(8,16)and g['line_bytes']==128 and g['sets']*g['ways']<=1024,'qualified four geometry domain')
 need(o['-gpgpu_ep_l2_bank_ops']in('1','2'),'Source92 bank_ops mustbe1or2');ops=int(o['-gpgpu_ep_l2_bank_ops'])
 reference=doc(ROOT/'evidence/REFERENCE_282_BY_MODE.json')[mode]
 need(set(o)==set(reference),'actual282 keyset changed')
 for k,v in reference.items():
  if k not in VARIABLE_INPUT|{'-gpgpu_cache:dl2','-gpgpu_ep_l2_bank_ops'}:need(o[k]==v,'unqualified hardware/background/statistics option '+k)
 need(o['-trace']==s['trace_entry'],'trace actual option binding')
 need(s['observer_env']==ENV,'formal Source92 performance requires exact four-heavy OFF plus frozen inactive SUMMARY_STAGE wire mode')
 need(all(o[k]==v for k,v in PERF_PROFILE['options'].items()),'MS/B0/M0a each1 fixed')
 need(o['-gpgpu_cache:dl2']==f"S:{g['sets']}:128:{g['ways']},L:B:m:L:P,A:128:1,128:0,32",'real Taggeometry/hash/MSHR/MissQ mapping')
 mapping=doc(ROOT/'evidence/SOURCE92_MAPPING_AND_GUARD_SOURCE.json');need(mapping['source_identity']==SID,'new Source mapping proof identity')
 for r in mapping['files'].values():need(sha(r['path'])==r['sha256'],'Source92 mapping/guard code drift')
 cpu=doc(ROOT/'evidence/SOURCE92_CONSTRUCTOR_LOADER.json');build=doc(ROOT/'evidence/SOURCE92_FULL_BUILD.json')
 need(cpu['status']=='P2_ACTUAL_S_CACHE_F_LOADER_AND_FOUR_GEOMETRY_CPU_PASS_NOT_APPLICATION'and cpu['source_identity']==SID,'new actual constructor/loader evidence')
 need(build['status']=='PRIVATE_P2_FULL_BUILD_PASS_NOT_NATIVE_OR_APPLICATION_QUALIFICATION'and build['source_commit']==SID['core_source_commit'],'new full Source build proof')
 artifact_by_path={r['path']:r['sha256']for r in build['artifact_refs']}
 for path,digest in cpu['library_refs'].items():need(artifact_by_path.get(path)==digest and sha(path)==digest,'actual same-new-library constructor proof drift')
 label=f"CTOR_{mode}_G{g['sets']}W{g['ways']}_P{ops}";row=next((x for x in cpu['checks']if x['case']==label),None)
 need(row is not None and row['RO_loader_whole_commandlist_bound']is(mode=='F'),'new actual ctor population missing')
 need(len(row['actual_getters'])==2,'actual two-subpartition getters required')
 for a in row['actual_getters']:
  wanted={'sets':str(g['sets']),'ways':str(g['ways']),'line':'128','atom':'32','MSHR':'128','descriptor':'512','WAD':'128','physical_payload_line_slots':'1168','bank_ops_per_CORE_cycle':str(ops),'all_sets_reached':'1','no_GPU_object':'1','no_requests':'1'}
  need(all(a[k]==v for k,v in wanted.items()),'actual new Source physical/geometry/bank getter mismatch')
 assertions=doc(ROOT/'evidence/SOURCE92_PRODUCTION_ASSERTION_STATE.json')
 need(assertions['source_identity']==SID and assertions['status']=='ALL_NEW_PRODUCTION_ARCHIVE_AND_MAIN_TUS_NDEBUG_UNDEFINED_ASSERTIONS_ENABLED'and assertions['production_NDEBUG_final_undefined']is True,'actual production-library assertion state required, not only fixture assert')
 for archive in assertions['archives']:need(archive['all_production_member_NDEBUG_undefined']is True and archive['mapped_compile_count']==archive['actual_ar_member_count'],'all actual archive members assertion-state join')
 policy=doc(ROOT/'evidence/SOURCE92_P2_POLICY.json')
 need(policy['source_identity']==SID and policy['status']=='CPU_FUNCTION_AND_NI_PASS_PENDING_MAIN_SOURCEQ','Source92 P2 engineering policy identity')
 need(policy['P2_policy']=='MAX2_DISTINCT_PHYSICAL_SLOT_OPS_PER_BANK_PER_PHYSICAL_CORE_TICK; SAME_SLOT_MAX1_ALL_R_W_COMBINATIONS; RETAINED_SELECTED_AGE_ORDER','conservative same-slot Source policy changed')
 return dict(schema='EP_SOURCE92_P1P2_STRICT_PHYSICAL_MATH_BINDING_V1',source_identity=SID,geometry=g,logical_tags_per_slice=g['sets']*g['ways'],physical_payload_line_slots_per_slice=1168,modeled_payload_data_bytes_GPU=9568256,D=512,LineMSHR=128,WAD=128,banks=4,bank_ops_per_physical_CORE_tick=ops,same_slot_max_ops_per_CORE_tick=1 if ops==2 else'P1_GLOBAL_BANK_MAX1',caller_ports_unchanged=True,retained_native_identity_required=ops==2,actual_bank_identity_enabled=(mode=='F'or ops==2),P1_to_P2_causal_intervention='DEFINED_CONSERVATIVE_P2_ORGANIZATION; S identity false-to-true plus max2 distinct-slot service and same-slot serialization; F identity already true; not pure bandwidth sensitivity',normal_MS_B0_M0a1=True,observer_env=ENV,CPU_ctor_case=label,CPU_constructor_source_identity=cpu['source_identity'],mapping_and_guard_refs=mapping['files'],numeric_output='UNKNOWN',scientific_acceptance_granted=False)

def verify_math_manifest(r):
 m=exact(r);need(m['schema']=='EP_SOURCE92_P1P2_MATH_PACKAGE_V1','exact new math package manifest')
 expected={**PINS,P(__file__).name:sha(__file__)}
 need(set(m['files'])==set(expected),'complete exact math dependency graph')
 for rel,d in expected.items():need(m['files'][rel]['sha256']==d and sha(ROOT/rel)==d,'math manifest module mismatch '+rel)
 return m

def qualify_sourceq(s,sourceq_path,sourceq_sha):
 need(sha(sourceq_path)==sourceq_sha,'new SourceQ SHA mismatch');sq=doc(sourceq_path)
 need(sq.get('schema')=='EP_FULL_PERF_P2_SOURCE_QUALIFICATION_V1'and sq.get('status')=='SOURCEQ_CPU_PASS_NOT_APPLICATION_ACCEPTED','new Main SourceQ schema/status required')
 need(sq.get('goal')==GOAL and sq.get('qualified_by')=='EP-MAIN'and sq.get('source_identity')==SID,'Main new-Source identity/owner only')
 need(sq.get('application_acceptance_inherited')is False and sq.get('scientific_acceptance_granted')is False and sq.get('full_application_qualified')is False and sq.get('scientific_application_permission')is False,'SourceCPU qualification cannot inherit/accept applications or itself authorize science')
 need(sq.get('performance_profile')==PERF_PROFILE and sq.get('ET_global_clock_scientific_qualified')is False,'separate fourOFF performance versus ET HOLD')
 need(sq.get('supported_geometry')==[[32,8],[64,8],[32,16],[64,16]]and sq.get('supported_bank_ops')==[1,2]and sq.get('supported_modes')==['S','F']and sq.get('P2_policy_id')=='P2_DISTINCT_PHYSICAL_SLOT_CORE_TICK_V1','SourceQ exact mode/geometry/service policy scope')
 refs=sq['evidence_refs'];required=set(REQUIRED_CPU_SHA)|{'producer','main_source_review','source_release','host_math_package_manifest'}
 need(required<=set(refs),'new SourceQ complete evidence graph required')
 data={k:exact(v)for k,v in refs.items()}
 for k,digest in REQUIRED_CPU_SHA.items():need(refs[k]['sha256']==digest,'actual Source92 CPU evidence substitution '+k)
 producer=data['producer'];need(producer['schema']=='EP_FULL_PERF_P2_PRODUCER_IDENTITY_V1'and producer['source_identity']==SID,'new actual producer')
 need(producer['binary_path']==s['binary_path']and producer['static_library_path']==s['static_library_path'],'new producer actual file paths')
 need(sha(producer['binary_path'])==SID['binary_sha256']and sha(producer['static_library_path'])==SID['archive_sha256'],'new producer artifact drift')
 review=data['main_source_review'];need(review.get('status')=='MAIN_SOURCE92_P1P2_MINIMAL_DIFF_REVIEW_PASS'and review.get('qualified_by')=='EP-MAIN'and review.get('source_identity')==SID,'Main minimal-source review missing')
 release=data['source_release'];need(release.get('schema')=='EP_FULL_PERF_P2_SOURCE_RELEASE_BINDING_V1'and release.get('source_identity')==SID and release.get('source_keep')is True and release.get('two_native_restores_verified')is True and release.get('all_artifact_sha256_verified')is True and release.get('genuine164_verified')is True,'new artifact genuine164/SourceKEEP/archive/two restore proof missing')
 need(re.fullmatch(r'[0-9a-f]{64}',release.get('source_tar_sha256',''))is not None and release.get('static_library_sha256')==SID['archive_sha256']and release.get('main_elf_sha256')==SID['binary_sha256'],'Core source tar mustnotmasquerade as static archive identity')
 need(release.get('restore_scope')=='ARCHIVE_BYTES_AND_CONTENTS_SHA_VERIFIED_NOT_REBUILD'and len(release.get('actual_receipt_refs',[]))>=3,'actual archive/two restore refs and honest restore scope required')
 for proof in release['actual_receipt_refs']:exact(proof)
 verify_math_manifest(refs['host_math_package_manifest'])
 expected_ref=s.get('source_qualification_ref')
 need(expected_ref==dict(path=str(sourceq_path),sha256=sourceq_sha),'spec exact SourceQ ref mismatch')
 return sq

def adapted_numeric_body(body):
 need(hashlib.sha256(body.encode()).hexdigest()==OLD_BODY_SHA and body.count(OLD_ELIGIBILITY)==1,'original numeric body/premise bytes changed')
 changed=body.replace(OLD_ELIGIBILITY,NEW_ELIGIBILITY)
 need(changed.replace(NEW_ELIGIBILITY,OLD_ELIGIBILITY)==body,'one exact numeric premise replacement only')
 return changed

def private_c():
 base=load('host_scaling/lowcost_terminal_scaled.py','isolated_original_scaled_C2');c=base.frozen_c()
 original=(ROOT/'host_scaling/frozen_math/lowcost_terminal_v2.py').read_text()
 history=c.function(original,'history_for');marker="need(s['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128),'first physical geometry qualified only')"
 need(history.count(marker)==1 and history.count("'-gpgpu_ep_l2_bank_ops':'1'")==1 and history.count('ops_per_bank_cycle=1')==1,'frozen private history markers')
 history_new=history.replace(marker,'qualify_history_spec(s)').replace("'-gpgpu_ep_l2_bank_ops':'1'","'-gpgpu_ep_l2_bank_ops':s['expected_effective_options']['-gpgpu_ep_l2_bank_ops']").replace('ops_per_bank_cycle=1',"ops_per_bank_cycle=int(s['expected_effective_options']['-gpgpu_ep_l2_bank_ops'])")
 ns=dict(c.__dict__,qualify_history_spec=qualify_history_spec);exec(compile(history_new,'SOURCE92_STRICT_SAME_PHYSICAL_BUDGET_HISTORY','exec'),ns);c.history_for=ns['history_for']
 # The original factory builds the exact pure body. Only the named P1 premise
 # is changed, with original hash + inverse byte check before every compile.
 fn=c.function(original,'numeric_math');marker='body=full[full.index(marker):]';need(fn.count(marker)==1,'numeric factory marker')
 factory_new=fn.replace(marker,marker+'\n body=adapted_numeric_body(body)')
 ns=dict(c.__dict__,adapted_numeric_body=adapted_numeric_body);exec(compile(factory_new,'SOURCE92_ONE_EXACT_BANK_ELIGIBILITY_PREMISE','exec'),ns);factory=ns['numeric_math']
 def numeric():
  parse,receipt=factory();rolling=load('host_scaling/rolling_structure_core.py','Source92_original_rolling_final_math')
  def structure(raw,h,final):
   value,census=rolling.parse_structure_with_receipt(raw,h,final);receipt['structure_stream_census']=census;return value
  parse.__globals__['parse_structure']=structure
  rawparse=parse
  def checked_parse(raw,h,q):
   f=h['identity']['feature_vector'];o=h['profile_semantics']['effective_options']
   need(f['ops_per_bank_cycle']in(1,2)and str(f['ops_per_bank_cycle'])==o['-gpgpu_ep_l2_bank_ops']and f['payload_capacity_per_slice']==1168 and f['static_s64']is False,'strict normal1168 P1/P2 numeric history')
   return rawparse(raw,h,q)
  # Expose private globals only for explicitly pure engineering controls.
  checked_parse.__wrapped_numeric__=rawparse
  receipt.update(original_numeric_body_sha256=OLD_BODY_SHA,numeric_body_changed_only_one_named_P1_eligibility_premise=True,eligibility_old_line=OLD_ELIGIBILITY,eligibility_new_line=NEW_ELIGIBILITY,eligibility_old_sha256=hashlib.sha256(OLD_ELIGIBILITY.encode()).hexdigest(),eligibility_new_sha256=hashlib.sha256(NEW_ELIGIBILITY.encode()).hexdigest(),frozen_final_suffix_sha256=rolling.FINAL_SUFFIX_SHA,structure_adapter_sha256=PINS['host_scaling/rolling_structure_core.py'],authority_inherited=False)
  return checked_parse,receipt
 c.numeric_math=numeric
 text=c.function(original,'validate_case');old="need(s['source_identity']['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04','exact source only')";new="need(s['source_identity']==SID,'exact new Source92 only')";need(text.count(old)==1,'frozen source-identity marker')
 ns=dict(c.__dict__,SID=SID);exec(compile(text.replace(old,new),'SOURCE92_NO_OLD_APPLICATION_AUTHORITY','exec'),ns);c.validate_case=ns['validate_case']
 return c

def history_for(spec):
 s=doc(spec);qualify_history_spec(s);return private_c().history_for(s)
def numeric_math():verify_pins();return private_c().numeric_math()

def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 s=doc(spec);q=doc(qualification);binding=qualify_history_spec(s);sq=qualify_sourceq(s,sourceq_path,sourceq_sha)
 need(q.get('status')=='EP_PERF_PREPARE_PASS_NO_START'and q.get('cohort')==s['cohort']and q.get('source_identity')==SID and type(q.get('science_starts'))is int and q.get('science_starts')==0,'new exact Main NativeQ/prelaunch required')
 if not isinstance(spec,dict):need(q.get('spec_sha256')==sha(spec),'NativeQ exact frozen spec SHA mismatch')
 policy=load('p2_policy_wire.py','Source92_complete_policy_wire').scan_policy(raw,binding['bank_ops_per_physical_CORE_tick'])
 c=private_c();result=c.validate_case(raw,s,q,sourceq_path,sourceq_sha)
 need(policy['raw_logical_sha256']==result['raw_logical_sha256']and policy['raw_logical_bytes']==result['raw_uncompressed_bytes']and policy['raw_lines']==result['application']['raw_lines'],'P2 whole raw census mismatch')
 need(result['math_binding']['structure_stream_census']['raw_logical_sha256']==result['raw_logical_sha256'],'original rolling whole raw disagreement')
 result['source92_physical_math_binding']=binding;result['source92_policy_wire']=policy
 result['source92_math_provenance']=dict(entry_sha256=sha(__file__),dependencies=verify_pins(),SourceQ_ref=dict(path=str(sourceq_path),sha256=sourceq_sha),new_Source_cpu_evidence_used=True,old_Source78_application_acceptance_inherited=False,ET_global_clock_scientific_qualified=False,remaining_unchanged_math='original numeric body except explicit P1 premise; original full STRUCT final suffix and FT/RO/sector/descriptor/drain equations',science_granted=False)
 service=result['model']['mechanism_metrics']['local_service']
 service['eligibility_scope']='NORMAL_PAID_BANK_SERVICE; original generic eligible bool doesnotmean P1 bandwidth'
 service['actual_bank_ops_per_CORE_tick']=binding['bank_ops_per_physical_CORE_tick']
 service['hardware_P1_throughput_eligible']=binding['bank_ops_per_physical_CORE_tick']==1
 service['hardware_defined_P2_throughput_eligible']=binding['bank_ops_per_physical_CORE_tick']==2
 service['grant_unit']='LOGICAL_SLOT_OPERATION; not uniformly32B/128B or endtoend bandwidth'
 result['model']['source_map']['mechanism']['actual_source_identity']=SID
 result['model']['source_map']['full_system']='Actual Source92 finite FT/TVD/RO producer; pinned legacy pure equations, explicit new P2 service policy'
 result['outer_join_required']+=['Main Source92 source review/release/native bridge and new-Source P1 application NI; never cross-ELF performance pairing']
 need(result['scientific_acceptance_granted']is False,'pure candidate may not grant science')
 return result



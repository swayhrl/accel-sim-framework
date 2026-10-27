"""Finite, pure proposal generator. NOT a native stage/spec or budget registrar.
Reads only explicit small metadata/config-option references; does not read Trace bodies.
"""
import argparse, hashlib, json, re
from pathlib import Path
GOAL="EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1"
CATALOG_SHA="110be382dbfee88a55d36606ac6951d83776c6cb1391556481807f2463b2baf4"
COMBINATIONS_SHA="2d0e718470f6985f3f0d0d5b945661e1ce2a683ee664c6fc9d1fb34667294ed6"
SOURCE_FIELDS=("core_source_commit","framework_source_commit","vendor_pybind11_commit","binary_sha256","archive_sha256")

def need(ok,msg):
 if not ok:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(r):
 data=Path(r['path']).read_bytes();need(hashlib.sha256(data).hexdigest()==r['sha256'],'metadata SHA drift '+r['path']);return json.loads(data)
def source5(v):return {k:v[k]for k in SOURCE_FIELDS}
def geometry(options):
 p=options['-gpgpu_cache:dl2'].split(',');f=p[0].split(':');need(len(p)==5 and len(f)==4,'cache tuple grammar');return p,int(f[1]),int(f[2]),int(f[3])
def guard(options,mode):
 need(len(options)==282,'complete282 required');p,sets,line,ways=geometry(options)
 need(sets in (32,64)and ways in (8,16)and line==128 and sets*ways<=1024,'qualified logical geometry domain')
 need(p[0].startswith('S:')and p[1]=='L:B:m:L:P'and p[2]=='A:128:1','sector/writeback/on-miss/lazy/P/lineMSHR invariant')
 eq={'-gpgpu_ep_l2_payload_mode':'2','-gpgpu_ep_l2_descriptor_pool_size':'512','-gpgpu_ep_l2_descriptor_per_line_cap':'32','-gpgpu_ep_l2_wad_entries':'128','-gpgpu_ep_l2_wbuf_entries':'16','-gpgpu_ep_l2_bank_ops':'1',
 '-gpgpu_ep_l2_ft_mode':'1'if mode=='S'else'2','-gpgpu_ep_l2_ro_tag_detach':'1'if mode=='F'else'0','-gpgpu_ep_l2_ro_line_mshr_bypass':'1'if mode=='F'else'0','-gpgpu_ep_l2_tvd_clean':'0'if mode=='S'else'1','-gpgpu_ep_l2_tvd_dirty':'0'if mode=='S'else'1'}
 need(mode in('S','F','WV_ZERO_RO'),'mode stratum')
 for k,v in eq.items():need(options[k]==v,'finite full-mode invariant '+k)
 zero=['-gpgpu_ep_l2_wb_local_cap','-gpgpu_ep_l2_mq2','-gpgpu_ep_l2_rg1','-gpgpu_ep_l2_ideal_wb','-gpgpu_ep_l2_ideal_meta','-gpgpu_ep_l2_ideal_read_hit','-gpgpu_ep_l2_diag_copy_free','-gpgpu_ep_l2_diag_l2_data_free','-gpgpu_ep_l2_payload_policy','-gpgpu_ep_l2_feature_unified_payload','-gpgpu_ep_l2_feature_ro_pending_state','-gpgpu_ep_l2_feature_tvd','-gpgpu_ep_l2_feature_adaptive_policy']
 for k in zero:need(options[k]=='0','blocked/optimistic direction '+k)
 if mode!='S':need(options['-gpgpu_ep_l2_static_s64']=='0','RO/TVD requires static_s64OFF')
 if options['-gpgpu_ep_l2_static_s64']=='1':need(mode=='S'and options['-gpgpu_ep_l2_ms_observer']=='0','S64 engineering profile must disable incompatible ms observer')
 need(options['-gpgpu_n_mem']=='32'and options['-gpgpu_n_sub_partition_per_mchannel']=='2','fixed32channels/64slices')
 need(options['-gpgpu_simple_dram_model']=='0'and options['-gpgpu_l2_rop_latency']=='160','detailed DRAM and fixedROP')
 need(int(options['-gpgpu_frfcfs_dram_sched_queue_size'])>0 and int(options['-gpgpu_dram_return_queue_size'])>0 and options['-dram_seperate_write_queue_enable']=='0','finite ordinary credit range')
 return {'sets':sets,'ways':ways,'slices':64,'line_bytes':128,'logical_tags_per_slice':sets*ways,'physical_payload_lines_per_slice':1168,'physical_payload_bytes_per_slice':1168*128,'bank_ops_per_CORE_cycle':1,'descriptor_pool512':True,'line_MSHR128':True,'WAD128':True}

def load_catalogs():
 b=Path(__file__).parent;cr={'path':str(b/'PARAMETER_CATALOG_V2.json'),'sha256':CATALOG_SHA};rr={'path':str(b/'CAUSAL_COMBINATIONS_V1.json'),'sha256':COMBINATIONS_SHA};c=exact(cr);r=exact(rr)
 need(c['goal']==GOAL and r['goal']==GOAL and r['catalog_ref']==cr,'catalog lineage')
 return c,r,cr,rr

def profile_table(c,r):
 out={}
 for x in c['candidates']:
  out[x['candidate_id']]={'common_delta':x['exact_effective_delta_common_to_S_and_F'],'mode_specific_delta':x.get('mode_specific_option_delta',{}),'hardware_cost':x['expected_resource_cost'],'refs':x['source_refs'],'candidate_status':x['status']}
 for x in r['combinations']:
  out[x['candidate_id']]={'common_delta':x['exact_common_effective_delta'],'mode_specific_delta':{},'hardware_cost':x['resource_proxies'],'refs':x['component_candidate_ids'],'candidate_status':x['status']}
 return out

def validate_all_candidate_options():
 c,r,cr,rr=load_catalogs();table=profile_table(c,r);results=[]
 for name,p in table.items():
  for mode in('S','F'):
   o=dict(c['reference_templates'][mode]['effective_options']);o.update(p['common_delta']);o.update(p['mode_specific_delta'].get(mode,{}))
   # The S64 special stratum explicitly requests the common msOFF profile;
   # this engineering option validation does not change any accepted reference.
   if name=='P_S64_VS_UNIFIED1168':o.update(c['common_low_cost_profile_proposal']['options'])
   g=guard(o,mode);results.append({'profile':name,'mode':mode,'geometry':g,'option_contract_SHA':hashlib.sha256(canonical(o)).hexdigest()})
 return {'status':'PURE_OPTION_GUARD_SCREEN_PASS_NOT_CPU_CONFIG_INITIALIZATION','count':len(results),'results':results,'source_refs':['gpu-cache.h:3337-3440','ro-store-port.h:24-25'],'model_starts':0,'CPU_cache_initializations':0}

def propose(manifest,phase,selected_profiles=None,selected_inputs=None):
 c,r,cr,rr=load_catalogs();need(manifest['schema']=='EP_FULL_PERF_SEARCH_INPUT_MANIFEST_V1'and manifest['goal']==GOAL,'input manifest identity')
 need(source5(manifest['source_identity'])==source5(c['reference_templates']['S']['source_identity']),'catalog Source differs; no qualification inherited')
 table=profile_table(c,r)
 if phase=='reference':profiles=['REF_G32_W8']
 elif phase=='singles':profiles=c['finite_search_design']['phase1']['candidates']
 elif phase=='combinations':profiles=[x['candidate_id']for x in r['combinations']]
 elif phase=='common_validation':
  profiles=selected_profiles or[];need(1<=len(profiles)<=3 and len(profiles)==len(set(profiles)),'one to3 globally fixed profiles required')
 else:raise ValueError('unreviewed finite phase')
 need(all(x in table for x in profiles),'unknown profile')
 inputs=manifest['inputs'];need(len({x['input_identity_sha256']for x in inputs})==len(inputs),'duplicate input content ID; resolve aliases explicitly')
 if phase in('singles','combinations'):
  need(selected_inputs and len(selected_inputs)==len(set(selected_inputs)),'explicit predeclared exploration input set required')
  exact(manifest['exploration_selection_ref'])
  have={x['input_identity_sha256']for x in inputs};need(set(selected_inputs)<=have,'missing selected input')
  inputs=[x for x in inputs if x['input_identity_sha256']in selected_inputs]
 elif selected_inputs:raise ValueError('all-coverage phase cannot be narrowed to selected programs')
 plans=[];pending=[]
 for inp in inputs:
  for mode in('S','F'):
   if mode not in inp['base_specs_by_mode']:
    pending.append({'input_identity_sha256':inp['input_identity_sha256'],'mode':mode,'status':'QUALIFICATION_PENDING_NOT_DROPPED_FROM_TARGET_UNIVERSE'});continue
   sr=inp['base_specs_by_mode'][mode];s=exact(sr);e=exact(s['eligibility_ref'])
   need(s['input_identity_sha256']==inp['input_identity_sha256']and source5(s['source_identity'])==source5(manifest['source_identity']),'base spec input/Source')
   need(e['status']=='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE'and mode in e['modes_qualified']and e['input_identity_sha256']==s['input_identity_sha256'],'mode/input eligibility')
   need(len(s['ordered_configs'])==4,'exactfour config files only')
   for cfg in s['ordered_configs']:need(sha(cfg['path'])==cfg['sha256'],'config byte drift')
   need(all(s['observer_env'].get(k)=='0'for k in('EPL2_DETACH_DIAG','EPL2_TAGPRESSURE_DIAG','EPL2_TAG_LIFETIME','EP_L2_EVENT_TIMELINE')),'default heavy observers must beOFF')
   if mode=='F':
    q=exact(s['ro_qualification_ref']);need(q['status']=='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED'and q['input_identity_sha256']==s['input_identity_sha256']and source5(q['source_identity'])==source5(s['source_identity']),'F certificate identity')
    for kind in('ranges','manifest'):
     ir=q[kind+'_ref'];need(sha(ir['path'])==ir['sha256']and s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind]==ir['path']and s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind+'_sha256']==ir['sha256'],'F actual RO mapping')
   else:need(s['ro_qualification_ref']is None,'S may not inherit RO permission')
   guard(s['expected_effective_options'],mode)
   for profile in profiles:
    p=table[profile];delta=dict(p['common_delta']);delta.update(p['mode_specific_delta'].get(mode,{}));o=dict(s['expected_effective_options']);o.update(delta)
    g=guard(o,mode);diff={k:{'old':s['expected_effective_options'][k],'new':v}for k,v in o.items()if v!=s['expected_effective_options'][k]}
    label=re.sub('[^A-Z0-9_]','_',inp['program'].upper())[:32];cohort='EP_PERF_'+label+'_'+profile+'_'+mode+'_'+inp['input_identity_sha256'][:12]+'_V1'
    need(len(cohort)<170,'cohort bound')
    plans.append({'cohort_proposal':cohort,'program':inp['program'],'input_identity_sha256':inp['input_identity_sha256'],'mode':mode,'profile':profile,
      'reference_spec_ref':sr,'source_identity':source5(s['source_identity']),'four_config_refs':s['ordered_configs'],'observer_env_unchanged':s['observer_env'],
      'geometry':g,'exact_effective_option_delta':diff,'complete282_expected_options_canonical_sha256':hashlib.sha256(canonical(o)).hexdigest(),
      'hardware_cost':p['hardware_cost'],'source_refs':p['refs'],'application_budget_if_main_qualified_and_registered':1,
      'CPU_config_and_native_qualification':'REQUIRED_NOT_GRANTED','existing_exact_start_and_acceptance_dedup':'MAIN_MUST_CHECK; no automatic reuse/retry from this proposal'})
 return {'schema':'EP_FULL_PERF_FINITE_SEARCH_STAGE_PROPOSAL_V1','goal':GOAL,'status':'PROPOSAL_ONLY_NOT_REGISTERABLE_NATIVE_STAGE',
  'phase':phase,'maximum_new_starts_proposed':len(plans),'plans':plans,'pending_qualification_populations':pending,'profile_contracts':{k:table[k]for k in profiles},
  'catalog_ref':cr,'combinations_ref':rr,'source_identity':source5(manifest['source_identity']),'target_input_count':len(manifest['inputs']),'stage_input_count':len(inputs),
  'coverage_is_not_capped_at8_or12_programs':True,'frozen_specs_or_budgets_written':0,'models_started':0,'prior_budget_inherited':False,
  'requires_Main':['review exact candidate and finite count','reuse only exact accepted reference after all joins','materialize four byte-patched configs and exact282','CPU config smoke/nativeQ before spending a model','freeze actual native stage specs and new authorization','one Main dispatcher under actual resources']}

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--input-manifest',required=True);a.add_argument('--input-manifest-sha256',required=True);a.add_argument('--phase',required=True,choices=['reference','singles','combinations','common_validation']);a.add_argument('--profile',action='append');a.add_argument('--exploration-input',action='append');a.add_argument('--output',required=True);args=a.parse_args()
 data=Path(args.input_manifest).read_bytes();need(hashlib.sha256(data).hexdigest()==args.input_manifest_sha256,'input manifest SHA drift')
 result=propose(json.loads(data),args.phase,args.profile,args.exploration_input);p=Path(args.output);need(not p.exists()and not p.is_symlink(),'fresh output required')
 with p.open('x')as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'status':result['status'],'proposed_starts':result['maximum_new_starts_proposed'],'models_started':0}))

if __name__=='__main__':main()

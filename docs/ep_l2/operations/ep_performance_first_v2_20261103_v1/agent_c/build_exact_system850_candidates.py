from pathlib import Path
import json,hashlib,subprocess,copy,re,csv
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');C=J/'research/performance_first_v2_20261103_v1/agent_c'
for d in ['option_previews','spec_candidates','cpu/option_echo_runs']: (C/d).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p);return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
source=json.loads((J/'control/SOURCE_QUALIFICATION.json').read_text())['source_identity'];cells=[];echo=[]
refs={}
for program,key in [('FWT','FASTWALSHTRANSFORM_FC3A9062'),('GEMM','GEMM_140F6ED3')]:
 for mode in ['S','WV_ZERO_RO']:
  sp=J/f'cases/EP_PERF_{key}_{mode}_REF_V1/control/FROZEN_SPEC.json';base=json.loads(sp.read_text());assert base['source_identity']==source
  refs[(program,mode)]=ref(sp)
  for family,geo,fr in [('G64W16',True,128),('FRFCFS256',False,256),('G64W16_FRFCFS256',True,256)]:
   ident=f'EP_PERF_PFV2_SYSTEM850_{program}_{mode}_{family}_V1';opts=copy.deepcopy(base['expected_effective_options']);assert len(opts)==282
   if geo:opts['-gpgpu_cache:dl2']='S:64:128:16,L:B:m:L:P,A:128:1,128:0,32'
   opts['-gpgpu_frfcfs_dram_sched_queue_size']=str(fr)
   delta={k:{'before':base['expected_effective_options'][k],'after':opts[k]} for k in opts if opts[k]!=base['expected_effective_options'][k]}
   assert opts['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0' and opts['-dram_latency']=='100'
   assert opts['-gpgpu_ep_l2_ro_tag_detach']==opts['-gpgpu_ep_l2_ro_line_mshr_bypass']=='0'
   ov=C/'option_previews'/f'{ident}.config';ov.write_text('# CPU-qualified exact final delta; not native authorization\n'+''.join(k+' '+d['after']+'\n' for k,d in sorted(delta.items())))
   op=C/'option_previews'/f'{ident}.json';op.write_text(json.dumps(opts,indent=2)+'\n')
   cmd=[str(C/'cpu/option_echo_full_cpu')]
   for z in base['ordered_configs']:assert sha(z['path'])==z['sha256'];cmd+=['-config',z['path']]
   cmd+=['-config',str(ov),'-trace',base['trace_entry']];log=C/'cpu/option_echo_runs'/f'{ident}.stdout';r=subprocess.run(cmd,stdout=log.open('w'),stderr=subprocess.STDOUT,timeout=45);actual={}
   for l in log.read_text().splitlines():
    if not l.startswith('-'):continue
    x=l.split(' # ',1)[0].strip().split(None,1);value=x[1].strip() if len(x)>1 else '';assert x[0] not in actual or actual[x[0]]==value, 'conflicting duplicate option echo';actual[x[0]]=value
   diff={k:{'expected':opts[k],'actual':actual.get(k)} for k in opts if opts[k]!=actual.get(k)};extra=sorted(set(actual)-set(opts));assert r.returncode==0 and len(actual)==282 and not diff and not extra,(ident,r.returncode,len(actual),diff,extra)
   er={'id':ident,'argv':cmd,'returncode':r.returncode,'option_count':len(actual),'identical_legacy_duplicate_registration':'gpgpu_shmem_warp_parts appears twice with identical value1; canonical282 unique options, conflicts rejected','exact282_PASS':True,'actual_options_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True).encode()).hexdigest(),'stdout_ref':ref(log),'changed_options':delta};echo.append(er)
   keep=['source_worktrees','binary_path','static_library_path','source_keep','input_identity_sha256','input_binding_ref','trace_entry','command_count','all_unique_kernel_members','expected_kernel_launches','expected_kernel_scopes','expected_CTA','expected_instructions','numeric_output','original_capture_completeness','scientific_scope','limits','estimated_peak_RAM_bytes','estimated_wall_seconds','observer_env','host_cpu','output_forecast']
   sk={k:copy.deepcopy(base[k]) for k in keep if k in base};sk.update(schema='EP_PF_V2_SYSTEM850_EXACT_SPEC_CANDIDATE_V1',status='CPU282_AND_PROTOCOL_QUALIFIED_NOT_NATIVE_AUTHORIZED',cohort=ident,program=program,mode=mode,profile='PFV2_SYSTEM850_'+family,family=family,source_identity=source,expected_effective_options=opts,geometry={'slices':64,'sets':64 if geo else 32,'ways':16 if geo else 8,'line_bytes':128},ordered_configs=base['ordered_configs']+[ref(ov)],fresh_scope_request_id=None,goal=None,launch_permission=False,automatic_retry=False,refund=False,old_application_acceptance_inherited=False,source_qualification_evidence_ref=base['source_qualification_ref'],input_eligibility_evidence_ref=base['eligibility_ref'],RO_certificate='NOT_APPLICABLE_RO_DISABLED',reference850_spec_ref=ref(sp),exact_option_preview_ref=ref(op),pending_Main_qualifications=['finitefamily_user_authorization','fresh_Source/input/modeCPU_Main_review','Host/parser/newgeometry_newprofile_negative_controls','native soleentry_scope_andfreshbudget','dynamic_resources_andcurrentboot_namespace_pins','true164 archive_andindependentrestore_entry'])
   sf=C/'spec_candidates'/f'{ident}.json';sf.write_text(json.dumps(sk,indent=2)+'\n');cells.append({'id':ident,'program':program,'mode':mode,'family':family,'stage':'CONDITIONAL_COMBINATION' if geo and fr==256 else 'PRIMARY_SINGLE_FAMILY','geometry':sk['geometry'],'input_identity_sha256':base['input_identity_sha256'],'source_identity':source,'DRAM_MHz':850,'dram_latency':100,'FRFCFS':fr,'returnQ':192,'shared_credit_limit':fr+192-1,'modeled_incremental_resources':{'Tag_entries_per_slice':1024-256 if geo else 0,'FRFCFS_entries_per_channel':fr-128,'shared_credit_per_partition':fr-128,'physical_payload_extra_slots':0},'option_delta':delta,'old_REF850_spec_ref':ref(sp),'candidate_spec_ref':ref(sf),'option_preview_ref':ref(op),'final_overlay_ref':ref(ov),'CPU_echo_pass':True,'Host_native_status':'NOT_QUALIFIED_FOR_NEW_PROFILE','new_science_starts':0})
(C/'ACTUAL_282_SYSTEM850_CPU_RECEIPT.json').write_text(json.dumps({'schema':'EP_PF_V2_SYSTEM850_ACTUAL282_CPU_RECEIPT_V1','status':'PASS_ALL12_CORE_PLUS_TRACE_OPTION_ECHO','source_identity':source,'producer_binary_ref':ref(C/'cpu/option_echo_full_cpu'),'runs':echo,'scope':'CPU option registration/parse/print, no model loop; constructor/protocol checked in separate CPU receipt','science_starts':0},indent=2)+'\n')
(C/'MATCHED_S_EP_CONFIG_MATRIX.json').write_text(json.dumps({'schema':'EP_PF_V2_SYSTEM850_MATCHED_CONFIG_MATRIX_V1','status':'EXACT12_CANDIDATE_CELLS_NOT_NATIVE_REGISTERED','source_identity':source,'cells':cells,'first8':[z['id'] for z in cells if z['stage']=='PRIMARY_SINGLE_FAMILY'],'conditional4':[z['id'] for z in cells if z['stage']=='CONDITIONAL_COMBINATION'],'new_science_starts':0},indent=2)+'\n')
with (C/'MATCHED_S_EP_CONFIG_MATRIX.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['id','program','mode','family','stage','sets','ways','DRAM_MHz','dram_latency','FRFCFS','returnQ','shared_credit_limit','input_identity_sha256','CPU_echo_pass','Host_native_status']);w.writeheader()
 for z in cells:w.writerow({k:(z['geometry'][k] if k in ['sets','ways'] else z[k]) for k in w.fieldnames})
print('PASS12 actual282 CPU echoes; spec candidates/matrix written')

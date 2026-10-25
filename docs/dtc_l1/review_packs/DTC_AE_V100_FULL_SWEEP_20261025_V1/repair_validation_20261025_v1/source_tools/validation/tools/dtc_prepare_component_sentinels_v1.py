"""Prepare ten reviewable engineering cases; never executes a simulator."""
import pathlib,json,hashlib,importlib.util,subprocess,copy,datetime,re
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=R/'control/sentinels';D.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,o):
 p=P(p)
 with p.open('x') as s:json.dump(o,s,sort_keys=True,indent=2);s.write('\n')
def text_new(p,s):
 p=P(p)
 with p.open('x') as f:f.write(s)
micro=P('/root/share/mnt164/huangrulin/dtc_failure_repair_20261025_v1/component_sentinels/mixed_v1');micro.mkdir(parents=True,exist_ok=False)
instructions=[
 '0000 ffffffff 1 R0 MOV 0 0',
 '0010 ffffffff 1 R3 MOV 0 0',
 '0020 ffffffff 1 R4 LDG.E.SYS 1 R0 4 1 0x100000 4',
 '0030 ffffffff 1 R5 LDG.E.STRONG.GPU 1 R0 4 1 0x200000 4',
 '0040 ffffffff 0 STG.E.SYS 2 R0 R4 4 1 0x300000 4',
 '0050 ffffffff 1 R6 ATOMG.E.ADD.STRONG.GPU 3 R0 R0 R5 4 1 0x400000 0',
 '0060 ffffffff 0 RED.E.ADD.STRONG.GPU 2 R0 R5 4 1 0x500000 0',
 '0070 ffffffff 1 R4 LDG.E.SYS 1 R0 4 1 0x600000 4',
 '0080 ffffffff 0 EXIT 0 0']
microbody='''-kernel name = DTC_REPAIR_COMPONENT_MIXED_V1
-kernel id = 1
-grid dim = (1,1,1)
-block dim = (32,1,1)
-shmem = 0
-nregs = 8
-binary version = 70
-cuda stream id = 0
-shmem base_addr = 0x0
-local mem base_addr = 0x0
-accelsim tracer version = 3

# Engineering trace-format fixture, authored, not an NVBit capture or workload result.
#BEGIN_TB
thread block = 0,0,0
warp = 0
insts = 9
'''+ '\n'.join(instructions)+'\n#END_TB\n'
text_new(micro/'kernel-1.traceg',microbody)
text_new(micro/'kernelslist.g','\n'.join('MemcpyHtoD,'+addr+','+str(size) for addr,size in [('0x100000',128),('0x200000',128),('0x400000',4),('0x500000',4),('0x600000',128)])+'\nkernel-1.traceg\n')
sourcepins={str(p):sha(p) for p in [F/'core/src/gpgpu-sim/shader.cc',F/'core/src/abstract_hardware_model.cc',F/'framework/gpu-simulator/trace-driven/trace_driven.cc',F/'framework/gpu-simulator/trace-parser/trace_parser.cc',F/'framework/docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md',F/'framework/docs/dtc_l1/implementation/WORKLOAD_MANIFEST.md']}
put(D/'MIXED_ENGINEERING_TRACE_AUTHORSHIP_AND_SOURCE_CONTRACT.json',{'schema':'AUTHORED_TRACE_FORMAT_COMPONENT_FIXTURE_V1','source_pins':sourcepins,'classification':'ENGINEERING_SYNTHETIC_COMPONENT_SENTINEL_NOT_FORMAL','not_NVBit_capture':True,'not_recovered_original_M4_asset':True,'native_numerical_values':'UNPROVEN','instruction_contract':instructions,'expected_per_warp_atomics':2,'expected_atomic_lane_operations':64,'returning_ATOMG_and_zero_destination_RED':True,'same_address_atomic_requests_are_never_merged':True,'all_architecture_and_original_workload_assets_unchanged':True,'purpose':'Exercise real decoded load, bypass, store, returning atomic, zero-dest RED lifecycle and final drain only; no performance aggregate.'})
orig=read(N/'control/EP_VECTORADD_S_TRACE_RECEIPT.json');vecroot=P(orig['native_mirror_mount_path']);roots=[('VECTORADD_ORIGINAL4M',vecroot,'REUSED_ORIGINAL_FULL_TRACE_NOT_TRIMMED'),('M4_MIXED_AUTHORED',micro,'ENGINEERING_SYNTHETIC_COMPONENT_SENTINEL_NOT_FORMAL')]
spec=importlib.util.spec_from_file_location('read_only_ratebound_actual_audit',T/'tools/body_audit_ratebound.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
assets=[]
for name,root,classification in roots:
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(root)],text=True))['filesystems'][0];assert fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared'
 members=[{'relative_path':n,'sha256':sha(root/n),'size':(root/n).stat().st_size} for n in ['kernelslist.g','kernel-1.traceg']]
 if name=='VECTORADD_ORIGINAL4M':assert members==orig['members']
 digest=hashlib.sha256(json.dumps(members,sort_keys=True,separators=(',',':')).encode()).hexdigest();trace=root/'kernel-1.traceg';before=trace.stat();body=audit.audit({'path':str(trace),'actual_sha256':members[1]['sha256'],'workload':digest,'ordinal':1});after=trace.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns);body['full_SHA_current_size_mtime']=[after.st_size,after.st_mtime_ns]
 assert body['binary_version']==70 and not body['sparse_mask_base_stride_records'] and not body['unaligned_lane_memory_addresses'];assert body['coverage']=='ALL_DECLARED_WARPS_AND_FULL_GRID_WITH_TERMINAL_EXIT';assert not body['memory_instruction_paths'].get('GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED')
 qualification={'schema':'DTC_COMPONENT_SENTINEL_FULL_BODY_QUALIFICATION_V1','status':'BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS','issues':[],'trace_entry':str(root/'kernelslist.g'),'rows':[body],'expected_commands':(root/'kernelslist.g').read_text().splitlines(),'expected_instructions':body['active_thread_instructions'],'expected_CTA':body['complete_ctas'],'expected_kernels':1,'input_digest':digest,'model_starts':0,'program':name,'suite':'COMPONENT_SENTINEL_NOT_FORMAL','native_numerical_correctness':'UNPROVEN','classification':classification}
 asset={'program':name,'suite':'COMPONENT_SENTINEL_NOT_FORMAL','architecture':'SM70','trace_entry':str(root/'kernelslist.g'),'trace_directory':str(root),'members':members,'commandlist_sha256':members[0]['sha256'],'kind':classification,'logical_bytes':sum(m['size'] for m in members),'kernel_launches':1,'scientific_qualification_granted':False,'source_version_evidence':str(N/'control/EP_VECTORADD_S_TRACE_RECEIPT.json') if name=='VECTORADD_ORIGINAL4M' else str(D/'MIXED_ENGINEERING_TRACE_AUTHORSHIP_AND_SOURCE_CONTRACT.json')}
 binding={'schema':'DTC_REPAIR_COMPONENT_INPUT_BINDING_V1','input_digest':digest,'asset':asset,'qualification':qualification,'body_parser_sha256':sha(T/'tools/body_audit_ratebound.py'),'classification':'COMPONENT_SENTINEL_NOT_FORMAL','capture_status':classification,'prior_scientific_statuses':['ORIGINAL_CAPTURE_IDENTITY_PRESERVED_NO_NEW_FORMAL_CLAIM'] if name=='VECTORADD_ORIGINAL4M' else ['AUTHORED_ENGINEERING_TRACE_NO_CAPTURE_CLAIM'],'current_source_scope':'NEW_SEPARATE_REPAIR_COMPONENT_TEST_ONLY','new_formal_workload':False}
 binding_path=D/(digest+'.INPUT_BINDING.json');put(binding_path,binding);assets.append({'name':name,'input_digest':digest,'binding':binding,'binding_path':str(binding_path),'classification':classification})
print(json.dumps({'assets_prepared':[{'name':a['name'],'input_digest':a['input_digest'],'expected':{k:a['binding']['qualification'][k] for k in ['expected_instructions','expected_CTA','expected_kernels']},'bodysha':a['binding']['qualification']['rows'][0]['sha256']} for a in assets],'model_starts':0}),flush=True)
put(D/'ASSETS_CANDIDATE_V1.json',{'assets':[{k:v for k,v in a.items() if k!='binding'} for a in assets]})

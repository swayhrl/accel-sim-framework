"""Finite CPU-only full-body/SHA/applicability intake; zero simulator API."""
import pathlib,json,hashlib,importlib.util,time,os,resource,re,concurrent.futures,traceback
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');A=P('/root/data/dtc_main_20261023_v1/ae_fair_v1')
def read(p):return json.loads(P(p).read_bytes())
def write(p,x):
 p=P(p);tmp=p.with_name(p.name+'.writing');tmp.write_text(json.dumps(x,indent=2)+'\n');os.replace(tmp,p)
def worker(r):
 os.sched_setaffinity(0,{1+(int(r['input_digest'][:2],16)%2)});resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
 key=r['input_digest'];out=T/'qualification'/key;out.mkdir(exist_ok=True);started=time.time()
 try:
  spec=importlib.util.spec_from_file_location('pinned_ratebound_body_parser',T/'tools/body_audit_ratebound.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  a=r['asset'];members={x['relative_path']:x for x in a['members']};entry=P(r['trace_entry'])
  assert hashlib.sha256(entry.read_bytes()).hexdigest()==a['commandlist_sha256']
  rows=[];problems=[]
  opcode_source=A/'framework/gpu-simulator/ISA_Def/volta_opcode.h';opcodes=set(re.findall(r'\{\s*"([^"]+)"',opcode_source.read_text()))
  for ordinal,name in enumerate(r['ordered_kernels'],1):
   p=entry.parent/name;before=p.stat();member=members[name]
   assert before.st_size==member['size']
   body=m.audit({'path':str(p),'workload':key,'ordinal':ordinal,'actual_sha256':member['sha256']});after=p.stat()
   assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
   body['FUSE_before_inode_informational']=before.st_ino;body['FUSE_after_inode_informational']=after.st_ino
   body['full_SHA_current_size_mtime']=[after.st_size,after.st_mtime_ns]
   unknown=sorted({op.split('.')[0] for op in body['opcodes']}-opcodes)
   if unknown:problems.append({'kernel':ordinal,'reason':'NOT_IN_PINNED_VOLTA_OPCODE_MAP','opcodes':unknown})
   if body['sparse_mask_base_stride_records']:problems.append({'kernel':ordinal,'reason':'NONCONTIGUOUS_ACTIVE_MASK_BASE_STRIDE_INTERPRETATION_HOLD','records':body['sparse_mask_base_stride_records']})
   for domain in ['GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED','OTHER_MEMORY_FORM_REVIEW']:
    if body['memory_instruction_paths'].get(domain):problems.append({'kernel':ordinal,'reason':domain,'records':body['memory_instruction_paths'][domain]})
   if body['binary_version']!=70:problems.append({'kernel':ordinal,'reason':'NOT_SM70'})
   row=dict(body);row.update(kernel=body['kernel'],active_thread_instructions=body['active_thread_instructions'],complete_ctas=body['complete_ctas']);rows.append(row)
   write(out/('kernel_'+str(ordinal)+'.json'),body)
   write(out/'PROGRESS.json',{'state':'BODY_READ_AND_SHA_VERIFIED','ordinal':ordinal,'kernels':len(r['ordered_kernels']),'elapsed_seconds':time.time()-started,'model_starts':0})
  if any('HOLD_SHARED_TRACE_INTERPRETATION' in s or s=='SCIENTIFIC_HOLD_PRESERVED' for s in r['prior_scientific_statuses']):problems.append({'reason':'PRIOR_EXACT_INPUT_SCIENTIFIC_HOLD_PRESERVED_REQUIRES_SEPARATE_REVIEW'})
  if any(s.startswith('Memcpy') and not s.startswith('MemcpyHtoD,') for s in r['expected_commands']):problems.append({'reason':'UNSUPPORTED_OR_UNQUALIFIED_COMMAND_KIND'})
  result={'schema':'DTC_SWEEP_FULL_CURRENT_BODY_SHA_QUALIFICATION_V1','input_digest':key,'bundle_id':r['bundle_id'],'program':r['program'],'suite':r['suite'],'status':'BODY_COMPLETE_SHA_PASS_PENDING_DOMAIN_REVIEW' if problems else 'BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS','issues':problems,'rows':rows,'expected_instructions':sum(x['active_thread_instructions'] for x in rows),'expected_CTA':sum(x['complete_ctas'] for x in rows),'expected_kernels':len(rows),'expected_commands':r['expected_commands'],'trace_entry':r['trace_entry'],'prior_scientific_statuses_preserved':r['prior_scientific_statuses'],'capture_complete_native_input':'NOT_NEWLY_CERTIFIED;whole_declared_trace_only','native_numerical_correctness':'UNPROVEN','opcode_map_source_sha256':hashlib.sha256(opcode_source.read_bytes()).hexdigest(),'elapsed_seconds':time.time()-started,'model_starts':0}
  write(out/'QUALIFICATION.json',result)
  return {'input_digest':key,'program':r['program'],'bundle_id':r['bundle_id'],'status':result['status'],'issues':problems,'instructions':result['expected_instructions'],'CTA':result['expected_CTA'],'kernels':len(rows),'elapsed_seconds':result['elapsed_seconds']}
 except BaseException as e:
  result={'input_digest':key,'bundle_id':r['bundle_id'],'program':r['program'],'status':'HOLD_FULL_BODY_OR_SHA_AUDIT_FAILED','error':repr(e),'traceback':traceback.format_exc(),'elapsed_seconds':time.time()-started,'model_starts':0};write(out/'QUALIFICATION.json',result);return result
def main():
 assert not (T/'control/BODY_QUALIFICATION_START.json').exists(),'one finite body qualification worker;inspect existing progress'
 write(T/'control/BODY_QUALIFICATION_START.json',{'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'workers':2,'per_worker_IO_cap_bytes_s':5*1024**2,'model_starts':0,'operation':'finite_readonly_all_normal_unique_inputs'})
 inputs=read(T/'control/INTAKE_CANDIDATES.json')['inputs'];unique={}
 for r in inputs:unique.setdefault(r['input_digest'],r)
 pending=sorted(unique.values(),key=lambda r:r['asset']['logical_bytes']);done=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  futures={pool.submit(worker,r):r for r in pending}
  for future in concurrent.futures.as_completed(futures):
   item=future.result();done.append(item);state={'state':'READONLY_BODY_QUALIFYING' if len(done)<len(pending) else 'ALL_FINITE_BODY_QUALIFICATIONS_CLOSED','total_unique':len(pending),'closed':len(done),'rows':done,'model_starts':0,'observed_unix':time.time()};write(T/'analysis/BODY_QUALIFICATION_PROGRESS.json',state)
   print(json.dumps({'closed':len(done),'total':len(pending),'result':{k:v for k,v in item.items() if k not in ['traceback']}}),flush=True)
if __name__=='__main__':main()

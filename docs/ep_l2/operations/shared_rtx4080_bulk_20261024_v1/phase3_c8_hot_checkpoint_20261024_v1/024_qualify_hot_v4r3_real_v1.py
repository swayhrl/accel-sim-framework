import pathlib,json,hashlib,subprocess,time
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');R=B/'objects/ORD_Parboil_stencil_c2c817b38690_A001';V=C/'validate_app_hot_resume_v4r3.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(V)=='85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909'
baseline=json.loads((R/'FULL_RECORD_VALIDATION.json').read_text());rows=[]
for workers in [8,16]:
 work=C.parent/f'validator_hot_v4r3_real_w{workers}_A1';out=C/f'VALIDATOR_HOT_V4R3_REAL_W{workers}_A1.json';cache=C.parent/'validator_resume_v3_qualification_A1/CACHE_FIRST50.json'
 cmd=['python3','-B',str(V),str(R),str(R/'map/manifest.json'),'--helper',str(C/'stencil_original_f9_validator.py'),'--parser',str(R/'contract/validate_v7.py'),'--work',str(work),'--output',str(out),'--raw-manifest',str(R/'MANIFEST.json'),'--raw-manifest-sha256',sha(R/'MANIFEST.json'),'--max-workers',str(workers),'--deadline','1800']
 if workers==16:cmd+=['--reuse-manifest',str(cache),'--reuse-manifest-sha256',sha(cache)]
 start=time.time()
 with(C/f'VALIDATOR_HOT_V4R3_REAL_W{workers}_A1.log').open('x')as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=1900)
 assert p.returncode==0 and not(work/'FAILURE.json').exists();complete=json.loads((work/'CONTROLLER_COMPLETE.json').read_text());assert complete['output_sha256']==sha(out)
 q=json.loads(out.read_text())
 for k in ['kernels','ctas','warps','counts','per_kernel','stream_ids']:assert q[k]==baseline[k],k
 assert q['reused_terminal_results_old_exit_not_separately_recorded']==(50 if workers==16 else 0)
 rows.append({'workers':workers,'seconds':time.time()-start,'status':'REAL_FULL100_KERNEL_ALL_COUNTS_FIELDS_HEADER_EQUIVALENCE_PASS','source_records':q['counts']['sass_records'],'reused_terminal_results_old_exit_not_separately_recorded':q['reused_terminal_results_old_exit_not_separately_recorded'],'controller':complete,'result_sha256':sha(out),'complete_sha256':sha(work/'CONTROLLER_COMPLETE.json'),'source_KEEP':True,'GPU_runs':0})
 (C/'VALIDATOR_HOT_V4R3_REAL_EQUIVALENCE_V1.json').write_text(json.dumps({'validator_sha256':sha(V),'rows':rows},indent=2)+'\n')
print(json.dumps(rows))

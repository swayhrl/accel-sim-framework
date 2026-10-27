import pathlib,json,hashlib,subprocess,collections
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1');E=json.loads((A/'evidence/prior_EVIDENCE_SNAPSHOT.json').read_bytes());T=P('/root/data/dtc_main_v100_sweep_20261025_v1');repo=P('/root/data/dtc_failure_repair_20261025_v1/core');sha='2e3bef4364e578cddd0e881c0baace2e51c55930';qual=[];sources=[]
for r in E['rows']:
 if r['intake']['program']not in ['BICG','ATAX','MVT','dwt2d','mri-q','GEMM','3MM']or not r['original_modes']:continue
 p=T/'qualification'/r['intake']['input_digest']/'QUALIFICATION.json';b=p.read_bytes();q=json.loads(b);qual.append(dict(program=r['intake']['program'],input_digest=r['intake']['input_digest'],source=str(p),sha256=hashlib.sha256(b).hexdigest(),kernel_opcode_counts=[{k:a.get(k)for k in ['ordinal','kernel','complete_ctas','complete_warps','active_thread_instructions','warp_instruction_records','opcodes','memory_instruction_paths']}for a in q['rows']]))
for rel,terms in [('src/gpgpu-sim/gpu-sim.cc',['gpu_stall_icnt2mem++','gpu_stall_mem2icnt++','gpu_stall_dramfull','m_perf_sim_memcpy','kernel_launch_latency']),('src/gpgpu-sim/shader.cc',['void ldst_unit::dtc_l1_service_retired','void ldst_unit::dtc_l1_sample_service_occupancy','DTC_SERVICE_V1_%s','DTC_L1_oo_tag_evictions','service_retire.commit'])]:
 r=subprocess.run(['git','-C',str(repo),'show',sha+':'+rel],capture_output=True);assert r.returncode==0;ls=r.stdout.decode().splitlines();idx=[n for n,l in enumerate(ls)if any(t in l for t in terms)];sources.append(dict(commit=sha,path=rel,sha256=hashlib.sha256(r.stdout).hexdigest(),segments=[dict(start=max(1,n-7),end=min(len(ls),n+25),text='\n'.join(f'{i+1}: {ls[i]}'for i in range(max(0,n-8),min(len(ls),n+25))))for n in idx]))
out=dict(qualification_opcodes=qual,source_excerpts=sources);(A/'evidence/BOTTLENECK_SUPPLEMENT.json').write_text(json.dumps(out,indent=2)+'\n')
for r in qual:
 if r['program']in ['dwt2d','mri-q']:
  count=collections.Counter()
  for k in r['kernel_opcode_counts']:count.update(k['opcodes'])
  print(r['program'],r['input_digest'][:16],count.most_common(13),{k:v for k,v in count.items()if 'MUFU'in k})
print('SOURCE GPU STALL EXCERPTS',sources[0]['segments'][:3])

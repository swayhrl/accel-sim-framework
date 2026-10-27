import pathlib,json,gzip,re,hashlib,subprocess,datetime
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/D');A.mkdir(parents=True,exist_ok=True)
L=json.loads(P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1/evidence/LEDGER_AUDIT.json').read_bytes()); digests={'ATAX':'eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950','MVT':'f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079','BICG':'ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef'};rows=[]
for r in L['current_original']:
 if digests.get(r['program'])!=r['input_digest']:continue
 for mode in ['CH','DH']:
  m=r['modes'][mode];assert m['strict']['performance_accepted'] and m['DONE']['launcher_wait_returncode']==0
  p=P(m['out'])/'raw.log.gz';assert p.stat().st_size<64*1024**2;h=hashlib.sha256();ss=[];c={};n=0
  with gzip.open(p,'rb') as f:
   for n,b in enumerate(f,1):
    h.update(b);s=b.decode(errors='replace').rstrip();z=re.match(r'^\s*([\w:.\[\]-]+)\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*$',s)
    if z and z[1].startswith(('DTC_','gpu_','gpgpu_','L1D_','L2_','averagemf','maxmf','avg_')):
     k,v=z.groups();c.setdefault(k,[]).append({'line':n,'value':float(v) if any(t in v for t in '.eE') else int(v)})
    if any(t in s for t in ['DTC_SERVICE_V1','DTC_L1_','kernel_name','gpu_sim_cycle','gpu_tot_sim_cycle','GLOBAL_ACC_R[','GLOBAL_ACC_W[','n_rd=','n_cmd=','avg_mrq']):ss.append({'line':n,'text':s})
  assert h.hexdigest()==m['DONE']['raw_uncompressed_sha256'];rows.append(dict(program=r['program'],input_digest=r['input_digest'],mode=mode,cohort=m['cohort'],uuid=m['uuid'],raw_path=str(p),raw_uncompressed_sha256=h.hexdigest(),raw_total_lines=n,strict=m['strict'],DONE=m['DONE'],launch=m['launch'],spec=m['spec'],archive=m['archive'],files=m['files'],raw_counter_series=c,raw_selected_lines=ss))
out={'schema':'DTC_STRIDED_CLOSED_ORIGINAL_RAW_V1','observed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'new_model_starts':0,'raw_files_modified':False};(A/'CLOSED_RAW_EVIDENCE.json').write_text(json.dumps(out,indent=2)+'\n')
core=P('/root/data/dtc_failure_repair_20261025_v1/core');commit='2e3bef4364e578cddd0e881c0baace2e51c55930';sources=[]
for f in ['src/gpgpu-sim/l2cache.cc','src/gpgpu-sim/dram.cc','src/gpgpu-sim/dram_sched.cc','src/gpgpu-sim/mem_latency_stat.cc']:
 z=subprocess.run(['git','-C',str(core),'show',commit+':'+f],capture_output=True);assert z.returncode==0;sources.append({'path':f,'commit':commit,'sha256':hashlib.sha256(z.stdout).hexdigest(),'text':z.stdout.decode()})
(A/'DOWNSTREAM_SOURCE_FILES.json').write_text(json.dumps(sources,indent=2)+'\n');print(json.dumps({'rows':len(rows),'raw_extract_bytes':(A/'CLOSED_RAW_EVIDENCE.json').stat().st_size,'sources':len(sources)}))

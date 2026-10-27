import pathlib,json,gzip,re,hashlib,subprocess,datetime
P=pathlib.Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/C');A.mkdir(parents=True,exist_ok=True)
L=json.loads(P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1/evidence/LEDGER_AUDIT.json').read_bytes())
names=['2DCONV','3DCONV','particlefilter_naive','3MM','GEMM'];rows=[]
for r in L['current_original']:
 if r['program'] not in names:continue
 for mode,m in r['modes'].items():
  assert m['strict']['performance_accepted'] and m['DONE']['launcher_wait_returncode']==0
  p=P(m['out'])/'raw.log.gz'; h=hashlib.sha256(); selected=[]; counters={}; n=0
  with gzip.open(p,'rb') as f:
   for n,b in enumerate(f,1):
    h.update(b);s=b.decode(errors='replace').rstrip()
    z=re.match(r'^\s*([\w:.\[\]-]+)\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*$',s)
    if z and z[1].startswith(('DTC_','gpu_','gpgpu_','L1D_','L2_','averagemf','maxmf','avg_')):
     k,v=z.groups();counters.setdefault(k,[]).append({'line':n,'value':float(v)if any(t in v for t in '.eE')else int(v)})
    if any(t in s for t in ['DTC_SERVICE_V1','DTC_L1_','kernel_name','gpu_sim_cycle','gpu_tot_sim_cycle','GLOBAL_ACC_R[','GLOBAL_ACC_W[']):selected.append({'line':n,'text':s})
  assert h.hexdigest()==m['DONE']['raw_uncompressed_sha256']
  rows.append(dict(program=r['program'],input_digest=r['input_digest'],mode=mode,cohort=m['cohort'],uuid=m['uuid'],raw_path=str(p),raw_uncompressed_sha256=h.hexdigest(),raw_total_lines=n,strict=m['strict'],DONE=m['DONE'],launch=m['launch'],spec=m['spec'],archive=m['archive'],files=m['files'],raw_counter_series=counters,raw_selected_lines=selected))
out={'schema':'DTC_POSITIVE_RAW_EVIDENCE_V1','observed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'new_model_starts':0,'raw_files_modified':False}
(A/'RAW_EVIDENCE_EXTRACT.json').write_text(json.dumps(out,indent=2)+'\n')
core=P('/root/data/dtc_failure_repair_20261025_v1/core');commit='2e3bef4364e578cddd0e881c0baace2e51c55930'; sources=[]
for f in ['src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','src/gpgpu-sim/dtc-l1-tag-index.h']:
 z=subprocess.run(['git','-C',str(core),'show',commit+':'+f],capture_output=True);assert z.returncode==0
 sources.append({'path':f,'commit':commit,'sha256':hashlib.sha256(z.stdout).hexdigest(),'text':z.stdout.decode()})
(A/'ORIGINAL_SOURCE_FILES.json').write_text(json.dumps(sources,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'raw_extract_bytes':(A/'RAW_EVIDENCE_EXTRACT.json').stat().st_size,'source_bytes':(A/'ORIGINAL_SOURCE_FILES.json').stat().st_size,'new_model_starts':0}))

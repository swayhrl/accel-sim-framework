"""Close CPU-only G0 admission with actual evidence; no training or CUDA calls."""
from common import *
import resource,subprocess,zipfile,sys,ast
before=time.monotonic();http=[json.loads(x) for x in (ROOT/'raw/http_receipts.jsonl').read_text().splitlines()];assert any('ogb.stanford.edu/docs/nodeprop/'in x['url'] and x.get('status')==200 for x in http)
license_rows=[x for x in http if 'amazon-reviews-pds' in x['url']];assert len(license_rows)>=5 and all(x.get('status')==403 for x in license_rows)
relay=json.loads((ROOT/'raw/controller_source_and_license_receipt.json').read_text());relay['controller_s3_check']['response_body_bytes']='NOT_METERED; conservative controller metadata reserve used';(ROOT/'raw/controller_source_and_license_receipt.json').write_text(json.dumps(relay,indent=2))
source=ROOT/'source/dgl_v240_dataset_controller_relay.py';raw=source.read_bytes();assert hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()=='df3b51f8b074406867ea68e364f98dae2e1e61f6'
assert 'https://data.dgl.ai/dataset/graphbolt/'in source.read_text() and 'ogbn-products-seeds'in source.read_text()
cache=pathlib.Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/wheels/torch-2.2.0+cu121-cp310-cp310-linux_x86_64.whl');stat=cache.stat();digest=sha(cache);after=cache.stat();assert stat.st_size==after.st_size and stat.st_mtime_ns==after.st_mtime_ns
with zipfile.ZipFile(cache) as z:metadata=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode();expanded=sum(x.file_size for x in z.infolist())
worktrees=[];blocks=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=WORK,text=True).split('\n\n')
for block in blocks:
 lines=block.splitlines()
 if not lines:continue
 p=lines[0].split(' ',1)[1]
 if any(s in p for s in ['a26gr1','a45h','a50g']):
  head=next((s.split(' ',1)[1] for s in lines if s.startswith('HEAD ')),None);status=subprocess.check_output(['git','-C',p,'status','--porcelain'],text=True);worktrees.append({'path':p,'HEAD':head,'status_porcelain':status,'role':'observed existing tree only; no checkout/reset/asset writes'})
# Do not import torch/DGL, initialize CUDA, inspect VRAM or touch the GPU lock.
for p in (WORK/'tools/aiarch_a59').glob('*.py'):compile(p.read_text(),str(p),'exec')
source_ids={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (ROOT/'source').glob('*') if p.is_file()}
node_bytes=sum(x.get('bytes',0) for x in http if x['method']!='OFFICIAL_GITHUB_CONNECTOR_CONTROLLER_RELAY');relay_bytes=sum(x.get('bytes',0) for x in http if x['method']=='OFFICIAL_GITHUB_CONNECTOR_CONTROLLER_RELAY')
# 16MiB conservative reserve covers unmetered controller web/API metadata,
# repeated source read, independent failed license request and small Git fetches.
# This is not represented as a measured transfer count.
out={'terminal':'DATA_LICENSE_NO_GO','G0':'FAIL_UNRESOLVED_APPLICABLE_DATASET_USAGE_TERMS','G1':'NOT_RUN_G0_FAILED','G2':'NOT_RUN_G0_FAILED','G3':'NOT_RUN_NO_NATIVE_EVIDENCE','G4':'LEGAL_EVIDENCE_PUBLICATION_PENDING','fixed_start':'d730ad41c6ca8ce60183e431bda23638c7a8e3e5','license_requests':license_rows,'source_files':source_ids,'node_HTTP_body_bytes_metered':node_bytes,'controller_relay_origin_and_transfer_counted_bytes':relay_bytes,'unmetered_controller_docs_and_Git_bytes_conservative_reserve':16*1024**2,'all_network_budget_upper_accounting_bytes':node_bytes+relay_bytes+16*1024**2,'scientific_data_download_bytes':0,'dependency_wheel_download_bytes':0,'installation':0,'GPU_lock_seconds':0,'GPU_initializations':0,'training_steps':0,'data_present_or_absent':'NOT_ESTABLISHED; no real graph payload acquired','license_legality_claim':'NO_ILLEGALITY_OR_REVOCATION_CLAIM; applicable grant not verified under this Goal mandatory gate','official_software_candidate':{'DGL':'2.4.0+cu121','wheel_status':'HEAD200','wheel_declared_bytes':483914623,'wheel_sha256':'NOT_DOWNLOADED_NOT_AVAILABLE','Torch_cached_version':'2.2.0+cu121','Torch_cached_wheel_bytes':stat.st_size,'Torch_cached_wheel_SHA256':digest,'Torch_cached_wheel_expanded_bytes':expanded,'Torch_requires_dist':[s for s in metadata.splitlines() if s.startswith('Requires-Dist:')],'read_only_cache_stat_unchanged':True,'binary_ABI':'NOT_RUN_NOT_PROVEN','formal_backend_P_or_D':'NOT_FROZEN_G0_FAILED'},'old_worktrees_metadata':worktrees,'no_old_worktree_or_cache_write_performed':True,'effective_CPU_affinity':sorted(os.sched_getaffinity(0)),'CPU_preparation_elapsed_seconds_to_closeout':time.time()-json.loads((ROOT/'start.json').read_text())['epoch'],'CPU_closeout_peak_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'whole_goal_peak_RSS':'NOT_CONTINUOUSLY_METERED; earlier CPU-only metadata probes were not under a persistent RSS supervisor','CPU_closeout_seconds':time.monotonic()-before,'new_allocated_bytes_to_closeout':check(),'FS_free_bytes':shutil.disk_usage(ROOT).free,'no_next_goal':True}
(ROOT/'g0_receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['source_files','license_requests','old_worktrees_metadata','official_software_candidate']},indent=2))

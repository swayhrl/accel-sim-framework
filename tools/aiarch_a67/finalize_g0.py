"""Final CPU-only source authority, isolation and resource admission."""
import ast,json,subprocess,time,shutil
from pathlib import Path
from paths import R,W,OLD,OLD65,sha,save,usage,DISPATCH_EPOCH
from preflight import snapshot

def main():
 assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='266314db14686b75d643c446824ebf8d59ba3a51'
 authorities={}
 pairs=[('266314db14686b75d643c446824ebf8d59ba3a51','docs/ai_workload_research/goals/AI_ARCH_A67_IGB_SMALL_EAGER_SCOPE_BOUNDED_WALL_109_V1.md'),('759dc19022233b375af626761f058c2eb898350b','docs/ai_workload_research/reviews/AI_ARCH_A66_A65_SAME_BATCH_NUMERIC_AND_STORAGE_INDEPENDENT_REVIEW_2026-10-16_V1.md'),('326dcac6227d1c1af6b38e4f76d21566525f35aa','docs/ai_workload_research/reviews/AI_ARCH_A64_A61_GNN_NUMERIC_STOP_INDEPENDENT_REVIEW_2026-10-16_V1.md')]
 import hashlib
 for c,p in pairs:
  body=subprocess.check_output(['git','show',c+':'+p]);authorities[c+':'+p]={'blob':subprocess.check_output(['git','rev-parse',c+':'+p],text=True).strip(),'SHA256':hashlib.sha256(body).hexdigest()}
 save('authority_identity.json',authorities)
 for name in ['native.py','native_utils.py']:
  p='tools/aiarch_a61/'+name;assert subprocess.check_output(['git','show','37120f98186b83a946f4812755523f5d73245491:'+p])==(W/p).read_bytes()
 for name in ['numeric.py','gpu_supervisor.py']:
  p='tools/aiarch_a65/'+name;assert subprocess.check_output(['git','show','3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79:'+p])==(W/p).read_bytes()
 for c,tree in [('37120f98186b83a946f4812755523f5d73245491','d13b446ca4824cb3ad7ffae25b5ce91c023b75a1'),('3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79','7a37e87cc063d03ee2a7b4a2212cad2a6da098eb')]:assert subprocess.check_output(['git','rev-parse',c+'^{tree}'],text=True).strip()==tree
 assert snapshot(OLD)==json.loads((R/'old_A61_metadata_before.json').read_text())
 assert snapshot(OLD65)==json.loads((R/'old_A65_metadata_before.json').read_text())
 for p in (W/'tools/aiarch_a67').glob('*.py'):
  tree=ast.parse(p.read_text())
  assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='compile' and isinstance(n.func.value,ast.Name) and n.func.value.id=='torch' for n in ast.walk(tree))
 guard=(R/'runtime/lib/python3.10/site-packages/sitecustomize.py').read_text();assert str(R) in guard and str(W) in guard and str(OLD65) not in guard
 assert shutil.disk_usage(R).free>=64*1024**3
 assert time.time()-DISPATCH_EPOCH<3600
 pre={'status':'PASS','CPU_prepare_seconds':time.time()-DISPATCH_EPOCH,'W_allocated_bytes':usage([W]),'R_allocated_bytes':usage([R]),'FS_free_bytes':shutil.disk_usage(R).free,'estimated_new_evidence_bytes':16*1024**2,'raw_log_hard_limit_bytes':32*1024**2,'new_disk_hard_limit_bytes':256*1024**2,'host_RAM_estimate':'A65 observed9.57GiB plus small oracle/metadata, below16GiB; parent15.5GiB early margin','FULL_VRAM_estimate':'A61 onebatch reserved8.10GiB plus conservative1-2prefetched feature buffers; retained allocator.70 and NVML early margin, actual new warmups gate capacity','no_Torch_import_no_GPU_lock':True,'old_assets_metadata_unchanged':True,'eager_only_static_check':'PASS_NO_TORCH_COMPILE_CALL','boundary_handshake':'NVML PID acknowledgement strictly outside formal timer','raw_budget_excludes_existing_authority':'inherited A61/A65 Git evidence; counted in new disk footprint nonetheless'}
 save('G0_final.json',pre);print('A67_ALL_CPU_GATES_PASS',json.dumps(pre),flush=True)

if __name__=='__main__':main()

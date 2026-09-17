import csv,json,hashlib
from pathlib import Path
W=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-q05-native-context-v1');O=W/'docs/vm_tlb/review_packs/AWMA_Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1';O.mkdir(parents=True,exist_ok=True)
p=Path('/data/c16/awma/qwen25_s2_kernel_census_20260917T101100Z/analysis/ALL_KERNEL_LAUNCHES.tsv'); rows=list(csv.DictReader(p.open(),delimiter='\t')); q=next(i for i,r in enumerate(rows) if r['global_launch_index']=='34' and 'pytorch_flash::flash_fwd_kernel' in r['exact_kernel_name'])
cols=['relative_position_to_Q05','global_launch_navigation','phase','exact_kernel_function','normalized_family','grid','block','duration_ns','identity_basis']
out=[]
for i,r in enumerate(rows[:q+1]):out.append({'relative_position_to_Q05':i-q,'global_launch_navigation':r['global_launch_index'],'phase':r['phase'],'exact_kernel_function':r['exact_kernel_name'],'normalized_family':r['normalized_kernel_family'],'grid':r['grid'],'block':r['block'],'duration_ns':r['duration_ns'],'identity_basis':'accepted NSYS census; Q05 binding is exact family+first PREFILL same-shape occurrence, global launch navigation only'})
with (O/'Q05_PREDECESSOR_SEQUENCE.tsv').open('w',newline='') as f:
 x=csv.DictWriter(f,fieldnames=cols,delimiter='\t');x.writeheader();x.writerows(out)
ident={'model':'Qwen/Qwen2.5-0.5B-Instruct','revision':'7ae557604adf67be50417f59c2c2f167def9a775','scenario':'S2_TEXT','batch':1,'prefill_tokens':2048,'decode_tokens':32,'dtype':'FP16','backend':'SDPA','target':'Q05_PREFILL_ATTN_FLASH','accepted_census_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'q05_navigation_launch':34,'prefill_predecessor_count':34}
(O/'WORKLOAD_IDENTITY.json').write_text(json.dumps(ident,indent=2)+'\n')
(O/'LOCK_BLOCKER.md').write_text('D0 GPU lock is held by pid 681650 (interactive bash in accel-sim-c16-olmoe-s2-v32). Normal nonblocking flock refused; no bypass/kill performed. No GPU observer/timing/NCU action was started.\n')

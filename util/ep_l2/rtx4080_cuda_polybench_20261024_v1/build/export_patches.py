from pathlib import Path
import json,hashlib,difflib,subprocess,io,tarfile
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');P=R/'source_patches';P.mkdir(exist_ok=False);pairs=[]
for n in ['adapted_v3','adapted_v4']:pairs.append((n,R/'source/polybench-gpu-1.0',R/n/'polybench-gpu-1.0'))
for d in (R/'adapted_sdk42').iterdir():
 if not d.is_dir():continue
 name=d.name;n='histogram' if name.startswith('histogram') else 'scan' if name.startswith('scan') else 'threadFenceReduction' if name.startswith('threadFence') else 'dxtc' if name.startswith('dxtc') else 'eigenvalues' if name.startswith('eigenvalues') else None
 if n:pairs.append((name,R/'source/sdk/4.2'/n,d))
for root in [R/'modern_repair_volume_v1',R/'modern_correct_volume_arg_v1']:
 for d in (root/'Samples/5_Domain_Specific').iterdir():
  if d.is_dir():pairs.append((root.name+'_'+d.name,R/'source/cuda-samples-11.8/Samples/5_Domain_Specific'/d.name,d))
index=[]
for name,base,new in pairs:
 patch=[];files=[]
 for p in sorted(new.rglob('*')):
  if not p.is_file() or p.suffix not in ['.cu','.cpp','.cuh','.h']:continue
  rel=p.relative_to(new);op=base/rel
  if not op.exists():continue
  a=op.read_bytes();b=p.read_bytes()
  if a==b:continue
  patch.extend(difflib.unified_diff(a.decode().splitlines(True),b.decode().splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel)));files.append({'path':str(rel),'original_sha256':hashlib.sha256(a).hexdigest(),'modified_sha256':hashlib.sha256(b).hexdigest()})
 out=P/(name+'.patch');out.write_text(''.join(patch));index.append({'variant':name,'base_root':str(base),'modified_root':str(new),'patch':str(out),'patch_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':files})
(P/'PATCH_INDEX.json').write_text(json.dumps(index,indent=2)+'\n');print('patches',len(index),'changed_files',sum(len(x['files']) for x in index))

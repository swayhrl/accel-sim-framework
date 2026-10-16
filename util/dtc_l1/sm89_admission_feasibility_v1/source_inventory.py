#!/usr/bin/env python3
import hashlib,json,pathlib,re,subprocess,datetime
repo=pathlib.Path(__file__).resolve().parents[3];root=pathlib.Path('/data/c16/dtc_sm89_admission_feasibility_109_v1');pack=repo/'docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1'
def git(*a,cwd=repo):return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()
def data(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=repo)
commits={'frozen':'18a68dcccd795f1b6cda75504e9450d00c9cee02','awma_opt_in':'6f9c1df1a03bd9d26130b80be1c31f5957074630','awma_ada_named':'aeec5b9a69865012b16ac0a6627143e29f1fee06','c16_address_namespace':'2fa207fbc37a48f12641d810319b03ba1cf4e381','default_head':'565381ef5d43286895cefb3c71912c9d896516e9'}
rows=[]
for name,ref in commits.items():
 for path in ['gpu-simulator/trace-driven/trace_driven.cc','gpu-simulator/ISA_Def/ampere_opcode.h','gpu-simulator/trace-parser/trace_parser.cc','gpu-simulator/trace-parser/trace_parser.h']:
  b=data(ref,path);safe=name+'_'+path.rsplit('/',1)[1];(root/'assets'/safe).write_bytes(b)
  s=b.decode();rows.append(dict(role=name,commit=ref,path=path,git_blob=git('rev-parse',ref+':'+path),sha256=hashlib.sha256(b).hexdigest(),lines=len(s.splitlines()),sm89_lines=[dict(line=n,text=t.strip()) for n,t in enumerate(s.splitlines(),1) if '89' in t or 'ADA_RTX' in t],source_scope='source artifact only; no transferred platform qualification'))
roots=[l.split(' ',1)[1] for l in git('worktree','list','--porcelain').splitlines() if l.startswith('worktree ')]
groups={}
for r in roots:
 p=pathlib.Path(r)/'gpu-simulator/trace-driven/trace_driven.cc'
 if not p.is_file():continue
 b=p.read_bytes();h=hashlib.sha256(b).hexdigest();g=groups.setdefault(h,dict(paths=[],representative_head=None,representative_blob_matches=None,sm89_lines=[]));g['paths'].append(str(p))
 if g['representative_head'] is None:
  head=git('rev-parse','HEAD',cwd=r);expected=data(head,'gpu-simulator/trace-driven/trace_driven.cc');g.update(representative_head=head,representative_blob_matches=expected==b,sm89_lines=[dict(line=n,text=t.strip()) for n,t in enumerate(b.decode().splitlines(),1) if '89' in t or 'ADA_RTX' in t])
(pack/'SOURCE_ARTIFACTS.json').write_text(json.dumps(dict(commits=commits,artifacts=rows,local_worktrees_scanned=len(roots),distinct_decoder_variants=groups),indent=2)+'\n')
# Retain exact, selected inherited latency file and provenance; not an Ada calibration claim.
p='gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config';b=data(commits['awma_ada_named'],p);(pack/'EXISTING_AWMA_TRACE_CONFIG.txt').write_bytes(b)
refs=[('NVIDIA_CUDA_BINARY_UTILITIES_13_1','https://docs.nvidia.com/cuda/archive/13.1.0/cuda-binary-utilities/index.html#nvidia-ampere-gpu-and-ada-instruction-set'),('NVIDIA_ADA_COMPATIBILITY_12_8','https://docs.nvidia.com/cuda/archive/12.8.1/ada-compatibility-guide/index.html')];web=[]
for name,url in refs:
 web.append(dict(name=name,url=url,reviewed_date='2026-10-16',review_method='Official archival page opened/read using web tool during source review',sha256='NOT_LOCALLY_ARCHIVED',scope='Documentation reference only; no local tool installed. Optional slow HTML fetch stopped; CPU pipeline has no HTML download dependency.'))
(pack/'PRIMARY_REFERENCES.json').write_text(json.dumps(web,indent=2)+'\n')
print('local worktrees',len(roots),'distinct decoder variants',len(groups),'source artifacts',len(rows));print(json.dumps(web,indent=2))

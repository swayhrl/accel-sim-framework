from pathlib import Path
import json,re,hashlib,subprocess,datetime
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');S=R/'source/sdk/4.2';rows=[]
for d in sorted(S.iterdir()):
 if not d.is_dir():continue
 files=[p for p in d.rglob('*') if p.is_file()];srcs=[p for p in files if p.suffix in ['.cu','.cpp','.c','.h','.cuh']]
 txt='\n'.join(p.read_text(errors='replace') for p in srcs);mk=(d/'Makefile').read_text(errors='replace') if (d/'Makefile').exists() else ''
 flags=dict(re.findall(r'^\s*(\w+)\s*:?=\s*(.*)',mk,re.M));headers=sorted(set(re.findall(r'#\s*include\s*[<\"]([^>\"]+)',txt)))
 assets=[{'path':str(p.relative_to(d)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.suffix not in ['.cu','.cpp','.c','.h','.cuh','.pdf','.doc','.html'] and p.name!='Makefile']
 row={'program':d.name,'suite':'CUDA SDK','source_version':'4.2','source_head':'b059fdae25c2aabf737486aada743fca114469ce','source_tree_sha256':hashlib.sha256(''.join(str(p.relative_to(d))+' '+hashlib.sha256(p.read_bytes()).hexdigest()+'\n' for p in sorted(files)).encode()).hexdigest(),'makefile_flags':flags,'headers':headers,'bundled_noncode_assets':assets,'graphics_dependency':bool(re.search(r'(USEGL(LIB|UT)?\s*:?=\s*1|<GL/|<GLUT/|glutMainLoop|cudaGraphicsGL)',mk+'\n'+txt)),'texture_reference_legacy':bool(re.search(r'\btexture\s*<|cudaBindTexture|cudaUnbindTexture',txt)),'driver_api_legacy':bool(re.search(r'cuParamSet|cuLaunchGrid|cuModuleGetTexRef|CUdevprop',txt)),'needs_multigpu':d.name in ['simpleMultiGPU','simpleP2P','simpleMPI'],'build_status':'NOT_ATTEMPTED','native_status':'NOT_ATTEMPTED'}
 rows.append(row)
(R/'manifests/SDK42_DENOMINATOR_AUDIT_V1.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'programs':len(rows),'graphics_dependencies':sum(x['graphics_dependency'] for x in rows),'texture_legacy':sum(x['texture_reference_legacy'] for x in rows),'multigpu':sum(x['needs_multigpu'] for x in rows)}))

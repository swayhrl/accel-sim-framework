import pathlib,json,hashlib,subprocess,re
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1');E=json.loads((A/'evidence/prior_EVIDENCE_SNAPSHOT.json').read_bytes());C=P('/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection');D=P('/root/data/dtc_main_v100_sweep_20261025_v1/docs-worktree');records=[]
def add(p,lo=1,hi=None):
 p=P(p)
 if not p.is_file():return
 b=p.read_bytes();ls=b.decode(errors='replace').splitlines();records.append(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),start=lo,end=min(hi or len(ls),len(ls)),text='\n'.join(f'{i+1}: {ls[i]}'for i in range(lo-1,min(hi or len(ls),len(ls))))))
for rel in ['docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md','docs/dtc_l1/m5/handoffs/M5_E1_EXTENDED20_FORMALIZATION.md','docs/dtc_l1/m5/extended20/RODINIA_E1_SOURCE_AUDIT.md','docs/dtc_l1/m5/extended20/RODINIA_E1_DATA_RECOVERY.md','docs/dtc_l1/m5/extended20/FWT_11_19_E1_RECOVERY.md']:add(D/rel)
for rel in ['src/cuda/rodinia/2.0-ft/heartwall/main.cu','src/cuda/rodinia/2.0-ft/heartwall/kernel.cu','src/cuda/rodinia/3.1/cuda/lud/cuda/lud.cu','src/cuda/rodinia/3.1/cuda/lud/common/common.c','src/cuda/rodinia/3.1/cuda/dwt2d/main.cu']:add(C/rel)
rows=[]
programs=['fastWalshTransform','gaussian','hybridsort','heartwall','dwt2d','lud','cfd']
for r in E['rows']:
 if r['intake']['program']not in programs or not r['original_modes']:continue
 x=r['intake'];scripts={s['sha256']:s for a in x['asset']['source_aliases']for s in a.get('capture_scripts',[])};rows.append(dict(program=x['program'],digest=x['input_digest'],version=x['asset']['source_version_evidence'],commands=x['expected_commands'],kernel_sequence=[a['kernel']for a in r['kernel_geometry']],geometries=[{k:a[k]for k in ['complete_ctas','complete_warps','active_thread_instructions']}for a in r['kernel_geometry']],scripts=list(scripts.values())))
result=dict(records=records,inputs=rows);(A/'evidence/ADJUDICATION_EVIDENCE.json').write_text(json.dumps(result,indent=2)+'\n');print('docs',[(r['path'].split('/')[-1],len(r['text']))for r in records]);print('INPUTS',json.dumps([{k:v for k,v in r.items()if k not in ['scripts','geometries']}for r in rows],indent=2)[:13000])
# Exact original Core-source excerpts, never patched repaired Core semantics.
repo=P('/root/data/dtc_failure_repair_20261025_v1/core');commit='2e3bef4364e578cddd0e881c0baace2e51c55930';segments=[]
for rel,rs in [('src/gpgpu-sim/dtc-l1-tag-index.h',[(1,80)]),('src/gpgpu-sim/dtc-l1-common.h',[(1,150),(530,680),(860,910),(1695,1805)]),('src/gpgpu-sim/shader.cc',[(3010,3060),(3270,3340),(3565,3645),(5080,5115),(5690,5890),(5910,6160)]),('src/gpgpu-sim/gpu-cache.cc',[(95,145),(920,1000)])]:
 z=subprocess.run(['git','-C',str(repo),'show',commit+':'+rel],capture_output=True);assert z.returncode==0;ls=z.stdout.decode().splitlines();segments.append(dict(commit=commit,path=rel,sha256=hashlib.sha256(z.stdout).hexdigest(),ranges=[dict(start=lo,end=min(hi,len(ls)),text='\n'.join(f'{n+1}: {ls[n]}'for n in range(lo-1,min(hi,len(ls)))))for lo,hi in rs]))
(A/'evidence/ORIGINAL_CORE_SOURCE_EXCERPTS.json').write_text(json.dumps(segments,indent=2)+'\n')

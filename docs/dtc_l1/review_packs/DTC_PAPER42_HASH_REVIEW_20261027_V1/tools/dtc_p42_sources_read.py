import pathlib,json,hashlib,gzip,subprocess
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1');E=json.loads((A/'evidence/prior_EVIDENCE_SNAPSHOT.json').read_bytes());C=P('/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection');FW=P('/root/workspace/offline-sim-v1/accel-sim-framework');D=P('/root/data/dtc_main_v100_sweep_20261025_v1/docs-worktree')
records=[]
def add(p,ranges=None):
 p=P(p)
 if not p.is_file():records.append(dict(path=str(p),missing=True));return
 b=p.read_bytes();lines=b.decode(errors='replace').splitlines();segs=[dict(start=a,end=min(z,len(lines)),text='\n'.join(f'{i+1}: {lines[i]}'for i in range(a-1,min(z,len(lines)))))for a,z in(ranges or [(1,len(lines))])]
 records.append(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),segments=segs))
add(FW/'util/job_launching/apps/define-all-apps.yml',[(1,62),(500,700)])
for rel in ['src/cuda/polybench-gpu-1.0/CUDA/ATAX/atax.cu','4.2/C/src/scalarProd/scalarProd.cu','4.2/C/src/vectorAdd/vectorAdd.cu','4.2/C/src/fastWalshTransform/fastWalshTransform.cu','src/cuda/rodinia/3.1/cuda/cfd/euler3d.cu','src/cuda/rodinia/3.1/cuda/gaussian/gaussian.cu','src/cuda/rodinia/3.1/cuda/hybridsort/main.cu','src/cuda/rodinia/3.1/cuda/dwt2d/main.cu','src/cuda/rodinia/3.1/cuda/streamcluster/streamcluster_cuda.cu']:
 p=C/rel
 if p.exists()and p.stat().st_size>60000:
  text=p.read_text(errors='replace');ln=text.splitlines();inds=[i for i,l in enumerate(ln)if any(s in l for s in['argc','argv[','main(','getopt','npoints','numofpoints','dim =','fscanf','ITERATIONS','for(int i','for (int i'])];ran=[]
  for i in inds:
   a=max(1,i-5);z=min(len(ln),i+16)
   if ran and a<=ran[-1][1]:ran[-1]=(ran[-1][0],max(z,ran[-1][1]))
   else:ran.append((a,z))
  add(p,ran)
 else:add(p)
for rel in ['docs/dtc_l1/m5/extended20/SDK42_PARAMETERIZED_E1_SOURCE_AUDIT.md','docs/dtc_l1/m5/extended20/CUDA_SDK_E1_SOURCE_AUDIT.md','docs/dtc_l1/m5/handoffs/M5_E1_V100_CAPTURE_READINESS.md']:add(D/rel)
heads=[]
for r in E['rows']:
 if r['intake']['program']not in ['ATAX','scalarProd','vectorAdd','cfd']:continue
 if not r['original_modes']:continue
 row=dict(program=r['intake']['program'],digest=r['intake']['input_digest'],expected_commands=r['intake']['expected_commands'],headers=[])
 for mem in r['intake']['asset']['members']:
  if not mem['relative_path'].endswith(('.traceg','.traceg.gz')):continue
  p=P(r['intake']['asset']['trace_directory'])/mem['relative_path'];op=gzip.open if p.name.endswith('.gz')else open
  with op(p,'rt')as h:
   lines=[]
   for n,line in enumerate(h):
    lines.append(line.rstrip())
    if n>=35:break
  row['headers'].append(dict(path=str(p),bytes=p.stat().st_size,text='\n'.join(lines)))
 heads.append(row)
result=dict(source_records=records,trace_headers=heads);(A/'evidence/SOURCE_CONTENT.json').write_text(json.dumps(result,indent=2)+'\n');print('SAVED',len(records),len(heads));print('MISSING',[x['path']for x in records if x.get('missing')]);print('ATAX HEADERS',json.dumps([x for x in heads if x['program']=='ATAX'],indent=2))
print('OTHER COMMANDS',[(x['program'],x['digest'][:16],x['expected_commands'])for x in heads if x['program']!='ATAX'])

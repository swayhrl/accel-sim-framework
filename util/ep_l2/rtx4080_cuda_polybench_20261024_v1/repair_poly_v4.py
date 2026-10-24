from pathlib import Path
import shutil,re,json,hashlib,subprocess,difflib
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');O=R/'adapted_v3/polybench-gpu-1.0';A=R/'adapted_v4/polybench-gpu-1.0';shutil.copytree(O,A);rows=[];patches=[]
base={x['program']:x for x in json.loads((R/'manifests/POLYBENCH_QUEUE_V3.json').read_text())}
for n in ['FDTD-2D','GRAMSCHM']:
 src=list((A/'CUDA'/n).glob('*.cu'))[0];s=src.read_text();old=s
 if n=='FDTD-2D':
  s=s.replace('ex[i*NY + j] =','ex[i*(NY+1) + j] =',1)
  s=s.replace('(DATA_TYPE*)malloc(NX*(NY+1)*sizeof(DATA_TYPE))','(DATA_TYPE*)calloc(NX*(NY+1),sizeof(DATA_TYPE))').replace('(DATA_TYPE*)malloc((NX+1)*NY*sizeof(DATA_TYPE))','(DATA_TYPE*)calloc((NX+1)*NY,sizeof(DATA_TYPE))')
  before,after=s.split('__global__',1);before=before.replace('0.5*','0.5f*').replace('0.7*','0.7f*');s=before+'__global__'+after
  reason='Fix ex initialization stride to NY+1, deterministic zero ghost boundaries; float CPU coefficients match unchanged float GPU equations; -fmad=false matches operation rounding'
 else:
  s=s.replace('A[i*N + j] = ((DATA_TYPE) (i+1)*(j+1)) / (M+1);','A[i*N + j] = (i == j ? 1.0f : ((DATA_TYPE)((i*17 + j*13) % 100)) / 1000000.0f);')
  s=s.replace('printf("i: %d j: %d \\n1: %f\\n 2: %f\\n", i, j, A[i*N + j], A_outputFromGpu[i*N + j]);','if(fail <= 8) printf("i: %d j: %d \\n1: %f\\n 2: %f\\n", i, j, A[i*N + j], A_outputFromGpu[i*N + j]);')
  reason='Original deterministic matrix is rank1; replace with full-rank strictly diagonally dominant deterministic dense matrix, same2048x2048, unchanged classical Gram-Schmidt kernels; log first8 errors only'
 src.write_text(s);patches.extend(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='v3/'+n,tofile='v4/'+n))
 # Extract each global kernel's brace-balanced source to demonstrate no kernel edits.
 def kernels(txt):
  out=[]
  for m in re.finditer(r'__global__\s+',txt):
   a=txt.index('{',m.start());level=1;i=a+1
   while level:level+=(txt[i]=='{')-(txt[i]=='}');i+=1
   out.append(txt[m.start():i])
  return out
 assert kernels(s)==kernels(old)
 q=dict(base[n]);cmd=[x.replace('/adapted_v3/','/adapted_v4/').replace('_checked_v3','_checked_v4') for x in q['build_command']];cmd.insert(1,'--fmad=false');cp=subprocess.run(cmd,capture_output=True,text=True,timeout=120);(R/'build'/(n+'_checked_v4.log')).write_text(cp.stdout+cp.stderr)
 q.update(build_command=cmd,build_exit=cp.returncode,source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),argv=[str(R/'bin'/(n+'_checked_v4'))],variant='deterministic_input_repair_v4_full_default_dimensions',repair_rationale=reason,relation_to_original='Distinct repaired input; original failed baseline retained, not claimed identical',cwd_policy='ABSENT native/capture attempt directory',kernel_source_sha256=hashlib.sha256('\n'.join(kernels(s)).encode()).hexdigest(),kernel_source_unchanged=True)
 if cp.returncode==0:q['binary_sha256']=hashlib.sha256(Path(q['argv'][0]).read_bytes()).hexdigest()
 rows.append(q);print(n,cp.returncode,reason)
(R/'build/POLY_INPUT_REPAIRS_V4.patch').write_text(''.join(patches));(R/'manifests/POLYBENCH_REPAIRED_2_QUEUE_V4.json').write_text(json.dumps(rows,indent=2)+'\n')

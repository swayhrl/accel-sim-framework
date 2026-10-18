"""AC2 CPU-only source-capacity audit. No simulator entrypoint is executed."""
import hashlib,json,os,shlex,subprocess,sys
from pathlib import Path
ROOT=Path('/workspace/dtc-lane-ac2-compact-collect-174-v1/final-cpu')
ROOT.mkdir(parents=True,exist_ok=False)
CORE=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-ac2-compact-collect-core-174-v1')
FRAME=Path(__file__).resolve().parents[5]
PARENT=Path('/workspace/worktrees/gpgpu-sim-dtc-lane-ac2-parent-source-174-v1')
X2=Path('/workspace/worktrees/gpgpu-sim-dtc-lane-ac2-x2-source-174-v1')
BUILDS={key:Path('/workspace/builds/dtc-lane-ac2-'+key+'-174-v1') for key in ['candidate','parent','x2']}
BUILDS['candidate']=Path('/workspace/builds/dtc-lane-ac2-final-release-174-v1')
AC=Path(__file__).resolve().parents[2]/'DTC_LANE_AC_COLLECT_PIPELINE_V1/scripts'
sys.path.insert(0,str(AC))
from run_cpu_matrix import CASES,common,normal
from parse_collect_wb import parse

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def capture(label,argv,lib=None,timeout=120,ok=True):
 env=os.environ.copy();env.pop('LD_PRELOAD',None);env.pop('LD_AUDIT',None)
 if lib: env['LD_LIBRARY_PATH']=str(lib.parent)
 proc=subprocess.run(list(map(str,argv)),cwd=ROOT,env=env,capture_output=True,timeout=timeout)
 out=ROOT/(label+'.stdout');err=ROOT/(label+'.stderr')
 out.write_bytes(proc.stdout);err.write_bytes(proc.stderr)
 rec={'label':label,'argv':list(map(str,argv)),'exit':proc.returncode,'stdout':{'path':str(out),'sha256':sha(out)},'stderr':{'path':str(err),'sha256':sha(err)}}
 if lib:
  rec.update(executable_sha256=sha(argv[0]),library_sha256=sha(lib),library=str(lib),actual_maps=[l for l in proc.stdout.decode().splitlines() if '_LIBRARY_MAP ' in l])
 receipts.append(rec); (ROOT/'EXECUTIONS.json').write_text(json.dumps(receipts,indent=2)+'\n')
 if ok: assert proc.returncode==0,(label,proc.stderr.decode()[-2000:])
 return proc.stdout.decode(),rec

receipts=[]; compilations=[]
def compile_probe(tag,source,baseline=False):
 entry=next(x for x in json.loads((BUILDS['candidate']/'compile_commands.json').read_text()) if x['file'].endswith('dtc_l1_ac2_capacity_probe.cc'))
 flags=shlex.split(entry['command']);flags=flags[:flags.index('-o')]
 src={'parent':PARENT,'x2':X2}[tag]
 flags=[s.replace(str(CORE),str(src)).replace(str(BUILDS['candidate']),str(BUILDS[tag])) for s in flags]
 if baseline: flags+=['-DDTC_COLLECT_WB_PROBE_BASELINE=1']
 if source.name=='dtc_l1_ac2_capacity_probe.cc' and baseline: flags+=['-include',str(CORE/'src/gpgpu-sim/dtc-l1-collect-wb.h')]
 exe=ROOT/(tag+'-'+source.stem)
 argv=flags+[str(source),'-L'+str(BUILDS[tag]),'-Wl,-rpath,'+str(BUILDS[tag]),'-lcudart','-ldl','-pthread','-o',str(exe)]
 _,rec=capture('compile-'+exe.name,argv,timeout=180);compilations.append(rec)
 return exe

for tag in BUILDS:
 capture('ctest-'+tag,['ctest','--test-dir',BUILDS[tag],'--output-on-failure'])
text,rec=capture('negative-compact-option',[BUILDS['candidate']/'dtc_l1_ac2_capacity_probe','compact-option'],BUILDS['candidate']/'libcudart.so',ok=False)
assert rec['exit']==1 and 'Unknown' in (ROOT/'negative-compact-option.stderr').read_text()
capture('parent-source-recovery',[sys.executable,AC/'audit_source_delta.py','--core',PARENT,'--output',ROOT/'PARENT_SOURCE_RECOVERY.json'])
parent_cap=compile_probe('parent',CORE/'tests/dtc_l1_ac2_capacity_probe.cc')
x2_cap=compile_probe('x2',CORE/'tests/dtc_l1_ac2_capacity_probe.cc',True)
x2_ac=compile_probe('x2',CORE/'tests/dtc_l1_collect_wb_pipeline_probe.cc',True)
# Repeat the immutable parent qualification against new independent products.
capture('parent-matrix-fresh',[sys.executable,AC/'run_cpu_matrix.py','--probe',BUILDS['candidate']/'dtc_l1_collect_wb_pipeline_probe','--baseline-probe',x2_ac,'--core',CORE,'--baseline-library',BUILDS['x2']/'libcudart.so','--output',ROOT/'fresh-parent-matrix'],timeout=600)
config=CORE/'configs/tested-cfgs/SM7_GV100/gpgpusim.config'
equivalence=[];capacity=[]
for case,sectors,k1 in CASES:
 args=[config,'1',case,str(sectors),'3','1',str(k1),'1']
 a,ra=capture(f'new-ac-{case}-{sectors}',[BUILDS['candidate']/'dtc_l1_collect_wb_pipeline_probe',*args],BUILDS['candidate']/'libcudart.so')
 b,rb=capture(f'parent-ac-{case}-{sectors}',[BUILDS['parent']/'dtc_l1_collect_wb_pipeline_probe',*args],BUILDS['parent']/'libcudart.so')
 assert common(a)==common(b) and normal(a)==normal(b)
 assert parse(a,sms=1)==parse(b,sms=1)
 equivalence.append({'case':case,'sectors':sectors,'typed_state_sha256':hashlib.sha256(common(a).encode()).hexdigest(),'normal_boundaries':3,'parent_AC_ON_exact':True})
for sectors in [4,8,16,128,129,256,257,512,2560]:
 kind='pool' if sectors==2560 else 'coalesced'
 outputs={}
 for tag,exe,flag in [('candidate',BUILDS['candidate']/'dtc_l1_ac2_capacity_probe','0'),('candidate',BUILDS['candidate']/'dtc_l1_ac2_capacity_probe','1'),('parent',parent_cap,'0'),('parent',parent_cap,'1'),('x2',x2_cap,'omitted')]:
  text,rec=capture(f'capacity-{sectors}-{tag}-{flag}',[exe,config,flag,str(sectors),kind,'1'],BUILDS[tag]/'libcudart.so')
  assert rec['actual_maps'] and f'AC2_LIBRARY {BUILDS[tag]}/libcudart.so' in text
  assert f'AC2_ELF {exe}' in text and 'PASS_PARENT_CAPACITY_WITNESS_ONLY' in text
  parse(text,enabled=(flag=='1'),sms=1)
  outputs[(tag,flag)]=text
  capacity.append({'sectors':sectors,'tag':tag,'pipeline':flag,'scope':'PRODUCTION_COALESCER_API' if kind=='coalesced' else 'MANUAL_FULL_POOL_STRUCTURAL','receipt':rec['label']})
 for flag in ['0','1']:
  assert common(outputs[('candidate',flag)])==common(outputs[('parent',flag)])
  assert normal(outputs[('candidate',flag)])==normal(outputs[('parent',flag)])
 assert common(outputs[('candidate','0')])==common(outputs[('x2','omitted')])
 assert normal(outputs[('candidate','0')])==normal(outputs[('x2','omitted')])
result={'status':'PASS_CPU_PARENT_REGRESSION_AND_CAPACITY_WITNESS_ONLY_COMPACT_SCIENTIFIC_STOP','AC_ON_equivalence':equivalence,'capacity_cases':capacity,'executions':len(receipts),'compact_implemented':False,'full_simulator_canary_native_GPU_starts':0,'value_correctness':'UNPROVEN'}
(ROOT/'QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'capacity_processes':len(capacity),'AC_ON_cases':len(equivalence),'executions':len(receipts)}))

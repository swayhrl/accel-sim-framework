#!/usr/bin/env python3
import pathlib,json,re,shlex,hashlib,subprocess
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');P=R/'assets/parboil_source_verified';queue=[];gaps=[]
for program in sorted((P/'datasets').iterdir()):
 if not program.is_dir():continue
 for d in sorted(program.iterdir()):
  if not d.is_dir():continue
  name=program.name;inp=d/'input';gold=d/'output'
  files=sorted(p.name for p in inp.iterdir() if p.is_file() and p.name!='DESCRIPTION' and not p.name.startswith('.')) if inp.exists() else []
  desc=(inp/'DESCRIPTION').read_text() if (inp/'DESCRIPTION').exists() else ''
  match=re.search(r'^Inputs:\s*(.*)$',desc,re.M)
  if match:files=shlex.split(match.group(1))
  elif len(files)>1:
   gaps.append({'program':name,'dataset':d.name,'status':'AMBIGUOUS_DEFAULT_INPUT_ORDER','files':files});continue
  pm=re.search(r'^Parameters:\s*(.*)$',desc,re.M);params=shlex.split(pm.group(1)) if pm else []
  outs=sorted(p for p in gold.iterdir() if p.is_file() and p.name!='DESCRIPTION' and not p.name.startswith('.')) if gold.exists() else []
  expected=outs[0] if len(outs)==1 else None
  inputmeta=[];missing=[]
  for n in files:
   p=inp/n
   if not p.exists():missing.append(str(p));continue
   inputmeta.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  binary=R/'bin'/('parboil_'+name)
  argv=[str(binary)]
  if files:argv+=['-i',','.join(str(inp/f) for f in files)]
  argv+=['-o','actual.out']+params
  checker=P/'benchmarks'/name/'tools/compare-output'
  check=['bash',str(checker),str(expected),'{attempt}/actual.out'] if name=='histo' else [str(R/'toolchains/pypy2.7-v7.3.20-linux64/bin/pypy'),str(checker),str(expected),'{attempt}/actual.out']
  q={'suite':'Parboil','version':'4e0fc548','program':name,'variant':d.name+'_complete_official_input','source_head':'4e0fc54866546efa44fe93af57c9cef62f6c8eb9','argv':argv,'cwd':str(P/'benchmarks'/name),'cwd_policy':'ABSENT attempt; all input paths absolute','binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'input_identity':inputmeta,'parameters':params,'input_description':desc,'golden_output':{'path':str(expected),'bytes':expected.stat().st_size,'sha256':hashlib.sha256(expected.read_bytes()).hexdigest()} if expected else None,'native_timeout_sec':1200,'capture_timeout_sec':21600,'capture_max_bytes':80*1024**3,'correctness':{'exit':0,'postcheck_command':check,'postcheck_timeout_sec':180,'postcheck_stdout_regex':'Pass','source_predicate':'unmodified Parboil source checker; NaN rejection not inferred beyond checker domain'},'env':{'PYTHONPATH':str(P/'common/python'),'LD_LIBRARY_PATH':str(R/'toolchains/cuda11.8/lib')},'actual_cubin_arch':89,'embedded_PTX':'not yet frozen','capture_gpu_uuid':None,'producer_contract':'AWAIT_SEMANTIC_FREEZE','simulator_qualification':'NOT_GRANTED','missing_input_files':missing,'readiness':'READY_NATIVE' if not missing and expected else 'INPUT_OR_GOLDEN_GAP'}
  queue.append(q)
(R/'control/PARBOIL_EXACT_INPUT_QUEUE_V1.json').write_text(json.dumps(queue,indent=2)+'\n');(R/'control/PARBOIL_INPUT_METADATA_GAPS.json').write_text(json.dumps(gaps,indent=2)+'\n')
print('queue',len(queue),'ready',sum(q['readiness']=='READY_NATIVE' for q in queue),'gaps',gaps)
print([(q['program'],q['variant'],q['readiness']) for q in queue])


"""CPU-only review: read real saved c8 captures and rerun all prepared negative fixtures."""
import pathlib,importlib.util,json,subprocess,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('--root',default='/data/c16/ada_trace_extensions_v8_20261024_v1');a=p.parse_args();R=pathlib.Path(a.root)
validator=R/'qualify_input_capsule_v4.py'
assert hashlib.sha256(validator.read_bytes()).hexdigest()=='7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388'
s=importlib.util.spec_from_file_location('q',validator);q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
positive=[]
for mode in ['sync','async','random','constant65','vector4m']:
 for kind in ['native_observer','instrumented']:
  A=R/'attempts'/('snapshot7_'+mode+'_'+kind+'_v3_attempt1');result=q.qualify(A)
  assert result['tool_sha256']=='c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352'
  positive.append(dict(attempt=A.name,bytes=result['total_bytes'],launches=result['lifecycle']['recognized_launch_count']))
corpus=R/'cpu_negative/input_capsule_v4r2_guard';expected=json.loads((R/'CAPSULE_VALIDATOR_V4R2_NEGATIVE_QUALIFICATION.json').read_text())
assert {x.name for x in corpus.iterdir()if x.is_dir()}=={x['case']for x in expected['negative']}
negative=[]
for case in expected['negative']:
 A=corpus/case['case'];cp=subprocess.run(['python3','-B',str(validator),str(A)],capture_output=True,text=True)
 assert cp.returncode!=0 and not(A/'INPUT_CAPSULE_QUALIFICATION_V4R2.json').exists(),A
 negative.append(dict(case=A.name,reason=cp.stderr.splitlines()[-1]))
print(json.dumps(dict(CPU_only=True,GPU_launched=False,positive=positive,negative=negative),indent=2))

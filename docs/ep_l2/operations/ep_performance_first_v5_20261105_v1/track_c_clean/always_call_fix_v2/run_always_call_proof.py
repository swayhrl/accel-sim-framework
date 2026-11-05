from pathlib import Path
import subprocess,json,hashlib
r=Path(__file__).parent;plan=json.loads((r/'INCREMENTAL_BUILD_PLAN.json').read_text());out=Path(plan['new_build'])/'always_call_cpu';out.mkdir(exist_ok=True)
assert (r/'INCREMENTAL_BUILD_RESULT.json').exists()
rows=[]
for label,source,flag,expected in [('new_NDEBUG','always_call_extracted_new.cc','-DNDEBUG',0),('new_assertions','always_call_extracted_new.cc','-UNDEBUG',0),('old_NDEBUG_negative','always_call_extracted_old_negative.cc','-DNDEBUG',99)]:
 exe=out/label;cmd=['/usr/bin/c++','-O0','-g0','-std=c++17',flag,str(r/source),'-o',str(exe)]
 c=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert c.returncode==0,c.stderr
 q=subprocess.run([str(exe)],cwd=str(out),capture_output=True,text=True,timeout=10);assert q.returncode==expected,(label,q.returncode,q.stderr)
 pp=subprocess.run(['/usr/bin/c++','-E','-P','-std=c++17',flag,str(r/source)],capture_output=True,text=True,timeout=10);assert pp.returncode==0
 calls=pp.stdout.count('->set_done(');assert calls==(0 if label=='old_NDEBUG_negative' else 2),(label,calls)
 rows.append({'label':label,'argv':cmd,'compile_rc':c.returncode,'run_rc':q.returncode,'expected_rc':expected,'runtime_stdout':q.stdout,'required_calls_after_preprocess':calls,'actual_fragment_source':str(r/source),'fragment_sha256':hashlib.sha256((r/source).read_bytes()).hexdigest(),'scope':'only these exact2 production callsite statements, not whole-Core NDEBUG qualification'})
result={'status':'PASS_ALWAYS_CALL_NEW_DELTA_WITH_OLD_NDEBUG_COUNTEREXAMPLE','rows':rows,'old12_3185_parser_rerun':False,'new_complete_application_starts':0}
(r/'ALWAYS_CALL_CPU_PROOF.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

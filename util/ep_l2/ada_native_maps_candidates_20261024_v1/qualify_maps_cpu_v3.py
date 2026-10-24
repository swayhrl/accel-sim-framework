from pathlib import Path
import subprocess,json,os,signal,time,hashlib,importlib.util
r=Path(__file__).parent;t=r/'maps_cpu_qualification_A3';t.mkdir()
fixture=r/'maps_cpu_qualification_A1/fixture'
sp=importlib.util.spec_from_file_location('maps',r/'native_maps_observer_v2.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins={str(x.resolve()):sha(x) for x in [fixture,Path('/lib/x86_64-linux-gnu/libc.so.6'),Path('/lib/x86_64-linux-gnu/libm.so.6'),Path('/lib64/ld-linux-x86-64.so.2'),Path('/etc/ld.so.cache')]}
results={}
def run(name,pins,wrongpid=False,omitlast=False):
 out=t/name;out.mkdir();p=subprocess.Popen([str(fixture)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 observer=m.MapsObserver(p.pid,pins,out/'maps')
 try:
  if wrongpid:observer.primary_identity['start_ticks']+=1
  deadline=time.monotonic()+5;stops=0
  while p.poll() is None:
   if time.monotonic()>deadline:raise RuntimeError('CPU fixture timeout')
   st=m.stat(p.pid)
   if st['state']=='T':
    label=['FIRST_ISSUE','TERMINAL'][stops];stops+=1
    if not(omitlast and label=='TERMINAL'):observer.sample(label)
    os.kill(p.pid,signal.SIGCONT)
   else:observer.sample()
   time.sleep(.01)
  assert p.wait()==0
  proof=observer.require_terminal()
  results[name]={'status':'PASS','proof':proof}
 except Exception as e:results[name]={'status':'REJECTED','reason':str(e)}
 finally:
  if p.poll()is None:p.kill();p.wait()
run('positive_new_late_mapping',pins)
bad=dict(pins);bad.pop(str(Path('/lib/x86_64-linux-gnu/libm.so.6').resolve()));run('negative_new_unpinned_mapping',bad)
bad=dict(pins);bad[str(Path('/lib/x86_64-linux-gnu/libm.so.6').resolve())]='0'*64;run('negative_late_hash_drift',bad)
run('negative_pid_identity',pins,True)
run('negative_missing_terminal',pins,False,True)
saved_digest=m.digest
def vanished_mapping(path):
 if str(path).endswith('/libm.so.6'):raise FileNotFoundError('CPU directed observed-path hash race')
 return saved_digest(path)
m.digest=vanished_mapping
run('negative_observed_path_unreadable',pins)
m.digest=saved_digest

assert results['positive_new_late_mapping']['status']=='PASS',results
expected={'negative_new_unpinned_mapping':'unfrozen mapped dependency /usr/lib/x86_64-linux-gnu/libm.so.6','negative_late_hash_drift':'mapped dependency hash drift /usr/lib/x86_64-linux-gnu/libm.so.6','negative_pid_identity':'primary PID reused','negative_missing_terminal':'missing/reordered explicit issue/terminal maps'}
expected['negative_observed_path_unreadable']='observed mapped dependency unreadable /usr/lib/x86_64-linux-gnu/libm.so.6'
for k,reason in expected.items():assert results[k]['status']=='REJECTED' and reason in results[k]['reason'],results
proof={'CPU_ONLY_NOT_SIMULATOR_APPLICATION':True,'observer_sha256':sha(r/'native_maps_observer_v2.py'),'results':results,'all_expected_reasons':True}
(t/'QUALIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

import pathlib,subprocess,os,json,time,hashlib
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1')
assert not (T/'control/CONTROLLER_LAUNCH.json').exists()
q=json.loads((T/'control/QUALIFICATION.json').read_text())
for name,h in q['tool_sha256'].items():assert hashlib.sha256((T/'tools'/name).read_bytes()).hexdigest()==h
with (T/'control/CONTROLLER.log').open('xb') as log:
 p=subprocess.Popen(['/usr/bin/python3','-B',str(T/'tools/short3_controller.py')],cwd=T,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 time.sleep(.2)
 tick=int(pathlib.Path('/proc',str(p.pid),'stat').read_text().rsplit(')',1)[1].split()[19])
 proof={'pid':p.pid,'start_ticks':tick,'controller_sha256':hashlib.sha256((T/'tools/short3_controller.py').read_bytes()).hexdigest(),'max_starts':12,'request':'DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1','scope':'One original finite controller, no restart'}
 with (T/'control/CONTROLLER_LAUNCH.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof))

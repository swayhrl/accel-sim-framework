"""Finite foreground composition of the existing six helpers; no second flow."""
import sys,subprocess,json,datetime
import tls_target as t
first,last=map(int,sys.argv[1:]);assert 11<=first<=last<=33

def run(wid,stage,name,*args):
 p=t.META/(wid+'_'+stage+'_FOREGROUND.log')
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(),wid,stage,'START',flush=True)
 with p.open('wb') as out:
  r=subprocess.run([sys.executable,str(t.META/name),*args],cwd=t.REPO,stdout=out,stderr=subprocess.STDOUT)
 if r.returncode:
  print(p.read_text(encoding='utf-8',errors='replace')[-4500:],flush=True)
  raise RuntimeError(wid+' '+stage+' FAILED: preserve all state, resume only this exact phase; no whole-cycle repeat')
 print(wid,stage,'PASS',flush=True)

for number in range(first,last+1):
 wid='TLS_V10_P9_PUBLIC_B%04d'%number
 t.require_tls_restore_location(wid)
 run(wid,'WAIT_READY','wait_source_control_once.py',wid,'SOURCE_READY_COPY16.json','600')
 ready=json.loads((t.META/'last_source_control_wait.json').read_bytes())
 if ready['status']!='SOURCE_CONTROL_FOUND':print(json.dumps(ready),flush=True);break
 commit=ready['commit']
 run(wid,'FETCH_CONTROLS','fetch_exact_window_controls.py',wid,commit)
 run(wid,'RECEIVE','receive_exact_window.py',wid,commit,'source_'+commit[:7])
 run(wid,'PUBLISH_PROOFS','publish_received_window.py',wid)
 d=t.get(wid+'_DEST_VERIFIED.json');print(wid,'REAL164_AND_NATIVE_RANGES',d['range_count'],d['raw_bytes'],'SOURCE_KEEP',flush=True)
 run(wid,'WAIT_ACK','wait_source_control_once.py',wid,'SOURCE_KEEP_ACK.json','600')
 ack=json.loads((t.META/'last_source_control_wait.json').read_bytes())
 if ack['status']!='SOURCE_CONTROL_FOUND':print(json.dumps(ack),flush=True);break
 run(wid,'EXACT_CLOSE_ROLL','close_and_roll.py',wid,ack['commit'],ack['cached_prefix'])
 print(wid,'CLOSED',t.git('rev-parse','HEAD').decode().strip(),flush=True)
else:print('P9_ALL_REQUESTED_WINDOWS_CLOSED; FULL141_FROM164_NATIVE_RESTORE_AND_CERTIFICATE_NEXT',flush=True)

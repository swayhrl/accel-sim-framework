"""Report-only single analysis daemon. Root starts it after review; no models/Git/native writers."""
from pathlib import Path
import os,fcntl,time,json,hashlib,importlib.util,sys,datetime,argparse
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D/'produce_snapshot.py';EXPECTED='15e0c910db46a56bd65d7dd424a7b94a3a10f799de94593648a5685eca60566f'
def atomic(p,v):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--interval',type=int,default=120);a=ap.parse_args();assert a.interval>=30
 assert hashlib.sha256(P.read_bytes()).hexdigest()==EXPECTED
 with(D/'SERVICE.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);sp=importlib.util.spec_from_file_location('pinned_report_only_snapshot',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);st=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split();atomic(D/'PID.json',{'pid':os.getpid(),'start_ticks':int(st[19]),'mode':'READONLY_REPORT_ONLY_NOT_MODEL_DISPATCHER','interval_seconds':a.interval,'full_archive_audit_seconds':1800,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
  while True:
   try:
    out=m.run_once()
    if out.get('all_registered48_terminal_verified')is True:
     atomic(D/'SERVICE_COMPLETED.json',{'utc':m.now(),'provider':str(D/'PUBLICATION_PROVIDER.json'),'all_registered48_terminal_verified':True,'new_model_starts':0});return
   except Exception as e:
    hold={'status':'READONLY_CONSUMER_ENGINEERING_HOLD','utc':m.now(),'source_qualified':False,'error':repr(e),'model_retries':0,'new_model_starts':0};atomic(D/'HEALTH.json',hold)
    if(D/'PUBLICATION_PROVIDER.json').exists():
     provider=json.loads((D/'PUBLICATION_PROVIDER.json').read_bytes());provider.update(source_qualified=False,source_qualification_hold=hold,all_registered48_terminal_verified=False,historical_snapshot_retained=True);atomic(D/'PUBLICATION_PROVIDER.json',provider)
   time.sleep(a.interval)
if __name__=='__main__':main()

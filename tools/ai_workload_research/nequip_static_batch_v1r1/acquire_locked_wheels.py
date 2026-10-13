"""Fetch only exact official frozen wheel artifacts; hashes checked before installation."""
import os,pathlib,json,subprocess,hashlib,urllib.parse,sys,re,traceback
root=pathlib.Path(os.environ['TASK_DATA']);old=pathlib.Path(os.environ['OLD_TASK_DATA']);raw=root/'raw';state=json.loads((raw/'FROZEN_WHEEL_AVAILABILITY.json').read_text());assert state['status']=='PASS_ALL82_WHEEL_ARTIFACTS_AVAILABLE';records=[]
def save(status,error=None):(raw/'LOCKED_WHEEL_DOWNLOADS.json').write_text(json.dumps({'status':status,'error':error,'resolver_invoked':False,'records':records},indent=2)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
try:
 for r in state['packages']:
  dest=root/'wheelhouse'/r['filename']
  if dest.exists():assert sha(dest)==r['sha256'];records.append({**r,'local_path':str(dest),'acquisition':'ALREADY_VALIDATED_LOCAL_ANTLR_WHEEL'});continue
  # Reuse old same-artifact wheels without modifying the previous STOP data/cache.
  cached=old/'wheels'/r['filename']
  if cached.exists() and sha(cached)==r['sha256']:
   import shutil
   shutil.copy2(cached,dest);records.append({**r,'local_path':str(dest),'acquisition':'READ_ONLY_V1_CACHE_REUSE'});save('RUNNING');continue
  assert urllib.parse.urlparse(r['url']).hostname in ['files.pythonhosted.org','download.pytorch.org','download-r2.pytorch.org']
  # Known-size budget gate plus monitored whole-interface cumulative accounting.
  ledger=json.loads((raw/'NETWORK_LEDGER.json').read_text())['new_accounted_bytes'];remaining=5256821765-ledger
  cap=r['bytes'] if r.get('bytes') else min(remaining-64*2**20,1536*2**20)
  assert cap>0 and cap<remaining-32*2**20,'REMAINING_DOWNLOAD_BUDGET_INSUFFICIENT'
  cmd=['curl','--fail','--location','--connect-timeout','15','--max-time','900','--max-filesize',str(cap),'--output',str(dest),r['url']]
  with (raw/'WHEEL_DOWNLOAD_TRANSFER.log').open('a') as log:
   log.write('\nDISTRIBUTION '+r['distribution']+' '+r['version']+'\n');log.flush();result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
  assert result.returncode==0,'OFFICIAL_WHEEL_DOWNLOAD_FAILED '+r['distribution'];assert sha(dest)==r['sha256'],'FROZEN_ARTIFACT_SHA256_MISMATCH '+r['distribution']
  if r.get('bytes') is not None:assert dest.stat().st_size==r['bytes']
  records.append({**r,'actual_bytes':dest.stat().st_size,'local_path':str(dest),'acquisition':'OFFICIAL_EXACT_FROZEN_ARTIFACT'});save('RUNNING');print('VERIFIED',r['distribution'],r['version'],dest.stat().st_size,flush=True)
 # Extra install lock: only ANTLR's artifact digest changes; all82 versions retained.
 (root/'V1R1_INSTALL_ARTIFACT_LOCK.txt').write_text(''.join(r['distribution']+'=='+r['version']+' --hash=sha256:'+r['sha256']+'\n' for r in state['packages']),encoding='utf-8')
 save('PASS_ALL82_ARTIFACT_BYTES_VERIFIED')
except Exception as e:save('STOP',str(e));print(traceback.format_exc(),flush=True);sys.exit(1)

#!/usr/bin/env python3
"""Finite exact native-only entry under original E engineering test lease.
Captures real wait/identity/log/old semantics; no scientific parser/acceptance,
controller, lease acquisition, native rerun, simulator application, or rebuild.
"""
import argparse,datetime,hashlib,json,os,selectors,subprocess,sys,time
from pathlib import Path

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(path,v):
 t=path.with_name(path.name+'.tmp')
 with t.open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,path);fd=os.open(str(path.parent),os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def summary(raw):
 lines=raw.decode('utf-8').splitlines();frames=[];old=[];model=[]
 for line in lines:
  if line.startswith('EPL2DETACH_DIAG_V1|'):frames.append(json.loads(line.split('|',1)[1]))
  if line.startswith(('EPL2ROV1|','EPL2ROC1|')):old.append(line)
  if line.startswith('EPL2MS_TEST|SEMANTIC|'):model.append(line)
 return {'semantic':model,'old_RO_lines':old,'old_212_frames':frames,'semantic_sha256':canonical(model),'old_RO_sha256':canonical(old),'old_212_sha256':canonical(frames),'r5_records':sum(x.startswith('EPL2TAGPRESSUREV1|') for x in lines)}
def process_stat(pid):
 try:
  text=Path('/proc/'+str(pid)+'/stat').read_text().strip();fields=text[text.rfind(')')+2:].split();return {'pid':pid,'start_ticks':int(fields[19]),'stat':text}
 except FileNotFoundError:return {'pid':pid,'start_ticks':None,'stat':None}
def main():
 a=argparse.ArgumentParser();a.add_argument('--plan',required=True);a.add_argument('--expected-plan-sha256',required=True);a.add_argument('--out',required=True);args=a.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=False);results=[];code=3;status='NATIVE_PRECHECK_NOT_COMPLETE';total=0;boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 try:
  if sha(args.plan)!=args.expected_plan_sha256:raise ValueError('exact native plan mismatch')
  plan=json.loads(Path(args.plan).read_text());assert plan['planned_finite_native_invocations']==len(plan['commands'])==15
  cap=plan['aggregate_native_output_hard_cap_bytes'];assert cap==33554432
  bref=plan['build_artifacts_ref'];assert sha(bref['path'])==bref['sha256'];build=json.loads(Path(bref['path']).read_text());assert build['source_identity']['core_source_commit']==plan['new_core']
  binaries={}
  for name in ('native','metadata'):
   row=build['artifacts'][name];assert sha(row['path'])==row['sha256'];binaries[row['path']]=row['sha256']
  for path,ref in plan['asset_refs'].items():assert Path(path).stat().st_size==ref['bytes'] and sha(path)==ref['sha256'],path
  oldref={}
  for case,ref in plan['old_r4_references'].items():
   assert sha(ref['receipt_path'])==ref['receipt_sha256'];r=json.loads(Path(ref['receipt_path']).read_text());assert r['actual_exit']==0 and r['raw_log']==ref['raw_path'] and r['binary_sha256']==ref['old_binary_sha256']
   assert Path(ref['raw_path']).stat().st_size==ref['raw_bytes'] and ref['raw_bytes']<=16*2**20 and sha(ref['raw_path'])==ref['raw_sha256'];oldref[case]=summary(Path(ref['raw_path']).read_bytes());assert len(oldref[case]['semantic'])==1
  save(out/'ENTRY_BEGIN.json',{'schema':'E2_R5_EXACT_FINITE_NATIVE_ENTRY_V1','plan_path':args.plan,'plan_sha256':args.expected_plan_sha256,'source_identity':build['source_identity'],'actual_binaries':binaries,'pid':os.getpid(),'process':process_stat(os.getpid()),'boot_id':boot,'started_utc':stamp(),'no_full_application':True})
  for row in plan['commands']:
   cid=row['id'];directory=out/cid;directory.mkdir();rawpath=directory/'native.log';argv=row['argv'];assert argv[0] in binaries
   env=os.environ.copy();env.update(row['env_overrides']);start=stamp();clock=time.monotonic();print('R5_NATIVE_BEGIN '+cid,flush=True)
   with rawpath.open('xb') as sink:
    child=subprocess.Popen(argv,cwd=directory,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);identity=process_stat(child.pid)
    save(directory/'START.json',{'case':cid,'argv':argv,'env_overrides':row['env_overrides'],'pid_identity':identity,'boot_id':boot,'binary_sha256':binaries[argv[0]],'started_utc':start,'timeout_seconds':row['timeout_seconds']})
    sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ);timed=False;overflow=False;omitted=[]
    while sel.get_map():
     if time.monotonic()-clock>row['timeout_seconds'] and child.poll() is None:timed=True;child.terminate()
     if timed and time.monotonic()-clock>row['timeout_seconds']+2 and child.poll() is None:child.kill()
     for key,events in sel.select(0.2):
      data=os.read(key.fileobj.fileno(),65536)
      if not data:sel.unregister(key.fileobj);continue
      if len(data)>cap-total:
       overflow=True;omitted.append({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
       if child.poll() is None:child.kill()
      elif not overflow:sink.write(data);total+=len(data)
      else:omitted.append({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    actual=child.wait();sel.close();child.stdout.close()
   text=rawpath.read_bytes();receipt={'id':cid,'case':row['case'],'variant':row['variant'],'argv':argv,'environment_overrides':row['env_overrides'],'binary_sha256':binaries[argv[0]],'native_pid_identity':identity,'boot_id':boot,'started_utc':start,'finished_utc':stamp(),'wall_seconds':time.monotonic()-clock,'actual_native_wait_exit':actual,'timeout':timed,'output_limit_exceeded':overflow,'output_omitted_chunks_if_failed':omitted,'raw_path':str(rawpath),'raw_sha256':sha(rawpath),'raw_bytes':len(text),'aggregate_native_raw_bytes':total,'scope':row.get('scope','FINITE_NATIVE_ONLY_NOT_FULL_APPLICATION')}
   # Persist true exit BEFORE any terminal/parser expectation can fail.
   save(directory/'NATIVE_EXIT.json',receipt);results.append(receipt);save(out/'PROGRESS.json',{'tests':results,'actual_native_invocations':len(results),'raw_bytes':total,'app_starts':0})
   if actual!=0 or timed or overflow:raise ValueError('actual native execution failed: '+cid)
   lines=text.decode('utf-8').splitlines();required=row['required_terminal'];assert sum(required in x for x in lines)==1,('terminal',cid)
   if row.get('extra_required_terminal'):assert lines.count(row['extra_required_terminal'])==1
   if row['variant']=='SYNTHETIC_METADATA':
    assert 'SYNTHETIC_FIXTURE=1' in text.decode();proof={'scope':'SYNTHETIC_METADATA_ONLY','actual_exit0':True}
   else:
    proof=summary(text);assert len(proof['semantic'])==1,(cid,'one actual semantic signature')
    if row['case'] in oldref:
     reference=oldref[row['case']];assert proof['semantic']==reference['semantic'],(cid,'actual model semantic differs from sealed saved r4');assert proof['old_RO_lines']==reference['old_RO_lines'],(cid,'actual old RO counters differ')
     if row['variant']!='ALL_OFF':
      current=proof['old_212_frames'];prior=reference['old_212_frames'];assert len(current)==len(prior),(cid,'212 frame count')
      actual_population_changes=[]
      for index,(new,old) in enumerate(zip(current,prior)):
       expected=json.loads(json.dumps(old))
       if old['record']=='GLOBAL':
        assert old['slice']==2 and old['epoch_closed'] is False and new['slice']==1 and new['epoch_closed'] is True,(cid,'only source-proved actual fixture population2->1 and closurefalse->true')
        expected['slice']=1;expected['epoch_closed']=True;actual_population_changes.append({'frame_index':index,'old_registered':2,'new_registered':1,'old_closed':False,'new_closed':True})
       assert new==expected,(cid,'212 values/metadata beyond exact native membership difference')
      proof['documented_actual_native_population_changes']=actual_population_changes
    if row['variant']=='ALL_OFF':assert not proof['old_212_frames'] and proof['r5_records']==0
    if row['variant']=='R4_ONLY':assert proof['old_212_frames'] and proof['r5_records']==0
    if row['variant']=='R5_ON':assert proof['old_212_frames'] and proof['r5_records']>0
   save(directory/'SEMANTIC_AND_COUNTER_EVIDENCE.json',proof);receipt['terminal_and_semantic_expectations']='PASS';save(directory/'NATIVE_EXIT.json',receipt);print('R5_NATIVE_END '+cid+' native_wait='+str(actual),flush=True)
  status='REAL15_CORRECTED_NATIVE_WAIT_TERMINAL_SEMANTIC_PASS_PENDING_INDEPENDENT_R5_DECODER';code=0;return 0
 except Exception as e:
  save(out/'FAILURE.json',{'type':type(e).__name__,'message':str(e),'time':stamp(),'actual_native_invocations':len(results),'no_retry':True});print('R5_NATIVE_FAILURE '+type(e).__name__+': '+str(e),flush=True);return code
 finally:save(out/'RECEIPT.json',{'schema':'E2_R5_ACTUAL_FINITE_NATIVE_RECEIPT_V1','status':status,'exit_code':code,'actual_native_invocations':len(results),'tests':results,'native_raw_bytes':total,'finished_utc':stamp(),'full_application_starts':0,'independent_r5_parser_pass_claimed':False,'formal_producer_or_application_qualification':False})
if __name__=='__main__':sys.exit(main())

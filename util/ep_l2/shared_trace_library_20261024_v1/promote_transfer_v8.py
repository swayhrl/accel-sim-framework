"""Promote only after the running V7 batch closes; touch only our controllers."""
from pathlib import Path
import os,sys,json,time,signal,subprocess,hashlib,traceback,fcntl
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
lease=(R/'control/V8_PROMOTER.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
def ident(pid):
 p=Path('/proc')/str(pid)
 try:
  st=(p/'stat').read_text().rsplit(')',1)[1].split()
  return {'pid':int(pid),'start_ticks':int(st[19]),'state':st[0],'ppid':int(st[1]),'argv':[(x.decode()) for x in (p/'cmdline').read_bytes().split(b'\0') if x]}
 except FileNotFoundError:return None
def alive(row):
 x=ident(row['pid']);return x and x['start_ticks']==row['start_ticks'] and x['state']!='Z'
def await_dead(row):
 for _ in range(100):
  if not alive(row):return
  time.sleep(.1)
 raise RuntimeError('OWN_CONTROLLER_FAILED_TO_EXIT')
candidate=json.loads((R/'control/ENGINE_V8_CANDIDATE.json').read_text());sha=hashlib.sha256(e.SELF_BYTES).hexdigest();assert candidate['engine_sha256']==sha
for name in ['IO_V8_QUALIFICATION.json','PIPELINE_V8_QUALIFICATION.json','ARCHIVE_SENDER_QUALIFICATION_ISOLATED_V8.json']:
 q=json.loads((R/'control'/name).read_text());assert q['status']=='PASS' and q['engine_sha256']==sha
q=json.loads((R/'control/PROTOCOL_QUALIFICATION_ISOLATED_V8.json').read_text());assert q['status']=='PASS'
for report in q['reports']:
 if report.get('receipt',{}).get('bundle'):assert hashlib.sha256((Path(report['receipt']['bundle'])/'trace_copy.py').read_bytes()).hexdigest()==sha
assert not (R/'control/ENGINE_V8_PROMOTION.json').exists()
supervisor=json.loads((R/'control/SUPERVISOR_PID.json').read_text());assert alive(supervisor)
parents=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 x=ident(p.name)
 if x and str(R/'tools/transfer_batches.py') in x['argv']:parents.append(x)
assert len(parents)==1;parent=parents[0];assert parent['ppid']==supervisor['pid'] and parent['state']!='T'
old_driver=(R/'tools/transfer_batches.py').read_bytes();assert old_driver==(R/'tools/transfer_batches_v7.py').read_bytes()
parent_ended=False;promoted=False
try:
 os.kill(parent['pid'],signal.SIGSTOP)
 for _ in range(100):
  x=ident(parent['pid']);assert x and x['start_ticks']==parent['start_ticks']
  if x['state']=='T':break
  time.sleep(.01)
 assert ident(parent['pid'])['state']=='T'
 state=json.loads((R/'control/TRANSFER_PROGRESS.json').read_text());b=state['batch'];m=json.loads(Path(b['manifest']).read_text());bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1))
 intent={'parent':parent,'supervisor':supervisor,'current_transfer':state,'engine_sha256':sha,'old_controller_paused_only_receiver_continues_unchanged':True,'finite_wait_deadline_unix':time.time()+7200}
 (R/'control/TRANSFER_V8_BOUNDARY_INTENT.json').write_text(json.dumps(intent,indent=2)+'\n')
 deadline=time.monotonic()+7200
 while True:
  active=[]
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   x=ident(p.name)
   if x and str(R/'tools/library_copy_v7.py') in x['argv'] and str(Path(b['manifest'])) in x['argv'] and x['state']!='Z':active.append(x)
  if not active and (bundle/'COMMIT.json').exists():break
  assert time.monotonic()<deadline,'OLD_BATCH_NOT_CLOSED_WITHIN_FINITE_WAIT'
  time.sleep(5)
 e.verify_committed(bundle);assert alive(parent) and ident(parent['pid'])['state']=='T'
 os.kill(parent['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGCONT);await_dead(parent);parent_ended=True
 if alive(supervisor):os.kill(supervisor['pid'],signal.SIGTERM);await_dead(supervisor)
 p=R/'synthetic/kernelslist.g';row=e.identity(p);row.update(relative_path='kernelslist.g',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),header_prefix_hex=p.read_bytes().hex())
 fixture={'payload_kind':'CAS_FILES_V1','source_backend':'native','freeze_status':'FROZEN_SYNTHETIC_QUALIFICATION','primary_asset_id':'NATIVE_BACKEND_PROTOCOL_V8','object_id':hashlib.sha256(e.canon(row)).hexdigest(),'source_root':str(p.parent),'source_root_identity':e.identity(p.parent),'members':[row],'source_data_bytes':row['size'],'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/inbox/qualification/NATIVE_BACKEND_PROTOCOL_V8','reuse':False}
 native=e.migrate(fixture);e.verify_committed(Path(native['bundle']),rehash=True)
 proof={'status':'PASS_PROMOTED_AT_CLOSED_BATCH_BOUNDARY',**{k:v for k,v in candidate.items() if k!='status'},'old_batch':b,'old_batch_commit_sha256':hashlib.sha256((bundle/'COMMIT.json').read_bytes()).hexdigest(),'native_backend_qualification':native,'parent_terminated_only_after_receiver_source_exit_and_commit':True,'observed_unix':time.time()}
 (R/'control/ENGINE_V8_PROMOTION.json').write_text(json.dumps(proof,indent=2)+'\n')
 temp=R/'tools/transfer_batches.writing';temp.write_bytes((R/'tools/transfer_batches_v8.py').read_bytes());os.replace(temp,R/'tools/transfer_batches.py');promoted=True
 p=subprocess.Popen(['python3','-B',str(R/'tools/run_goal.py')],stdin=subprocess.DEVNULL,stdout=(R/'logs/supervisor_v8.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'status':proof['status'],'new_supervisor_pid':p.pid,'engine_sha256':sha}),flush=True)
except BaseException:
 (R/'control/ENGINE_V8_PROMOTION_FAILURE.txt').write_text(traceback.format_exc())
 if not parent_ended and alive(parent) and ident(parent['pid'])['state']=='T':os.kill(parent['pid'],signal.SIGCONT)
 elif parent_ended and not promoted:
  assert (R/'tools/transfer_batches.py').read_bytes()==old_driver
  if not alive(supervisor):
   subprocess.Popen(['python3','-B',str(R/'tools/run_goal.py')],stdin=subprocess.DEVNULL,stdout=(R/'logs/supervisor_v8_fallback_v7.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
 raise

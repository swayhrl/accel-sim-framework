"""Finish the old transaction first; only then switch our finite controller."""
from pathlib import Path
import os,sys,json,signal,time,subprocess,shutil,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v7 as e
intent=json.loads((R/'control/TRANSFER_V7_BOUNDARY_INTENT.json').read_text());b=intent['current_transfer']['batch'];m=json.loads(Path(b['manifest']).read_text());bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1))
def exact_alive(row):
 p=Path('/proc')/str(row['pid'])
 try:
  state=(p/'stat').read_text().rsplit(')',1)[1].split();return int(state[19])==row['start_ticks'] and state[0]!='Z'
 except FileNotFoundError:return False
deadline=time.monotonic()+3600
while True:
 active=[]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:a=(proc/'cmdline').read_bytes().split(b'\0')
  except OSError:continue
  if str(R/'tools/library_copy.py').encode() in a and str(Path(b['manifest'])).encode() in a:active.append(int(proc.name))
 if not active and (bundle/'COMMIT.json').exists():break
 assert time.monotonic()<deadline,'OWN_OLD_BATCH_NOT_CLOSED_WITHIN_FINITE_PROMOTION_WAIT'
 time.sleep(5)
e.verify_committed(bundle)
parent=intent['parent'];assert exact_alive(parent)
args=(Path('/proc')/str(parent['pid'])/'cmdline').read_bytes().split(b'\0');assert str(R/'tools/transfer_batches.py').encode() in args
os.kill(parent['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGCONT)
for _ in range(100):
 if not exact_alive(parent):break
 time.sleep(.1)
assert not exact_alive(parent),'own former controller still live'
supervisor=json.loads((R/'control/SUPERVISOR_PID.json').read_text())
for _ in range(100):
 if not exact_alive(supervisor):break
 time.sleep(.1)
assert not exact_alive(supervisor),'old supervisor not terminal'
candidate=json.loads((R/'control/ENGINE_V7_CANDIDATE.json').read_text());assert candidate['engine_sha256']==hashlib.sha256(e.SELF_BYTES).hexdigest()
for file in ['IO_V7_QUALIFICATION.json','ARCHIVE_SENDER_QUALIFICATION_ISOLATED_V7.json']:
 q=json.loads((R/'control'/file).read_text());assert q['status']=='PASS' and q['engine_sha256']==candidate['engine_sha256']
q=json.loads((R/'control/PROTOCOL_QUALIFICATION_ISOLATED_V7.json').read_text());assert q['status']=='PASS'
for report in q['reports']:
 if 'receipt' in report and report['receipt'].get('bundle'):
  assert hashlib.sha256((Path(report['receipt']['bundle'])/'trace_copy.py').read_bytes()).hexdigest()==candidate['engine_sha256']
p=R/'synthetic/kernelslist.g';row=e.identity(p);row.update(relative_path='kernelslist.g',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),header_prefix_hex=p.read_bytes().hex())
fixture={'payload_kind':'CAS_FILES_V1','source_backend':'native','freeze_status':'FROZEN_SYNTHETIC_QUALIFICATION','primary_asset_id':'NATIVE_BACKEND_PROTOCOL_V7','object_id':hashlib.sha256(e.canon(row)).hexdigest(),'source_root':str(p.parent),'source_root_identity':e.identity(p.parent),'members':[row],'source_data_bytes':row['size'],'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/inbox/qualification/NATIVE_BACKEND_PROTOCOL_V7','reuse':False}
native=e.migrate(fixture);e.verify_committed(Path(native['bundle']),rehash=True)
promotion={'status':'PASS_PROMOTED_AT_CLOSED_BATCH_BOUNDARY',**{k:v for k,v in candidate.items() if k!='status'},'old_batch':b,'old_batch_commit_sha256':hashlib.sha256((bundle/'COMMIT.json').read_bytes()).hexdigest(),'native_backend_qualification':native,'parent_terminated_only_after_receiver_source_exit_and_commit':True,'observed_unix':time.time()}
(R/'control/ENGINE_V7_PROMOTION.json').write_text(json.dumps(promotion,indent=2)+'\n')
old=R/'tools/transfer_batches_v6.py'
if not old.exists():shutil.copyfile(R/'tools/transfer_batches.py',old)
temp=R/'tools/transfer_batches.writing';temp.write_bytes((R/'tools/transfer_batches_v7.py').read_bytes());os.replace(temp,R/'tools/transfer_batches.py')
p=subprocess.Popen(['python3','-B',str(R/'tools/run_goal.py')],stdin=subprocess.DEVNULL,stdout=(R/'logs/supervisor_v7.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'status':promotion['status'],'new_supervisor_pid':p.pid,'engine_sha256':promotion['engine_sha256']}),flush=True)

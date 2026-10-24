"""Real subprocess crash/resume and corrupt-input qualification, synthetic only."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,signal,struct,io
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
THIS=Path(__file__)

def manifest(case):
 src=R/'synthetic';members=[]
 for rel in ['payload.bin','kernelslist.g']:
  p=src/rel;row=e.identity(p);row.update(relative_path=rel,sha256=e.hash_file(p,rate=0),header_prefix_hex=p.read_bytes()[:128].hex());members.append(row)
 return {'schema':'SHARED_SM70_CAS_PAYLOAD_PROTOCOL_V1','payload_kind':'CAS_FILES_V1','freeze_status':'FROZEN_SYNTHETIC_QUALIFICATION','primary_asset_id':'PIPELINE_V8_'+case,'object_id':hashlib.sha256(e.canon(members)).hexdigest(),'source_root':str(src),'source_root_identity':e.identity(src),'members':members,'source_data_bytes':sum(x['size'] for x in members),'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/inbox/qualification/PIPELINE_V8_'+case,'reuse':False}

def spawn(manifest,skip,testing=False):
 p=subprocess.Popen(['python3','-B',str(THIS),'--source',MODE],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 p.stdin.write(e.canon({'manifest':manifest,'skip':skip}));p.stdin.close();return p

if sys.argv[1:2]==['--source']:
 mode=sys.argv[2];request=json.loads(sys.stdin.buffer.readline());e.CHUNK=2*e.MIB
 if mode=='real':e.source_send(request,testing=True);sys.exit(0)
 # Derive negative streams from the actual sender, then corrupt one property.
 saved=sys.stdout;out=io.BytesIO();sys.stdout=type('BoundedOutput',(),{'buffer':out})()
 e.source_send(request,testing=True);sys.stdout=saved;raw=out.getvalue();pos=0;frames=[]
 while pos<len(raw):
  n=struct.unpack('!Q',raw[pos:pos+8])[0];pos+=8;event=json.loads(raw[pos:pos+n]);pos+=n
  body=raw[pos:pos+event['size']] if event['event']=='CHUNK' else b'';pos+=len(body);frames.append([event,body])
 if mode=='bad_incoming_sha':next(x for x in frames if x[0]['event']=='CHUNK')[0]['sha256']='0'*64
 elif mode=='duplicate_offset':
  chunks=[x for x in frames if x[0]['event']=='CHUNK'];chunks[1][0]['offset']=chunks[0][0]['offset']
 elif mode=='bad_file_end':next(x for x in frames if x[0]['event']=='FILE_END')[0]['sha256']='0'*64
 elif mode=='missing_file_end':frames=[x for x in frames if x[0]['event']!='FILE_END']
 elif mode=='missing_source_done':frames=[x for x in frames if x[0]['event']!='SOURCE_DONE']
 elif mode!='nonzero_sender_exit':raise AssertionError(mode)
 for event,body in frames:
  b=e.canon(event);sys.stdout.buffer.write(struct.pack('!Q',len(b))+b+body);sys.stdout.buffer.flush()
 sys.exit(7 if mode=='nonzero_sender_exit' else 0)

if sys.argv[1:2]==['--crash_worker']:
 MODE='real';e.spawn_sender=spawn;original=e.hash_file
 def slow_hash(path,*a,**kw):
  if str(path).endswith('.writing'):time.sleep(.5)
  return original(path,*a,**kw)
 e.hash_file=slow_hash;e.migrate(manifest('REAL_KILL_R1'),testing=True);sys.exit(0)

report=R/'control/PIPELINE_V8_QUALIFICATION.json'
if report.exists():
 q=json.loads(report.read_text());assert q['status']=='PASS' and q['engine_sha256']==e.digest(e.SELF_BYTES);print(report);sys.exit(0)
MODE='real';e.spawn_sender=spawn;tests=[]
m=manifest('REAL_KILL_R1');bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));assert not bundle.exists(),'fresh synthetic case required'
log=(R/'logs/pipeline_v8_real_kill.log').open('ab');p=subprocess.Popen(['python3','-B',str(THIS),'--crash_worker'],stdout=log,stderr=subprocess.STDOUT)
deadline=time.monotonic()+45
while True:
 indexed=list((bundle/'chunks').glob('*/*.part.json')) if bundle.exists() else []
 if indexed:break
 assert p.poll() is None,'worker ended before real interruption'
 assert time.monotonic()<deadline,'bounded crash qualification deadline';time.sleep(.02)
assert not (bundle/'COMMIT.json').exists();os.kill(p.pid,signal.SIGKILL);assert p.wait()==-signal.SIGKILL;log.close()
tests.append({'test':'actual_SIGKILL_after_durable_chunk_before_COMMIT','status':'PASS_EXPECTED_UNCOMMITTED','receiver_pid':p.pid,'indexed_ranges_at_kill':len(indexed)})
time.sleep(.3);receipt=e.migrate(m,testing=True);e.verify_committed(bundle,rehash=True)
assert receipt['reused_verified_range_bytes']>0 and receipt['bounded_verification_pipeline']['observed_peak_pending']==3
tests.append({'test':'actual_kill_resume_all_closed_hashes_and_bounded_overlap','status':'PASS','receipt':receipt})
# Corrupt a real, uncommitted durable synthetic chunk; resume must refuse it.
m=manifest('CORRUPT_RESUME_R1');bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));assert not bundle.exists()
try:e.migrate(m,testing=True,inject_after_ranges=1)
except RuntimeError as x:assert str(x)=='INJECTED_BOUNDED_OWN_RANGE_CRASH'
else:raise AssertionError('missing injected interruption')
chunk=next((bundle/'chunks').glob('*/*.part'))
with chunk.open('r+b') as f:
 b=f.read(1);f.seek(0);f.write(bytes([b[0]^1]));f.flush();os.fsync(f.fileno())
try:e.migrate(m,testing=True)
except RuntimeError as x:assert 'resume chunk damaged' in str(x) or 'orphan range SHA mismatch' in str(x);reason=str(x)
else:raise AssertionError('damaged resume accepted')
assert not (bundle/'COMMIT.json').exists();tests.append({'test':'actual_closed_chunk_corruption_blocks_resume','status':'PASS_EXPECTED_REJECTION','reason':reason})
for MODE in ['bad_incoming_sha','duplicate_offset','bad_file_end','missing_file_end','missing_source_done','nonzero_sender_exit']:
 m=manifest(MODE.upper()+'_R1');bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));assert not bundle.exists()
 try:e.migrate(m,testing=True)
 except RuntimeError as x:reason=str(x)
 else:raise AssertionError('corrupt stream accepted '+MODE)
 assert not (bundle/'COMMIT.json').exists();tests.append({'test':MODE,'status':'PASS_EXPECTED_REJECTION','reason':reason})
q={'status':'PASS','engine_sha256':e.digest(e.SELF_BYTES),'tests':tests,'actual_source_function_used_for_positive_and_negative_stream_basis':True,'qualification_only_source_chunk_bytes':2*e.MIB,'production_source_chunk_bytes':128*e.MIB,'source_original_payloads_unchanged':True,'scientific_starts':0,'foreign_processes_touched':0}
report.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)

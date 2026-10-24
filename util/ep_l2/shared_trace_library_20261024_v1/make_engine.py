from pathlib import Path
import json,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
src=Path('/root/data/ep_dtc_trace_migration_20261024_v1/tools/trace_copy.py');s=src.read_text();before=hashlib.sha256(src.read_bytes()).hexdigest()
s=s.replace("TASK=P('/root/data/ep_dtc_trace_migration_20261024_v1')","TASK=P('/root/data/shared_sm70_trace_library_20261024_v1')")
# User explicitly revised the native free-space floor on 2026-10-24.
# Preserve every registered project reservation and the additional 1GiB headroom.
assert "required=7*GIB+reserved+GIB+64*MIB" in s
s=s.replace("required=7*GIB+reserved+GIB+64*MIB","required=5*GIB+reserved+GIB+64*MIB")
old_io="if active:need(pressure.get('some',{}).get('avg10',0)<=5 and pressure.get('full',{}).get('avg10',0)<=1,'RESOURCE_HOLD_ACTIVE_SCIENCE_IO_HEADROOM')"
assert old_io in s
s=s.replace(old_io,"# User authorizes adaptive low-priority progress rather than a blanket IO HOLD.\n  io_rate=adaptive_io_rate(30*MIB,pressure.get('full',{}).get('avg10',100))")
s=s.replace("'host_IO_pressure':pressure,","'host_IO_pressure':pressure,'adaptive_IO_max_read_bytes_sec':io_rate,'IO_policy':'USER_AUTHORIZED_ADAPTIVE_THROTTLE',")
io_helpers=r'''
_io_pressure_cached=(0,100)
def adaptive_io_rate(maximum,full=None):
 global _io_pressure_cached
 if full is None:
  now=time.monotonic()
  if now-_io_pressure_cached[0]>=5:
   try:
    line=next(x for x in P('/proc/pressure/io').read_text().splitlines() if x.startswith('full '));full=float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
   except (OSError,StopIteration,ValueError):full=100
   _io_pressure_cached=(now,full)
  full=_io_pressure_cached[1]
 return min(maximum,(30 if full<5 else 10 if full<10 else 4 if full<20 else 1)*MIB)
def adaptive_io_pace(count,maximum):time.sleep(count/adaptive_io_rate(maximum))
'''
s=s.replace('class Resources:',io_helpers+'\nclass Resources:')
# Discover the second currently registered DTC controller without modifying it.
s=s.replace("for f in ae.glob('*.INTENT.json'):","pending_intents=set(ae.glob('*.INTENT.json'))\n  for registered in registry.get('registered_future_requests',{}).values():\n   consumed=registered.get('consumed',{})\n   if not isinstance(consumed,dict):continue\n   for record in consumed.values():\n    if isinstance(record,dict) and not record.get('execution_receipt') and record.get('intent'):pending_intents.add(P(record['intent']))\n  for f in sorted(pending_intents):")
s=s.replace("NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_ep_dtc_trace_inputs_v1')","NAS=P('/root/share/mnt164/huangrulin/traces')")
old="if row['relative_path']==manifest['entry_name']:need(p.read_bytes().hex()==manifest['commandlist_bytes_hex'],'commandlist bytes/order drift')\n  else:need(first[:128].hex()==row['header_prefix_hex'],'kernel header differs from source')"
new="if manifest.get('payload_kind')=='CAS_FILES_V1':\n   if row.get('header_prefix_hex'):need(first[:128].hex()==row['header_prefix_hex'],'CAS prefix differs from frozen source')\n  elif row['relative_path']==manifest['entry_name']:need(p.read_bytes().hex()==manifest['commandlist_bytes_hex'],'commandlist bytes/order drift')\n  else:need(first[:128].hex()==row['header_prefix_hex'],'kernel header differs from source')"
assert old in s;s=s.replace(old,new)
# New backend is deliberately separate from the unchanged regular-file sender.
s=s.replace("manifest=request['manifest'];skip=request['skip']","manifest=request['manifest'];skip=request['skip']\n if manifest.get('source_backend')=='archive':return source_archive_send(request,testing)")
s=s.replace("else:need(os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]','wrong old174 source namespace')","else:need((os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]') or (manifest.get('source_backend')=='native' and os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'),'wrong frozen source namespace')")
s=s.replace("if testing:\n  p=subprocess.Popen", "if testing or manifest.get('source_backend')=='native':\n  p=subprocess.Popen")
s=s.replace("str(P(__file__)),'source-synthetic'", "str(P(__file__)),('source-native' if manifest.get('source_backend')=='native' else 'source-synthetic')")
s=s.replace("if sys.argv[1:] in [['source-synthetic']]:source_send(json.loads(sys.stdin.buffer.readline()),testing=True)","if sys.argv[1:] in [['source-synthetic']]:source_send(json.loads(sys.stdin.buffer.readline()),testing=True)\n  elif sys.argv[1:] in [['source-native']]:source_send(json.loads(sys.stdin.buffer.readline()),testing=False)")
addon=r'''
def source_archive_send(request,testing=False):
 import tarfile,gzip,threading
 m=request['manifest'];archive=P(m['archive_path']);skip=request['skip']
 if testing:need(archive.is_relative_to(TASK/'synthetic'),'archive test outside owned source')
 else:need(os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]','archive source identity')
 need(same_source(identity(archive),m['archive_identity']),'archive identity changed before stream')
 lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:os.nice(19)
 except OSError:pass
 def frame(o):b=canon(o);sys.stdout.buffer.write(struct.pack('!Q',len(b))+b);sys.stdout.buffer.flush()
 wanted={r['archive_member']:r for r in m['members']};found=[];decoder=None;feeder=None;errors=[];started=time.monotonic();physical=[0]
 fd=os.open(archive,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0));raw=os.fdopen(fd,'rb')
 class RateReader:
  def read(self,n=-1):
   b=raw.read(n);physical[0]+=len(b);time.sleep(max(0,physical[0]/(30*MIB)-(time.monotonic()-started)));return b
 reader=RateReader()
 if str(archive).endswith('.zst'):
  decoder=subprocess.Popen([('/usr/bin/zstd' if P('/usr/bin/zstd').is_file() else str(TASK/'tools/zstd')),'-dc'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  def feed():
   try:
    while True:
     b=reader.read(MIB)
     if not b:break
     decoder.stdin.write(b)
    decoder.stdin.close()
   except Exception as x:errors.append(str(x))
  feeder=threading.Thread(target=feed);feeder.start();tf=tarfile.open(fileobj=decoder.stdout,mode='r|')
 else:tf=tarfile.open(fileobj=reader,mode='r|gz')
 try:
  for ti in tf:
   name=ti.name
   if name not in wanted or name in found:continue
   row=wanted[name];need(ti.isfile() and ti.size==row['size'],'archive member type/size drift');f=tf.extractfile(ti);h=hashlib.sha256();offset=0
   while True:
    b=f.read(CHUNK)
    if not b:break
    h.update(b)
    if offset>=skip[row['relative_path']]:
     frame({'event':'CHUNK','path':row['relative_path'],'offset':offset,'size':len(b),'sha256':digest(b)})
     for i in range(0,len(b),MIB):part=memoryview(b)[i:i+MIB];time.sleep(len(part)/RATE);sys.stdout.buffer.write(part);sys.stdout.buffer.flush()
    offset+=len(b)
   need(offset==row['size'] and h.hexdigest()==row['sha256'],'archive member full SHA drift');found.append(name)
   frame({'event':'FILE_END','path':row['relative_path'],'size':offset,'sha256':h.hexdigest(),'source_before_after_identity_unchanged':True,'source_disposition':'SOURCE_KEEP'})
  need(found==[r['archive_member'] for r in m['members']],'archive member order or EOF mismatch')
  need(same_source(identity(archive),m['archive_identity']),'archive changed during stream')
 finally:
  tf.close()
  if decoder:
   while decoder.stdout.read(MIB):pass
   feeder.join();need(not errors,'zstd input stream error');need(decoder.wait()==0,'zstd decoder failed')
  raw.close()
 need(same_source(identity(archive),m['archive_identity']),'archive changed before final source close')
 frame({'event':'SOURCE_DONE','Source_simulator_starts':0,'source_disposition':'SOURCE_KEEP'})
'''
s=s.replace("if __name__=='__main__':",addon+"\nif __name__=='__main__':")
s=s.replace("lock=(BRIDGE/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)","lock=((TASK/'synthetic/.SOURCE_TEST.lock') if testing else (BRIDGE/'.TLS_V10_SOURCE_SENDER.lock')).open('a' if testing else 'rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)")
s=s.replace("'root_directory_original_numeric_metadata':True", "'root_directory_original_numeric_metadata':manifest.get('payload_kind')!='CAS_FILES_V1','root_directory_manifest_numeric_metadata':True")
s=s.replace('time.sleep(len(part)/RATE)','adaptive_io_pace(len(part),RATE)')
s=s.replace('time.sleep(max(0,physical[0]/(30*MIB)-(time.monotonic()-started)))','adaptive_io_pace(len(b),30*MIB)')
compile(s,'library_copy.py','exec')
p=R/'tools/library_copy.py';temp=p.with_suffix('.writing');temp.write_text(s);temp.replace(p)
receipt={'source_engine':str(src),'source_engine_sha256':before,'derived_engine':str(p),'derived_engine_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'same_existing_sender_receiver_locks':True,'chunk_bytes':128*1024**2,'transfer_rate_bytes_sec':15*1024**2,'qualified_V9_primitives_unchanged':True,'native_free_floor_bytes':5*1024**3,'extra_unregistered_headroom_bytes':1024**3,'registered_foreign_reservations_preserved':True,'resource_policy_authority':'Explicit user instruction 2026-10-24: safety margin 5G; verified migration to164 and removal of our local copies authorized when necessary','extensions':['dedicated task and genuine164 library destination','CAS payload has no pretend kernelslist; full-file SHA and EOF unchanged','streaming immutable archive backend; regular sender unchanged','user-authorized5GiB disk floor plus existing reservations and1GiB headroom'],'original_engine_modified':False}
receipt['IO_amendment_authority']='Explicit user instruction2026-10-24: handle IO/resource protection; start parallel all-workload4080 capture and semantic validation, do not remain blocked solely by resource policy'
receipt['IO_policy']={'mode':'ADAPTIVE_LOW_PRIORITY_PROGRESS','full_PSI_avg10_thresholds':[5,10,20],'read_MiB_per_second':[30,10,4,1],'max_transfer_MiB_per_second':15,'scientific_process_freshness_guard_retained':True,'foreign_tools_and_reservations_modified':False}
(R/'control/ENGINE_DERIVATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))

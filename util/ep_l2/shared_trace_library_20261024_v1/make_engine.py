from pathlib import Path
import json,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
src=Path('/root/data/ep_dtc_trace_migration_20261024_v1/tools/trace_copy.py');s=src.read_text();before=hashlib.sha256(src.read_bytes()).hexdigest()
s=s.replace("TASK=P('/root/data/ep_dtc_trace_migration_20261024_v1')","TASK=P('/root/data/shared_sm70_trace_library_20261024_v1')")
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
compile(s,'library_copy.py','exec')
p=R/'tools/library_copy.py';p.write_text(s)
receipt={'source_engine':str(src),'source_engine_sha256':before,'derived_engine':str(p),'derived_engine_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'same_existing_sender_receiver_locks':True,'chunk_bytes':128*1024**2,'transfer_rate_bytes_sec':15*1024**2,'qualified_V9_primitives_unchanged':True,'extensions':['dedicated task and genuine164 library destination','CAS payload has no pretend kernelslist; full-file SHA and EOF unchanged','streaming immutable archive backend; regular sender unchanged'],'original_engine_modified':False}
(R/'control/ENGINE_DERIVATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))

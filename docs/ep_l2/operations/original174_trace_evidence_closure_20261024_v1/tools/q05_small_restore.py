from closure_local import *
from closure_resources import UTIL,checkpoint
checkpoint('BEFORE_Q05_166KB_SAMPLE_RESTORE')
code=UTIL+r'''
import hashlib,uuid,re
src='/root/share/mnt164/huangrulin/awma_q05_full_kernel_translation_analysis_v1/r0_natural_completion_interrupted_transport/run.log'
base='/root/data/original174_trace_evidence_closure_20261024_v1'
dest=base+'/q05_natural_r0_sample'
before=meta(src);mem=int(next(z.split()[1] for z in Path('/proc/meminfo').read_text().splitlines() if z.startswith('MemAvailable:')))*1024
free=os.statvfs('/root/data').f_bavail*os.statvfs('/root/data').f_frsize
reg=json.loads(Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_text())
reserved=sum(int(r.get('reserved_write_bytes',0)) for r in reg.get('registered_future_requests',{}).values())
required=7*1024**3+reserved+2*1024**2
o=dict(utc=time.time(),source=src,source_before=before,destination=dest,native_fs=cmd(['findmnt','-J','-T','/root/data']),ssd_available=free,required_bytes=required,other_reserved_bytes=reserved,MemAvailable_bytes=mem,temporary_restore_cap_bytes=2*1024**2,Share_payload_written_bytes=0,no_Source_sender_or_archive_receiver_used=True)
if free<required or mem<64*1024**3 or os.path.lexists(dest) or before.get('size',10**10)>512*1024:
 o['status']='RESTORE_RESOURCE_OR_ABSENCE_HOLD';print(json.dumps(o));raise SystemExit
mnt=json.loads(cmd(['findmnt','-J','-T',src]))['filesystems'][0]
if mnt.get('source')!='admin-wcx@10.208.130.164:/home/shared' or mnt.get('fstype')!='fuse.sshfs':o['status']='TRUE164_IDENTITY_HOLD';print(json.dumps(o));raise SystemExit
io=Path('/proc/pressure/io').read_text();avg=float(re.search(r'some avg10=([0-9.]+)',io).group(1));o['IO_before']=io
if avg>10:o['status']='SMALL_RESTORE_DEFERRED_IO';print(json.dumps(o));raise SystemExit
with open(src,'rb') as f:b=f.read(512*1024+1)
assert len(b)==before['size']
o['source_sha256']=hashlib.sha256(b).hexdigest();text=b.decode(errors='replace')
o['owner_terminal_scope_checks']=dict(cycles_885681=bool(re.search(r'gpu_sim_cycle\s*=\s*885681\b',text)),instructions_368696302=bool(re.search(r'gpu_sim_insn\s*=\s*368696302\b',text)),cta_224='224' in text)
if not all(o['owner_terminal_scope_checks'].values()):o['status']='OWNER_IDENTITY_HOLD';print(json.dumps(o));raise SystemExit
os.makedirs(base,exist_ok=True);os.mkdir(dest)
p=dest+'/run.log'
fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o444)
with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
with open(p,'rb') as f:restored=f.read()
o['restored_sha256']=hashlib.sha256(restored).hexdigest();o['restored_stat']=meta(p);o['source_after']=meta(src);o['source_identity_stable']=all(before.get(k)==o['source_after'].get(k) for k in ['dev','inode','size','mtime_ns','ctime_ns']);o['archive_and_native_restored_content_equal']=restored==b;o['status']='TRUE164_NATURAL_R0_NATIVE_TARGET_CONTENT_SAMPLE_RESTORE_VERIFIED';o['original_numeric_metadata_restore_status']='HOLD_NO_ORIGINAL_NATIVE_METADATA_MANIFEST; SSHFS projection not substituted';o['accepted_scope']='Separate natural R0 diagnostic885681cycles; NOT fixed10000 SIM_EVIDENCE_c8b4175d';o['restore_not_a_new_scientific_run']=True
print(json.dumps(o))
'''
x=remote('hrl-174-new',code,60);save('evidence/Q05_TRUE164_NATURAL_R0_NATIVE_TARGET_CONTENT_SAMPLE_RESTORE.json',x);print(x['status'],x.get('source_sha256'))

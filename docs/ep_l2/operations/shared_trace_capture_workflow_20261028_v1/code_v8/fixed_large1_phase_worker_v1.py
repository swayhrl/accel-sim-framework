"""One fixed group or full66 model worker, inheriting only its Root-owned private memfd OFD; no arbitrary commands."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,runpy,fcntl
P=Path(__file__).resolve().parent;G=2**30
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def main():
 fd=int(os.environ['CFI_CPU6_SLOT_FD']);desc=json.loads(os.environ['CFI_CPU6_SLOT_DESC']);st=os.fstat(fd)
 owned=desc['private_owned_fd'];need(owned['type']=='ROOT_PRIVATE_MEMFD_FLOCK'and owned['name']=='LARGE1_OWNED_CPU_POST_LEASE','ROOT_PRIVATE_LEASE_DESCRIPTOR')
 need((st.st_dev,st.st_ino,st.st_uid,st.st_mode&0o777,st.st_size)==(owned['dev'],owned['inode'],owned['uid'],owned['mode'],0)and st.st_uid==os.getuid()and st.st_mode&0o777==0o600,'INHERITED_PRIVATE_FD_IDENTITY')
 need(os.readlink('/proc/self/fd/'+str(fd))=='/memfd:LARGE1_OWNED_CPU_POST_LEASE (deleted)','ONLY_OWN_PRIVATE_MEMFD_PATH')
 parentstat=os.stat('/proc/'+str(desc['guard'][0])+'/fd/'+str(fd));need((parentstat.st_dev,parentstat.st_ino)==(st.st_dev,st.st_ino),'ACTUAL_GUARD_SAME_PRIVATE_OFD_INODE')
 lines=[l for l in Path('/proc/self/fdinfo/'+str(fd)).read_text().splitlines()if l.startswith('lock:')]
 need(len(lines)==1 and ['FLOCK','ADVISORY','WRITE',str(desc['guard'][0])]==lines[0].split()[2:6],'REAL_INHERITED_GUARD_FLOCK')
 stat=Path('/proc',str(desc['guard'][0]),'stat').read_text().rsplit(')',1)[1].split();need(stat[19]==desc['guard'][1] and os.getppid()==desc['guard'][0],'GUARD_PARENT_TICKS')
 actual=Path('/sys/fs/cgroup')/Path('/proc/self/cgroup').read_text().strip().split('::',1)[1].lstrip('/')
 need(str(actual)==desc['cgroup'] and int((actual/'memory.max').read_text())==2*G,'ACTUAL_OWN_HARD2_MEMBERSHIP')
 os.set_inheritable(fd,True);old=subprocess.Popen
 class InheritCPU6(old):
  def __init__(self,*args,**kwargs):
   kwargs['pass_fds']=tuple(sorted(set(kwargs.get('pass_fds',()))|{fd}));kwargs['close_fds']=True;super().__init__(*args,**kwargs)
   try:
    child=Path('/proc',str(self.pid));cs=(child/'fd'/str(fd)).stat();cl=[x for x in(child/'fdinfo'/str(fd)).read_text().splitlines()if x.startswith('lock:')]
    need((cs.st_dev,cs.st_ino)==(st.st_dev,st.st_ino) and len(cl)==1 and cl[0].split()[2:6]==['FLOCK','ADVISORY','WRITE',str(desc['guard'][0])],'ACTUAL_EXEC_CHILD_CPU6_INHERITED_FD')
    receipt=dict(pid=self.pid,start_ticks=(child/'stat').read_text().rsplit(')',1)[1].split()[19],slot_fd=fd,dev=cs.st_dev,inode=cs.st_ino,fdinfo_lock_lines=cl,scope_sha256=desc['scope_sha256'])
   except FileNotFoundError:receipt=dict(pid=self.pid,gone_before_FD_snapshot=True,returncode=self.poll())
   q=Path(os.environ['CFI_WORKER_BIRTH_RECEIPT']+'.EXEC_'+str(self.pid)+'.json')
   with q.open('x')as f:json.dump(receipt,f,indent=2)
 subprocess.Popen=InheritCPU6
 birth=dict(pid=os.getpid(),start_ticks=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19],slot_fd=fd,slot_dev=st.st_dev,slot_inode=st.st_ino,actual_fdinfo_lock_lines=lines,scope_sha256=desc['scope_sha256'],actual_RLIMIT_AS=list(__import__('resource').getrlimit(__import__('resource').RLIMIT_AS)))
 with Path(os.environ['CFI_WORKER_BIRTH_RECEIPT']).open('x')as f:json.dump(birth,f,indent=2)
 mode=sys.argv[1];need(mode in('VALIDATE','GROUP'),'ONLY_FIXED_VALIDATE_OR_GROUP')
 mfraw=(P/'CODE_MANIFEST.json').read_bytes();need(hashlib.sha256(mfraw).hexdigest()==desc['code_manifest_sha256'],'EXACT_CHILD_CODE_MF')
 mf=json.loads(mfraw)
 def module(name):
  raw=(P/name).read_bytes();r=mf['files'][name];need(len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'RAW_CHILD_SOURCE_PIN')
  m=__import__('types').ModuleType(name);m.__file__=str(P/name);exec(compile(raw,str(P/name),'exec'),m.__dict__);return m
 data=json.loads((P/'EXACT_LARGE1_DATA_V1.json').read_bytes());qid=sys.argv[2]
 need(qid in desc['exact_jobs']==data['qids']and len(data['qids'])==1,'EXACT_TINY2_ONLY')
 c=next(x for x in data['rows']if x['qid']==qid);out=Path(desc['output_root'])/qid
 if mode=='VALIDATE':
  need(len(sys.argv)==4 and Path(sys.argv[3])==out,'FIXED_VALIDATE_OUTPUT')
  S=module('single2_source_guard_v1.py');headers=S.preflight_headers(c)
  T=module('post_feature_tap_v1.py');tap=T.FeatureTap();F=module('f9_observation_samebytes_v2.py')
  V=F.load(P/'frozen_ordinary_F9.py',P/'frozen_parser_f4.py',tap)
  r=V.validate(Path(c['source_root']),Path(c['metadata_refs']['map']['path']))
  need(r['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and r['kernels']==c['header_count']and r['stream_ids']==[0]and r['counts']['sass_records']==c['declared_source_records'],'EXACT_SMALL_RECORD_STREAM_COUNTS')
  need(r['map_sha256']==c['metadata_refs']['map']['sha256']and all(type(k['header'].get('stream_id'))is int and k['header']['stream_id']==0 for k in r['per_kernel']),'EXACT_MAP_AND_EXPLICIT_STREAM_POSTJOIN')
  for i,k in enumerate(r['per_kernel']):
   k['producer_command_index']=i;k['original_kernel_index']=int(__import__('re').fullmatch(r'kernel-(\d+)-ctx_0x[0-9a-fA-F]+\.trace\.xz',k['name'])[1])
  r['explicit_single_stream_header_preflight']=headers;r['original_checks_observation_proof']=V.observation_proof
  def save(p,x):
   with p.open('x')as f:json.dump(x,f,indent=2,sort_keys=True);f.write(chr(10));f.flush();os.fsync(f.fileno())
  save(out/'FULL_RECORD_VALIDATION.json',r)
  save(out/'SAME_PASS_FEATURE_TAP_STATE.json',dict(features=tap.features,records=tap.records,active=tap.active,inactive=tap.inactive,active_unknown=tap.active_unknown,max_features=tap.max_features))
 else:
  need(len(sys.argv)==6,'EXACT_GROUP_PATHS')
  src,dest,work=map(Path,sys.argv[3:])
  need(src.parent==Path(c['source_root'])/'traces'and src.name in c['command_names'],'EXACT_ORIGINAL_TINY_RAW_KERNEL')
  need(dest==out/'grouped'/src.name.replace('.trace.xz','.traceg.xz')and work==out/'scratch'/src.name,'EXACT_OWN_GROUP_OUTPUT_SCRATCH')
  script=P/'postprocess_nas_sharded_v4.py';r=mf['files'][script.name];need(script.stat().st_size==r['bytes']and sha(script)==r['sha256'],'UNCHANGED5D')
  sys.argv=[str(script),str(src),str(dest),str(work),'--cta-span','64','--scratch-budget',str(64*G)];runpy.run_path(str(script),run_name='__main__')
if __name__=='__main__':main()

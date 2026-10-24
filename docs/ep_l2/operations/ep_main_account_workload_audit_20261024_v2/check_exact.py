import os,sys,json,stat,hashlib,datetime
requests=json.loads(sys.argv[1])
out=[]
def ident(s):return dict(dev=s.st_dev,inode=s.st_ino,bytes=s.st_size,mtime_ns=s.st_mtime_ns,mode=stat.S_IMODE(s.st_mode))
for request in requests:
 p=request['path']; row=dict(request)
 try:
  fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOATIME',0))
  with os.fdopen(fd,'rb') as f:
   before=ident(os.fstat(f.fileno()));assert before['bytes']<=1048576
   b=f.read(1048577);stable=before==ident(os.fstat(f.fileno()))==ident(os.stat(p))
  lines=b.decode(errors='replace').splitlines();order=[];commands=[];unknown=[]
  for line in lines:
   n=line.strip()
   if not n or n.startswith('#'):continue
   if n.lower().startswith(('memcpy','cudamemcpy')):commands.append(n);continue
   if not os.path.isabs(n) and '..' not in n.split('/') and '.trace' in n:order.append(n)
   else:unknown.append(n)
  members=[]
  for n in dict.fromkeys(order):
   q=os.path.join(os.path.dirname(p),n)
   try:
    s=os.stat(q);members.append(dict(path=q,realpath=os.path.realpath(q),exists=True,readable=os.access(q,os.R_OK),regular=stat.S_ISREG(s.st_mode),stat=ident(s)))
   except OSError as e:members.append(dict(path=q,exists=False,error=str(e)))
  row.update(exists=True,realpath=os.path.realpath(p),sha256=hashlib.sha256(b).hexdigest(),stat=before,stable=stable,text=b.decode(errors='replace'),kernel_launches=len(order),members=members,unknown_lines=unknown,complete_by_metadata=bool(order) and not unknown and all(m.get('exists') and m.get('readable') and m.get('regular') and m['stat']['bytes']>0 for m in members))
  scripts=[]
  for q in [os.path.join(os.path.dirname(p),'run.sh'),os.path.join(os.path.dirname(os.path.dirname(p)),'run.sh')]:
   if os.path.isfile(q) and os.stat(q).st_size<=65536:
    fd=os.open(q,os.O_RDONLY|getattr(os,'O_NOATIME',0))
    with os.fdopen(fd,'rb') as f:bb=f.read(65537)
    scripts.append(dict(path=q,sha256=hashlib.sha256(bb).hexdigest(),text=bb.decode(errors='replace')))
  row['capture_scripts']=scripts
 except Exception as e:row.update(exists=False,error=str(e))
 out.append(row)
print(json.dumps(dict(schema='EXACT_SUITE_COMMANDLIST_AND_DECLARED_MEMBER_METADATA_V2',hostname=os.uname().nodename,namespace=os.readlink('/proc/self/ns/mnt'),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=out,trace_body_bytes_read=0,workload_execs=0),ensure_ascii=False))

#!/usr/bin/env python3
"""Finite account-scoped metadata census. Never opens trace bodies or executes workloads."""
import os, sys, json, time, stat, hashlib, datetime, collections
start = time.monotonic()
label = sys.argv[1]
roots = json.loads(sys.argv[2])
skip_names = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv', 'site-packages', 'model-cache', 'model_cache', 'checkpoints'}
skip_exact = {'/root/share', '/root/data/ep_l2_main_20261023_v1/asset_audit_20261024_v2'}
allow = ['/workspace', '/root', '/opt', '/usr/local']
def suite(p):
    x = p.lower()
    if 'polybench' in x: return 'PolyBench/GPU'
    if 'parboil' in x: return 'Parboil'
    if 'rodinia' in x: return 'Rodinia'
    if any(s in x for s in ['/cudasdk/', 'cuda-samples', 'cuda_samples', '_cuda_samples', '/sdk/', 'nvidia_gpu_computing_sdk']): return 'CUDA Samples'
    return None
def ident(s):
    return dict(dev=s.st_dev, inode=s.st_ino, bytes=s.st_size, mtime_ns=s.st_mtime_ns, mode=stat.S_IMODE(s.st_mode))
def small(p, limit=1048576):
    fd = os.open(p, os.O_RDONLY | getattr(os, 'O_NOATIME', 0))
    with os.fdopen(fd, 'rb') as f:
        a = ident(os.fstat(f.fileno()))
        if a['bytes'] > limit: raise ValueError('metadata exceeds limit')
        b = f.read(limit+1)
        stable = a == ident(os.fstat(f.fileno())) == ident(os.stat(p))
    return b, a, stable
errors=[]; links=[]; aliases=[]; dirs=[]; source_files=[]; archives=[]; lists=[]; seen=set(); counts=collections.Counter(); root_status=[]
queue=collections.deque()
for root in roots:
    try:
        s=os.stat(root); root_status.append(dict(path=root, realpath=os.path.realpath(root), stat=ident(s)));queue.append((root,0))
    except OSError as e: root_status.append(dict(path=root,error=str(e)))
truncated=False
while queue:
    if time.monotonic()-start>480 or counts['directories']>=400000:
        truncated=True;break
    p,depth=queue.popleft()
    try:
        s=os.stat(p); key=(s.st_dev,s.st_ino)
        if key in seen:
            aliases.append(dict(path=p,realpath=os.path.realpath(p)));continue
        seen.add(key)
        with os.scandir(p) as it: es=list(it)
        counts['directories']+=1;counts['entries']+=len(es)
    except OSError as e:
        errors.append(dict(path=p,error=str(e)));continue
    su=suite(p)
    bn=os.path.basename(p).lower()
    if su and (depth<18 or bn in ['cuda','benchmarks','data','src','bin','traces']):
        dirs.append(dict(path=p,suite=su,children=[e.name for e in es if not e.name.startswith('.')],stat=ident(s)))
    elif bn in ['gpu-app-collection','gpgpu-workloads','hw_run','traces','trace','benchmarks','samples']:
        dirs.append(dict(path=p,suite=None,children=[e.name for e in es if not e.name.startswith('.')],stat=ident(s)))
    for e in es:
        try:
            q=e.path; lower=e.name.lower()
            if e.name.startswith('.') or e.name in skip_names: continue
            if e.is_symlink():
                target=os.readlink(q);real=os.path.realpath(q)
                permitted=any(real==a or real.startswith(a+'/') for a in allow) and not (real.startswith('/root/share/') and not any(real==r or real.startswith(r+'/') for r in roots if r.startswith('/root/share/')))
                links.append(dict(path=q,target=target,realpath=real,exists=os.path.exists(q),followed=permitted))
                if not permitted:continue
            if e.is_dir(follow_symlinks=True):
                if q in skip_exact:continue
                queue.append((q,depth+1));continue
            counts['files']+=1
            sq=suite(q)
            if lower in ['kernelslist.g','kernelslist','kernelslist.txt']:
                row=dict(path=q,realpath=os.path.realpath(q),suite=sq)
                try:
                    b,st,stable=small(q);text=b.decode('utf-8',errors='replace')
                    members=[];commands=[];unknown=[];order=[]
                    for line in text.splitlines():
                        n=line.strip()
                        if not n or n.startswith('#'):continue
                        if n.lower().startswith(('memcpy','cudamemcpy')):commands.append(n);continue
                        if '/' not in n and ('.trace' in n or n.endswith(('.g','.xz','.gz','.zst','.tracez'))):order.append(n)
                        else:unknown.append(n)
                    for n in dict.fromkeys(order):
                        z=os.path.join(p,n)
                        try:
                            t=os.stat(z);members.append(dict(name=n,path=z,realpath=os.path.realpath(z),exists=True,readable=os.access(z,os.R_OK),regular=stat.S_ISREG(t.st_mode),stat=ident(t)))
                        except OSError as ex:members.append(dict(name=n,path=z,exists=False,error=str(ex)))
                    row.update(stat=st,stable=stable,sha256=hashlib.sha256(b).hexdigest(),text=text,kernel_launches=len(order),members=members,commands=commands,unknown_lines=unknown,complete_by_metadata=bool(order) and not unknown and all(m.get('exists') and m.get('readable') and m.get('regular') and m['stat']['bytes']>0 for m in members))
                except Exception as ex:row['error']=str(ex)
                lists.append(row)
            if sq and (lower.endswith(('.cu','.cuh','.c','.cpp','.h','.cl')) or lower in ['makefile','description','readme','readme.md','readme.txt']):
                source_files.append(dict(path=q,suite=sq,stat=ident(e.stat())))
            if any(lower.endswith(x) for x in ['.tar','.tar.gz','.tgz','.tar.xz','.zip','.7z','.tar.zst']) and (sq or any(x in lower for x in ['trace','benchmark','cuda','gpu-app','workload'])):
                archives.append(dict(path=q,suite=sq,stat=ident(e.stat())))
        except OSError as ex:errors.append(dict(path=e.path,error=str(ex)))
print(json.dumps(dict(schema='EP_MAIN_ACCOUNT_WORKLOAD_CENSUS_V2',label=label,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),hostname=os.uname().nodename,namespace=os.readlink('/proc/self/ns/mnt'),uid=os.getuid(),roots=root_status,exclusions=sorted(skip_names|skip_exact),counts=dict(counts),elapsed_seconds=time.monotonic()-start,truncated=truncated,pending_directories=list(queue),errors=errors,links=links,aliases=aliases,directories=dirs,source_files=source_files,archives=archives,commandlists=lists,trace_body_bytes_read=0,workload_execs=0),ensure_ascii=False))

import subprocess,hashlib
def staged_checks(base):
    entries=[]
    for item in subprocess.check_output(['git','ls-files','--stage','-z','--',base]).split(b'\0'):
        if not item: continue
        meta,name=item.split(b'\t',1);mode,oid,stage=meta.split()
        assert stage==b'0' and mode in [b'100644',b'100755']
        name=name.decode('utf-8')
        assert '__pycache__' not in name
        if not name.endswith('/SHA256SUMS'): entries.append((name,oid))
    proc=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    result=[]
    try:
        for name,oid in entries:
            proc.stdin.write(oid+b'\n');proc.stdin.flush()
            head=proc.stdout.readline().split();assert len(head)==3 and head[0]==oid and head[1]==b'blob'
            remaining=int(head[2]);digest=hashlib.sha256()
            while remaining:
                chunk=proc.stdout.read(min(remaining,1024*1024));assert chunk
                digest.update(chunk);remaining-=len(chunk)
            assert proc.stdout.read(1)==b'\n'
            result.append(digest.hexdigest()+'  '+name[len(base)+1:]+'\n')
        proc.stdin.close();assert proc.wait(timeout=30)==0
        return result
    finally:
        if proc.poll() is None: proc.terminate();proc.wait(timeout=10)

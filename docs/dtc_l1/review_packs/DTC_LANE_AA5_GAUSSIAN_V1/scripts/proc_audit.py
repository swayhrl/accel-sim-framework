"""Read-only process/fdinfo helpers; no signal or flock acquisition capability."""
from common import *

def process_snapshot():
    s=snapshot()
    for p in s['processes']:
        try:
            q=Path('/proc')/str(p['pid']);st=(q/'stat').read_text().rsplit(')',1)[1].split();p.update(ppid=int(st[1]),pgrp=int(st[2]),session=int(st[3]),cwd=os.readlink(q/'cwd'),exe=os.readlink(q/'exe'))
        except OSError:p['racy_read']=True
    return s

def flock_records(s):
    records=[]
    for p in s['processes']:
        for f in (Path('/proc')/str(p['pid'])/'fdinfo').glob('*'):
            try:
                info=f.read_text()
                if '\nlock:' not in info:continue
                target=os.readlink(f.parent.parent/'fd'/f.name)
                if any(x in target.lower() for x in ['dtc','fast64','lane']):records.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],fd=f.name,path=target,fdinfo=info))
            except OSError:pass
    return records

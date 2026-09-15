import shutil,hashlib
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def verify(source,dest):
 s=sorted(p for p in Path(source).rglob('*') if p.is_file());d=Path(dest)
 for p in s:
  q=d/p.relative_to(source)
  if not q.is_file() or p.stat().st_size!=q.stat().st_size or sha(p)!=sha(q):return False
 return True

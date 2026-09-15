import shutil,hashlib
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def verify(source,dest):
 s={p.relative_to(source):p for p in Path(source).rglob('*') if p.is_file()};d={p.relative_to(dest):p for p in Path(dest).rglob('*') if p.is_file()}
 if set(s)!=set(d):return False
 return all(p.stat().st_size==d[r].stat().st_size and sha(p)==sha(d[r]) for r,p in s.items())

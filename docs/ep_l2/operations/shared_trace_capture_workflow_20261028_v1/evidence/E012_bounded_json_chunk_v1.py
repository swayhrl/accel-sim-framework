"""Private same-cap reader for the frozen resources.py ABI; no disk/source or policy mutation."""
from pathlib import Path
CAP=128*2**20
CHUNK=64*2**10
def bounded_json_raw(p):
 path=Path(p);before=path.stat()
 if before.st_size>CAP:raise RuntimeError('RESOURCE_HOLD_PLATFORM_METADATA128MIB')
 chunks=[];total=0
 with path.open('rb')as f:
  while True:
   b=f.read(min(CHUNK,CAP+1-total))
   if not b:break
   chunks.append(b);total+=len(b)
   if total>CAP:raise RuntimeError('RESOURCE_HOLD_PLATFORM_METADATA_GROWTH128MIB')
 return b''.join(chunks)
def install(module):
 module.bounded_json_raw=bounded_json_raw
 return module

"""CPU-only sealed-entry handoff primitive, not a science admission authority.

prepare() opens/pins exact reviewed routing and scoped bytes, then seals a memfd.
Only invoke_cpu_stub() executes here, and it accepts one exact harmless stub.
Main can integrate Prepared.fd into an independently authorized native executor;
this module neither installs routes nor invokes production scientific artifacts.
"""
import dataclasses,fcntl,json,os,subprocess
from pathlib import Path
import safe_native_candidate as c
CPU_STUB=(b"#!/bin/sh\nexec /usr/bin/python3 -c 'import json,os,sys; "
          b'print(json.dumps({"marker":"APPROVED_SEALED_CPU_STUB","argv":sys.argv[1:],'
          b'"token":os.environ.get("EP_CPU_STUB_TOKEN"),"extra":os.environ.get("EP_CPU_STUB_EXTRA")}))'
          b"' \"$@\"\n")
SEALS=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
@dataclasses.dataclass
class Prepared:
 fd:int
 entry_sha256:str
 global_sha256:str
 shared_route_status:str
 entry_token:dict
 production_activated:bool=False
 def close(self):
  if self.fd>=0:os.close(self.fd);self.fd=-1
 def __enter__(self):return self
 def __exit__(self,*exc):self.close()
def prepare(global_path,base_ref,grant_ref,entry_ref):
 """References themselves must be pinned by Main's immutable manifest.

 No mutable shared path is used to execute. No source or mode admission is granted.
 Grant authorization/handler validation are read-only, not foreign execution.
 """
 base,_=c.pin(base_ref)
 grant=json.loads(c.pin(grant_ref)[0]) if grant_ref else None
 if grant is not None:c.validate_grant(grant)
 current,_=c.stable_read(global_path)
 route=c.validate_global(current,base,grant)
 entry,token=c.pin(entry_ref)
 fd=os.memfd_create("EP-reviewed-scoped-entry",os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
 try:
  view=memoryview(entry)
  while view:
   count=os.write(fd,view)
   c.need(count>0,"short memfd write")
   view=view[count:]
  os.lseek(fd,0,os.SEEK_SET)
  fcntl.fcntl(fd,fcntl.F_ADD_SEALS,SEALS)
  c.need(fcntl.fcntl(fd,fcntl.F_GET_SEALS)==SEALS,"memfd not completely sealed")
  c.need(c.digest(os.pread(fd,len(entry),0))==entry_ref["sha256"],"sealed entry SHA")
  return Prepared(fd,entry_ref["sha256"],c.digest(current),route,token)
 except BaseException:
  os.close(fd);raise
def invoke_cpu_stub(prepared,argv,env):
 """Only the exact constant harmless JSON-printing stub may execute in this helper."""
 c.need(prepared.fd>=0 and prepared.production_activated is False,"invalid CPU-only handle")
 b=os.pread(prepared.fd,len(CPU_STUB)+1,0)
 c.need(b==CPU_STUB and prepared.entry_sha256==c.digest(CPU_STUB),
        "CPU fixture executor rejects any nonstub entry, including scientific Native")
 c.need(fcntl.fcntl(prepared.fd,fcntl.F_GET_SEALS)==SEALS,"sealed execution contract")
 # The inherited fd resolves identical sealed bytes despite any later path replacement.
 # Do not execute global_path, entry_ref.path, a shell command string, or a foreign handler.
 return subprocess.run(["/bin/sh","/proc/self/fd/"+str(prepared.fd),*argv],
   env=env,pass_fds=(prepared.fd,),capture_output=True,text=True,timeout=5,check=False)

"""Private single-helper resource/IO adapter; does not launch science."""
import pathlib,json,hashlib,importlib.util,os,time,fcntl,shutil
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';WORK=N/(ID+'_post_epoch4_single768')
LIMIT=768*2**20;HYSTERESIS=128*2**20
CORE_SHA='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def module(p,name,expected):
 assert sha(p)==expected;s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
R10=module(C/'resource_library_copy_v10_pinned.py','resource10','7e5b290e330cbc1fcc845b6a9c7ce3487d181677d117a8d77a31c60d12a42521')
AUTH=module(C/'read_native_foreign_reserve_v1.py','auth','441fec1917c436781cc0aa6e7e0b35f7a9aa0dc019b2fe96540fca27c78a29ba')
SCAN=module(C/'post_app_parallel_v5.py','scan','c6fdc374344f4bb1d9cdec8f396807a9aef8d9b1fcf4741fc8477b18b86a0c2a')
NORMAL=R10.Resources();last=None;last_at=0
def policy(free,reserved,used=0,stage_budget=LIMIT,admission=False):
 floor=5*2**30+reserved+2**30+64*2**20
 required=floor+max(0,stage_budget-used)+(HYSTERESIS if admission else 0)
 return {'floor':floor,'required':required,'PASS':free>=required and used<=LIMIT}
def resources(force=False,stage_budget=0,admission=False):
 global last,last_at
 if force or last is None or time.monotonic()-last_at>=10:
  deadline=time.monotonic()+10
  while True:
   r=NORMAL(True);a=AUTH.snapshot()
   if r['registered_foreign_write_reservations_bytes']==a['sum_all_records_reserved_write_bytes']:break
   assert time.monotonic()<deadline,'registry changed during normal/epoch resource read'
  last={'normal':r,'authority':a};last_at=time.monotonic()
 used=SCAN.tree_size_race_safe(WORK)if WORK.exists()else 0
 free=shutil.disk_usage(N).free;p=policy(free,last['authority']['sum_all_records_reserved_write_bytes'],used,stage_budget,admission)
 assert p['PASS'],('dynamic floor/own remaining stage allowance',p,free,used)
 return dict(last,policy=p,Native_used=used,Native_free=free)
def digest(path,destination=None,expected_bytes=None):
 path=pathlib.Path(path);h=hashlib.sha256();total=0
 lock=open(N/(ID+'_validation_hot_epoch2/AGGREGATE_NAS_READ.lock'),'a')
 out=None
 try:
  if destination is not None:
   destination=pathlib.Path(destination);destination.parent.mkdir(parents=True,exist_ok=True);out=destination.open('xb')
  with path.open('rb')as inp:
   while True:
    fcntl.flock(lock,fcntl.LOCK_EX)
    try:
     b=inp.read(2**20)
     if not b:break
     total+=len(b);assert expected_bytes is None or total<=expected_bytes
     h.update(b)
     if out:out.write(b)
     resources(stage_budget=0)
     R10.adaptive_io_pace(len(b),15*2**20)
    finally:fcntl.flock(lock,fcntl.LOCK_UN)
  if out:out.flush();os.fsync(out.fileno())
 finally:
  if out:out.close()
  lock.close()
 assert expected_bytes is None or total==expected_bytes
 return h.hexdigest()
def save(p,o):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();t=p.with_name(p.name+'.tmp')
 with t.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def replace(p,o):
 p=pathlib.Path(p);t=p.with_name(p.name+'.tmp')
 with t.open('w')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)

"""Derive immutable V7 channel; leave the running V6 engine untouched."""
from pathlib import Path
import hashlib,json
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');src=R/'tools/library_copy.py';raw=src.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='c937d48e3c2ffbcb84d15fa065af89f4b2c119cc554747f3c4749c53051cf261'
s=raw.decode();s=s.replace('CHUNK=128*MIB;RATE=15*MIB','CHUNK=128*MIB;RATE=32*MIB')
s=s.replace('sys.dont_write_bytecode=True',"sys.dont_write_bytecode=True\nSELF_BYTES=P(__file__).read_bytes() if '__file__' in globals() else b''")
s=s.replace('source=P(__file__).read_text();boot=',"source=SELF_BYTES.decode();boot=")
s=s.replace("publish_bytes(bundle/'trace_copy.py',P(__file__).read_bytes(),v)","publish_bytes(bundle/'trace_copy.py',SELF_BYTES,v)")
s=s.replace("lock=(BRIDGE/'.SHARED_SM70_LIBRARY_TARGET.lock').open('a')","lock=(BRIDGE/('.SHARED_SM70_V7_QUAL_TARGET.lock' if testing else '.SHARED_SM70_LIBRARY_TARGET.lock')).open('a')")
start=s.index('_io_pressure_cached=(0,100)');end=s.index('def adaptive_io_pace',start)
s=s[:start]+'''_io_pressure_cached=(0,100)
_block_observation=None
_block_health={'known':False}
def block_health():
 global _block_observation,_block_health
 now=time.monotonic()
 if _block_observation and now-_block_observation[0]<5:return _block_health
 try:
  row=next(line.split() for line in P('/proc/diskstats').read_text().splitlines() if line.split()[2]=='sdf')
  values=list(map(int,row[3:]));previous=_block_observation;_block_observation=(now,values)
  if previous:
   elapsed=now-previous[0];old=previous[1];ops=values[0]-old[0]+values[4]-old[4]
   busy=max(0,values[9]-old[9])/elapsed/10
   await_ms=max(0,values[3]-old[3]+values[7]-old[7])/max(1,ops)
   _block_health={'known':True,'device':'sdf','busy_percent':busy,'await_ms':await_ms,'inflight':values[8]}
 except (OSError,StopIteration,ValueError,IndexError):_block_health={'known':False}
 return _block_health
def adaptive_io_rate(maximum,full=None):
 global _io_pressure_cached
 if full is None:
  now=time.monotonic()
  if now-_io_pressure_cached[0]>=5:
   try:
    line=next(x for x in P('/proc/pressure/io').read_text().splitlines() if x.startswith('full '));full=float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
   except (OSError,StopIteration,ValueError):full=100
   _io_pressure_cached=(now,full)
  full=_io_pressure_cached[1]
 health=block_health()
 if health.get('known') and health['busy_percent']<10 and health['await_ms']<25 and health['inflight']<4:
  return min(maximum,32*MIB)
 return min(maximum,(30 if full<5 else 10 if full<10 else 4 if full<20 else 1)*MIB)
''' +s[end:]
s=s.replace("'IO_policy':'USER_AUTHORIZED_ADAPTIVE_THROTTLE'","'IO_policy':'V7_BLOCK_HEALTH_DISTINGUISHES_NAS_SELF_WAIT','physical_block_health':dict(_block_health)")
compile(s,'library_copy_v7.py','exec');out=R/'tools/library_copy_v7.py'
if out.exists():assert out.read_text()==s,'V7 immutable candidate collision'
else:out.write_text(s)
proof={'status':'CANDIDATE_REQUIRES_QUALIFICATION','engine_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'base_engine_sha256':hashlib.sha256(raw).hexdigest(),'rate_ceiling_MiB_per_second':32,'healthy_local_block_gate':{'device':'sdf','busy_below_percent':10,'await_below_ms':25,'inflight_below':4},'unknown_or_busy_uses_original_PSI_throttle':True,'immutable_process_source_bytes':True,'foreign_processes_and_runtime_unchanged':True,'promotion_only_at_closed_batch_boundary':True}
(R/'control/ENGINE_V7_CANDIDATE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

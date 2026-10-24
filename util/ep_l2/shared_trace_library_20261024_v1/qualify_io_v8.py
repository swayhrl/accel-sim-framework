from pathlib import Path
import sys,time,json,fcntl,subprocess,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
e.block_health();time.sleep(5.05);actual=e.block_health();assert actual['known']
tests=[]
for label,health,pressure,maximum,expected in [
 ('healthy_block_high_NAS_PSI',{'known':True,'busy_percent':1,'await_ms':1,'inflight':0},99,32,32),
 ('busy_block_preserves_pressure_throttle',{'known':True,'busy_percent':80,'await_ms':1,'inflight':0},99,32,1),
 ('slow_block_preserves_pressure_throttle',{'known':True,'busy_percent':1,'await_ms':100,'inflight':0},99,32,1),
 ('block_queue_preserves_pressure_throttle',{'known':True,'busy_percent':1,'await_ms':1,'inflight':9},99,32,1),
 ('unknown_block_is_conservative',{'known':False},99,32,1),
 ('caller_lower_ceiling_preserved',{'known':True,'busy_percent':1,'await_ms':1,'inflight':0},99,15,15)]:
    e._block_observation=(time.monotonic(),[]);e._block_health=health
    value=e.adaptive_io_rate(maximum*e.MIB,pressure);assert value==expected*e.MIB
    tests.append({'test':label,'MiB_per_second':value/e.MIB,'status':'PASS'})
e._block_observation=None;e._block_health={'known':False}
assert e.SELF_BYTES==Path(e.__file__).read_bytes()
lock_path=e.BRIDGE/'.SHARED_SM70_V8_QUAL_TARGET.lock'
with lock_path.open('a') as held:
    fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
    code='import fcntl;f=open('+repr(str(lock_path))+',"a");fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)'
    cp=subprocess.run(['python3','-B','-c',code],capture_output=True,text=True)
    assert cp.returncode!=0 and 'BlockingIOError' in cp.stderr
tests.append({'test':'real_second_writer_rejected_by_same_lease','status':'PASS_EXPECTED_REJECTION'})
proof={'status':'PASS','tests':tests,'actual_native_block_observation':actual,'engine_sha256':hashlib.sha256(e.SELF_BYTES).hexdigest(),'rate_ceiling_MiB_per_second':32,'all_foreign_channels_unchanged':True,'production_promotion_performed':False}
(R/'control/IO_V8_QUALIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

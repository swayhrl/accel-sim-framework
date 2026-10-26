#!/usr/bin/env python3
"""V3 true native CPU completion, compression/version, bitmap oracle and synthetic65 tests."""
import pathlib,sys,os,json,time,hashlib,lzma,gzip,copy,random,resource,contextlib,gc,collections
D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(D))
os.sched_setaffinity(0,{0,1});os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
import sm70_decoder_stream_v3 as A
from compact_completion_v3 import CompactWarpCompletion as State,MAX_KEYS,MAX_STATE_BYTES
tests=[];started=time.time()
PAIRS=[('EP','EP_R5'),('DTC','DTC_DM'),('DTC','DTC_DH'),('DTC','DTC_CM'),('DTC','DTC_CH')]
def mark(name,**kw):tests.append(dict(case=name,PASS=True,**kw))
def reject(name,fn):
 try:fn()
 except (ValueError,RuntimeError,KeyError,TypeError,EOFError,lzma.LZMAError)as e:mark(name,rejected=True,reason=str(e));return
 raise AssertionError('false accepted '+name)
def header(version=3,li=0,grid=(1,1,1),threads=2):
 return ('-kernel name = V3_SYNTHETIC_ONLY\n-kernel id = 1\n-grid dim = (%d,%d,%d)\n-block dim = (%d,1,1)\n-shmem = 0\n-nregs = 8\n-binary version = 70\n-cuda stream id = 0\n-shmem base_addr = 0x40000000\n-local mem base_addr = 0x50000000\n-accelsim tracer version = %d\n-enable lineinfo = %d\n#traces format = synthetic only\n'%(*grid,threads,version,li))
def rec(pc,mask,op='IADD3'):
 return '%x %x '%(pc,mask)+('0 EXIT 0 0 0'if op=='EXIT'else'1 R1 IADD3 2 R2 R3 0 0')
def lines(records,version,li,coord=(0,0,0),warp=0):
 pre=('%d %d %d %d '%(*coord,warp)if version<3 else'')+('123 'if li else'')
 return ''.join(pre+r+'\n'for r in records)
def payload(records,kind='traceg',v=3,li=0,threads=2,grid=(1,1,1)):
 h=header(v,li,grid,threads)
 if kind=='traceg':return (h+'#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\ninsts = '+str(len(records))+'\n'+lines(records,v,li)+'#END_TB\n').encode()
 return (h+lines(records,v,li)).encode()
def meta(b,cfg,kind='traceg',enc='text'):
 return dict(profile='EP'if cfg=='EP_R5'else'DTC',configuration_profile=cfg,kind=kind,compression=enc,size=len(b),sha256=hashlib.sha256(b).hexdigest(),max_decoded_bytes=2**28,max_state_keys=MAX_KEYS,max_state_bytes=MAX_STATE_BYTES)
def run(s,b,kind='traceg',enc='text',chunk=7):
 o=s.begin(meta(b,s.configuration_profile,kind,enc))
 for i in range(0,len(b),chunk):o.feed(b[i:i+chunk])
 r=o.end();assert o.state is None and o.decoder is None;return r
def fail_native(name,b,profile,cfg,kind='traceg',enc='text'):
 with A.Session(profile,cfg)as s:reject(name,lambda:run(s,b,kind,enc))
positive=[rec(0,3),rec(16,3),rec(32,3,'EXIT')]
diverge=[rec(0,3),rec(16,1,'EXIT'),rec(32,2),rec(48,2,'EXIT')]
for profile,cfg in PAIRS:
 with A.Session(profile,cfg)as s:
  for v in range(5):
   for li in [0,1]:
    plain=payload(diverge,v=v,li=li)
    for enc,b in [('text',plain),('xz',lzma.compress(plain)),('gzip',gzip.compress(plain))]:
     r=run(s,b,enc=enc)
     assert r['records']==4 and r['physical_lane_completion']['physical_lanes_exited']==2 and r['physical_lane_completion']['fully_exited_warps']==1
     mark(cfg+':traceg_v%d_li%d_%s_partial_divergence'%(v,li,enc))
  for v in range(3):
   for li in [0,1]:
    plain=payload(diverge,kind='trace',v=v,li=li)
    for enc,b in [('text',plain),('xz',lzma.compress(plain)),('gzip',gzip.compress(plain))]:
     r=run(s,b,kind='trace',enc=enc);assert r['physical_lane_completion']['physical_lanes_exited']==2
     mark(cfg+':legacy_raw_v%d_li%d_%s_partial_divergence'%(v,li,enc))
  for label,records in [
   ('Root_positive_full_exit',positive),
   ('zero_mask_EXIT_no_credit_before_real_exits',[rec(0,3),rec(16,0,'EXIT'),rec(32,1,'EXIT'),rec(48,2,'EXIT')]),
   ('zero_mask_after_all_exit_is_no_active_metadata',[rec(0,3,'EXIT'),rec(16,0)]),
   ('other_live_lane_can_continue',[rec(0,1,'EXIT'),rec(16,2),rec(32,2,'EXIT')])]:
   r=run(s,payload(records));assert r['physical_lane_completion']['physical_lanes_exited']==2;mark(cfg+':'+label)
 negatives=[
  ('Root_missing_EXIT_lane',[rec(0,3),rec(16,3),rec(32,1,'EXIT')]),
  ('premature_no_EXIT',[rec(0,3),rec(16,3)]),
  ('active_revival_after_exit',[rec(0,1,'EXIT'),rec(16,3),rec(32,2,'EXIT')]),
  ('duplicate_reEXIT_lane',[rec(0,1,'EXIT'),rec(16,1,'EXIT'),rec(32,2,'EXIT')]),
  ('zero_mask_EXIT_cannot_complete',[rec(0,3),rec(16,0,'EXIT')]),
  ('outside_physical_lane',[rec(0,7),rec(16,3,'EXIT')])]
 for label,records in negatives:
  fail_native(cfg+':'+label,payload(records),profile,cfg)
  for v in [0,1,2]:fail_native(cfg+':raw_v%d_'%v+label,payload(records,kind='trace',v=v),profile,cfg,kind='trace')
 for v in [3,4]:fail_native(cfg+':raw_version_without_inline_CTA_rejected_v%d'%v,payload(positive,kind='trace',v=v),profile,cfg,kind='trace')
 plain=payload(positive)
 fail_native(cfg+':missing_TB_EOF',plain.replace(b'#END_TB\n',b''),profile,cfg)
 fail_native(cfg+':final_newline_missing',plain[:-1],profile,cfg)
 fail_native(cfg+':declared_instcount_mismatch',plain.replace(b'insts = 3',b'insts = 4'),profile,cfg)
 fail_native(cfg+':duplicate_CTA',plain+plain.split(b'#traces format = synthetic only\n')[1],profile,cfg)
 dupe=plain.replace(b'#END_TB\n',b'warp = 0\ninsts = 1\n40 3 0 EXIT 0 0 0\n#END_TB\n')
 fail_native(cfg+':duplicate_warp',dupe,profile,cfg)
 fail_native(cfg+':missing_second_physical_warp',payload([rec(0,0xffffffff,'EXIT')],threads=33),profile,cfg)
 fail_native(cfg+':unknown_compression',plain,profile,cfg,enc='zstd')
 fail_native(cfg+':unknown_large_integer_grid',plain.replace(b'(1,1,1)',b'(99999999999999999999999,1,1)',1),profile,cfg)
 fail_native(cfg+':malformed_negative_mask',plain.replace(b'0 3 1 R1',b'0 -1 1 R1',1),profile,cfg)
 broken=bytearray(gzip.compress(plain));broken[-5]^=1
 with A.Session(profile,cfg)as s:
  try:run(s,bytes(broken),enc='gzip')
  except Exception as e:mark(cfg+':gzip_CRC_corruption',rejected=True,reason=str(e))
  else:raise AssertionError('gzip corrupt accepted')
# All version encodings were real native parsed/decoded. Below is independent small state oracle only.
rng=random.Random(20261027);oracle_events=0
for blocks in [1,2,7,8,9,31,32,33,64]:
 for threads in [1,2,31,32,33,65]:
  state=State((blocks,1,1),(threads,1,1),10000,MAX_STATE_BYTES);refmask={};ctas=set();warps=set()
  order=[(c,w)for c in range(blocks)for w in range((threads+31)//32)];rng.shuffle(order)
  for c,w in order:
   key=state.touch_warp((c,0,0),w);ctas.add(c);warps.add((c,w));physical=(1<<min(32,threads-w*32))-1;refmask[(c,w)]=0
   live=physical
   while live:
    bit=live&-live
    state.apply(key,live,'IADD3');assert state.exit_masks[key]==refmask[(c,w)]
    state.apply(key,bit,'EXIT');refmask[(c,w)]|=bit;live&=~bit;oracle_events+=2
    assert state.exit_masks[key]==refmask[(c,w)] and state.seen_ctas==len(ctas)and state.seen_warps==len(warps)
   state.require_warp_complete(key)
  state.finish();assert state.complete_warps==len(warps)
mark('small_reference_tuple_dict_oracle_test_only',geometry_cases=54,events=oracle_events)
def rss():return int(next(x.split()[1]for x in pathlib.Path('/proc/self/status').read_text().splitlines()if x.startswith('VmRSS:')))*1024
before=rss();large=[State((MAX_KEYS,1,1),(1,1,1),MAX_KEYS,MAX_STATE_BYTES)for _ in range(5)];after=rss()
summaries=[]
for state in large:
 for c in [0,7,8,MAX_KEYS-1]:
  key=state.touch_warp((c,0,0),0);state.apply(key,1,'EXIT');state.require_warp_complete(key)
 reject('large_partial_bitmap_does_not_imply_full_grid',state.finish);summaries.append(state.summary())
assert sum(x['array_payload_bytes']for x in summaries)==170_000_000
reject('max_keys8Mplus1_rejected_before_allocate',lambda:State((MAX_KEYS+1,1,1),(1,1,1),MAX_KEYS,MAX_STATE_BYTES))
reject('state_byte_budget_exact1short_rejected',lambda:State((MAX_KEYS,1,1),(1,1,1),MAX_KEYS,33_999_999))
reject('bool_state_key_limit',lambda:State((1,1,1),(1,1,1),True,MAX_STATE_BYTES))
reject('bitmap_out_of_range',lambda:large[0].touch_cta((MAX_KEYS,0,0)))
reject('state_reexit_covered_lane',lambda:large[0].apply(0,1,'EXIT'))
mark('five_actual8M_compact_arrays_memory_measurement',payload_bytes=170_000_000,RSS_before=before,RSS_after=after,RSS_delta=after-before,profiles=summaries)
del large;gc.collect()
# Same previously frozen synthetic65MiB object, one NAS read broadcasts to all5 newV3 sessions.
C=D.parent/'sm70_native_decoder_component_prepare_20261027_v1';info=json.loads((C/'SYNTHETIC_SOURCE_MANIFEST_V1.json').read_bytes());path=pathlib.Path(info['path'])
need_path=path==C/'SYNTHETIC_ONLY_65MiB.traceg'and info['synthetic_only']is True
assert need_path and info['sha256']=='96424db004ca27217ff8fdaf13602c522cbc230ac2dbf185e666bd28e4d7d93d'
results=[];streamhash=hashlib.sha256();n=0;pace=time.monotonic()
with contextlib.ExitStack()as stack:
 objects=[]
 for profile,cfg in PAIRS:
  s=stack.enter_context(A.Session(profile,cfg));m=meta(b'x',cfg);m.update(size=info['size'],sha256=info['sha256'],max_decoded_bytes=info['size']);objects.append(s.begin(m))
 with path.open('rb',buffering=0)as f:
  fd_before=os.fstat(f.fileno())
  while True:
   b=f.read(2**20)
   if not b:break
   n+=len(b);streamhash.update(b)
   for o in objects:o.feed(b)
   delay=n/(8*2**20)-(time.monotonic()-pace)
   if delay>0:time.sleep(delay)
  fd_after=os.fstat(f.fileno())
 assert (fd_before.st_dev,fd_before.st_ino,fd_before.st_size,fd_before.st_mtime_ns,fd_before.st_ctime_ns)==(fd_after.st_dev,fd_after.st_ino,fd_after.st_size,fd_after.st_mtime_ns,fd_after.st_ctime_ns)
 assert n==info['size']and streamhash.hexdigest()==info['sha256']
 for o in objects:
  r=o.end();assert r['actual_native_decoder_records']==1041 and r['literal_native_bytes_sha256']==r['decoded_text_sha256']==info['sha256']and r['physical_lane_completion']['physical_lanes_exited']==32
  results.append(r);mark(r['configuration_profile']+':same_synthetic65MiB_midopcode64MiB_completion')
out=dict(schema='SM70_STREAM_COMPLETION_V3_REAL_CPU_FIXTURES_V1',PASS=True,case_count=len(tests),tests=tests,synthetic65_results=results,all_payload_synthetic=True,new_real_trace_or_header_read=False,physical_Native_or_GPU_or_model_cycle_executed=False,source_CPP_decoder_configuration_changed=False,small_oracle_events=oracle_events,five_max_grid_profile_payload_bytes=170_000_000,five_max_grid_RSS_before=before,five_max_grid_RSS_after=after,elapsed_seconds=time.time()-started,completed_unix=time.time())
(D/'COMPLETION_CPU_RELEASE_RESULT_V3.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(PASS=True,cases=len(tests),oracle_events=oracle_events,elapsed=out['elapsed_seconds'],RSS_delta=after-before)))

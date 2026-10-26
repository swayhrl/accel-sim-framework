#!/usr/bin/env python3
"""Real liblzma resource gate experiments, actual fullV3 decoder positives, no physical Native."""
import pathlib,sys,os,resource,time,json,hashlib,lzma,gc,contextlib,subprocess
D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(D))
os.sched_setaffinity(0,{0,1});os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30))
import sm70_decoder_stream_v3 as A
from format_envelope_v3 import StreamResourceHold
C=D.parent/'sm70_native_decoder_component_prepare_20261027_v1';info=json.loads((C/'SYNTHETIC_SOURCE_MANIFEST_V1.json').read_bytes());source=pathlib.Path(info['path'])
assert info['synthetic_only']is True and source==C/'SYNTHETIC_ONLY_65MiB.traceg'
M=2**20;PAIRS=[('EP','EP_R5'),('DTC','DTC_DM'),('DTC','DTC_DH'),('DTC','DTC_CM'),('DTC','DTC_CH')]
def rss(pid='self'):
 try:return int(next(x.split()[1]for x in pathlib.Path('/proc',str(pid),'status').read_text().splitlines()if x.startswith('VmRSS:')))*1024
 except (OSError,StopIteration):return None
def ref(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def dictionary(xz):
 assert xz[:6]==b'\xfd7zXZ\x00'and xz[13]&3==0 and xz[14]==0x21 and xz[15]==1
 prop=xz[16];assert prop<=40
 return (2|(prop&1))<<(prop//2+11)if prop<40 else 0xffffffff
cases=[];compression=[];bodies={}
for preset in [6,9]:
 before=rss();t=time.time();enc=lzma.LZMACompressor(format=lzma.FORMAT_XZ,preset=preset);h=hashlib.sha256();n=0;parts=[];pace=time.monotonic()
 with source.open('rb',buffering=0)as f:
  while True:
   b=f.read(M)
   if not b:break
   h.update(b);n+=len(b);parts.append(enc.compress(b))
   delay=n/(8*M)-(time.monotonic()-pace)
   if delay>0:time.sleep(delay)
 parts.append(enc.flush());del enc;gc.collect()
 xz=b''.join(parts);del parts
 assert n==info['size']and h.hexdigest()==info['sha256']
 p=D/('SYNTHETIC65_PRESET%d.traceg.xz'%preset);p.write_bytes(xz);bodies[preset]=xz
 dictionary_bytes=dictionary(xz);assert dictionary_bytes==(8*M if preset==6 else 64*M)
 compression.append(dict(preset=preset,source_sha=info['sha256'],XZ_ref=ref(p),actual_LZMA2_dictionary_bytes=dictionary_bytes,RSS_before=before,RSS_after_encoder_freed=rss(),process_peak_RSS=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,seconds=time.time()-t))
def full_liblzma_accept(xz,limit):
 dec=lzma.LZMADecompressor(memlimit=limit);h=hashlib.sha256();n=0
 try:
  part=dec.decompress(xz,max_length=M)
  while True:
   h.update(part);n+=len(part)
   if dec.eof:break
   assert not dec.needs_input
   part=dec.decompress(b'',max_length=M)
 except lzma.LZMAError as e:
  if'Memory usage limit exceeded'in str(e):return False
  raise
 assert not dec.unused_data and n==info['size']and h.hexdigest()==info['sha256']
 return True
for preset,xz in bodies.items():
 low,high=1,256*M//1024
 while low<high:
  mid=(low+high)//2
  if full_liblzma_accept(xz,mid*1024):high=mid
  else:low=mid+1
 threshold=low*1024
 assert full_liblzma_accept(xz,threshold)and not full_liblzma_accept(xz,threshold-1024)
 compression[[6,9].index(preset)]['full_EOF_liblzma_required_memlimit_interval_bytes']=[threshold-1024+1,threshold]
 assert threshold>dictionary(xz)
cases.append(dict(case='real_full_EOF_memory_gate_is_dictionary_plus_overhead',PASS=True))
def all5(preset,limit):
 xz=bodies[preset];before=rss();peak=before;child_peak=0;results=[];limits_before=resource.getrlimit(resource.RLIMIT_AS)
 with contextlib.ExitStack()as stack:
  objects=[];sessions=[]
  for profile,cfg in PAIRS:
   s=stack.enter_context(A.Session(profile,cfg,parent_budget_bytes=2*2**30));sessions.append(s)
   assert resource.getrlimit(resource.RLIMIT_AS)==limits_before
   meta=dict(profile=profile,configuration_profile=cfg,kind='traceg',compression='xz',size=len(xz),sha256=hashlib.sha256(xz).hexdigest(),max_decoded_bytes=info['size'],max_state_keys=8_000_000,max_state_bytes=40*M)
   if limit is not None:meta['max_xz_decoder_bytes']=limit
   objects.append(s.begin(meta))
  for start in range(0,len(xz),1024):
   b=xz[start:start+1024]
   for o in objects:
    o.feed(b);peak=max(peak,rss());child_peak=max(child_peak,sum(rss(s.p.pid)or 0 for s in sessions)+sum(rss(s.p2.pid)or 0 for s in sessions))
  for o in objects:
   r=o.end();assert r['actual_native_decoder_records']==1041 and r['decoded_text_sha256']==info['sha256']and r['physical_lane_completion']['physical_lanes_exited']==32;results.append(r)
 assert resource.getrlimit(resource.RLIMIT_AS)==limits_before
 return dict(preset=preset,configured_memlimit=64*M if limit is None else limit,profiles=5,RSS_before=before,parent_peak_RSS_observed=peak,owned10_CPP_processes_total_RSS_peak_sampled=child_peak,parent_RLIMIT_AS_before_after_unchanged=list(limits_before),records_each=1041,decoded_SHA=info['sha256'],metadata_SHA_by_profile={r['configuration_profile']:r['decoded_metadata_sha256']for r in results})
positives=[all5(6,None),all5(9,128*M),all5(9,256*M)]
for p in positives:cases.append(dict(case='preset%d_all5_complete_with_explicit_bound%d'%(p['preset'],p['configured_memlimit']),PASS=True))
for preset,limit in [(6,M),(9,64*M)]:
 for profile,cfg in PAIRS:
  with A.Session(profile,cfg)as s:
   xz=bodies[preset];meta=dict(profile=profile,configuration_profile=cfg,kind='traceg',compression='xz',size=len(xz),sha256=hashlib.sha256(xz).hexdigest(),max_decoded_bytes=info['size'])
   if preset==6:meta['max_xz_decoder_bytes']=limit
   o=s.begin(meta)
   try:o.feed(xz)
   except StreamResourceHold as e:assert e.code=='SM70_STREAM_RESOURCE_HOLD_XZ_MEMORY';cases.append(dict(case=cfg+':preset%d_approved_limit%d_insufficient_RESOURCE_HOLD'%(preset,limit),PASS=True,not_ISA_unsupported=True,code=e.code))
   else:raise AssertionError('insufficient memory gate accepted')
for invalid in [0,-1,True,257*M,float('inf')]:
 with A.Session('DTC','DTC_DH')as s:
  b=bodies[6];meta=dict(profile='DTC',configuration_profile='DTC_DH',kind='traceg',compression='xz',size=len(b),sha256=hashlib.sha256(b).hexdigest(),max_decoded_bytes=info['size'],max_xz_decoder_bytes=invalid)
  try:s.begin(meta)
  except ValueError:cases.append(dict(case='invalid_decoder_budget_'+str(invalid),PASS=True,rejected=True))
  else:raise AssertionError('bad memory policy')
before=resource.getrlimit(resource.RLIMIT_AS)
try:A.Session('DTC','DTC_DH',parent_budget_bytes=M)
except ValueError:cases.append(dict(case='readonly_parent_budget_mismatch_does_not_mutate_caller',PASS=True))
else:raise AssertionError('declaration without cap')
assert resource.getrlimit(resource.RLIMIT_AS)==before
# This dedicated child alone establishes a lower limit; Session must leave it alone.
script="import resource,sys;sys.path.insert(0,"+repr(str(D))+");import sm70_decoder_stream_v3 as A;resource.setrlimit(resource.RLIMIT_AS,(1073741824,2147483648));before=resource.getrlimit(resource.RLIMIT_AS);s=A.Session('DTC','DTC_DH',parent_budget_bytes=2147483648);assert resource.getrlimit(resource.RLIMIT_AS)==before;s.close();assert resource.getrlimit(resource.RLIMIT_AS)==before;print('unchanged lower caller limit')"
r=subprocess.run([sys.executable,'-B','-c',script],capture_output=True,text=True,timeout=15);assert r.returncode==0,r.stderr
cases.append(dict(case='actual_Session_preserves_existing_lower1GiB_caller_limit',PASS=True,stdout=r.stdout))
out=dict(schema='SM70_V3_REAL_XZ_RESOURCE_MEMORY_POLICY_FIXTURES_V1',PASS=True,case_count=len(cases),cases=cases,compression=compression,positive_five_profile_runs=positives,default_memlimit_bytes=64*M,maximum_explicit_memlimit_bytes=256*M,no_unbounded_or_auto_fallback=True,compressed_payload_all_synthetic=True,new_real_trace_or_header_read=False,physical_Native_or_GPU_or_model_called=False,parent_budget_measurement_scope='Dedicated test parent2GiB plus sampled separate native CPU frontend processes. This excludes R5 catalog/proof objects and is not a full library parent-budget proof.',full_state_five_profile_payload_bytes=170_000_000,decompression_five_profile_max_approved_memusage_bytes=5*256*M,these_two_items_are_not_total_process_RAM=True,completed_unix=time.time())
(D/'XZ_MEMORY_POLICY_RELEASE_RESULT_V3.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(PASS=True,cases=len(cases),compression=compression,positive_RSS=[p['parent_peak_RSS_observed']for p in positives])))

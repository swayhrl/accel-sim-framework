"""Derive a bounded verification pipeline without changing running V7 bytes."""
from pathlib import Path
import hashlib,json
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
raw=(R/'tools/library_copy_v7.py').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='5dde70e17b4efae4fca4aa5baee81c2aae4083342a72e1987908107ca6a45a90'
s=raw.decode().replace('import pathlib,os,sys,json,hashlib,struct,time,fcntl,subprocess,shlex,importlib.util,stat','import pathlib,os,sys,json,hashlib,struct,time,fcntl,subprocess,shlex,importlib.util,stat,threading\nfrom concurrent.futures import ThreadPoolExecutor\nfrom collections import deque')
s=s.replace("'.SHARED_SM70_V7_QUAL_TARGET.lock'","'.SHARED_SM70_V8_QUAL_TARGET.lock'")
s=s.replace('def __init__(self,testing=False):self.last=0;self.last_value=None;self.testing=testing;self.samples=[]','def __init__(self,testing=False):self.last=0;self.last_value=None;self.testing=testing;self.samples=[];self.mutex=threading.RLock()')
s=s.replace(' def __call__(self,force=False):\n  if not force',' def __call__(self,force=False):\n  with self.mutex:return self._checked(force)\n def _checked(self,force=False):\n  if not force')
old=" p=spawn_sender(manifest,skip,testing);ends=[];count_ranges=0\n"
new=""" p=spawn_sender(manifest,skip,testing);ends=[];count_ranges=0
 # Exactly one frame receiver and one source sender retain the original leases.
 # Two workers only verify distinct closed chunks; at most three chunks can be
 # pending. They never receive source frames, assemble trees, or publish COMMIT.
 pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix='closed_chunk_SHA')
 pending=deque();next_offsets=dict(skip);peak_pending=0
 def verify_closed(partial,dest,folder,leaf,c):
  need(hash_file(partial,gate=g)==c['sha256'],'closed chunk full SHA mismatch')
  v.rename_noreplace(partial,dest)
  need(hash_file(dest,gate=g)==c['sha256'],'published range reopen SHA')
  publish_bytes(folder/(leaf+'.json'),canon(c),v)
  return c
 def drain_one():
  nonlocal newbytes,count_ranges
  name,future=pending.popleft();c=future.result()
  ranges[name].append(c);newbytes+=c['size'];count_ranges+=1
  emit({'event':'RANGE_VERIFIED','asset':manifest['primary_asset_id'],'file':name,'verified_end':c['offset']+c['size'],'new_payload_bytes':newbytes})
  if inject_after_ranges is not None and count_ranges>=inject_after_ranges:raise RuntimeError('INJECTED_BOUNDED_OWN_RANGE_CRASH')
"""
assert s.count(old)==1;s=s.replace(old,new)
old="need(event['offset']==sum(c['size'] for c in ranges[name]) and 0<event['size']<=CHUNK,'range offset/size changed')"
assert s.count(old)==1;s=s.replace(old,"need(event['offset']==next_offsets[name] and 0<event['size']<=CHUNK,'range offset/size changed')")
start=s.index("   need(h.hexdigest()==event['sha256'] and hash_file(partial,gate=g)")
end=s.index("  rc=p.wait(timeout=30);",start)
s=s[:start]+"""   need(h.hexdigest()==event['sha256'],'received chunk full SHA mismatch')
   next_offsets[name]+=event['size']
   pending.append((name,pool.submit(verify_closed,partial,dest,folder,leaf,c)))
   peak_pending=max(peak_pending,len(pending))
   if len(pending)>=3:drain_one()
  while pending:drain_one()
"""+s[end:]
s=s.replace("  p.stdout.close();p.stderr.close()\n","  p.stdout.close();p.stderr.close()\n  pool.shutdown(wait=True)\n",1)
s=s.replace("'reused_verified_range_bytes':resumed,'Source_full_SHA_matches'","'reused_verified_range_bytes':resumed,'bounded_verification_pipeline':{'workers':2,'pending_chunk_limit':3,'observed_peak_pending':peak_pending,'source_and_target_writer_leases':1,'closed_and_published_chunk_full_SHA_preserved':True},'Source_full_SHA_matches'")
compile(s,'library_copy_v8.py','exec')
out=R/'tools/library_copy_v8.py'
if out.exists():assert out.read_text()==s,'immutable V8 collision'
else:out.write_text(s)
proof={'status':'CANDIDATE_REQUIRES_QUALIFICATION','engine_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'base_engine_sha256':hashlib.sha256(raw).hexdigest(),'verification_workers':2,'pending_closed_chunk_limit':3,'source_rate_ceiling_MiB_s':32,'each_verifier_read_ceiling_MiB_s':30,'single_receiver_and_source_leases_preserved':True,'source_eof_and_both_closed_chunk_hashes_and_tree_hashes_preserved':True,'active_V7_unchanged':True,'promotion_only_at_closed_batch_boundary':True}
(R/'control/ENGINE_V8_CANDIDATE.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))

import os,json,stat,datetime,hashlib,re,time,subprocess
from pathlib import Path
O=Path(__file__).parent; old=json.load(open(O/'census/SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json')); ids=[]; receipts={}; at=datetime.datetime.now(datetime.timezone.utc).isoformat()
def st(p):
 s=os.lstat(p);return dict(device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,size=s.st_size,allocated_bytes=s.st_blocks*512,mode_octal=oct(stat.S_IMODE(s.st_mode)),uid=s.st_uid,gid=s.st_gid,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,is_regular=stat.S_ISREG(s.st_mode),is_symlink=stat.S_ISLNK(s.st_mode))
for i,pair in enumerate(old['shards'],1):
 for kind in ['source','destination']:
  p=pair[kind]; actual=st(p); prev=pair[kind+'_stat']; changes={k:dict(previous=v,current=actual[k]) for k,v in prev.items() if k in actual and actual[k]!=v}; parents=[]; path=Path(p)
  for par in reversed(path.parents):
   s=os.lstat(par)
   if stat.S_ISLNK(s.st_mode):parents.append(dict(path=str(par),target=os.readlink(par)))
  actual.update(pair_id=i,set='MODEL_SOURCE' if kind=='source' else 'OUTBOUND_PACKAGE',package='P2' if '/C16_GPU_PACKAGE_P2_' in pair['destination'] else 'P3',path=p,canonical_path=os.path.realpath(p),parent_symlinks=parents,historical_payload_sha256=pair['prior_payload_sha256'],current_payload_sha256=None,current_payload_hashed=False,prior_census_metadata_changes=changes,prior_metadata_exact_match=not changes,release_authority='NOT_GRANTED',owner_use_decision='HOLD_PENDING_AUTHORITATIVE_CONSUMER_JOIN');ids.append(actual)
 for k in ['package_receipt','source_receipt']:
  p=pair[k]
  if p not in receipts:
   b=Path(p).read_bytes();j=json.loads(b);receipts[p]=dict(path=p,current_sha256=hashlib.sha256(b).hexdigest(),historical_receipt_sha256=pair[k+'_sha256'],current_matches_prior=hashlib.sha256(b).hexdigest()==pair[k+'_sha256'],stat=st(p),json=j)
assert len(ids)==12 and len({r['path'] for r in ids})==12
assert all(r['is_regular'] and not r['is_symlink'] and not r['parent_symlinks'] for r in ids)
(O/'exact_identities.json').write_text(json.dumps(dict(at_utc=at,files=ids,receipt_records=list(receipts.values()),payload_content_reads=0),indent=2)+'\n')
for k in ['MODEL_SOURCE','OUTBOUND_PACKAGE']:print(k,sum(r['allocated_bytes'] for r in ids if r['set']==k),'bytes','drift',sum(not r['prior_metadata_exact_match'] for r in ids if r['set']==k))
print('receipt SHA matches',sum(r['current_matches_prior'] for r in receipts.values()),'/',len(receipts))
# Bounded one-shot process view; no commands, environment secrets or private prompts are published.
out=[]; t=time.monotonic()
for n in os.listdir('/proc'):
 if not n.isdigit():continue
 try:
  d=Path('/proc')/n;raw=(d/'cmdline').read_bytes();args=raw.decode(errors='replace').replace('\0',' '); ps=(d/'stat').read_text().rsplit(')',1)[1].split();cwd=os.readlink(d/'cwd');exe=os.readlink(d/'exe');paths=sorted(set(re.findall(r'/(?:workspace|tmp|root/(?:data|share))/[A-Za-z0-9_./+@:=,~-]+',args)));fds=[]
  for fd in os.listdir(d/'fd')[:512]:
   try:
    target=os.readlink(d/'fd'/fd)
    if target.startswith(('/workspace/','/tmp/','/root/data/','/root/share/')):
     info=(d/'fdinfo'/fd).read_text();flags=next((l.split()[1] for l in info.splitlines() if l.startswith('flags:')),None);fds.append(dict(fd=fd,target=target,flags_octal=flags))
   except OSError:pass
  out.append(dict(pid=int(n),start_ticks=ps[19],state=ps[0],uid=os.stat(d).st_uid,cwd=cwd,exe=exe,argv_sha256=hashlib.sha256(raw).hexdigest(),argv_paths=paths,fd_paths=fds,c16_argv_marker=bool(re.search(r'c16|C16',args)),remote_endpoint_markers=sorted(set(re.findall(r'(?<![0-9])(?:10\.[0-9.]+|[A-Za-z0-9_.-]*(?:109|164)[A-Za-z0-9_.-]*)(?![0-9])',args)))[:12]))
 except (OSError,IndexError):pass
 if time.monotonic()-t>12:break
(O/'activity.json').write_text(json.dumps(dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),duration_seconds=time.monotonic()-t,processes=out,snapshot_racy=True,no_match_is_not_future_clearance=True),indent=2)+'\n')
for r in out:
 if r['pid']==280466 or r['c16_argv_marker'] or '/c16' in r['cwd']:print(json.dumps({k:r[k] for k in ['pid','start_ticks','state','cwd','argv_paths']}))

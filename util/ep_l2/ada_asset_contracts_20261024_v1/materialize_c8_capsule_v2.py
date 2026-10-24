"""CPU-only exact cold restore of the c8 engineering capsule and its immutable raw-byte references."""
import argparse,pathlib,hashlib,json,tarfile,os,time,shutil,importlib.util,socket
P=pathlib.Path
OLD_OBJECT='stage_evidence_input_capsule7_109_20261024_v1'
OLD_SHA='f2b875c226456fdf58600a352f47fbff49fb231953c6ae941d0a30455b37c58b'
OLD_MANIFEST='ae10775d059f750237655505783b15f5d6962ef5f5413d1b46070d3430f78211'
VALIDATOR_SHA='7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388'
PRODUCER_SHA='c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352'
RATE=15*2**20
def need(v,m):
 if not v:raise RuntimeError(m)
class LimitedReader:
 def __init__(self,f):self.f=f;self.start=time.monotonic();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.n+=len(b);delay=self.n/RATE-(time.monotonic()-self.start)
  if delay>0:time.sleep(delay)
  return b
def sha(p,limited=False):
 h=hashlib.sha256()
 with p.open('rb')as f:
  r=LimitedReader(f)if limited else f
  for b in iter(lambda:r.read(2**20),b''):h.update(b)
 return h.hexdigest()
def safe_path(root,name):
 pp=pathlib.PurePosixPath(name);need(not pp.is_absolute()and'..'not in pp.parts,'unsafe archive/reference path')
 out=root.joinpath(*pp.parts);need(out.resolve().is_relative_to(root.resolve()),'path escapes owned restore root');return out
def check_object(T,archive_sha,manifest_sha,commit_sha=None):
 need(T.is_dir()and not T.is_symlink(),'object path missing or symlink')
 if commit_sha:need(sha(T/'COMMIT.json')==commit_sha,'COMMIT SHA mismatch')
 need(sha(T/'MANIFEST.json')==manifest_sha,'manifest SHA mismatch')
 c=json.loads((T/'COMMIT.json').read_text());need(c['archive_sha256']==archive_sha and c['manifest_sha256']==manifest_sha,'COMMIT binding mismatch')
 need(sha(T/'CLOSED_READBACK.json')==c['readback_sha256'],'closed readback binding')
 need((T/'payload.tar').stat().st_size<128*2**20,'archive chunk bound')
 need(sha(T/'payload.tar',True)==archive_sha,'full closed tar SHA mismatch')
 m=json.loads((T/'MANIFEST.json').read_text());need(m['source_keep']and m['kind']=='ENGINEERING_STAGE_NOT_FORMAL_WORKLOAD','unexpected engineering disposition')
 expected={x['member']:x for x in m['files']};need(len(expected)==len(m['files']),'duplicate manifest member')
 need(sum(x['identity']['size']for x in expected.values())<128*2**20,'expanded object bound')
 return expected
def stream_verified(T,expected,write_member):
 seen=set()
 with(T/'payload.tar').open('rb')as raw:
  with tarfile.open(fileobj=LimitedReader(raw),mode='r|')as archive:
   for member in archive:
    need(member.isfile()and member.name in expected and member.name not in seen,'nonregular/extra/duplicate tar member')
    row=expected[member.name];need(member.size==row['identity']['size'],'member size mismatch')
    h=hashlib.sha256();target=write_member(member,row)
    if target is not None:target.parent.mkdir(parents=True,exist_ok=True);out=target.open('xb')
    else:out=None
    try:
     with archive.extractfile(member)as inp:
      for b in iter(lambda:inp.read(2**20),b''):
       h.update(b)
       if out:out.write(b)
     if out:out.flush();os.fsync(out.fileno())
    finally:
     if out:out.close()
    need(h.hexdigest()==row['sha256'],'tar member SHA mismatch')
    if target is not None:target.chmod(member.mode&0o777)
    seen.add(member.name)
 need(seen==set(expected),'missing manifest members')
 return len(seen)
def cache_selector(wanted,cache):
 selected=set()
 def choose(member,row):
  if member.name not in wanted or row['sha256']in selected:return None
  selected.add(row['sha256']);return cache/(row['sha256']+'.bin')
 return choose
def verify_launch_function_handles(path):
 entries={};joins=[]
 for line in path.read_text().splitlines():
  t=line.split('\t')
  if t[0]=='LAUNCH_ENTRY':
   need(len(t)==10 and int(t[1])not in entries,'external function-handle entry pairing')
   entries[int(t[1])]=t
  elif t[0]=='LAUNCH_EXIT':
   need(len(t)==10 and int(t[1])in entries,'external function-handle exit pairing')
   e=entries.pop(int(t[1]));need(e[2:7]==t[2:7],'external API/context/stream/function-handle/name changed across launch')
   handle=int(t[5],16);need(0<handle<2**64,'external function handle range')
   joins.append(dict(ordinal=int(t[1]),context=t[3],stream=t[4],function_handle=t[5],function=t[6]))
 need(not entries,'external unclosed function-handle entry')
 return joins

def main():
 a=argparse.ArgumentParser();a.add_argument('object');a.add_argument('destination');a.add_argument('--expected-control-sha',required=True);a.add_argument('--expected-manifest-sha',required=True);a.add_argument('--expected-commit-sha',required=True);v=a.parse_args()
 T=P(v.object);D=P(v.destination)
 need(socket.gethostname()=='huangrulin-sshfs-174'and os.stat('/root/data').st_dev==2128,'wrong Native host/filesystem')
 need(D.is_absolute()and D.resolve().is_relative_to(P('/root/data').resolve())and not D.exists(),'destination must be fresh owned Native root')
 need(shutil.disk_usage(D.parent).free>5*2**30+256*2**20,'Native5GiB floor plus bounded restore headroom')
 control=check_object(T,v.expected_control_sha,v.expected_manifest_sha,v.expected_commit_sha);D.mkdir(exist_ok=False)
 count=stream_verified(T,control,lambda member,row:safe_path(D,member.name))
 root=D/'109/ada_input_capsule_c8_release_20261024_v1';need(root.is_dir(),'unexpected control archive prefix')
 references=json.loads((root/'DURABLE_BLOB_REFERENCES.json').read_text())['all_references']
 need(sum(r['bytes']for r in references)<128*2**20,'raw reference destination bound')
 wanted={};destinations=set()
 for ref in references:
  need(ref['archive_object']==OLD_OBJECT and ref['archive_sha256']==OLD_SHA,'unapproved external object reference')
  need(ref['actual_new_capture_sha256']==ref['sha256']and ref['actual_new_capture_bytes']==ref['bytes'],'new-capture/full-SHA reference mismatch')
  dest=safe_path(root,ref['destination']);need(str(dest)not in destinations and not dest.exists(),'duplicate/existing recovered raw destination');destinations.add(str(dest))
  member=ref['archive_member'];safe_path(D,member)
  if member in wanted:need(wanted[member]['sha256']==ref['sha256'],'conflicting old member reference')
  wanted[member]=ref
 old=T.parent/OLD_OBJECT;old_manifest=check_object(old,OLD_SHA,OLD_MANIFEST);cache=D/'blob_cache';cache.mkdir()
 for name,ref in wanted.items():need(name in old_manifest and old_manifest[name]['sha256']==ref['sha256']and old_manifest[name]['identity']['size']==ref['bytes'],'reference not bound to old manifest')
 old_count=stream_verified(old,old_manifest,cache_selector(wanted,cache))
 for ref in references:
  cached=cache/(ref['sha256']+'.bin');need(cached.stat().st_size==ref['bytes']and sha(cached)==ref['sha256'],'recovered blob cache mismatch')
  dest=safe_path(root,ref['destination']);dest.parent.mkdir(parents=True,exist_ok=True)
  with cached.open('rb')as inp,dest.open('xb')as out:
   for b in iter(lambda:inp.read(2**20),b''):out.write(b)
   out.flush();os.fsync(out.fileno())
  need(sha(dest)==ref['sha256'],'restored destination SHA');dest.chmod(0o444)
 validator=root/'frozen/qualify_input_capsule_v4.py';need(sha(validator)==VALIDATOR_SHA and sha(root/'frozen/producer.so')==PRODUCER_SHA,'frozen final code identity')
 spec=importlib.util.spec_from_file_location('c8_capsule_validator',validator);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);positive={};comparisons={}
 for mode in ['sync','async','random','constant65','vector4m']:
  pair={}
  for kind in ['native_observer','instrumented']:
   A=root/'attempts'/('snapshot7_'+mode+'_'+kind+'_v3_attempt1');result=q.qualify(A);positive[A.name]=dict(bytes=result['total_bytes'],input_identity=result['ordered_input_identity_sha256'],launches=result['lifecycle']['recognized_launch_count'],function_handle_join=verify_launch_function_handles(A/'traces/ada-lifecycle.tsv'));pair[kind]=result['ordered_input_identity_sha256']
  comparisons[mode]='INPUT_IDENTICAL'if pair['native_observer']==pair['instrumented']else'INPUT_DIFF'
 need(all(comparisons[m]=='INPUT_IDENTICAL'for m in ['sync','async','constant65','vector4m'])and comparisons['random']=='INPUT_DIFF','actual cross-run input comparison mismatch')
 rejected=[];negative_expected={x['case']:x['reason']for x in json.loads((root/'frozen/CAPSULE_VALIDATOR_V4R2_NEGATIVE_QUALIFICATION.json').read_text())['negative']}
 for A in sorted((root/'cpu_negative').iterdir()):
  if not A.is_dir():continue
  try:q.qualify(A)
  except Exception as error:
   reason=type(error).__name__+': '+str(error);need(A.name in negative_expected and reason==negative_expected[A.name],'restored negative failed for an unexpected reason '+A.name);rejected.append(A.name)
  else:raise RuntimeError('negative admitted after cold restore '+A.name)
 need(len(rejected)==30,'negative corpus count')
 proof=dict(status='TRUE164_TWO_OBJECT_FULL_MEMBER_SHA_MATERIALIZED_C8_RESTORE_AND_HANDLE_JOIN_PASS',control_object=str(T),control_archive_sha256=v.expected_control_sha,old_raw_object=str(old),old_raw_archive_sha256=OLD_SHA,verified_control_members=count,verified_old_members=old_count,materialized_root=str(D),blob_reference_destinations=len(references),recovered_reference_bytes=sum(r['bytes']for r in references),producer_sha256=PRODUCER_SHA,validator_sha256=VALIDATOR_SHA,positive=positive,comparisons=comparisons,all30_structural_negatives_rejected=rejected,source_keep=True,release_bytes=0,GPU_or_simulator_executed=False,host_namespace=os.readlink('/proc/self/ns/mnt'),native_device=os.stat('/root/data').st_dev,rate_limit_mib_s=15)
 with(D/'MATERIALIZED_C8_RESTORE_PROOF.json').open('x')as f:json.dump(proof,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(proof,indent=2))
if __name__=='__main__':main()

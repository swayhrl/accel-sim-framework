"""Future-private-module JSON IO candidate, no import-time installation.
Atomic no-replace publication preserves exclusive one-start semantics. Bounded
reader retries only JSON decoding while retaining every original transformation.
Persistent malformed content fails with its real path/hash; no cached fallback.
"""
import pathlib,json,hashlib,os,time,uuid,functools
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ALLOWED={R/'tools/l2_native.py',R/'tools/l2_resources.py',R/'tools/l2_results.py',P('/root/data/dtc_failure_repair_20261025_v1/ops/revision20/resource_accounting_v1.py'),P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py')}
MARKER='_SHARED_JSON_PUBLICATION_V1'
def sha(b):return hashlib.sha256(b).hexdigest()
def atomic_exclusive(path,obj):
 p=P(path);data=(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode();tmp=p.with_name('.'+p.name+'.unpublished-'+uuid.uuid4().hex)
 try:
  with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  # link is atomic and fails EEXIST. Never replace a prior INTENT or result.
  os.link(tmp,p);tmp.unlink();fd=os.open(p.parent,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if tmp.exists():tmp.unlink()
def bounded_read(original,path,max_wait=1.0):
 assert 0<max_wait<=2.0
 began=time.monotonic();attempts=0;delay=.005
 while True:
  attempts+=1
  try:return original(path)
  except (json.JSONDecodeError,UnicodeDecodeError)as error:
   if time.monotonic()-began>=max_wait:
    p=P(path)
    try:b=p.read_bytes();detail=dict(path=str(p),bytes=len(b),sha256=sha(b))
    except OSError as e:detail=dict(path=str(p),inspection_error=repr(e))
    raise ValueError('SHARED_JSON_PERSISTENT_INVALID '+json.dumps(dict(detail,attempts=attempts,elapsed_seconds=time.monotonic()-began,original_error=str(error)),sort_keys=True))from error
   time.sleep(min(delay,max(0,max_wait-(time.monotonic()-began))));delay=min(.05,delay*1.5)
def install_private_module(module,expected_pins,max_wait=1.0):
 """Only supplied private module instance and its freshly loaded private children.
 Main must provide immutable source pins; no sys.modules/global-import patch.
 """
 path=P(module.__file__);assert path in ALLOWED and str(path)in expected_pins
 assert sha(path.read_bytes())==expected_pins[str(path)]
 if hasattr(module,MARKER):
  state=getattr(module,MARKER);assert state['max_wait']==max_wait;return state['binding']
 binding=dict(schema='SHARED_JSON_ATOMIC_EXCLUSIVE_BOUNDED_READ_V1',source_sha256=sha(P(__file__).read_bytes()),publication='FSYNC_SAME_DIRECTORY_LINK_NOREPLACE',json_decode_retry_seconds=max_wait,persistent_invalid='FAIL_CLOSED_WITH_PATH_SIZE_SHA_NO_CACHED_VALUE',scientific_completion_rules_unchanged=True)
 state=dict(binding=binding,max_wait=max_wait);setattr(module,MARKER,state)
 if hasattr(module,'read'):
  old=module.read
  @functools.wraps(old)
  def read(path):return bounded_read(old,path,max_wait)
  state['read']=old;module.read=read
 if hasattr(module,'load'):
  oldload=module.load
  def load(name,path):
   child=oldload(name,path)
   if P(child.__file__)in ALLOWED:install_private_module(child,expected_pins,max_wait)
   return child
  state['load']=oldload;module.load=load
 if path==R/'tools/l2_results.py':
  original_put=module.put
  def put(path,obj,exclusive=False):
   if not exclusive:return original_put(path,obj,False)
   P(path).parent.mkdir(parents=True,exist_ok=True);return atomic_exclusive(path,obj)
  state['put']=original_put;module.put=put
 if hasattr(module,'_original_exclusive'):
  original=module._original_exclusive
  assert original.__name__=='exclusive'and P(original.__code__.co_filename)==path
  state['original_exclusive']=original;module._original_exclusive=atomic_exclusive
  # Preserve all original consume/binding/observer wrappers above the leaf.
  oldexclusive=module.exclusive
  def exclusive(path,obj):
   p=P(path)
   if p.name.endswith('.INTENT.json')or p.name in['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:obj=dict(obj,shared_json_publication_binding=binding)
   return oldexclusive(path,obj)
  state['exclusive']=oldexclusive;module.exclusive=exclusive
 return binding

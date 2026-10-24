"""Only SHA IO is adapted; group() is the exact frozen 5d implementation."""
import pathlib,json,sys,importlib.util,hashlib
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
jobpath=pathlib.Path(sys.argv[1]);job=json.loads(jobpath.read_text())
p=C/'stencil768_common_v2.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==job['common_sha256']
s=importlib.util.spec_from_file_location('common768',p);u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
assert u.sha(pathlib.Path(__file__))==job['adapter_sha256']
core=u.module(C/'postprocess_nas_sharded_v4.py','frozen5d',u.CORE_SHA)
raw=pathlib.Path(job['source_raw']);dest=pathlib.Path(job['grouped']);work=pathlib.Path(job['work'])
assert u.B in raw.resolve().parents and u.WORK in work.resolve().parents and u.WORK in dest.resolve().parents
state=json.loads((work/'CHECKPOINT.json').read_text())
assert state['partition_complete']and state['source_sha256']==job['source_sha256']and state['span']==64
assert len(state['groups'])==9 and len(state['partition_members'])==16
assert any('-accelsim tracer version = 7'in h for h in state['header'])
native_sha=core.sha;observed=[]
def pure_sha_io_adapter(path):
 p=pathlib.Path(path)
 if p==raw:
  h=u.digest(p,expected_bytes=job['source_bytes']);assert h==job['source_sha256'];observed.append(h);return h
 assert u.WORK in p.resolve().parents
 return native_sha(p)
core.sha=pure_sha_io_adapter
rec=core.group(raw,dest,work,64,512*2**20,0)
assert len(observed)==1 and rec['status']=='GROUPED_ALL_SHARDS_CRC_PASS'
assert rec['source_sha256']==job['source_sha256']and rec['records']==job['records']
assert rec['ctas']==job['ctas']and rec['warps']==job['warps']
assert dest.stat().st_size<=64*2**20,'closed output exceeded engineering planning allowance; retain, do not promote'
rec.update(adapter_sha256=u.sha(pathlib.Path(__file__)),algorithm_sha256=u.CORE_SHA,
           source_SHA_IO_scope='Only source raw pure SHA delegates to bounded adaptive15MiB helper; no raw Native copy or scientific SASS parse; group algorithm otherwise unchanged',
           copied_checkpoint_complete_frames_before=9,source_original_raw_keep=True)
print(json.dumps(rec))

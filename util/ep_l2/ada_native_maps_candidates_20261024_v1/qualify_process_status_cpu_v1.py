from pathlib import Path
import importlib.util,json,hashlib
r=Path(__file__).parent
spec=importlib.util.spec_from_file_location('status',r/'native_process_status_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Process:
 pid=12345
 def __init__(self,values):self.values=iter(values);self.last=None
 def poll(self):
  try:self.last=next(self.values)
  except StopIteration:pass
  return self.last
results={}
def read_alive():return 'Name: fixture\nVmRSS: 4096 kB\n'
def missing():raise FileNotFoundError('directed terminal exit')
def zombie():return 'Name: fixture\nState: Z (zombie)\n'
assert m.sample_live_rss(Process([None,None]),read_alive)==4194304
results['positive_live_rss']='PASS'
assert m.sample_live_rss(Process([0]),lambda:(_ for _ in ()).throw(AssertionError('must not read exited PID')))is None
results['positive_exited_before_read']='PASS'
assert m.sample_live_rss(Process([None,0]),missing)is None
results['positive_exit_during_status_read']='PASS'
assert m.sample_live_rss(Process([None,0]),zombie)is None
results['positive_zombie_before_rss']='PASS'
assert m.sample_live_rss(Process([None,0]),read_alive)is None
results['positive_exit_after_read']='PASS'
for name,reader in [('negative_live_missing',missing),('negative_live_no_rss',zombie)]:
 try:m.sample_live_rss(Process([None,None]),reader)
 except RuntimeError as error:
  assert 'live process RSS/status unreadable'in str(error);results[name]='EXPECTED_REJECTION'
 else:raise AssertionError('live unreadable accepted')
proof={'CPU_ONLY_NOT_SIMULATOR_APPLICATION':True,'helper_sha256':hashlib.sha256((r/'native_process_status_v1.py').read_bytes()).hexdigest(),'results':results}
p=r/'PROCESS_STATUS_CPU_QUALIFICATION.json';p.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

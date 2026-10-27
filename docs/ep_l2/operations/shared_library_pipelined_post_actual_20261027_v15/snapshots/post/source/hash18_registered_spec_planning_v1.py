"""Readonly local planning adapter for exactly registry-admitted DTC HASH18 SPECs."""
from pathlib import Path
import json,os,hashlib,re,stat,resource
REQ='DTC_HASH_DOWNSTREAM18_20261027_V1'
ROOT=Path('/root/data/dtc_hash_downstream18_20261027_v1')
G=2**30
def need(ok,text):
 if not ok:raise RuntimeError('HASH18_LOCAL_RAM_PROFILE_HOLD_'+text)
class Resolver:
 def __init__(self):self.cache={}
 def data(self,p,expected=None,limit=8*2**20):
  p=Path(p);before=p.stat();need(stat.S_ISREG(before.st_mode)and before.st_size<=limit,'BOUNDED_METADATA')
  b=p.read_bytes();after=p.stat()
  need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'STABLE_METADATA')
  h=hashlib.sha256(b).hexdigest();need(expected is None or h==expected,'REF_SHA')
  return json.loads(b),dict(path=str(p),bytes=len(b),sha256=h)
 def file_pin(self,p,expected):
  p=Path(p);s=p.stat();key=(str(p),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  if key not in self.cache:
   h=hashlib.sha256()
   with p.open('rb')as f:
    for b in iter(lambda:f.read(2**20),b''):h.update(b)
   t=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns),'CODE_CHANGED_DURING_READ')
   self.cache[key]=h.hexdigest()
  need(self.cache[key]==expected,'CODE_CONFIG_INPUT_DRIFT')
  return dict(path=str(p),bytes=s.st_size,sha256=expected)
 def resolve(self,rid,q,cohort,live):
  need(rid==REQ and q['request']==REQ,'EXACT_REQUEST_ONLY')
  need(re.fullmatch(r'E2-DTCHASH18-[0-9a-f]{16}-(CH|DH)-(PQ|P0|PS)-V1',cohort),'EXACT_COHORT')
  path=ROOT/'control/specs'/(cohort+'.json')
  spec,sr=self.data(path,q['admitted_specs'][cohort])
  need(spec['request']==REQ and spec['cohort']==cohort and spec['project']=='DTC'and spec['program']in['ATAX','MVT','BICG'],'EXACT_SPEC_IDENTITY')
  need(spec['estimated_peak_model_RAM_bytes']==4*G and spec['limits']['max_process_tree_rss_bytes']==16*G,'REGISTERED_SPEC_4_16')
  plan,pr=self.data(ROOT/'control/EXECUTION_PLAN.json',q['execution_plan_sha256'])
  engine=self.file_pin(ROOT/'tools/ds18_native.py',q['engine_sha256'])
  pins={x['path']:x['sha256']for x in plan['source_pins']}
  guards=[]
  for p in [ROOT/'tools/ds18_resources.py',ROOT/'tools/ds18_native.py',Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py')]:
   need(str(p)in pins,'RESOURCE_AND_ENGINE_PIN_CHAIN')
   guards.append(self.file_pin(p,pins[str(p)]))
  profile,pfr=self.data(ROOT/'control/BUILD_PROFILE.json',spec['build_profile_sha256'])
  need(profile['estimated_working_set_per_point_bytes']==4*G and plan['build_profile_sha256']==pfr['sha256'],'SAME_APPROVED_BUILD_PROFILE')
  consumed=q['consumed'][cohort];need(consumed['charged']==1 and re.fullmatch(r'[a-f0-9-]{36}',consumed['uuid']),'REGISTERED_LIVE_GENERATION')
  out=ROOT/'DTC/run/results'/consumed['uuid']
  frozen,fr=self.data(out/'DOWNSTREAM_FROZEN_SPEC.json',sr['sha256'])
  need(frozen==spec,'SAME_ACTUAL_FROZEN_SPEC')
  mapping,mr=self.data(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
  pid=live['pid'];ticks=str(live['start_ticks']);need(mapping['pid']==pid and str(mapping['start_ticks'])==ticks,'SAME_APPROVED_PID_TICKS')
  proc=Path('/proc')/str(pid);before=proc.joinpath('stat').read_text().rsplit(')',1)[1].split()
  need(before[19]==ticks and before[0]not in['Z','X','x'],'CURRENT_PID_TICKS')
  argv=[os.fsdecode(x)for x in proc.joinpath('cmdline').read_bytes().split(b'\0')if x]
  expected=[str(ROOT/'common-lib/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(ROOT/'DTC/env/lib'),*spec['native_simulator_argv']]
  need(argv==expected and mapping['cmdline'].strip()==' '.join(expected),'SAME_ACTUAL_ARGV_INPUT_CONFIG')
  binding=mapping['downstream_execution_binding']
  need(binding['request']==REQ and binding['engine_sha256']==engine['sha256']and binding['plan_sha256']==pr['sha256']and binding['profile_sha256']==pfr['sha256']and binding['resource_source_sha256']==pins[str(ROOT/'tools/ds18_resources.py')],'ACTUAL_EXECUTION_PROFILE_BINDING')
  configs=[self.file_pin(x['path'],x['sha256'])for x in spec['configs']]
  binary=next(x for x in spec['runtime_files']if x['actual_realpath']==spec['native_simulator_argv'][0])
  br=self.file_pin(binary['actual_realpath'],binary['sha256']);need(br['sha256']==spec['binary_sha256'],'SAME_MODEL_BINARY')
  actualmaps=proc.joinpath('maps').read_text();need(any(line.split()[-1:]==[str(Path(binary['actual_realpath']).resolve())]for line in actualmaps.splitlines()),'CURRENT_MODEL_IMAGE_MAPPED')
  ib,ir=self.data(spec['input_binding_path'],spec['input_binding_sha256'])
  need(cohort.split('-')[2]==spec['input_digest'][:16],'SAME_ADMITTED_INPUT_DIGEST')
  limits=proc.joinpath('limits').read_text();row=next(l.split()for l in limits.splitlines()if l.startswith('Max address space'))
  need(row[3].isdigit()and row[4].isdigit()and min(int(row[3]),int(row[4]))==16*G,'ACTUAL_ROOT_AS16')
  after=proc.joinpath('stat').read_text().rsplit(')',1)[1].split();need(after[19]==ticks and after[1]==before[1],'CURRENT_IDENTITY_POSTCHECK')
  return dict(schema='ROOT_LOCAL_REGISTERED_SPEC_RAM_PLANNING_V1',request=REQ,cohort=cohort,pid=pid,start_ticks=ticks,estimated_peak_model_RAM_bytes=4*G,max_process_tree_rss_bytes=16*G,spec_ref=sr,frozen_run_spec_ref=fr,actual_mapping_ref=mr,execution_plan_ref=pr,profile_ref=pfr,engine_ref=engine,resource_guard_refs=guards,binary_ref=br,configs=configs,input_binding_ref=ir,registry_modified=False,budget_modified=False,planning_is_not_current_RSS_or_guaranteed_future_hardbound=True)

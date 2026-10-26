#!/usr/bin/env python3
"""One finite offline analysis of the already CLOSED accepted pair. No model/authority mutation."""
from pathlib import Path
import hashlib,importlib.util,json,os,resource,time,sys,datetime
J=Path('/root/data/ep_tag_reservation_lifetime_20261026_v1');N=Path('/root/data/ep_l2_dtc_l1_native_v2');M=1<<20;G=1<<30
CASES={'OFF':'EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2','ON':'EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2'}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(M),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):return {'path':str(p),'sha256':sha(p)}
def put(p,value):
 with Path(p).open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 resource.setrlimit(resource.RLIMIT_AS,(G,G));os.sched_setaffinity(0,{16});os.nice(10)
 assert os.statvfs(J).f_bavail*os.statvfs(J).f_frsize>8*G+128*M
 assert int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024>64*G+G
 regpath=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';epath=N/'control/CURRENT_SCIENCE_EPOCH.json'
 for i in range(4):
  rb=regpath.read_bytes();epoch=read(epath)
  if hashlib.sha256(rb).hexdigest()==epoch['native_registry_sha256']:break
  time.sleep(.1)
 else:raise ValueError('torn current authority')
 reg=json.loads(rb);manifest={'schema':'EP_L2_LIFETIME_ANALYSIS_INPUT_V1','status':'ACCEPTED_OFF_ON_NONINTERFERING_INPUTS','goal':'EP_L2_TAG_RESERVATION_LIFETIME_CAUSAL_V1','scientific_acceptance_owner':'EP-MAIN','cases':{}}
 rows={}
 for role,case in CASES.items():
  row=reg['registered_future_requests'][case];assert row['state']=='CLOSED' and row['budget']==row['consumed']==1 and row['remaining']==row['reserved_write_bytes']==0
  out=Path(row['output']);p=out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json';point=read(p)
  assert point['status']=='EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED' and sha(p)==row['accepted_point_sha256']
  for f in ['archive_receipt_path','independent_restore_path']:assert sha(row[f])==row[f.replace('_path','_sha256')]
  assert read(row['archive_receipt_path'])['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
  assert read(row['independent_restore_path'])['status']=='INDEPENDENT_BUNDLE_TO_NATIVE_TARGET_RESTORE_PASS'
  manifest['cases'][role]={'raw':ref(out/'raw.log'),'accepted_receipt':ref(p)};rows[role]=row
 on=Path(rows['ON']['output']);manifest['noninterference']=ref(on/'OFF_ON_NONINTERFERENCE.json')
 dest=J/'analysis';dest.mkdir(exist_ok=True);mp=dest/'ACCEPTED_PAIR_INPUT_V1.json';put(mp,manifest)
 sys.path.insert(0,str(J/'tools_v2'))
 import accepted_pair_pipeline as pipeline
 assert sha(pipeline.__file__)=='7bca05de662a1346da9b890b2608ebd72fa34375a5385c58bf5b770299d9a65f'
 index=pipeline.generate(mp,dest/'accepted_pair_v1')
 receipt={'status':'STRICT_ANALYSIS_FROM_TWO_CLOSED_ACCEPTED_NONINTERFERING_APPLICATIONS','manifest':ref(mp),'analysis_source_index':ref(dest/'accepted_pair_v1/ANALYSIS_SOURCE_INDEX.json'),'source_identity':index['source_identity'],'application_starts_by_this_script':0,'registry_or_budget_writes':0,'actual_full_application_starts_total':2,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 put(J/'control/ACCEPTED_PAIR_ANALYSIS_EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

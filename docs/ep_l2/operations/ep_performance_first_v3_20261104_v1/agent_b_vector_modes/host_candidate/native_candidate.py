import os,sys,json
from ep_perf_native_wv_modes_draft import spec_for
if __name__=='__main__':
 try:
  if len(sys.argv)!=3 or sys.argv[1]!='prepare-dry':raise RuntimeError('NO SCIENCE START AUTHORITY; only prepare-dry')
  s=spec_for(sys.argv[2]);print(json.dumps(dict(status='ENGINEERING_NATIVE_DRY_SPEC_BINDING_PASS',cohort=s['cohort'],mode=s['mode'],launch_permission=False,scientific_acceptance_granted=False,models_started=0)))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=str(e),models_started=0)));sys.exit(2)

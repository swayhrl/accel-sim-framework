"""Exact new prefix only; all prior native entry routes are preserved externally."""
import sys,pathlib,importlib.util,json
R=pathlib.Path('/root/data/dtc_hash_downstream18_20261027_v1')
def main(a):
 assert len(a)>=3 and a[2].startswith('E2-DTCHASH18-')
 if a[:2]==['result','archive']:
  p=R/'tools/ds18_outbox.py';s=importlib.util.spec_from_file_location('ds18_frontdoor_archive',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.archive(a[2])
 assert '--project'in a and a[a.index('--project')+1]=='DTC_L1'
 p=R/'tools/ds18_native.py';s=importlib.util.spec_from_file_location('ds18_frontdoor_engine',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 if a[:2]in[['experiment','prepare'],['experiment','inspect']]:return m.prepare(a[2])
 if a[:2]==['experiment','run-native']:return m.run_native(a[2])
 raise ValueError('Exact18 native operation unsupported')
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except(RuntimeError,OSError,ValueError,KeyError,AssertionError)as e:print(json.dumps(dict(status='HOLD',reason=str(e),error_type=type(e).__name__,model_retry=False)),file=sys.stderr);sys.exit(2)

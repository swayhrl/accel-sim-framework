"""Candidate private frontend; only explicitly guarded pilot uses overlay."""
import importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
R=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(args):
 if '--guarded-admission-v1'not in args:return load('l2_original_frontend',R/'tools/l2_frontend.py').main(args)
 a=[v for v in args if v!='--guarded-admission-v1']
 if len(a)<3 or a[:2]not in [['experiment','prepare'],['experiment','inspect'],['experiment','run-native']]:raise RuntimeError('GUARD_ONLY_EXPLICIT_EXPERIMENT_PILOT')
 if '--project'not in a or a[a.index('--project')+1]!='DTC_L1':raise RuntimeError('GUARD_PROJECT')
 m=load('l2_private_guarded_source',HERE/'guarded_native.py');e=m.guarded(a[2])
 return e.run_native(a[2])if a[:2]==['experiment','run-native']else e.prepare(a[2])
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as exc:print(json.dumps({'status':'HOLD','reason':str(exc),'science_retry':False}),file=sys.stderr);sys.exit(2)

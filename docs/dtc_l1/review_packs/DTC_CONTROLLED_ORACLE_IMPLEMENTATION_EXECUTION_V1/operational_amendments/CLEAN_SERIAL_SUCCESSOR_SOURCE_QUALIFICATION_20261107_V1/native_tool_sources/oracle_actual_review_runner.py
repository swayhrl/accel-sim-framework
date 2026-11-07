"""Independent authored verifier runner; CPU evidence reads only, no models."""
from pathlib import Path
import hashlib,json,os,sys,time,types
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(stage_root,cohort):
 root=Path(stage_root).resolve();assert root in [Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8'),Path('/root/data/dtc_controlled_oracle_20261106_v1/remaining24')]
 plan=json.loads((root/'control/EXECUTION_PLAN.json').read_bytes());assert cohort in plan['authorized_cohorts']and cohort in set(plan['initial_qualifiers'].values())
 ref=plan['actual_qualification_reviewer'];assert sha(ref['path'])==ref['sha256']
 module=types.ModuleType('DTC_ORACLE_INDEPENDENT_ACTUAL_QUALIFIER');module.__file__=ref['path'];exec(compile(Path(ref['path']).read_bytes(),ref['path'],'exec'),module.__dict__)
 value=getattr(module,ref['function'])(str(root),cohort)
 assert value['reviewer_source_sha256']==ref['sha256']
 target=root/'control/actual_qualification_reviews'/(cohort+'.json')
 if value['status']!='PASS':target=target.with_name(cohort+'.HOLD.'+str(time.time_ns())+'.json')
 b=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode();target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==b
 else:
  with target.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 print(json.dumps(dict(status=value['status'],cohort=cohort,path=str(target),sha256=sha(target))))
 return 0 if value['status']=='PASS'else 2
def mode_extension(stage_root,mode):
 root=Path(stage_root).resolve();assert root==Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8')
 plan=json.loads((root/'control/EXECUTION_PLAN.json').read_bytes());assert mode in plan['qualified_modes']
 ref=plan['actual_qualification_reviewer'];assert sha(ref['path'])==ref['sha256']
 module=types.ModuleType('DTC_ORACLE_INDEPENDENT_MODE_GATE2');module.__file__=ref['path'];exec(compile(Path(ref['path']).read_bytes(),ref['path'],'exec'),module.__dict__)
 value=module.verify_mode_core32_extension(str(root),mode);assert value['reviewer_source_sha256']==ref['sha256']
 target=Path(plan['mode_gate2_reviews'][mode])
 assert target.parent==root.parent/'control/GATE2_MODE_REVIEWS'
 if value['status']!='PASS':target=target.with_name(mode+'.HOLD.'+str(time.time_ns())+'.json')
 b=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode();target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==b
 else:
  with target.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 print(json.dumps(dict(status=value['status'],mode=mode,path=str(target),sha256=sha(target))))
 return 0 if value['status']=='PASS'else 2
if __name__=='__main__':
 if len(sys.argv)==4 and sys.argv[2]=='--mode':raise SystemExit(mode_extension(sys.argv[1],sys.argv[3]))
 raise SystemExit(main(*sys.argv[1:]))

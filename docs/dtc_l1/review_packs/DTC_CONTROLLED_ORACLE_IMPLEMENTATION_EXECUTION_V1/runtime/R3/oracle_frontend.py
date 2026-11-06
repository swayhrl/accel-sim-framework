"""Exact Oracle native route. Import inert; no hidden qualification models."""
from pathlib import Path
import json,os,sys,types
R=Path(__file__).resolve().parents[1]
def main(argv):
 assert len(argv)==5 and argv[0]in['experiment','result']and argv[3:]==['--project','DTC_L1']
 assert os.environ.get('DTC_CONTROLLED_ORACLE_NATIVE_ENTRY')=='1'
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes())
 assert plan['preparation_phase']=='SCIENCE_FINAL_FROZEN'and not plan.get('mock',False)
 assert argv[2]in plan['authorized_cohorts']
 name='oracle_outbox.py'if argv[:2]==['result','archive']else'oracle_native.py'
 p=R/'tools'/name;m=types.ModuleType('oracle_native_frontend');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__)
 if argv[:2]==['result','archive']:return m.archive(argv[2])
 if argv[:2]in[['experiment','prepare'],['experiment','inspect']]:return m.prepare(argv[2])
 if argv[:2]==['experiment','run-native']:return m.run_native(argv[2])
 raise ValueError('UNSUPPORTED_ORACLE_NATIVE_OPERATION')
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as error:print(json.dumps(dict(status='HOLD',reason=repr(error),model_retry=False)),file=sys.stderr);raise SystemExit(2)

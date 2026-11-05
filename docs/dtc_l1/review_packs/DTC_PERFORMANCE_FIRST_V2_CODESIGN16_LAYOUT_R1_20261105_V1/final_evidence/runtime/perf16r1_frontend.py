import types
import sys,pathlib,importlib.util,json,os
R=pathlib.Path('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1')
def main(a):
 assert len(a)==5 and a[0]in['experiment','result']and a[2]in{x['cohort']for x in json.loads((R/'control/MATRIX.fixed.json').read_bytes())['points']}and a[3:]==['--project','DTC_L1']
 assert os.environ.get('DTC_PERFV2_CODESIGN16_LAYOUT_R1_NATIVE_ENTRY')=='1'
 name='perf16r1_outbox.py'if a[:2]==['result','archive']else'perf16r1_native.py';p=R/'tools'/name;m=types.ModuleType('perf16r1_frontend_impl');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__)
 if a[:2]==['result','archive']:return m.archive(a[2])
 if a[:2]in[['experiment','prepare'],['experiment','inspect']]:return m.prepare(a[2])
 if a[:2]==['experiment','run-native']:return m.run_native(a[2])
 raise ValueError('Unsupported PerformanceFirst operation')
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=repr(e),science_retry=False)),file=sys.stderr);sys.exit(2)

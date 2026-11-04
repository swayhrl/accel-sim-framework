import sys,pathlib,importlib.util,json,os
R=pathlib.Path('/root/data/dtc_perf_first_remaining28_20261104_v1')
def main(a):
 assert len(a)==5 and a[0]in['experiment','result']and a[2]in{x['cohort']for x in json.loads((R/'control/MATRIX.json').read_bytes())['points']}and a[3:]==['--project','DTC_L1']
 assert os.environ.get('DTC_PERFFIRST_REMAINING28_NATIVE_ENTRY')=='1'
 name='perf28_outbox.py'if a[:2]==['result','archive']else'perf28_native.py';s=importlib.util.spec_from_file_location('perf28_frontend_impl',R/'tools'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 if a[:2]==['result','archive']:return m.archive(a[2])
 if a[:2]in[['experiment','prepare'],['experiment','inspect']]:return m.prepare(a[2])
 if a[:2]==['experiment','run-native']:return m.run_native(a[2])
 raise ValueError('Unsupported PerformanceFirst operation')
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=repr(e),science_retry=False)),file=sys.stderr);sys.exit(2)

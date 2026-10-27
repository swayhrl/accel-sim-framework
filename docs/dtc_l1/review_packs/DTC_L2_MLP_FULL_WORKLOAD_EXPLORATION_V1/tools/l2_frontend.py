import sys,pathlib,importlib.util,json
R=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def main(a):
 assert len(a)>=3 and a[2].startswith('E2-DTCL2MLP-')
 name='l2_outbox.py'if a[:2]==['result','archive']else'l2_native.py';s=importlib.util.spec_from_file_location('l2_frontend_impl',R/'tools'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 if a[:2]==['result','archive']:return m.archive(a[2])
 assert '--project'in a and a[a.index('--project')+1]=='DTC_L1'
 if a[:2]in [['experiment','prepare'],['experiment','inspect']]:return m.prepare(a[2])
 if a[:2]==['experiment','run-native']:return m.run_native(a[2])
 raise ValueError('Unsupported L2 native operation')
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=str(e),science_retry=False)),file=sys.stderr);sys.exit(2)

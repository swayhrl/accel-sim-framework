import pathlib,importlib.util,json,hashlib,subprocess
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');cell='E2-AEF3-NN-DM'
assert json.loads((T/'control/R3_PUBLICATION_READBACK.json').read_text())['verified']
s=importlib.util.spec_from_file_location('corrected_exact_strict',T/'tools/short3_strict_r2.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
science=m.terminal(cell);out=P(json.loads((T/'control/qualification_ledger'/(cell+'.INTENT.json')).read_text())['output'])
with (out/'AEFAIR_STRICT.json').open('x') as f:json.dump(science,f,indent=2);f.write('\n')
qual={'status':'AEFAIR_SCIENCE_QUALIFIED','uuid':science['uuid'],'cohort':cell,'strict_sha256':hashlib.sha256((out/'AEFAIR_STRICT.json').read_bytes()).hexdigest(),'cycles':science['cycles'],'SOURCE_KEEP':True,'expectation_metadata_correction':'R2; original spent model reused, no scientific retry'}
with (T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')).open('x') as f:json.dump(qual,f,indent=2);f.write('\n')
r=subprocess.run([str(N/'bin/result'),'archive',cell],capture_output=True,text=True,timeout=300)
(T/'control'/('EXISTING_NN_DM_R2.ARCHIVE_CLI.json')).write_text(r.stdout+r.stderr);r.check_returncode()
a=json.loads(r.stdout);assert a['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
print(json.dumps({'status':'EXISTING_SPENT_NN_DM_ACCEPTED_ARCHIVED_AND_NATIVE_RESTORED','cycles':science['cycles'],'uuid':science['uuid'],'receipt':a['receipt'],'new_model_starts':0},indent=2))

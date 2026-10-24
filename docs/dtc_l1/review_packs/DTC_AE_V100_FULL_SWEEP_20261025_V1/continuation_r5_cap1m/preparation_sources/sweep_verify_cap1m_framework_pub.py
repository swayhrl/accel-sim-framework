import pathlib,json,hashlib,subprocess,datetime
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1');F=T/'telemetry_v2/framework';read=lambda p:json.loads(p.read_bytes());r=read(T/'control/CAP1M_FRAMEWORK_GITHUB_RESPONSE.json');build=read(T/'telemetry_v2/BUILD_RESULT.json')
def git(*a):return subprocess.check_output(['git','-C',str(F),*a],text=True).strip()
assert r['commit']==r['branch_commit']==git('rev-parse','HEAD')==build['framework_commit'] and r['parent']==build['framework_parent'] and r['tree']==git('rev-parse','HEAD^{tree}') and not git('status','--porcelain')
assert len(r['files'])==1 and r['files'][0]['path']=='gpu-simulator/ag7_policyb_progress.h' and r['files'][0]['changes']==2
file=F/r['files'][0]['path'];b=file.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest()==r['files'][0]['sha']
old=subprocess.check_output(['git','-C',str(F),'show',r['parent']+':'+r['files'][0]['path']]);assert old.replace(b'kMaximumRecords = 8192;',b'kMaximumRecords = 1048576;')==b
proof=dict(r,verified=True,source_blob_bytes_match=True,source_delta_exact_one_observational_constant=True,models_started=0,verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with (T/'control/CAP1M_FRAMEWORK_PUBLICATION_READBACK.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print('OBSERVATIONAL_FRAMEWORK_SOURCE_PUBLICATION_EXACT_NATIVE_BYTE_READBACK_PASS',r['commit'])

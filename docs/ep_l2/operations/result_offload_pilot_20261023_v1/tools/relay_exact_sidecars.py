import pathlib,hashlib,json,subprocess,base64,shlex,zlib,time
import argparse
ap=argparse.ArgumentParser(description='Exact owner-frozen9 sidecar finite relay; completed archives are verified/reused, never retransmitted.')
ap.add_argument('--audit-dir',required=True);args=ap.parse_args()
R=pathlib.Path(__file__).resolve().parents[1];W=R.parents[3];D=pathlib.Path(args.audit_dir).resolve();D.mkdir(parents=True,exist_ok=True)
endpoint=(R/'tools/real_sidecar_endpoint.py').read_bytes()
# Preserve the original transaction reservation provenance across qualified
# endpoint revisions. The scientific/owner commits are in the manifest.
head='b70254a71fff359156fb48c7e6a3f154043a7e50'
v9=subprocess.check_output(['git','show','13b30fa613b55eb929785a5dfc015aae95a17a37:docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261018_storageops_v9_target_01/v9_transaction.py'],cwd=W)
assert hashlib.sha256(v9).hexdigest()=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
idx=json.loads((R/'OWNER_READY_INTAKE_AND_PREPARED_REAL_INDEX.json').read_bytes());confirm=hashlib.sha256((R/'USER_CONFIRMED_ZERO_SHARE.json').read_bytes()).hexdigest()

def command(config):
 code=('CONFIG='+repr(config)+'\n').encode()+endpoint;packed=zlib.compress(code)
 runner="import sys,zlib; n=int(sys.stdin.buffer.readline());exec(compile(zlib.decompress(sys.stdin.buffer.read(n)),'<frozen_sidecar_endpoint>','exec'))"
 return 'timeout -k 3s 100s python3 -B -c '+shlex.quote(runner),str(len(packed)).encode()+b'\n'+packed
for p in idx['projects']:
 slug=p['slug'];m=json.loads((R/'prepared_real'/(slug+'_V9_MANIFEST.json')).read_bytes());owner=R/'owner_ready'/slug/('COPY_READY.json' if slug=='EP_L2_E057' else 'COPY_READY_AD_GEMM.json');cfg={'role':'target','slug':slug,'manifest':m,'txid':p['candidate_txid'],'owner_raw':base64.b64encode(owner.read_bytes()).decode(),'v9_raw':base64.b64encode(v9).decode(),'tool_publication':head,'zero_share_confirmation_sha256':confirm}
 with (D/(slug+'.target.stderr')).open('wb') as err:
  cmd,boot=command(cfg)
  target=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','hrl-174-new',cmd],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err)
  target.stdin.write(boot);target.stdin.flush()
  ready=target.stdout.readline();(D/(slug+'.target.stdout')).write_bytes(ready)
  if not ready:target.wait(timeout=10);raise RuntimeError((D/(slug+'.target.stderr')).read_text())
  msg=json.loads(ready);assert msg['event']=='READY' and msg['txid']==p['candidate_txid'];print('Target ready',slug,msg['missing_names'],flush=True)
  scfg=dict(cfg,role='source',missing_names=msg['missing_names']);scfg.pop('v9_raw')
  cmd,boot=command(scfg)
  source=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','hrl',cmd],input=boot,capture_output=True,timeout=50);(D/(slug+'.source.stderr')).write_bytes(source.stderr)
  if source.returncode:
   target.stdin.close();target.wait(timeout=15);raise RuntimeError(source.stderr.decode())
  assert len(source.stdout)<=512*1024;target.stdin.write(source.stdout);target.stdin.close();out=target.stdout.read();rc=target.wait(timeout=100)
  with (D/(slug+'.target.stdout')).open('ab') as f:f.write(out)
  if rc:raise RuntimeError((D/(slug+'.target.stderr')).read_text())
  done=json.loads(out.splitlines()[-1]);assert done['event']=='DONE';(D/(slug+'_RESULT.json')).write_bytes((json.dumps(done,indent=2)+'\n').encode());print(json.dumps({'project':slug,'status':done['receipt']['status'],'files':done['receipt']['files'],'bytes':done['receipt']['raw_bytes'],'txid':done['receipt']['txid'],'peaks':done['observed_allocated_peaks_including_receipts']}),flush=True)
  # Fresh Source byte/stat verification AFTER target archive+native restore;
  # original owner reconfirmation is separate, never impersonated by T.
  scfg['missing_names']=[];cmd,boot=command(scfg);after=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','hrl',cmd],input=boot,capture_output=True,timeout=50);after.check_returncode();j=json.loads(after.stdout);assert all('data_base64' not in f for f in j['files']);(D/(slug+'_SOURCE_POSTCOPY_READONLY_CHECK.json')).write_bytes((json.dumps(j,indent=2)+'\n').encode());print('Source postcopy bytes+identity unchanged',slug,flush=True)

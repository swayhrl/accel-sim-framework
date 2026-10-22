#!/usr/bin/env python3
"""Produce tmp CLIENT candidate from exact overlay; never install it."""
import argparse,copy,hashlib,json,re,subprocess
from pathlib import Path
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
CLIENT=Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/CLIENT_CONTRACT.json')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--publication-commit',required=True);p.add_argument('--qualification',required=True);p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 assert re.fullmatch('[0-9a-f]{40}',a.publication_commit)
 out=Path(a.out);assert out.resolve().is_relative_to(Path('/tmp'))
 c=json.loads(CLIENT.read_text());previous=copy.deepcopy({k:c[k] for k in ('source_files','source_publication_commit','resource_lease_api_sha256')})
 folder=E/'util/ep_l2/mechanism_e';overlay=Path(a.runtime)
 files={x.name:x for x in folder.glob('*.py') if not x.name.startswith('test_')}
 for x in overlay.glob('*.py'):
  assert not x.name.startswith('test_');files[x.name]=x
 c.setdefault('source_binding_history',[]).append(dict(previous,reason='Exact one-point Goal observer deployment; previous scientific and resource contracts retained'))
 c['source_files']={'util/ep_l2/mechanism_e/'+k:digest(v) for k,v in sorted(files.items())}
 for name,sha in c['source_files'].items():
  blob=subprocess.check_output(['git','show',a.publication_commit+':'+name],cwd=E)
  assert hashlib.sha256(blob).hexdigest()==sha,'published source differs: '+name
 c['source_publication_commit']=a.publication_commit
 c['resource_lease_api_sha256']=digest(overlay/'coordinator.py')
 c['policy_helper_sha256']=digest(overlay/'policy_v2.py')
 m=json.loads(Path(a.manifest).read_text());q=json.loads(Path(a.qualification).read_text());b=m['scientific_binding']
 assert m['deployment_state']=='E_SEALED_FORMAL_RELEASE' and m['pairs']==[]
 assert q['status']=='INDEPENDENTLY_QUALIFIED' and q['synthetic_fixture'] is False
 assert b['qualification']['path']==str(Path(a.qualification)) and b['qualification']['sha256']==digest(a.qualification)
 assert b['source_identity']==q['source_identity']
 c['detach_observer_diagnostic_runtime']=b['source_identity']
 c['detach_observer_diagnostic_qualification']={'path':a.qualification,'sha256':digest(a.qualification)}
 c['detach_observer_diagnostic_manifest']={'path':a.manifest,'sha256':digest(a.manifest)}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(c,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':'STAGED_ONLY_EXACT_LOCAL_COMMIT_BLOBS_VERIFIED_REMOTE_READBACK_REQUIRED','source_files':len(files),'out':str(out)}))
if __name__=='__main__':main()

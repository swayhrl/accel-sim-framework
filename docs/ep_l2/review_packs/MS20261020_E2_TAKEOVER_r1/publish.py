"""Commit authorized E2 evidence, push and read back exact remote bytes."""
from pathlib import Path
import subprocess,sys,time,json
ROOT=Path(__file__).resolve().parents[4]
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=ROOT)
def publish(message,paths):
 git('add','-f',*[str(Path(p).resolve().relative_to(ROOT)) for p in paths])
 staged=git('diff','--cached','--name-only').decode().splitlines()
 assert staged,'no changes to publish'
 git('commit','-m',message)
 head=git('rev-parse','HEAD').decode().strip()
 git('push','origin','HEAD:refs/heads/hrl/ep-l2-ms20261019-e-eval-v1')
 git('fetch','origin','hrl/ep-l2-ms20261019-e-eval-v1')
 assert git('rev-parse','FETCH_HEAD').decode().strip()==head
 for p in staged:assert git('show',head+':'+p)==(ROOT/p).read_bytes(),p
 result=dict(remote_commit=head,verified_paths=staged,at_unix=time.time())
 print(json.dumps(result),flush=True);return result
if __name__=='__main__':
 result=publish(sys.argv[1],sys.argv[2:])
 (Path(__file__).parent/'LATEST_REMOTE_READBACK.json').write_text(json.dumps(result,indent=2)+'\n')

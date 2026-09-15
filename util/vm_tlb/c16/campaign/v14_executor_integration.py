import json,subprocess,tempfile,sys
from pathlib import Path
DRIVER=Path(__file__).with_name('driver.py')
def run(c,resume=False):
 p=subprocess.run([sys.executable,str(DRIVER),'--campaign',str(c)]+(['--resume'] if resume else []),text=True,capture_output=True);return p.returncode,p.stdout+p.stderr
with tempfile.TemporaryDirectory() as td:
 t=Path(td); base={'campaign_id':'fixture','model':{'model_id':'fixture','revision':'r'},'scenario':'s','phase':'p','state_root':str(t/'state'),'semantic_inputs':{'token':'a'},'handlers':{'ASSET_AUTHORITY':['/bin/true']}}
 c=t/'c.json';c.write_text(json.dumps(base));out=[]
 rc,txt=run(c);out.append(('missing_handler_blocks',rc==0 and (t/'state'/'BLOCKED.json').is_file() and 'BLOCKED_STAGE_EXECUTOR_MISSING_ENVIRONMENT_PREFLIGHT' in (t/'state'/'BLOCKED.json').read_text()))
 bad=dict(base,mode='FRAMEWORK_ONLY');c.write_text(json.dumps(bad));out.append(('framework_only_rejected',run(c)[0]!=0))
 c.write_text(json.dumps(base));run(c);base['semantic_inputs']={'token':'changed'};c.write_text(json.dumps(base));out.append(('digest_change_rejects_resume',run(c,True)[0]!=0))
 out.append(('partial_not_complete',not (t/'state'/'00_ASSET_AUTHORITY.json.partial').exists()))
 print(json.dumps({'status':'PASS' if all(x[1] for x in out) else 'FAIL','tests':out}))

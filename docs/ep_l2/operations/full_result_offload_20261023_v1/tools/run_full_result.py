"""Windows trusted SSH foreground coordinator for one frozen accepted result.

No daemon, second receiver, Source writes or scientific launch. config is a
reviewable Target normalization of independently published owner evidence.
"""
import argparse,ast,base64,datetime,hashlib,json,pathlib,subprocess,sys
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=pathlib.Path,required=True);p.add_argument('--audit-dir',type=pathlib.Path,required=True);a=p.parse_args()
 assert not a.audit_dir.exists(),'fresh local audit directory required; remote transaction resumes unchanged'
 config=json.loads(a.config.read_bytes());tool=pathlib.Path(__file__).with_name('full_result_bundle.py').read_bytes();ast.parse(tool)
 assert config['manifest']['source_disposition']=='SOURCE_KEEP'
 assert hashlib.sha256(base64.b64decode(config['owner_raw_base64'])).hexdigest()==config['manifest']['owner_ready_sha256']
 code=('import json,base64\nCONFIG=json.loads(base64.b64decode('+repr(base64.b64encode(json.dumps(config).encode()).decode())+'))\nTOOL=base64.b64decode('+repr(base64.b64encode(tool).decode())+').decode()\n')
 # Execute in one shared namespace; module main is suppressed for injected mode.
 code+='namespace={"__name__":"injected"};exec(compile(TOOL,"full_result_bundle.py","exec"),namespace);namespace["target"](CONFIG,TOOL)\n'
 a.audit_dir.mkdir(parents=True);(a.audit_dir/'CONFIG_SHA256.txt').write_bytes((hashlib.sha256(a.config.read_bytes()).hexdigest()+'\n').encode())
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();run=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','hrl-174-new','python3 -B -'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(a.audit_dir/'stderr.log').open('wb'))
 run.stdin.write(code.encode());run.stdin.close()
 with (a.audit_dir/'events.jsonl').open('xb') as log:
  for line in run.stdout:log.write(line);log.flush();print(line.decode(errors='replace').rstrip(),flush=True)
 result=run.wait();(a.audit_dir/'INVOCATION.json').write_bytes((json.dumps({'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':result,'config_sha256':hashlib.sha256(a.config.read_bytes()).hexdigest(),'tool_sha256':hashlib.sha256(tool).hexdigest(),'no_source_write':True,'Share_new_bytes':0},indent=2)+'\n').encode());sys.exit(result)
if __name__=='__main__':main()

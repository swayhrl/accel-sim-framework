from pathlib import Path
import os,sys,subprocess,json,csv,hashlib,gzip,time,ast
W=Path(subprocess.check_output(['git','-C',str(Path(__file__).parent),'rev-parse','--show-toplevel']).decode().strip());R=W/'docs/ep_l2/operations/original174_research_asset_archive_exec_20261024_v1';R.mkdir(parents=True,exist_ok=True)
P=Path('D:/repo/tmp/original174_research_asset_archive_exec_20261024_v1');P.mkdir(parents=True,exist_ok=True)
B=Path('D:/repo/original174-large-trace-evidence-closure-20261024-v1/docs/ep_l2/operations/original174_trace_evidence_closure_20261024_v1')
T=Path('D:/repo/ep-dtc-trace-migration-20261024-v1/docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1')
BASE='9a34666c025474367b9176764d2ae67e03b22b49';TASK='/root/data/research_asset_archive_exec_20261024_v1';NAS='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_trace_closure_followup_v1'
def load(p):
 p=Path(p);x=json.loads(p.read_text(encoding='utf8'))
 if isinstance(x,dict) and x.get('schema')=='LOSSLESS_AUDIT_METADATA_POINTER_V1':
  b=gzip.decompress((p.parent/x['compressed_file']).read_bytes());assert hashlib.sha256(b).hexdigest()==x['uncompressed_sha256'];return json.loads(b)
 return x
def rows(p):return list(csv.DictReader(Path(p).open(encoding='utf-8-sig')))
def save(n,x):
 p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def git(*a):return subprocess.check_output(['git','-c','http.version=HTTP/1.1','-C',str(W),*a])
def remote(alias,code,timeout=90):
 r=subprocess.run(['ssh','-o','BatchMode=yes',alias,'nice -n 19 ionice -c 3 python3 -B -'],input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-2500:])
 return json.loads(r.stdout)
def remote_command(alias,cmd,timeout=60):
 return subprocess.run(['ssh','-o','BatchMode=yes',alias,cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
def put_native(name,b):
 import base64
 code='from pathlib import Path;import base64,os,json\np=Path('+repr(TASK+'/'+name)+');p.parent.mkdir(parents=True,exist_ok=True);b=base64.b64decode('+repr(base64.b64encode(b).decode())+');p.write_bytes(b);print(json.dumps({"path":str(p),"bytes":len(b)}))'
 return remote('hrl-174-new',code)
if __name__=='__main__':
 req=['ARCHIVE_ACTION_QUEUE.csv','LARGE_TRACE_CLOSURE_MATRIX.csv','POLYBENCH_FULL_COVERAGE.csv','RAW_RESULTS_RESTORABILITY.csv','SOURCE_TO_TRUE164_RECOVERY_MAP.json','PROJECT_CLOSURE_SUMMARY.csv','CLOSURE_TOTALS_AND_NONADDITIVE_COUNTS.json','RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json','FINAL_STATUS_AND_RECEIPT.md']
 audit=[]
 for n in req:
  b=(B/n).read_bytes();assert b==git('show',BASE+':docs/ep_l2/operations/original174_trace_evidence_closure_20261024_v1/'+n);audit.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),parsed_rows=len(rows(B/n)) if n.endswith('.csv') else None))
 save('AUTHORITY_AND_FULL_BASELINE_READ.json',dict(base=BASE,files=audit,trace_baseline='b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b'))
 (R/'USER_EXECUTION_GOAL.md').write_text(Path('C:/Users/huang/.codex/attachments/e75db6a7-6066-4309-a312-617ac84e5754/已粘贴的文本.txt').read_text(encoding='utf8'),encoding='utf8')
 q=rows(B/'ARCHIVE_ACTION_QUEUE.csv');scopes=[];p2=load(B/'evidence/P2_BOUNDED_CURRENT_FULL_SOURCE_RAW_FILE_SHA_MANIFEST.json')['results']
 for r in q:
  if r['status']!='REQUIRES_COPY_AUTHORIZATION':continue
  if r['queue_id'].startswith('TRACE_'):
   x=load(B/r['manifest_reference']);fs=x['selected_uncovered_members'];expected=[dict(**f) for f in fs];kind='TRACE';source_host='hrl'
  elif r['queue_id'].startswith('RAW_DTC_'):
   x=next(z for z in p2 if z['path']==r['source']);expected=x['files'];kind='DTC_RAW';source_host='hrl'
  else:
   x=load(B/'evidence/AWMA_EXISTING_CONSUMER_AUDIT_AND_Q05_LOCAL_ORIGINAL.json')['q05_local_current'][0];expected=[dict(x,relative_path=Path(x['path']).name)];kind='Q05_FIXED10000';source_host='hrl-174-new'
  assert r['source'] and r['source'].startswith(('/workspace/','/root/share/accel-sim/','/root/share/workspace_migrated_20260905/','/root/workspace/'))
  if kind=='Q05_FIXED10000':source_root=r['source'].rsplit('/',1)[0]
  else:source_root=r['source']
  scopes.append(dict(queue=r,asset_id=r['queue_id'],kind=kind,source_alias=source_host,source_root=source_root,files=expected,expected_bytes=sum(f['size'] for f in expected),priority=r['priority']))
 save('FROZEN_AUTHORIZED_EXECUTION_SCOPES.json',dict(scopes=scopes,hold_only_queue_rows=[r for r in q if r['status']!='REQUIRES_COPY_AUTHORIZATION'],Source_release_authorized=False))
 print('Authorized scopes',len(scopes),'trace',sum(r['kind']=='TRACE' for r in scopes),'DTC',sum(r['kind']=='DTC_RAW' for r in scopes),'bytes',sum(r['expected_bytes'] for r in scopes))

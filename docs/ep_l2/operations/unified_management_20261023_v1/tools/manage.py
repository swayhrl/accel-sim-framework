"""174-new finite management entry. No scientific start, delete or scheduler API."""
import argparse,base64,hashlib,json,os,pathlib,shlex,struct,subprocess,sys,zlib,datetime
from management_guard import evaluate
P=pathlib.Path;ROOT=P(__file__).resolve().parent.parent;CATALOG=json.loads((ROOT/'data/asset_catalog.json').read_bytes());MIB=1024**2;GIB=1024**3
SSH=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-o','ConnectTimeout=10','-p','2233','root@10.208.130.174']
def require(ok,why):
 if not ok:raise RuntimeError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def rpc(req):
 tool=(ROOT/'tools/source_readonly.py').read_text();body=zlib.compress(canon({'code':tool,'request':req}));boot="import sys,json,zlib,struct; n=struct.unpack('!Q',sys.stdin.buffer.read(8))[0]; q=json.loads(zlib.decompress(sys.stdin.buffer.read(n))); e={'__name__':'injected'}; exec(compile(q['code'],'source_readonly.py','exec'),e); print(json.dumps(e['handle'](q['request'])))"
 p=subprocess.run(SSH+['python3 -B -c '+shlex.quote(boot)],input=struct.pack('!Q',len(body))+body,capture_output=True,timeout=45)
 require(p.returncode==0,'SOURCE_UNAVAILABLE_OR_CONSISTENCY_HOLD: '+p.stderr.decode(errors='replace')[-1800:]);return json.loads(p.stdout)
def target_identity():
 require(os.uname().nodename=='huangrulin-sshfs-174','entry must run on verified174-new');return {'host':os.uname().nodename,'namespace':os.readlink('/proc/self/ns/mnt'),'management_process':'finite foreground only','science_starts':0}
def status(project):
 s=rpc({'action':'status','project':project});require(s['data']['consistency'],'Source current control records inconsistent; no stale fallback');return s
def fence(operation,s):
 expected=json.loads((ROOT/'data/management_authority.json').read_bytes()) if (ROOT/'data/management_authority.json').exists() else {}
 req={'operation':operation,'epoch':expected.get('epoch'),'holder':os.uname().nodename};out=evaluate(req,s['data'].get('management_authority',{}));out['current_source_epoch']=s['data'].get('management_authority',{}).get('epoch');return out
def result_record(project,name):
 require(name in CATALOG['results'],'result is not a qualified indexed archived selector');r=CATALOG['results'][name];require(r['project']==project,'project/result identity mismatch');return r
def archive_metadata(r):
 mount=subprocess.check_output(['findmnt','-n','-T',r['manifest_path'],'-o','TARGET,SOURCE,FSTYPE'],text=True).split();require(mount==['/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs'],'genuine164 mount invalid')
 checks={}
 for key,expected in [('manifest_path','manifest_sha256'),('receipt_path','receipt_sha256'),('archive_index_path','archive_index_sha256'),('native_proof_path','native_proof_sha256'),('source_keep_confirmation','source_keep_confirmation_sha256')]:
  p=P(r[key]);require(p.is_file() and not p.is_symlink(),'missing164 evidence '+key);b=p.read_bytes();require(sha(b)==r[expected],'immutable evidence digest mismatch '+key);checks[key]=True
 m=json.loads(P(r['manifest_path']).read_bytes());ix=json.loads(P(r['archive_index_path']).read_bytes());base=P(r['manifest_path']).parent;commit=json.loads((base/'COMMIT.json').read_bytes());require(commit['txid']==r['txid'] and commit['manifest_sha256']==r['manifest_sha256'] and commit['archive_index_sha256']==r['archive_index_sha256'],'immutable COMMIT binding')
 offset=0
 for c in ix['chunks']:
  require(c['offset']==offset and 0<c['size']<=128*MIB,'range gap/size');p=base/'chunks'/c['name'];require(p.is_file() and not p.is_symlink() and p.stat().st_size==c['size'],'missing or truncated archive chunk');offset+=c['size']
 require(offset==ix['archive_bytes'],'range coverage length')
 for name,ref in m['reused_objects'].items():
  p=P(ref['path_on_target']);require(p.is_file() and p.stat().st_size==ref['size'],'missing pinned164 reuse dependency')
 return {'state':'ARCHIVE_ALREADY_VERIFIED_REUSED','mode':'READONLY_CONTROL_DIGEST_AND_RANGE_PRESENCE_CHECK','prior_full_content_SHA_and_native_restore':'REUSED_FROM_BOUND_BASELINE_RECEIPTS; large payload SHA not recomputed in this command','checks':checks,'archive_bytes':offset,'chunks':len(ix['chunks']),'txid':r['txid'],'new_result_payload_transferred_bytes':0,'new_restore_files':0,'manifest':m}
def assets(project):
 rows=[dict(r) for r in CATALOG['assets'] if r['project']==project];queries=list(dict.fromkeys(r['old174_path'] for r in rows));out=rpc({'action':'stat_many','paths':queries});paths={p['path']:p for p in out['data']['paths']}
 for r in rows:
  current=paths[r['old174_path']];r['current_source_access']=current;r['available']=current.get('exists') is True and current.get('readable') is True
  if r.get('expected_identity') and current.get('identity'):
   old=r['expected_identity'];r['owner_recorded_identity_matches_now']=all(old[k]==current['identity'][k] for k in ['dev','inode','nlink','size','uid','gid','mode','mtime_ns','ctime_ns'])
  if not r['available']:r['availability']='MISSING_OR_UNREADABLE_NOT_CLAIMED_AVAILABLE'
 return rows
def inspect(project,name,path=None):
 q=rpc({'action':'experiment','project':project,'experiment':name});d=q['data'];d['management_can_start_science']=False
 if path is not None:
  r=result_record(project,name);m=json.loads(P(r['manifest_path']).read_bytes());require(not P(path).is_absolute() and '..' not in P(path).parts and '\\' not in path,'unsafe relative result path');matches=[x for x in m['entries'] if x['path']==path];require(len(matches)==1,'path not in frozen result selector');d['selected_file']={'owner_manifest_record':matches[0],'source_readonly_access':rpc({'action':'stat_many','paths':[r['source_root']+'/'+path]})['data']['paths'][0]}
 return q
def prepare(project,name):
 s=status(project);f=fence('experiment.prepare',s);q=inspect(project,name);a=assets(project);missing=[r['asset_id'] for r in a if not r['available']];drift=[r['asset_id'] for r in a if r.get('owner_recorded_identity_matches_now') is False];res=s['data']['resources'];margin=res['workspace_available_bytes']-7*GIB
 return {'status':'HOLD_OWNER_QUALIFICATION_OR_ASSET' if missing or drift or q['data']['scientific_hold'] else 'READONLY_PRECHECK_COMPLETE_NO_LAUNCH','management_fence':f,'owner_record':q,'resources':res,'current_workspace_residual_after_scoped7GiB':margin,'current_readonly_resource_floor_pass':margin>=0 and res['MemAvailable_bytes']>=64*GIB,'missing_or_unreadable_assets':missing,'owner_identity_drift':drift,'qualification':'Owner-published accepted provenance only; no scientific revalidation or new experiment release','existing_experiment_relaunch_allowed':False,'scientific_start_allowed':False,'controller_interface':s['data']['existing_controller_interface'],'remaining_science_execution_gates':['Fresh exact owner-qualified new never-paid request/UUID and scientific scope','Mandatory epoch/request-id check in original controller start-consumption paths and control-source qualification','Existing original resource and budget/T0 gates','No starts authorized by this management Goal'],'Source_writes':0}
def execute_restore(r,destination):
 dest=P(destination);allowed=P('/root/data/full_result_offload_20261023_v1');require(dest.is_absolute() and dest.is_relative_to(allowed) and '..' not in dest.parts,'restore outside previously qualified native task scope');require(not os.path.lexists(dest),'restore requires NEW ABSENT target')
 return subprocess.run(['sh',r['restore_script'],str(dest)],check=True).returncode
def main():
 p=argparse.ArgumentParser(description=__doc__);top=p.add_subparsers(dest='group',required=True)
 pr=top.add_parser('project');pr.add_argument('action',choices=['status','assets']);pr.add_argument('--project',choices=['EP_L2','DTC_L1'],required=True)
 ex=top.add_parser('experiment');ex.add_argument('action',choices=['inspect','prepare']);ex.add_argument('experiment');ex.add_argument('--project',choices=['EP_L2','DTC_L1'],required=True);ex.add_argument('--path');ex.add_argument('--environment',action='store_true')
 rr=top.add_parser('result');rr.add_argument('action',choices=['archive','restore']);rr.add_argument('experiment');rr.add_argument('--project',choices=['EP_L2','DTC_L1'],required=True);rr.add_argument('--destination');rr.add_argument('--execute',action='store_true');rr.add_argument('--dry-run',action='store_true');rr.add_argument('--offer',type=P)
 args=p.parse_args();target=target_identity()
 if args.group=='project':out=status(args.project) if args.action=='status' else {'project':args.project,'assets':assets(args.project),'fresh_full_historical_hashes':0}
 elif args.group=='experiment':
  out=inspect(args.project,args.experiment,args.path) if args.action=='inspect' else prepare(args.project,args.experiment)
  if args.environment:out['SSH_environment_readonly']=rpc({'action':'environment'})
 else:
  require(not(args.execute and args.dry_run),'choose execute or dry-run');s=status(args.project);gate=fence('result.'+args.action,s);require(gate['allowed'],'management authority fence denied operation '+str(gate['reasons']))
  if args.offer is not None:
   require(args.offer.is_absolute() and args.offer.resolve().is_relative_to(ROOT/'outbox'),'offer must reside in task-native outbox; not active raw/lock/SQLite');offer=json.loads(args.offer.read_bytes());require(offer['project']==args.project and offer['experiment']==args.experiment,'outbox/CLI identity mismatch')
   pub=rpc({'action':'owner_publication','project':args.project,'commit':offer['owner_qualification_publication'],'path':offer['owner_ready_publication_path']});require(pub['data']['sha256']==offer['manifest']['owner_ready_sha256'],'owner publication raw bytes differ')
   from result_outbox import bind
   cfg,code,plan=bind(offer,CATALOG,rpc({'action':'experiment','project':args.project,'experiment':args.experiment}));res=s['data']['resources'];plan['resource_pass']=res['workspace_available_bytes']-cfg['native_reservation_bytes']-cfg['concurrent_write_reservation_bytes']>=7*GIB and res['MemAvailable_bytes']>=64*GIB;require(plan['resource_pass'],'new result full restore capacity/RAM HOLD')
   if args.action=='restore':
    dest=P(args.destination or '');require(dest.is_absolute() and dest.is_relative_to(ROOT/'result_recovery') and not os.path.lexists(dest) and '..' not in dest.parts,'new offer recovery requires own native NEW ABSENT destination');bundle=P(offer['manifest']['genuine164_destination_root'].replace('/home/shared','/root/share/mnt164',1))/offer['manifest']['txid'];require((bundle/'COMMIT.json').is_file(),'new result is not durably committed');plan['restore_command']=['sh',str(bundle/'RESTORE.sh'),str(dest)]
    if args.execute:subprocess.run(plan['restore_command'],check=True)
    else:print(json.dumps({'target':target,'result':plan,'mode':'NEW_OFFER_RESTORE_PREFLIGHT_ONLY','source_disposition':'SOURCE_KEEP','scientific_starts':0},indent=2))
   elif args.execute:
    ns={'__name__':'injected'};exec(compile(code,'bound_result_archive.py','exec'),ns);ns['target'](cfg,code)
   else:print(json.dumps({'target':target,'result':plan,'mode':'NO_PAYLOAD_PREPARATION_ONLY','source_disposition':'SOURCE_KEEP','scientific_starts':0},indent=2))
   return
  r=result_record(args.project,args.experiment);check=archive_metadata(r);m=check.pop('manifest');out={'project':args.project,'result':args.experiment,'management_fence':gate,'archive':check,'source_disposition':'SOURCE_KEEP','Source_release_bytes':0}
  if args.action=='restore':
   require(args.destination is not None,'--destination NEW_ABSENT required');dest=P(args.destination);require(dest.is_absolute() and dest.is_relative_to(P('/root/data/full_result_offload_20261023_v1')) and '..' not in dest.parts,'restore destination outside qualified native scope');require(not os.path.lexists(dest),'restore requires NEW ABSENT destination');res=s['data']['resources'];reserve=r['raw_bytes']+64*MIB;out['restore']={'mode':'PREFLIGHT_ONLY_NO_NEW_FILES','destination':str(dest),'raw_bytes':r['raw_bytes'],'workspace_available':res['workspace_available_bytes'],'required_native_bytes_plus_controls':reserve,'resource_pass':res['workspace_available_bytes']-reserve>=7*GIB and res['MemAvailable_bytes']>=64*GIB,'actual_worker':['sh',r['restore_script'],str(dest)],'prior_full_native_target_restore':'VERIFIED_BASELINE_NOT_REPEATED'}
   if args.execute:require(out['restore']['resource_pass'],'restore capacity/RAM HOLD');execute_restore(r,dest);out['restore']['mode']='RESTORE_VERIFIED_NATIVE_TARGET'
  else:out['archive']['execution']='COMPLETED_SELECTOR_REUSED_ZERO_PAYLOAD; new qualified offers are prepared through result outbox policy, no arbitrary selector admitted here'
 print(json.dumps({'target':target,'result':out},indent=2))
if __name__=='__main__':
 try:main()
 except (RuntimeError,FileNotFoundError,PermissionError,subprocess.SubprocessError,json.JSONDecodeError) as e:print(json.dumps({'status':'HOLD_OR_REFUSED','error':str(e),'scientific_starts':0,'Source_mutations':0}),file=sys.stderr);sys.exit(3)

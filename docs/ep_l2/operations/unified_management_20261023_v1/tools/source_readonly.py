"""Finite old174 read API; never import controllers or execute scientific code."""
import os,sys,json,pathlib,hashlib,stat,subprocess,shutil,datetime,re,base64
P=pathlib.Path;EP=P('/workspace/ep_l2_ft20261016_shared');DTC=P('/workspace/dtc-ag8r1-finite-resume-174-v1');CAMPAIGN='mechanism_study_20261019_v1'
def require(x,why):
 if not x:raise RuntimeError(why)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ident(s):return {'dev':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'size':s.st_size,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
def read_json(p):
 p=P(p);require(not p.is_symlink(),'control symlink refused');fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
 with os.fdopen(fd,'rb') as f:
  before=ident(os.fstat(f.fileno()));require(before['size']<=8*1024**2,'bounded control size');b=f.read(8*1024**2+1);require(ident(os.fstat(f.fileno()))==before==ident(p.stat()),'control changed while read')
 return json.loads(b),{'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'identity':before}
def process(d):
 if not d:return {'identity_live':False,'status':'NO_REGISTERED_IDENTITY'}
 p=P('/proc')/str(d.get('pid'));result={'registered':d,'identity_live':False,'status':'ABSENT'}
 try:
  tail=(p/'stat').read_text().rsplit(')',1)[1].split();ticks=int(tail[19]);state=tail[0];result.update(observed_start_ticks=ticks,state=state)
  match=ticks==d.get('start_ticks') and d.get('boot_id',P('/proc/sys/kernel/random/boot_id').read_text().strip())==P('/proc/sys/kernel/random/boot_id').read_text().strip();result.update(identity_live=match and state!='Z',status='LIVE' if match and state!='Z' else ('ZOMBIE_TERMINAL' if match else 'PID_REUSED_NOT_OWNED'))
 except FileNotFoundError:pass
 return result
def source_identity():
 require(os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]','wrong execution host/namespace')
 return {'host':os.uname().nodename,'boot_id':P('/proc/sys/kernel/random/boot_id').read_text().strip(),'namespace':os.readlink('/proc/self/ns/mnt')}
def management_authority(value):
 a=dict(value);a['commit_verified']=False
 if not a:return a
 try:
  p=P(a['commit_receipt']);require(p.is_relative_to(P('/root/data/ep_l2_dtc_l1_management_20261023_v1/source_authority')),'management commit outside task scope');done,ref=read_json(p)
  a['commit_verified']=done.get('state')=='COMMITTED_MANAGEMENT_ONLY_NO_SCIENTIFIC_START' and done.get('epoch')==a.get('epoch') and done.get('holder')==a.get('holder') and done.get('user_authorization_sha256')==a.get('user_authorization_sha256');a['commit_reference']=ref
 except (FileNotFoundError,KeyError):pass
 return a
def ep_status():
 v,ref=read_json(EP/'RUN_REGISTRY.json');c=v[CAMPAIGN];client,cr=read_json(EP/CAMPAIGN/'CLIENT_CONTRACT.json');states={}
 for row in c['attempts']:states[row.get('state','UNKNOWN')]=states.get(row.get('state','UNKNOWN'),0)+1
 return {'project':'EP_L2','canonical':ref,'client_contract':cr,'owner':'E/E2','raw_status_label':c['status'],'actual_starts':c['actual_starts'],'attempt_count':len(c['attempts']),'attempt_states':states,'accepted_result_count':len(c['accepted_results']),'maximum_actual_starts':c['maximum_actual_starts'],'remaining_start_capacity':c['remaining_start_capacity'],'null_budget_semantics':'NOT_UNLIMITED; per-condition qualifications and approvals remain required','screen_actual_starts':c.get('screen_actual_starts'),'screen_maximum':c.get('screen_maximum'),'t0_unix':c['t0_unix'],'controller':c['controller'],'controller_process':process(c.get('controller',{}).get('process')),'unresolved_intents':c.get('uncertain_start_intents'),'active_resource_leases':{k:x for k,x in v['resource_leases'].items() if x.get('status')!='RELEASED'},'management_authority':management_authority(v.get('management_authority',{})),'execution_environment':'original174','scientific_remote_execution_enabled':client['remote_execution_enabled'],'owner_goal_ui':'Not queryable from this API; owner latest full READY reports PAUSED_UNCHANGED','workspace_policy':c['workspace_disk_policy'],'existing_controller_interface':{'entry':client['controller_entry'],'lock':client['controller_lock'],'source_publication':client['source_publication_commit'],'entry_sha256':client['source_files'].get(str(P(client['controller_entry']).relative_to(client['execution_worktree']))),'invoke_allowed_this_stage':False},'consistency':c['actual_starts']==len(c['attempts'])}
def dtc_status():
 coordinator,co=read_json(DTC/'evidence/ROOT_COORDINATOR_CONTINUATION.json');active=P(coordinator['active_evidence']);require(active.is_relative_to(DTC/'evidence'),'DTC active authority escapes scope')
 budget,br=read_json(active/'AG8R1_BUDGET_LEDGER.json');terminal,tr=read_json(active/'c2_c3_once/CONTROLLER_TERMINAL.json');stale,sr=read_json(DTC/'evidence/AG8R1_BUDGET_LEDGER.json');registration,rr=read_json(active/'REGISTRATION_DRAFT.json')
 proc={'pid':coordinator['controller_pid'],'start_ticks':coordinator['controller_start_ticks']};model={'pid':coordinator['model_pid'],'start_ticks':coordinator['model_start_ticks']};result={'project':'DTC_L1','owner':'BA','canonical_coordinator':co,'canonical_active_budget':br,'canonical_terminal':tr,'active_evidence':str(active),'authority_registration_sha256':budget['authority_registration_sha256'],'actual_starts':budget['actual_forks'],'consumed_start_slots':budget['consumed_start_slots'],'maximum_new_starts':budget['maximum_new_starts'],'remaining_scoped_starts':max(0,budget['maximum_new_starts']-budget['consumed_start_slots']),'accepted':budget['accepted'],'F':budget['F'],'unresolved_intents':budget['unresolved_fork_slots'],'automatic_retry':budget['automatic_retry'],'controller_process':process(proc),'model_process':process(model),'terminal_state':terminal['status'],'terminal_reason':terminal.get('reason'),'entries':budget['entries'],'historical_budgets':{k:budget[k] for k in ['old_AG6_consumed','old_AG7_consumed','old_AG7_accepted','old_AG8_consumed','BA_original_consumed']},'stale_initial_budget_ignored':{'reference':sr,'actual_forks':stale['actual_forks'],'reason':'ROOT_COORDINATOR_CONTINUATION.active_evidence supersedes the initial zero-start artifact'},'management_authority':management_authority(coordinator.get('management_authority',{})),'owner_goal_ui':'Not queryable; authoritative owner coordination receipt FINAL_PUBLISHED_STOP, not a live Codex session handle','existing_controller_interface':{'entry':registration['controller_entry'],'own_lock':registration['own_lock'],'canonical_registration':str(P(registration['controller_entry']).parent/'IO_WARNING_AUTHORITY_REGISTRATION.json'),'registration_reference':rr,'invoke_allowed_this_stage':False},'consistency':budget['actual_forks']==terminal['actual_starts']==coordinator['actual_starts_positive_fork_proof'] and budget['accepted']==terminal['accepted']}
 return result
def resources():
 v=os.statvfs('/workspace');mem=int(next(l.split()[1] for l in P('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
 return {'workspace_available_bytes':v.f_bavail*v.f_frsize,'MemAvailable_bytes':mem,'IO_pressure':P('/proc/pressure/io').read_text(),'cgroup':{n:(P('/sys/fs/cgroup')/n).read_text().strip() for n in ['memory.current','memory.max','cpu.max','cpuset.cpus.effective']}}
def path_status(path):
 p=P(path);require(p.is_absolute() and str(p)==path and '..' not in p.parts and str(p).startswith(('/workspace/','/scratch/root/oss-eda/','/usr/bin/')),'source path outside read-only query scope')
 try:
  s=p.lstat();out={'path':path,'exists':True,'readable':os.access(p,os.R_OK),'identity':ident(s),'type':'directory' if stat.S_ISDIR(s.st_mode) else ('symlink' if stat.S_ISLNK(s.st_mode) else 'file')}
  if stat.S_ISLNK(s.st_mode):out['literal_target']=os.readlink(p);out['referent_exists']=p.exists()
  return out
 except FileNotFoundError:return {'path':path,'exists':False,'readable':False,'status':'MISSING_NOT_AVAILABLE'}
 except PermissionError:return {'path':path,'exists':None,'readable':False,'status':'PERMISSION_DENIED_NOT_AVAILABLE'}
def handle(req):
 identity=source_identity();action=req['action'];require(action in ['status','stat_many','environment','experiment','owner_publication'],'unsupported read-only action')
 if action=='status':
  project=req['project'];require(project in ['EP_L2','DTC_L1'],'unknown project');data=ep_status() if project=='EP_L2' else dtc_status();data['resources']=resources()
 elif action=='stat_many':
  paths=req['paths'];require(len(paths)<=256,'bounded path query');data={'paths':[path_status(p) for p in paths]}
 elif action=='environment':data={'python_version':sys.version,'python_executable':sys.executable,'tools':{n:shutil.which(n) for n in ['python3','gcc','g++','nvcc','git','tar','zstd']},'scope':'SSH command environment only; scientific runtime environment remains owner-bound, no application/compiler was executed','resources':resources()}
 elif action=='owner_publication':
  project=req['project'];require(project in ['EP_L2','DTC_L1'],'unknown project');commit=req['commit'];path=req['path'];require(re.fullmatch('[0-9a-f]{40}',commit) and not P(path).is_absolute() and '..' not in P(path).parts and path.startswith('docs/ep_l2/' if project=='EP_L2' else 'docs/dtc_l1/'),'unsafe owner publication reference')
  repo='/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1' if project=='EP_L2' else '/workspace/worktrees/accel-sim-iscas2027-dtc-ag8r1-finite-resume-174-v1';raw=subprocess.check_output(['git','--no-optional-locks','-C',repo,'show',commit+':'+path],timeout=30);require(len(raw)<=8*1024**2,'bounded publication control size');data={'commit':commit,'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'read_only_object_access':True}
  if req.get('include_bytes'):data['raw_base64']=base64.b64encode(raw).decode()
 else:
  name=req['experiment'];require(re.fullmatch(r'[A-Za-z0-9_-]{1,100}',name),'unsafe experiment identifier')
  if req['project']=='EP_L2':
   v,ref=read_json(EP/'RUN_REGISTRY.json');c=v[CAMPAIGN];ids={str(r.get('attempt_id',r.get('id',''))):r for r in c['attempts']};matches=[k for k in ids if k==name or k.startswith(name+'_')];require(len(matches)==1,'unknown or ambiguous registered experiment');key=matches[0];row=ids[key];accepted=c['accepted_results'].get(key);q=(accepted or row).get('qualification_id');data={'id':key,'owner_registered_attempt':row,'owner_accepted_reference':accepted,'source_root':'/workspace/ep_l2_ms20261019_e_results/'+key,'scientific_hold':c.get('scientific_holds',{}).get('qualification:'+str(q)),'registry_reference':ref,'relaunch_allowed':False}
  else:
   require(req['project']=='DTC_L1','unknown project');s=dtc_status();matches=[r for r in s['entries'] if r['point']==name or r['attempt_uuid']==name];require(len(matches)==1,'unknown registered DTC experiment');row=matches[0];data={'id':row['point'],'owner_registered_attempt':row,'owner_accepted_reference':row if row['accepted'] else None,'source_root':row['destination'],'scientific_hold':None if row['accepted'] else 'ORIGINAL_SCIENTIFIC_TERMINAL_FAILURE_NO_RETRY','registry_reference':s['canonical_active_budget'],'relaunch_allowed':False}
 return {'utc':stamp(),'Source_identity':identity,'action':action,'data':data,'Source_new_files':0,'scientific_starts':0}

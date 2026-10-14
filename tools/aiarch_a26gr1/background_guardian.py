"""Download-only pause handoff: strict cumulative limits, receipts, no later gates."""
import argparse,datetime,hashlib,json,os,pathlib,resource,signal,sys,time
from control import ROOT,WORK,allocated
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--pgid',type=int,required=True);a=p.parse_args()
def load(path):
 for attempt in range(5):
  try:return json.loads(path.read_text())
  except json.JSONDecodeError:
   if attempt==4:raise
   time.sleep(.02)
def write(name,data):
 dst=ROOT/name;temp=dst.with_suffix(dst.suffix+'.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(dst)
def own_pid():
 f=pathlib.Path('/proc')/str(a.pid)
 if not f.exists():return False
 if f.joinpath('stat').read_text().split()[2]=='Z':return False
 return b'tools/aiarch_a26gr1/download_parallel.py' in f.joinpath('cmdline').read_bytes() and f.joinpath('cwd').resolve()==WORK.resolve() and os.getpgid(a.pid)==a.pgid
def stop_owned(reason):
 if own_pid():
  os.killpg(a.pgid,signal.SIGTERM);time.sleep(2)
  if own_pid():os.killpg(a.pgid,signal.SIGKILL)
 return {'state':'STOPPED_BY_BUDGET_GUARD','reason':reason}
transfer=load(ROOT/'colmap_transfer_verified.json');extra=transfer['additional_download_and_relay_bytes']
final=None
while True:
 s=load(ROOT/'budget_state.json');elapsed=time.time()-s['r1_goal_started_epoch']+s['prior_cpu_prepare_seconds']
 rec=load(ROOT/'rubble-pixsfm.tgz.download.json');alive=own_pid()
 free=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize
 disk=s['prior_disk_conservative_bytes']+allocated(ROOT)+allocated(WORK)+s.get('controller_new_disk_bytes',0)+transfer['additional_controller_disk_bytes']
 network=s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes']+extra
 status={'state':'DOWNLOADING_BACKGROUND','goal_state':'PAUSE_REQUESTED','verified_archive_bytes':rec['completed_bytes'],'archive_total_bytes':rec['expected_size'],'network_accounted_upper_bound_bytes':network,'disk_allocated_conservative_bytes':disk,'filesystem_free_bytes':free,'cpu_prepare_cumulative_wall_seconds':elapsed,'gpu_initializations':0,'next_scientific_gate':'WAIT_FOR_USER_GOAL_RESUME','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 write('BACKGROUND_STATUS.json',status)
 if not alive:
  if rec.get('status')=='COMPLETE':
   target=ROOT/'downloads/rubble-pixsfm.tgz';sha=hashlib.sha256()
   with target.open('rb') as f:
    while b:=f.read(4*1024**2):
     sha.update(b)
     if time.time()-s['r1_goal_started_epoch']+s['prior_cpu_prepare_seconds']>=14400:raise RuntimeError('CPU_PREPARE_BUDGET_STOP_DURING_FINAL_HASH')
   assert target.stat().st_size==9773995561 and sha.hexdigest()==rec['sha256'];target.chmod(0o400)
   final={**status,'state':'DOWNLOAD_AND_SHA_COMPLETE_WAITING_FOR_GOAL_RESUME','archive_sha256':sha.hexdigest(),'colmap_dual_end_sha':'PASS','tar_scan_or_extraction_started':False,'environment_install_started':False,'gpu_started':False}
  else:final={**status,'state':'DOWNLOADER_EXITED_PARTIAL','reason':'inspect preserved range receipts/log before any retry'}
  break
 if elapsed>=14400-5:final={**status,**stop_owned('CPU_PREPARE_CUMULATIVE_DEADLINE')};break
 if free<64*1024**3+256*1024**2:final={**status,**stop_owned('FILESYSTEM_RESERVE_MARGIN')};break
 if disk>=60*1024**3-256*1024**2:final={**status,**stop_owned('CUMULATIVE_DISK_CAP_MARGIN')};break
 if network>=25*1024**3-256*1024**2:final={**status,**stop_owned('CUMULATIVE_DOWNLOAD_CAP_MARGIN')};break
 # Six simple CPU-only download/guardian processes fit the 24-thread and 48-GiB ceilings.
 rss=0;threads=0
 for f in pathlib.Path('/proc').iterdir():
  if not f.name.isdigit():continue
  try:
   stat=f.joinpath('stat').read_text().split()
   if int(stat[4])!=a.pgid:continue
   values=dict(line.split(':',1) for line in f.joinpath('status').read_text().splitlines() if ':' in line)
   rss+=int(values.get('VmRSS','0 kB').split()[0])*1024;threads+=int(values.get('Threads','0'))
  except (OSError,ValueError):continue
 if rss+resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024>=48*1024**3-512*1024**2:final={**status,**stop_owned('HOST_RSS_MARGIN')};break
 if threads+1>24:final={**status,**stop_owned('CPU_THREAD_TOTAL_LIMIT')};break
 status.update(download_process_tree_rss_bytes=rss,download_process_tree_threads=threads);write('BACKGROUND_STATUS.json',status)
 time.sleep(1)
s=load(ROOT/'budget_state.json')
if not s.get('colmap_large_transfer_merged'):
 s['http_new_body_bytes']+=sum(x['downloaded_body_bytes']+x['warning_metadata_body_bytes'] for x in transfer['files'])
 s['controller_relay_bytes']+=sum(x['controller_to_node_relay_bytes'] for x in transfer['files'])
 s['controller_new_disk_bytes']=s.get('controller_new_disk_bytes',0)+transfer['additional_controller_disk_bytes'];s['colmap_large_transfer_merged']=True
s['cpu_prepare_paused_completed_epoch']=time.time();s['r1_cpu_prepare_active_seconds_before_idle']=time.time()-s['r1_goal_started_epoch'];s['user_pause_idle_after_download_must_not_reset_or_charge_active_prepare_budget']=True
write('budget_state.json',s);write('BACKGROUND_STATUS.json',final);write('BACKGROUND_COMPLETION.json',final)
print(json.dumps(final),flush=True)

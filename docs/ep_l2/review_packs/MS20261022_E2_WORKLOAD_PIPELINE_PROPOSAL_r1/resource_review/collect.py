"""Read-only bounded resource review. Only writes its own JSON evidence file."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
UTIL = ROOT / 'util/ep_l2/mechanism_e'
sys.path.insert(0, str(UTIL))
import coordinator as c

def sha(raw): return hashlib.sha256(raw).hexdigest()
def file_info(path):
    p = Path(path); s = p.stat()
    return dict(path=str(p), device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                size_bytes=s.st_size, allocated_bytes=s.st_blocks * 512)
def fs(path):
    s = os.statvfs(path)
    return dict(path=path, device=os.stat(path).st_dev,
                available_bytes=s.f_bavail*s.f_frsize, total_bytes=s.f_blocks*s.f_frsize,
                free_inodes=s.f_favail, total_inodes=s.f_files)
def proc(pid):
    p=Path('/proc')/str(pid)
    try:
        raw=(p/'stat').read_text(); fields=raw[raw.rfind(')')+2:].split()
        return dict(pid=int(pid), state=fields[0], ppid=int(fields[1]), start_ticks=int(fields[19]),
                    cmdline=(p/'cmdline').read_bytes()[:8192].replace(b'\0',b' ').decode(errors='replace'))
    except (FileNotFoundError, ProcessLookupError): return dict(pid=int(pid), present=False)

reg=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
raw=reg.read_bytes(); data=json.loads(raw); item=data[c.FIELD]
baseline_path=ROOT/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/FINAL_RESOURCE_LEDGER.json'
baseline_raw=baseline_path.read_bytes(); baseline=json.loads(baseline_raw)
live=[dict(group=g,key=k,**{a:r.get(a) for a in ('status','host','owner','experiment_id','cpu_units','memory_bytes','process','disk_growth_bytes','monitor_reserve_bytes')})
      for g in ('runs','resource_leases') for k,r in data[g].items() if r.get('status') in ('RUNNING','RESERVED')]
matched=[]; scanned=0
for p in Path('/proc').iterdir():
    if not p.name.isdecimal(): continue
    scanned+=1
    if scanned>8192: raise RuntimeError('bounded process inspection limit')
    r=proc(p.name); cmd=r.get('cmdline','')
    if r['pid'] == os.getpid(): continue
    try: exe=(p/'exe').resolve().name
    except (FileNotFoundError,PermissionError): exe=''
    if exe=='accel-sim.out' or (exe.startswith('python') and any(x in cmd for x in ('mechanism_e/controller.py','mechanism_e/durable_exit.py','mechanism_e/runner.py','CAPACITY_DIAGNOSTIC_r1/run.py'))):
        matched.append(r)

# Metadata-only bounded inspection of this exact new-results root: never reads raw/trace bytes.
begin=time.monotonic(); stack=[c.OUTPUT]; files=0; dirs=0; sizes=0; allocated=0; errors=[]
while stack:
    directory=stack.pop(); dirs+=1
    if dirs>1024 or files>16384 or time.monotonic()-begin>10: raise RuntimeError('bounded result metadata limit')
    try:
        with os.scandir(directory) as entries:
            for x in entries:
                try:
                    s=x.stat(follow_symlinks=False)
                    if stat.S_ISDIR(s.st_mode): stack.append(Path(x.path))
                    elif stat.S_ISREG(s.st_mode): files+=1; sizes+=s.st_size; allocated+=s.st_blocks*512
                except FileNotFoundError: errors.append(x.path)
    except FileNotFoundError: errors.append(str(directory))
usage={'old_bytes':baseline['output_usage']['old_bytes'],
       'new_bytes':max(sizes,baseline['output_usage']['new_bytes'])}
usage['total_bytes']=usage['old_bytes']+usage['new_bytes']
resources=c.local_resources()
forecast=[]; view=copy.deepcopy(data)
for n in range(1,5):
    try:
        c.resource_gate(view,'simulation',1,8*c.GIB,384*2**20,resources,usage)
        outcome={'concurrent_endpoints':n,'fits_read_only_resource_gate':True}
        view['runs']['READONLY_PROPOSAL_'+str(n)]=dict(status='RESERVED',host=socket.gethostname(),
            experiment_id=c.CAMPAIGN,cpu_units=1,memory_bytes=8*c.GIB,disk_growth_bytes=384*2**20,
            monitor_reserve_bytes=2*c.GIB,result_directory='/__E2_READONLY_FORECAST_NONEXISTENT__/'+str(n),scan=False)
    except ValueError as e: outcome={'concurrent_endpoints':n,'fits_read_only_resource_gate':False,'reason':str(e)}
    forecast.append(outcome)

G=2**30; app=4*384*2**20; qualification=128*2**20; metadata=32*2**20
limits={k:item.get(k) for k in ('maximum_actual_starts','remaining_start_capacity','start_deadline_unix','intake_deadline_unix','per_end_timeout_seconds','additional_results_max_bytes','old_plus_new_results_max_bytes')}
lock_files=[file_info('/workspace/ep_l2_ft20261016_shared/REGISTRY.lock'),file_info('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/CONTROLLER.lock')]
lock_inodes={str(x['inode']) for x in lock_files}
lock_lines=[line for line in Path('/proc/locks').read_text().splitlines() if any(word.split(':')[-1] in lock_inodes for word in line.split())]
out=dict(schema='E2_WORKLOAD_PIPELINE_RESOURCE_COST_READ_ONLY_V1',
 at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 at_beijing=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
 host=socket.gethostname(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 registry=dict(**file_info(reg),sha256=sha(raw),unchanged_after_collection=sha(reg.read_bytes())==sha(raw)),
 frozen=dict(t0_unix=item['t0_unix'],actual_starts=item['actual_starts'],actual_start_recount=sum(x.get('actual_start') is True for x in item['attempts']),
             contingency_consumed=sum(x.get('actual_start') is True and c.policy_v2.charged_bucket(x,item['reservations'])=='contingency' for x in item['attempts']),
             limits=limits,formal_concurrency=item['formal_simulator_concurrency'],original_reservations=item['reservations']),
 controller=item['controller'],controller_process=proc(item['controller']['process']['pid']),
 known_terminal_native_and_collector=[proc(x) for x in (3089747,3089751)],
 active_registry_rows=live,process_inspection=dict(pid_count=scanned,matching_simulator_and_E_supervisor_processes=matched),
 locks=dict(files=lock_files,matching_proc_locks=lock_lines,probe_lock_acquisition=False),
 resources=resources,filesystems=[fs('/workspace'),fs('/root/share')],
 cpu=dict(online=os.cpu_count(),affinity_count=len(os.sched_getaffinity(0)),loadavg=Path('/proc/loadavg').read_text().strip(),
          cgroup_cpu_max=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),cgroup_cpuset_effective=Path('/sys/fs/cgroup/cpuset.cpus.effective').read_text().strip()),
 memory=dict(cgroup_max=Path('/sys/fs/cgroup/memory.max').read_text().strip(),cgroup_current_bytes=int(Path('/sys/fs/cgroup/memory.current').read_text())),
 cumulative_generation=dict(final_baseline=dict(path=str(baseline_path),sha256=sha(baseline_raw),output_usage=baseline['output_usage']),
    bounded_new_root_metadata=dict(root=str(c.OUTPUT),files=files,directories=dirs,logical_bytes=sizes,allocated_bytes=allocated,seconds=time.monotonic()-begin,vanished_paths=errors,content_bytes_read=0),
    conservative_usage=usage,metadata_growth_since_final_bytes=max(0,sizes-baseline['output_usage']['new_bytes']),
    old_usage_not_recounted_or_reset=True,remaining_new_bytes=limits['additional_results_max_bytes']-usage['new_bytes'],
    remaining_total_bytes=limits['old_plus_new_results_max_bytes']-usage['total_bytes']),
 resource_forecast_only=forecast,
 proposed_scope=dict(status='NOT_AUTHORIZED_NOT_RESERVED_NOT_EXECUTED',new_actual_starts_maximum=4,
    proposed_new_user_subbatches=[dict(id='FWT_MAIN61_RESTORATION_PROPOSED',starts=2,whole_endpoint_cap_bytes=384*2**20),dict(id='SGEMM_MAIN61_EXPLORATORY_PROPOSED',starts=2,whole_endpoint_cap_bytes=384*2**20)],
    original_32_and_contingency_buckets_not_expanded=True,actual_count_after_all_four_starts=50,
    application_whole_endpoint_caps_bytes=app,qualification_future_only_separate_cap_bytes=qualification,
    collector_metadata_future_only_separate_cap_bytes=metadata,all_proposed_generation_cap_bytes=app+qualification+metadata,
    remaining_new_after_all_proposed_bytes=limits['additional_results_max_bytes']-usage['new_bytes']-app-qualification-metadata,
    remaining_total_after_all_proposed_bytes=limits['old_plus_new_results_max_bytes']-usage['total_bytes']-app-qualification-metadata,
    four_endpoint_cpu_units=4,four_endpoint_reserved_memory_bytes=32*G,
    no_fixed_lane_count_cap=True,transactional_admission_required_before_every_actual_start=True,
    proposed_new_condition_timeout_seconds=None,proposed_timeout_policy_requires_exact_user_approval=True,
    walltime={'FWT_S_minutes_prior_only':[80,110],'FWT_F_minutes_prior_only':[85,120],'SGEMM_each_endpoint':'UNKNOWN','whole_batch_completion':'UNKNOWN; SGEMM full-application runtime unmeasured'},
    native_or_application_work_performed_this_review=False))
(HERE/'RESOURCE_COST_REVIEW.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'resource_gate_forecast':forecast,'active_rows':len(live),'matching_processes':len(matched),'registry_unchanged':out['registry']['unchanged_after_collection'],'usage':usage,'resources':resources,'proposed_bytes':app+qualification+metadata}))

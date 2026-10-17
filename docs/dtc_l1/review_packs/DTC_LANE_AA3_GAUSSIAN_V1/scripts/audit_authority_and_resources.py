"""All-project resource and exact old-controller audit; never signal or acquire locks."""
from common import *

def capture():
    s=snapshot();s['cpu_stat']=Path('/proc/stat').read_text().splitlines()[0]
    s['loadavg']=Path('/proc/loadavg').read_text();s['self_affinity']=sorted(os.sched_getaffinity(0))
    s['cgroup_cpu_max']=Path('/sys/fs/cgroup/cpu.max').read_text().strip()
    for p in s['processes']:
        q=Path('/proc')/str(p['pid'])
        try:
            p['ppid']=int((q/'stat').read_text().rsplit(')',1)[1].split()[1]);p['cwd']=os.readlink(q/'cwd');p['exe']=os.readlink(q/'exe');p['affinity']=sorted(os.sched_getaffinity(p['pid']));p['io']=(q/'io').read_text()
        except OSError:p['racy_proc_read']='UNAVAILABLE_PROCESS_CHANGED'
    return s

def locks(s):
    result=[]
    for p in s['processes']:
        for fd in (Path('/proc')/str(p['pid'])/'fdinfo').glob('*'):
            try:
                txt=fd.read_text()
                if '\nlock:' not in txt:continue
                target=os.readlink(fd.parent.parent/'fd'/fd.name)
                if any(x in target.lower() for x in ['dtc','fast64','lane']):result.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],fd=fd.name,target=target,fdinfo=txt))
            except OSError:pass
    return result

def main():
    first=capture();write(ROOT/'RESOURCE_FIRST.json',first);time.sleep(10.1)
    second=capture();write(ROOT/'RESOURCE_SECOND.json',second)
    rows=[]
    for phase,s in [('first',first),('second',second)]:
        cg=s['cgroup'];rows.append(dict(phase=phase,utc=s['utc'],host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup_current_bytes=cg['memory.current'],cgroup_limit_bytes=cg['memory.max'],cgroup_headroom_bytes=int(cg['memory.max'])-int(cg['memory.current']) if cg['memory.max']!='max' else 'UNLIMITED',all_project_RSS_sum_bytes=s['proc_RSS_sum_bytes'],cgroup_swap_bytes=cg['memory.swap.current'],pswpin=s['pswpin'],pswpout=s['pswpout'],memory_full_PSI_avg10=s['pressure']['memory']['full']['avg10'],io_full_PSI_avg10=s['pressure']['io']['full']['avg10'],cpu_some_PSI_avg10=s['pressure']['cpu']['some']['avg10'],disk_free_bytes=s['disk_free_bytes'],cpu_max=s['cgroup_cpu_max'],visible_affinity_cpus=len(s['self_affinity']),loadavg=s['loadavg'].strip(),AA3_simulators=0,admitted=False))
    table(PACK/'EXECUTION_RESOURCES.tsv',rows)
    checks=resource_checks(first,second)
    cpu1=list(map(int,first['cpu_stat'].split()[1:]));cpu2=list(map(int,second['cpu_stat'].split()[1:]));delta=[b-a for a,b in zip(cpu1,cpu2)]
    write(PACK/'RESOURCE_AUDIT.json',dict(utc=now(),checks=checks,resource_numeric_limits_pass=all(checks.values()),all_projects_included=True,probe_seconds=(second['monotonic_ns']-first['monotonic_ns'])/1e9,cpu_total_ticks=sum(delta[:8]),cpu_idle_iowait_ticks=sum(delta[3:5]),cpu_idle_fraction=sum(delta[3:5])/sum(delta[:8]),io_accounting='cgroup io.stat, host diskstats, per-project process io and RSS in raw snapshots',fresh_resource_pass_does_not_close_execution_authority=True))
    lock_records=locks(second)
    oldlock=Path('/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock');st=oldlock.stat()
    assert not proc(1425986)
    assert not any(l['target']==str(oldlock) for l in lock_records)
    write(PACK/'WATCHER_RELEASE_RECEIPT.json',dict(utc=now(),pid=1425986,start_ticks=584741606,parent_no_longer_exists=True,original_lock_file_preserved=True,lock_path=str(oldlock),device=st.st_dev,inode=st.st_ino,expected_original_inode=37920070,original_inode_unchanged=st.st_ino==37920070,no_remaining_fdinfo_FLOCK_holders=True,all_DTC_lock_records=lock_records,signal_sent='ONE_SIGTERM_TO_PIDFD_BOUND_PARENT',children_or_other_processes_signaled=False))
    selected=[];sources=[];oldrepo=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')
    names=['monitor_fast64_3_dynamic_base_evidence_v1.py','collect_fast64_repaired_ramp_v1.sh','collect_fast64_repaired_ramp2_v1.sh','collect_fast64_3_base_matrix_v2.py','collect_fast64_6_precompute_v1.sh','collect_fast64_6_precompute_v2.sh','collect_fast64_6_precompute_v3.sh','collect_fast64_6_precompute_v10.sh','validate_fast64_trace_row_alias_v3.py','prepare_fast64_3_core41_registry_v1.py','collect_fast64_1_qualification.sh','deferred_fast64_1_telemetry_rerun.sh','run_fast64_trace.sh']
    for name in names:
        p=oldrepo/'util/dtc_l1'/name;dest=PACK/'inputs/old_controls'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        sources.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,copied_source_sha256=sha(dest)))
    for name in ['FAST64_SINGLE_GOAL_CONTRACT.md','handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md']:
        p=oldrepo/'docs/dtc_l1/fast64'/name;dest=PACK/'inputs/old_controls'/Path(name).name;shutil.copy2(p,dest);sources.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,copied_source_sha256=sha(dest)))
    table(PACK/'OLD_CONTROL_SOURCE_SHA256.tsv',sources)
    for p in second['processes']:
        if p.get('cwd')!=str(oldrepo) and not any(a==str(oldrepo) or a.startswith(str(oldrepo)+'/') for a in p['argv']):continue
        a=p['argv']
        if a and a[0]=='sleep':continue
        if p['pid']==3291777:
            kind='LIVE_DEFERRED_DISPATCH_CAPABLE_AUTHORITY_UNRESOLVED_NOT_EXEMPT'
        elif any('accel-sim.out'==Path(v).name for v in a):kind='OTHER_DTC_SIMULATOR_STOP'
        else:kind='HISTORICAL_COLLECTOR_OR_VALIDATOR_LEFT_UNCHANGED; NOT_USED_AS_AA3_AUTHORITY'
        selected.append(dict(**p,classification=kind))
    other=proc(3291777);assert other and other['start_ticks']==550530984
    assert other['argv']==['bash',str(oldrepo/'util/dtc_l1/deferred_fast64_1_telemetry_rerun.sh')]
    oldcore=git('/workspace/worktrees/gpgpu-sim-decoupled-l1-m5','rev-parse','HEAD')
    dispatcher=(oldrepo/'util/dtc_l1/deferred_fast64_1_telemetry_rerun.sh').read_text()
    old_rows=re.search(r'old_rows=\((.*?)\)',dispatcher,re.S).group(1).split();gates=[]
    for row in old_rows:
        p=Path('/workspace/fast64-runs')/row/'RUN_MANIFEST.tsv';txt=p.read_text() if p.exists() else ''
        gates.append(dict(row=row,manifest_exists=p.exists(),manifest_sha256=sha(p) if p.exists() else 'UNAVAILABLE',observed_exit_status=re.findall(r'^simulator_exit_status\s+(\S+)',txt,re.M) or ['UNAVAILABLE']))
    actualsims=[]
    for p in second['processes']:
        if 'accel-sim.out' in p.get('exe','') or any(Path(a).name=='accel-sim.out' for a in p['argv']):
            external=p.get('exe','').startswith('/workspace/ep_l2_potential20261017_lane5_results/')
            actualsims.append(dict(**p,classification='EXTERNAL_EP_L2_ALL_RESOURCE_COUNTED' if external else 'UNKNOWN_OR_DTC_SIMULATOR_STOP',binary_sha256=sha(p['exe']) if Path(p.get('exe','')).is_file() else 'UNAVAILABLE'))
    write(PACK/'OTHER_AUTHORITY_REVIEW.json',dict(utc=now(),status='STOP_LEGAL_EXECUTION_AUTHORITY_NOT_CLOSED',processes=selected,all_visible_actual_simulators=actualsims,deferred_exact_identity=other,deferred_script_sha256=sha(oldrepo/'util/dtc_l1/deferred_fast64_1_telemetry_rerun.sh'),deferred_expected_Core='bbcbb5e7565417102087bc80b14c349b4e568c05',deferred_current_Core=oldcore,deferred_current_Core_gate_pass=False,old_row_gates=gates,full_future_path='wait seven terminal statuses -> exact oldCore/runtime/target gates -> seven setsid runner starts',old_path_scientific_status='R1 SUPERSEDED_NONFORMAL_EXECUTION_PATH_AT_RISK; not AA3 authorized workload',why_not_ignored='Technical gate failure is not proof of permanent retirement, ownership release or current scientific authorization. Live source has future dispatch side effects; it is not a read-only collector.',why_not_terminated='AA3 section II permits a single SIGTERM to specified Core41 watcher only. No explicit permission for PID3291777 or other controls.',AA3_execution_authority_acquired=False,AA3_actual_starts=0,old_locks_acquired_or_deleted=False,other_processes_signaled=False))
    print('Core41 watcher parent exited and inherited FLOCK released; other deferred dispatcher remains. STOP, 0/4.')

if __name__=='__main__':main()

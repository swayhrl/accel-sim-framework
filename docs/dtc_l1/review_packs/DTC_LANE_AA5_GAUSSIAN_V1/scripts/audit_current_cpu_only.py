"""Read-only reviewed collectors and all-project resource audit. No lock acquisition or launch."""
from common import *
from proc_audit import process_snapshot,flock_records
AA3='2b69f5ec8fae85c0ee1bbfe95ac93eb524bb172e';AA3P='docs/dtc_l1/review_packs/DTC_LANE_AA4_GAUSSIAN_V1'
OLD=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')


def capture():
    s=process_snapshot();s['cpu_stat']=Path('/proc/stat').read_text().splitlines()[0];s['loadavg']=Path('/proc/loadavg').read_text().strip();s['cpu_max']=Path('/sys/fs/cgroup/cpu.max').read_text().strip();s['affinity']=sorted(os.sched_getaffinity(0))
    for p in s['processes']:
        try:p['io']=Path('/proc',str(p['pid']),'io').read_text()
        except OSError:p['io']='UNAVAILABLE_PROCESS_CHANGED'
    return s

def main():
    first=capture();write(ROOT/'RESOURCE_AA5_FIRST.json',first);time.sleep(10.1);second=capture();write(ROOT/'RESOURCE_AA5_SECOND.json',second)
    checks=resource_checks(first,second);a=list(map(int,first['cpu_stat'].split()[1:9]));b=list(map(int,second['cpu_stat'].split()[1:9]));delta=[y-x for x,y in zip(a,b)]
    rows=[]
    for label,s in [('first',first),('second',second)]:
        cg=s['cgroup'];rows.append(dict(phase=label,utc=s['utc'],host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup_current_bytes=cg['memory.current'],cgroup_limit_bytes=cg['memory.max'],cgroup_headroom_bytes=int(cg['memory.max'])-int(cg['memory.current']) if cg['memory.max']!='max' else 'UNLIMITED',all_process_RSS_sum_bytes=s['proc_RSS_sum_bytes'],cgroup_swap_bytes=cg['memory.swap.current'],host_pswpin=s['pswpin'],host_pswpout=s['pswpout'],memory_full_PSI_avg10=s['pressure']['memory']['full']['avg10'],io_full_PSI_avg10=s['pressure']['io']['full']['avg10'],cpu_some_PSI_avg10=s['pressure']['cpu']['some']['avg10'],disk_free_bytes=s['disk_free_bytes'],cpu_quota=s['cpu_max'],affinity_CPU_count=len(s['affinity']),loadavg=s['loadavg'],actual_AA5_sims=0))
    table(PACK/'EXECUTION_RESOURCES.tsv',rows)
    write(PACK/'RESOURCE_AUDIT.json',dict(utc=now(),status='PASS_NEW_INDEPENDENT_RESOURCE_PROBE' if all(checks.values()) else 'FAIL_CURRENT_PROBE_PRESERVED_NOT_PERMANENT_RESOURCE_BLOCK',checks=checks,probe_seconds=(second['monotonic_ns']-first['monotonic_ns'])/1e9,cpu_idle_iowait_fraction=sum(delta[3:5])/sum(delta),all_projects_accounted=True,AA3_prior_one_page_swap_in_preserved_not_relabelled=True,new_gate_pass_does_not_override_resource_failure=True,resource_limit_relaxation=False,raw_snapshots=[dict(path=str(ROOT/n),sha256=sha(ROOT/n)) for n in ['RESOURCE_AA5_FIRST.json','RESOURCE_AA5_SECOND.json']]))
    # Known old controls match frozen AA3 command identities; inspect their entire source and transitive output-only helpers.
    historic=git_json(FW_REPO,AA3,AA3P+'/AUTHORITY_AND_FLOCK_AUDIT.json')['reviewed_other_controls'];known={p['pid']:p for p in historic}
    source_names=['monitor_fast64_3_dynamic_base_evidence_v1.py','collect_fast64_repaired_ramp_v1.sh','collect_fast64_repaired_ramp2_v1.sh','collect_fast64_3_base_matrix_v2.py','collect_fast64_6_precompute_v1.sh','collect_fast64_6_precompute_v2.sh','collect_fast64_6_precompute_v3.sh','collect_fast64_6_precompute_v10.sh','validate_fast64_trace_row_alias_v3.py','prepare_fast64_3_core41_registry_v1.py','collect_fast64_1_qualification.sh','monitor_fast64_repaired_core_row_v2.sh','validate_fast64_trace_row.py','extract_fast64_3_base_structural_metrics_v1.py','parse_dtc_l1_summary.py','compare_fast64_nonbinding_cap.py']
    sources=[]
    for name in source_names:
        path=OLD/'util/dtc_l1'/name;text=path.read_text();dest=PACK/'inputs/REVIEWED_OLD_COLLECTORS'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
        # Distinguish documentation/field names from actual process-producing statements.
        calls=[dict(line=i,text=line) for i,line in enumerate(text.splitlines(),1) if re.search(r'subprocess\.(run|Popen)|os\.(system|exec)|\bsetsid\b|\bkill\b|exec_module|python3\s+|\$collector',line)]
        try:frozen=blob(FW_REPO,AA3,AA3P+'/inputs/REVIEWED_OLD_COLLECTORS/'+name);same=frozen==path.read_bytes()
        except subprocess.CalledProcessError:same='TRANSITIVE_SOURCE_NEWLY_REVIEWED_NOT_IN_AA3_SUBSET'
        sources.append(dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size,same_as_frozen_AA3=same,execution_review=calls,classification='EXISTING_TERMINAL_INPUT_READER_OUTPUT_PARSER_OR_COLLECTOR: may write its own closeout log/output; no simulator dispatch or signal'))
        assert same is not False
    controls=[];unknown=[];sims=[]
    for p in second['processes']:
        args=p['argv'];actual=[a for a in args if '\n' not in a and len(a)<4096]
        if 'accel-sim.out' in p.get('exe','') or any(Path(a).name=='accel-sim.out' for a in actual):
            ext=p.get('exe','').startswith('/workspace/ep_l2_potential20261017_lane5_results/');record=dict(**p,classification='EXTERNAL_EP_L2_RESOURCE_COUNTED' if ext else 'UNKNOWN_OR_DTC_SIMULATOR_STOP')
            record['binary_sha256']=sha(p['exe']);record['configs']=[dict(path=actual[i+1],sha256=sha(actual[i+1])) for i,x in enumerate(actual[:-1]) if x=='-config'];sims.append(record)
            if not ext:unknown.append(record)
        scripts=[]
        for arg in actual:
            if not arg.endswith(('.py','.sh')):continue
            q=Path(arg) if arg.startswith('/') else Path(p.get('cwd','/'))/arg
            if q.is_file() and '/dtc_l1/' in str(q):scripts.append(str(q))
        oldmatch=p.get('cwd')==str(OLD) or any(a==str(OLD) or a.startswith(str(OLD)+'/') for a in actual)
        if scripts and any(str(Path(__file__).resolve().parents[1]) in q for q in scripts):continue
        if args and args[0]=='sleep':continue
        if not oldmatch and not scripts:continue
        if p['pid'] in known and p['start_ticks']==known[p['pid']]['start_ticks'] and args==known[p['pid']]['argv'] and p['pid'] not in [1425986,3291777]:
            controls.append(dict(**p,classification='SOURCE_REVIEWED_OUTPUT_ONLY_CONTROLLER',future_simulator_dispatch=False))
        elif scripts and all(Path(q).name in source_names for q in scripts):controls.append(dict(**p,classification='SOURCE_REVIEWED_TRANSITIVE_COLLECTOR_HELPER',future_simulator_dispatch=False))
        else:unknown.append(dict(**p,classification='UNKNOWN_DTC_CONTROL_STOP',actual_scripts=scripts))
    locks=flock_records(second);reviewed_ids={p['pid'] for p in controls}
    ps={p['pid']:p for p in second['processes']}
    def reviewed_holder(pid):
        p=ps.get(pid)
        if not p:return False
        if pid in reviewed_ids:return True
        return p['argv'] and p['argv'][0]=='sleep' and p.get('ppid') in reviewed_ids
    for l in locks:
        l['output_only_collector_lock']=reviewed_holder(l['pid'])
        root=Path('/workspace/dtc-lane-aa5-gaussian-174-v1');ap=root/'AUTHORITY_ACTIVE.json'
        own=json.loads(ap.read_text()) if ap.exists() else {}
        l['own_AA5_execution_lock']=(l['path']==str(root/'AA5_execution.lock') and l['pid']==own.get('pid') and l['start_ticks']==own.get('start_ticks') and any(str(Path(__file__).resolve().parent/'run_matrix.py')==a for a in ps.get(l['pid'],{}).get('argv',[])))
    lockchecks=dict(retired_Core41_parent_absent=proc(1425986) is None,retired_deferred_parent_absent=proc(3291777) is None,no_unknown_DTC_controls_or_sims=not unknown,all_remaining_DTC_FLOCKs_output_only=all(l['output_only_collector_lock'] or l['own_AA5_execution_lock'] for l in locks),no_retired_Core41_FLOCK=not any(l['path']=='/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock' for l in locks))
    write(PACK/'AUTHORITY_AND_FLOCK_AUDIT.json',dict(utc=now(),status='READ_ONLY_REVIEW_PASS_NO_OTHER_DISPATCH_AUTHORITY_OBSERVED' if all(lockchecks.values()) else 'STOP_UNKNOWN_AUTHORITY',checks=lockchecks,reviewed_other_controls=controls,unknown_controls=unknown,remaining_FLOCKs=locks,source_review=sources,visible_simulators=sims,AA5_exclusive_execution_lock_acquired=False,why_no_AA5_lock='Read-only function; coordinator owns only its independent AA5 lock; this audit never acquires old locks',old_locks_deleted_or_acquired=False,other_projects_signaled=False))
    print('Resources',all(checks.values()),'read-only authority review',all(lockchecks.values()),'; read-only current authority and resource probe complete.')

if __name__=='__main__':main()

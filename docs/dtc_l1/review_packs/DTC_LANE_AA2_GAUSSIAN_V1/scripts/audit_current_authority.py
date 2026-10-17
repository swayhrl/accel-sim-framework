"""Read current all-project resource usage, processes and locks. Never acquire them."""
from common import *


def classify(s):
    foreign=[];external=[];other_dtc=[]
    for p in s['processes']:
        a=p['argv']
        if not a:continue
        # Inspect actual script arguments rather than matching the text inside
        # an unrelated shell's -c argument, which can contain this program.
        scripts=[Path(v) for v in a if v.endswith(('.py','.sh')) and v.startswith('/') and Path(v).is_file()]
        for script in scripts:
            if any(tag in script.name for tag in ['auto_dispatch_fast64','service_closure_dispatch','run_pilot','run_holdout']):
                foreign.append(dict(**p,classification='FOREIGN_DTC_DISPATCH_CAPABLE_AUTHORITY',
                    script=str(script),script_sha256=sha(script),
                    action_by_AA2='NONE_NO_SIGNAL_NO_LOCK_ACQUISITION'))
            elif '/dtc_l1/' in str(script):
                other_dtc.append(dict(**p,script=str(script),script_sha256=sha(script),
                     classification='DTC_MONITOR_OR_HELPER_SOURCE_REVIEW_REQUIRED_NOT_BLANKET_EXEMPTED'))
        if Path(a[0]).name=='accel-sim.out':
            binary=Path(a[0]);configs=[]
            for i,arg in enumerate(a[:-1]):
                if arg=='-config':
                    cfg=Path(a[i+1]);configs.append(dict(path=str(cfg),sha256=sha(cfg)))
            kind='EXTERNAL_EP_L2_SIM_RESOURCE_COUNTED' if str(binary).startswith('/workspace/ep_l2_potential20261017_lane5_results/') else 'FOREIGN_OR_UNKNOWN_SIMULATOR'
            entry=dict(**p,classification=kind,binary_sha256=sha(binary),configs=configs,
                       CPU_and_RSS_and_IO_counted=True)
            external.append(entry)
            if kind=='FOREIGN_OR_UNKNOWN_SIMULATOR':foreign.append(entry)
    return foreign,external,other_dtc


def main():
    first=snapshot();write(ROOT/'AUTHORITY_PROBE_FIRST.json',first)
    start=time.monotonic()
    while time.monotonic()-start<10:time.sleep(max(0,min(1,10-(time.monotonic()-start))))
    second=snapshot();write(ROOT/'AUTHORITY_PROBE_SECOND.json',second)
    observations=[]
    for label,s in [('first',first),('second',second)]:
        foreign,external,helpers=classify(s)
        locks=[]
        for root in sorted(Path('/workspace').glob('dtc-*')):
            if root.is_dir():
                for p in sorted(root.glob('*.lock')):locks.append(lock_observation(p,s))
                if (root/'r2-attempts').is_dir():
                    for p in sorted((root/'r2-attempts').glob('*.lock')):locks.append(lock_observation(p,s))
        legacy=Path('/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock')
        locks.append(lock_observation(legacy,s))
        observations.append(dict(label=label,utc=s['utc'],foreign_DTC_authorities=foreign,
               external_project_simulators=external,other_DTC_helpers_requiring_review=helpers,
               locks=locks,no_foreign_DTC_authority=len(foreign)==0,
               no_observed_old_lock_owners=all(not l['owners'] for l in locks)))
    checks=resource_checks(first,second)
    checks['no_foreign_DTC_authority']=all(r['no_foreign_DTC_authority'] for r in observations)
    checks['no_old_lock_owners']=all(r['no_observed_old_lock_owners'] for r in observations)
    checks['all_other_DTC_helpers_reviewed']=all(not r['other_DTC_helpers_requiring_review'] for r in observations)
    write(PACK/'CURRENT_EXECUTION_ADMISSION.json',dict(status='HOLD_EXECUTION_AUTHORITY_OR_RESOURCES' if not all(checks.values()) else 'RESOURCE_ONLY_PASS_NOT_SCIENTIFIC_ADMISSION',
          checks=checks,observations=observations,utc=now(),AA2_authority_acquired=False,AA2_simulator_starts=0,
          old_locks_acquired=False,other_processes_signaled=False,old_files_deleted=False,
          note='U termination does not waive current authorities, unknown helpers or current external project resource usage. A future run requires a fresh full audit.'))
    summary=[]
    for label,s in [('first',first),('second',second)]:
        cg=s['cgroup']
        summary.append(dict(phase=label,utc=s['utc'],cgroup_memory_current_bytes=cg['memory.current'],
             cgroup_memory_max_bytes=cg['memory.max'],
             cgroup_headroom_bytes=int(cg['memory.max'])-int(cg['memory.current']) if cg['memory.max']!='max' else 'UNLIMITED',
             host_MemAvailable_bytes=s['host_MemAvailable_bytes'],proc_RSS_sum_bytes=s['proc_RSS_sum_bytes'],
             cgroup_swap_current_bytes=cg['memory.swap.current'],pswpin=s['pswpin'],pswpout=s['pswpout'],
             memory_full_PSI_avg10=s['pressure']['memory']['full']['avg10'],
             IO_full_PSI_avg10=s['pressure']['io']['full']['avg10'],disk_free_bytes=s['disk_free_bytes'],
             cgroup_IO_stat=cg['io.stat'].replace('\n','; '),actual_AA2_sims=0,admitted=False))
    table(PACK/'EXECUTION_RESOURCES.tsv',summary)
    print('Current authority/resource audit:',[k for k,v in checks.items() if not v])


if __name__=='__main__':main()

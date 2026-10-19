#!/usr/bin/env python3
"""Directed CPU tests for AG resource decisions, no signals/launches."""
from common import *
from resource_policy import *
import copy


def sample(seconds=0):
    return dict(host='huangrulin-174',uid=0,monotonic_ns=int(seconds*1e9),host_MemAvailable_bytes=64*GIB,
        disk_free_bytes=20*GIB,pswpin=100,pswpout=200,
        cgroup={'memory.current':str(32*GIB),'memory.max':str(128*GIB),
                'memory.swap.current':str(120*MIB),'events':{'oom':0,'oom_kill':17}},
        pressure={'memory':{'full':{'avg10':'0'}},'io':{'full':{'avg10':'10'}}})


def main():
    tests=[]
    def passed(name):tests.append(name)
    a=sample();b=sample(10);b['pswpin']+=1
    assert all(admission_checks(a,b).values());passed('single_global_page_is_not_admission_veto')
    policy=RuntimePolicy(a);r=policy.observe(b)
    assert r['decision']=='WARN' and not r['stop_reasons'] and r['next_full_sample_seconds']==5
    passed('single_global_page_warns_increases_sampling_never_stops')
    b=sample(1);b['cgroup']['events']['oom_kill']+=1
    assert RuntimePolicy(a).observe(b)['decision']=='STOP';passed('new_oom_kill_stops_immediately_on_observation')
    for field in ['host','cg','disk']:
        b=sample(1)
        if field=='host':b['host_MemAvailable_bytes']=8*GIB-1
        if field=='cg':b['cgroup']['memory.current']=str(120*GIB+1)
        if field=='disk':b['disk_free_bytes']=2*GIB-1
        assert RuntimePolicy(a).observe(b)['decision']=='STOP'
    passed('original_memory_and_disk_emergency_lines_retained')
    policy=RuntimePolicy(a)
    for t,n in [(10,1),(15,1),(20,2),(30,3)]:
        b=sample(t);b['cgroup']['memory.swap.current']=str(136*MIB)
        r=policy.observe(b)
        assert r['qualified_swap_samples']==n
        assert (r['decision']=='STOP')==(n==3)
    passed('16MiB_swap_requires_three_ge10s_observations_not_fast_warn_samples')
    policy=RuntimePolicy(a)
    for t,delta,n in [(10,16,1),(20,15,0),(30,16,1),(40,16,2)]:
        b=sample(t);b['cgroup']['memory.swap.current']=str((120+delta)*MIB)
        r=policy.observe(b);assert r['qualified_swap_samples']==n and r['decision']!='STOP'
    passed('swap_below_threshold_resets_persistence')
    policy=RuntimePolicy(a)
    for t,delta,n in [(10,16,1),(20,16,2),(25,15,0),(30,16,1)]:
        b=sample(t);b['cgroup']['memory.swap.current']=str((120+delta)*MIB)
        r=policy.observe(b);assert r['qualified_swap_samples']==n and r['decision']!='STOP'
    passed('faster_WARN_sample_recovery_also_resets_swap_persistence')
    for kind,limit in [('memory',10),('io',25)]:
        policy=RuntimePolicy(a)
        for t in [5,10,30,35,60,90]:
            b=sample(t);b['pressure'][kind]['full']['avg10']=str(limit+.01)
            r=policy.observe(b);assert (r['decision']=='STOP')==(t==90)
        policy=RuntimePolicy(a)
        for t in [30,60,90]:
            b=sample(t);b['pressure'][kind]['full']['avg10']=str(limit)
            assert policy.observe(b)['decision']!='STOP'
    passed('memory_and_IO_emergency_exact_comparator_and_three_ge30s_samples')
    for kind,limit in [('memory',10),('io',25)]:
        policy=RuntimePolicy(a)
        for t in [1,31,61]:
            b=sample(t);b['pressure'][kind]['full']['avg10']=str(limit+.01)
            r=policy.observe(b);assert (r['decision']=='STOP')==(t==61)
    passed('first_runtime_PSI_observation_is_immediate_no_extra_initial30s_delay')
    b=sample(10);r=RuntimePolicy(a).observe(b,own_major_faults=1)
    assert r['decision']=='WARN' and r['own_major_fault_delta']==1
    assert 'CORRELATED_MEMORY_CONTEXT_REPORT_AND_INCREASE_SAMPLING' in r['warnings']
    passed('own_majorfault_context_is_reported_without_false_swap_attribution')
    result=dict(status='PASS_PURE_CPU_AG_RESOURCE_POLICY',version=VERSION,cases=tests,
        policy_sha256=sha(PACK/'tools/resource_policy.py'),test_sha256=sha(Path(__file__)),
        simulations_started=0,signals=0,foreign_state_changes=0)
    write(PACK/'RESOURCE_POLICY_CPU_TESTS.json',result)
    print(json.dumps(result))


if __name__=='__main__':main()

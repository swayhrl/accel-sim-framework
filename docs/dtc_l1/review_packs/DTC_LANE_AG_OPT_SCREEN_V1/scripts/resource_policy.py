"""Versioned AG-only resource decisions. Pure logic, no signals or launches."""
GIB=1024**3
MIB=1024**2
VERSION='AG_DISCOVERY_RESOURCE_R2_V1'


def headroom(snapshot):
    c=snapshot['cgroup']
    return int(c['memory.max'])-int(c['memory.current']) if c['memory.max']!='max' else snapshot['host_MemAvailable_bytes']


def admission_checks(first,second):
    checks={}
    for name,s in [('first',first),('second',second)]:
        checks[name+'_original174']=s['host']=='huangrulin-174' and s['uid']==0
        checks[name+'_host_MemAvailable_ge32GiB']=s['host_MemAvailable_bytes']>=32*GIB
        checks[name+'_cgroup_headroom_ge32GiB']=headroom(s)>=32*GIB
        checks[name+'_disk_free_ge10GiB']=s['disk_free_bytes']>=10*GIB
        checks[name+'_memory_full_PSI_le1']=float(s['pressure']['memory']['full']['avg10'])<=1
        checks[name+'_io_full_PSI_le25']=float(s['pressure']['io']['full']['avg10'])<=25
    checks['two_samples_gap_ge10s']=second['monotonic_ns']-first['monotonic_ns']>=10_000_000_000
    checks['no_new_cgroup_oom']=all(second['cgroup']['events'][k]==first['cgroup']['events'][k] for k in ['oom','oom_kill'])
    # Global swap counters are recorded and warned about, never an isolated
    # single-page admission veto for this independent AG cohort.
    return checks


class RuntimePolicy:
    def __init__(self,first):
        self.first=first
        self.previous=first
        self.last_psi_check=None
        self.last_swap_check=None
        self.memory_psi_run=self.io_psi_run=self.swap_run=0

    def observe(self,current,own_major_faults=0,previous_own_major_faults=0):
        t=current['monotonic_ns']
        stop=[]
        warnings=[]
        cg=current['cgroup']
        if any(cg['events'][k]>self.first['cgroup']['events'][k] for k in ['oom','oom_kill']):
            stop.append('NEW_CGROUP_OOM_OR_OOM_KILL')
        if current['host_MemAvailable_bytes']<8*GIB or headroom(current)<8*GIB:
            stop.append('HOST_OR_CGROUP_HEADROOM_LT8GiB')
        if current['disk_free_bytes']<2*GIB:
            stop.append('DISK_FREE_LT2GiB')
        swap_delta=int(cg['memory.swap.current'])-int(self.first['cgroup']['memory.swap.current'])
        # A below-threshold observation also resets during a faster WARN sample;
        # a transient recovery must not be hidden by the qualification interval.
        if swap_delta<16*MIB:
            self.swap_run=0
        if self.last_swap_check is None or t-self.last_swap_check>=10_000_000_000:
            self.swap_run=self.swap_run+1 if swap_delta>=16*MIB else 0
            self.last_swap_check=t
        if self.swap_run>=3:
            stop.append('CGROUP_SWAP_GROWTH_GE16MiB_THREE_GE10S_SAMPLES')
        # Retain three >=30s-separated PSI observations; increased WARN
        # sampling does not silently shorten the old emergency observation gap.
        if self.last_psi_check is None or t-self.last_psi_check>=30_000_000_000:
            self.memory_psi_run=self.memory_psi_run+1 if float(current['pressure']['memory']['full']['avg10'])>10 else 0
            self.io_psi_run=self.io_psi_run+1 if float(current['pressure']['io']['full']['avg10'])>25 else 0
            self.last_psi_check=t
        if self.memory_psi_run>=3:
            stop.append('MEMORY_FULL_PSI_GT10_THREE_GE30S_SAMPLES')
        if self.io_psi_run>=3:
            stop.append('IO_FULL_PSI_GT25_THREE_GE30S_SAMPLES_AG_EXPLICIT_EXTENSION')
        global_delta={k:current[k]-self.previous[k] for k in ['pswpin','pswpout']}
        if any(n>0 for n in global_delta.values()):
            warnings.append('HOST_GLOBAL_SWAP_ACTIVITY_NOT_PROCESS_ATTRIBUTION')
        own_fault_delta=own_major_faults-previous_own_major_faults
        if own_fault_delta>0:
            warnings.append('OWN_MAJOR_FAULT_INCREMENT_RECORDED_NOT_EQUIVALENT_TO_SWAP')
        if warnings and (float(current['pressure']['memory']['full']['avg10'])>1 or own_fault_delta>0 or swap_delta>0):
            warnings.append('CORRELATED_MEMORY_CONTEXT_REPORT_AND_INCREASE_SAMPLING')
        self.previous=current
        return dict(version=VERSION,decision='STOP' if stop else 'WARN' if warnings else 'CONTINUE',
            stop_reasons=stop,warnings=warnings,global_page_deltas=global_delta,
            cgroup_swap_growth_bytes=swap_delta,own_major_fault_delta=own_fault_delta,
            qualified_swap_samples=self.swap_run,memory_PSI_samples=self.memory_psi_run,io_PSI_samples=self.io_psi_run,
            next_full_sample_seconds=5 if warnings else 10,
            no_signal_in_this_policy_module=True)

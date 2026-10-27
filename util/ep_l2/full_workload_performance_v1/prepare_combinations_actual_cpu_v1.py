"""Finite real Source78 constructor checks for composed profiles; never a model."""
import os,re,resource,subprocess,time
from ep_perf_common import *


def run():
    ctor_ref=ref(ROOT/'agent_b/config_init_cpu/runs/57000dc1-d258-4aa1-9adc-5bff2f68bfd8/RESULT.json')
    ctor=exact(ctor_ref)
    need(sha(ctor['binary_ref']['path'])==ctor['binary_ref']['sha256'],'actual constructor ELF drift')
    composer=module(ref(ROOT/'agent_b/compose_parameter_profiles.py'),'main_combo_compose')
    catalog=read(ROOT/'agent_b/PARAMETER_CATALOG_V2.json')
    geometry_plan=read(ROOT/'control/SEARCH_PLAN_GEOMETRY_V1.json')
    choices=[('COMBO_G64W8_L1L2MQ2',['G64_W8','U_L1MQ32','U_L2MQ256']),
             ('COMBO_G32W16_L2MQ2',['G32_W16','U_L2MQ256']),
             ('COMBO_G64W16_UD2',['G64_W16','UD_REQUEST_HEADROOM2']),
             ('COMBO_ICNT_LOWER2',['N_ICNT_BUFFERS1024','D_LOWERFIFO256'])]
    profiles=[];tests=[]
    folder=ROOT/'control/combo_constructor_v1';folder.mkdir(exist_ok=False)
    res=module(dict(path=str(ROOT/'agent_c/cpu_consistent_resources_v2.py'),sha256='07d0a21fb34419392c90f161dc49f0dfda9ba7eda99dd5d2e53b697ba9491237'),'combo_cpu_resources')
    sample=res.snapshot()
    floor_host=max(8*G,sample['confirmed_foreign_host_floor_bytes']);floor_cg=max(8*G,sample['confirmed_foreign_cgroup_floor_bytes'])
    need(not sample['foreign_metadata_errors'],'foreign metadata unavailable')
    need(sample['host_MemAvailable_bytes']>floor_host+512*M and sample['cgroup_effective_headroom_bytes']>floor_cg+512*M,'bounded CPU workset headroom')
    need(sample['native_free_bytes']>5*G+sample['foreign_remaining_write_bytes']+sample['cpu_engineering_read_consistency']['own_advertised_remaining_writes']+16*M,'CPU metadata incremental disk')
    # Exclude actual model affinities and their SMT siblings; no external process is moved.
    busy=set()
    for entry in P('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            argv=(entry/'cmdline').read_bytes()
            if b'accel-sim.out'in argv:
                busy.update(os.sched_getaffinity(int(entry.name)))
        except OSError:pass
    for cpu in list(busy):
        p=P('/sys/devices/system/cpu/cpu'+str(cpu)+'/topology/thread_siblings_list')
        if p.exists():
            for part in p.read_text().strip().split(','):
                v=part.split('-');busy.update(range(int(v[0]),int(v[-1])+1))
    available=sorted(set(os.sched_getaffinity(0))-busy)
    need(available,'no free CPU for tiny fixture');cpu=available[-1]
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(512*M,512*M));resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.nice(10);os.sched_setaffinity(0,{cpu})
    for profile,components in choices:
        composition=composer.compose(catalog,components);delta=composition['exact_common_effective_delta']
        profiles.append(dict(profile=profile,component_candidate_ids=components,expected_common_delta=delta))
        for mode in ['S','F']:
            base=next(t for t in ctor['tests']if t['case']=='G32W8_'+mode)
            text=P(base['memory_config_ref']['path']).read_text()
            for k,v in delta.items():
                pat=r'(?m)^'+re.escape(k)+r'[ \t]+[^\n]*$'
                if re.search(pat,text):text=re.sub(pat,k+' '+v,text)
                else:need(k in ['-gpgpu_cache:dl1','-icnt_in_buffer_limit','-icnt_out_buffer_limit'],'unreviewed constructor-only option '+k)
            path=folder/(profile+'_'+mode+'.memory.config')
            with path.open('x')as f:f.write(text)
            opts=copy.deepcopy(read(ROOT/'cases/EP_PERF_VECTOR4M_S_REF_V1/control/FROZEN_SPEC.json')['expected_effective_options']);opts.update(delta)
            g=opts['-gpgpu_cache:dl2'].split(',')[0].split(':');l1=opts['-gpgpu_cache:dl1']
            argv=list(base['argv']);argv[1]=str(path);argv[3:5]=[g[1],g[3]];argv[6:]=[l1,l1.split(',')[3].split(':')[0],opts['-icnt_in_buffer_limit']]
            t=time.monotonic();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits,timeout=60)
            stdout=folder/(profile+'_'+mode+'.stdout');stderr=folder/(profile+'_'+mode+'.stderr');stdout.write_bytes(p.stdout);stderr.write_bytes(p.stderr)
            need(p.returncode==0 and b'CONFIG_INIT_SCOPE|GPU_OBJECTS=0'in p.stdout,'actual composed constructor failed '+profile+' '+mode)
            tests.append(dict(profile=profile,mode=mode,component_candidate_ids=components,delta=delta,returncode=p.returncode,PASS=True,
                elapsed_seconds=time.monotonic()-t,actual_argv=argv,stdout_ref=ref(stdout),stderr_ref=ref(stderr),memory_config_ref=ref(path),actual_source_constructor=True,model=False,Trace_body_read=False))
    result=dict(status='ACTUAL_COMPOSED_SOURCE78_CONSTRUCTOR_8_PASS_NO_APPLICATION_AUTHORITY',source_identity=ctor['source_identity'],utc=now(),
        producer_ref=ctor_ref,resource_snapshot=sample,CPU=cpu,AS_limit_bytes=512*M,tests=tests,model_starts=0,registry_writes=0,
        fixed_clocks_and_delay_unchanged=True,Source_and_ELF_unchanged=True,all_negative_scientific_results_retained=True)
    result_path=folder/'RESULT.json';put(result_path,result,True)
    plan=copy.deepcopy(geometry_plan)
    plan.update(stage='STAGE_EXPLORE_CAUSAL_COMBINATIONS_3INPUT_24POINTS',utc=now(),maximum_new_starts=24,profiles=profiles,
        actual_composed_constructor_ref=ref(result_path),selection_basis='Three predeclared diverse inputs unchanged; known finite predesigned queue/geometry combinations plus G64W16+UD based on independent finite hardware headroom. No positive-only workload selection.',
        prior_results_ref=ref(ROOT/'analysis/LATEST_CROSS_PROFILE_RESULT.json'),
        causal_claim_boundary='Report same-mode absolute cycles and matched S/F separately; Vector4M F improvement with greater headroom is not automatically an EP mechanism gain; all negative outcomes retained.')
    put(ROOT/'control/SEARCH_PLAN_COMBINATIONS_V1.json',plan,True)
    return dict(status=result['status'],receipt_ref=ref(result_path),plan_ref=ref(ROOT/'control/SEARCH_PLAN_COMBINATIONS_V1.json'))


if __name__=='__main__':print(json.dumps(run()))

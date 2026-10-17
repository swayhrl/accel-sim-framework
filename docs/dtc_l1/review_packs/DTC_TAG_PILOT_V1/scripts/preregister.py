"""Freeze exactly seven new attempts, using accepted full discovery inputs only."""
import copy
import csv
import json
import re
import uuid
from pathlib import Path
from common import *


def main():
    assert not (PACK/'PRE_REGISTRATION.tsv').exists(), 'Immutable preregistration already exists'
    assert __import__('socket').gethostname() == 'huangrulin-174'
    source_check()
    assert json.loads((PACK/'CPU_DIRECTED_CHECKS.json').read_text())['status'].startswith('PASS')
    oldroot = Path('/workspace/dtc-service-closure-174-v1/r2-attempts')
    controls_ids = {'GEMM_IO256':'b106a859-3c31-4a7b-949a-bf83cdf17e51',
                    'GEMM_OO128':'c76bcd36-f912-4854-8d1c-481fbf8f488a',
                    'GEMM_CPLUS':'ba4b73f1-33bc-49ab-9945-f7df3d1a3955',
                    'Gaussian_OO128':'41e02b7d-474d-4bf1-9f2b-b515aa326179',
                    'Gaussian_CPLUS':'ef3d20bc-23bf-4326-ac88-247ee6989aa3'}
    expected_cycles = dict(GEMM_IO256=1457468,GEMM_OO128=1377919,GEMM_CPLUS=1511333,
                           Gaussian_OO128=3798174,Gaussian_CPLUS=3379152)
    controls = {}
    collect = old_collector().collect
    for name, uid in controls_ids.items():
        found = list(oldroot.glob('*_'+uid))
        assert len(found)==1
        run = found[0]
        start = json.loads((run/'RUN_START.json').read_text())
        spec = start['spec']
        strict = collect(run)
        assert strict['status']=='PASS_CHECKED_SCOPE', (name,strict)
        assert int(strict['cycles'])==expected_cycles[name]
        assert start['attempt_uuid']==uid
        for cfg in spec['configs']:
            assert sha(cfg['path'])==cfg['sha256']
        for file in ['RUN_START.json','RUN_TERMINAL.json','SPEC.json']:
            source = run/file
            if source.exists():
                (PACK/'inputs'/f'{name}_{file}').write_bytes(source.read_bytes())
        write(PACK/'inputs'/f'{name}_STRICT_RECHECK.json',strict)
        text = (run/'simulator.stdout').read_text()
        resolved = options([c['path'] for c in spec['configs']])
        echo = echo_options(text)
        mismatches = {k:(v,echo.get(k)) for k,v in resolved.items() if v!=echo.get(k)}
        assert not mismatches,(name,mismatches)
        controls[name] = dict(uuid=uid,run_dir=str(run),spec=spec,
                              stdout_sha256=sha(run/'simulator.stdout'),
                              start_sha256=sha(run/'RUN_START.json'),
                              terminal_sha256=sha(run/'RUN_TERMINAL.json'),
                              cycles=int(strict['cycles']),instructions=int(strict['instructions']),
                              effective_options=resolved,echo_options=echo,strict=strict)
    write(PACK/'ACCEPTED_CONTROLS.json',controls)

    with (PACK/'inputs/KERNEL_BODY_AUDIT.tsv').open() as f:
        bodies = list(csv.DictReader(f,delimiter='\t'))
    ordered, input_checks = {}, []
    for workload in ['GEMM','Gaussian']:
        spec = controls[workload+'_OO128']['spec']
        assert sha(spec['trace_list'])==spec['trace_list_sha256']
        listed = [x.strip() for x in Path(spec['trace_list']).read_text().splitlines()
                  if x.strip() and not x.lstrip().startswith('#')]
        kernels = [line for line in listed if line.startswith('kernel-')]
        assert kernels==[Path(m['path']).name for m in spec['members']]
        assert all(line.startswith(('kernel-', 'MemcpyHtoD,')) for line in listed)
        # These are commands in the FULL original list, not trace members.
        # Keep the original list untouched, including its cache-prefill copies.
        (PACK/'inputs'/f'{workload}_kernelslist.g').write_bytes(Path(spec['trace_list']).read_bytes())
        rows=sorted([r for r in bodies if r['workload'].lower()==workload.lower()],key=lambda r:int(r['ordinal']))
        assert len(rows)==len(spec['members'])
        for m,r in zip(spec['members'],rows):
            assert m['sha256']==r['sha256'] and m['path']==r['path']
            assert Path(m['path']).stat().st_size==m['bytes'] and sha(m['path'])==m['sha256']
            assert r['coverage']=='ALL_DECLARED_WARPS_AND_FULL_GRID_WITH_TERMINAL_EXIT'
            assert int(r['binary_version'])==70
            assert int(r['cacheable_local_max_width'])==0
            assert int(r['sparse_mask_base_stride_records'])==0
            assert int(r['unaligned_lane_memory_addresses'])==0
        assert sum(int(r['active_thread_instructions']) for r in rows)==spec['expected_instructions']
        ordered[workload]=[dict(ordinal=int(r['ordinal']),kernel=r['kernel'],member_path=r['path'],
                          member_sha256=r['sha256'],active_instructions=int(r['active_thread_instructions']),
                          complete_ctas=int(r['complete_ctas']),complete_warps=int(r['complete_warps']),
                          max_line_references=int(r['max_global_128b_line_references'])) for r in rows]
        input_checks.append(dict(workload=workload,member_count=len(rows),member_hashes='PASS',
                                 list_sha256=spec['trace_list_sha256'],ordered_names='PASS',
                                 active_instructions=spec['expected_instructions'],
                                 total_ctas=sum(r['complete_ctas'] for r in ordered[workload]),
                                 full_list_commands=len(listed),memcpy_commands=len(listed)-len(kernels),
                                 body_proof='REUSED_ACCEPTED_CPU_BODY_AUDIT_NO_TRACE_REDECODE'))
    write(PACK/'ORDERED_KERNELS.json',ordered)
    write(PACK/'INPUT_PREFLIGHT.json',dict(status='PASS',workloads=input_checks,
                                         new_full_simulator_attempts=0))

    # Small config snapshots preserve the original option order, with only a
    # final candidate-specific overlay. Original files remain read-only.
    config_copies={}
    for key in ['GEMM_IO256','GEMM_OO128']:
        for i,item in enumerate(controls[key]['spec']['configs']):
            name=('FAST64_IO.config' if key=='GEMM_IO256' else 'FAST64_OO.config') if i==0 else ['','FINITE_PRIMARY_COMMON.config','trace.config'][i]
            dest=PACK/'config'/name
            data=Path(item['path']).read_bytes()
            if dest.exists():assert dest.read_bytes()==data
            else:dest.write_bytes(data)
            config_copies[key,i]=dest
    candidates=[('T0','GEMM',32,4,'io'),
                ('T1-A','GEMM',32,8,'oo'),('T1-A','Gaussian',32,8,'oo'),
                ('T1-B','GEMM',64,4,'oo'),('T1-B','Gaussian',64,4,'oo'),
                ('T1-C','GEMM',64,8,'oo'),('T1-C','Gaussian',64,8,'oo')]
    plan, deltas, resources = [], [], []
    for priority,(candidate,workload,sets,ways,mode) in enumerate(candidates):
        control_name = workload+'_OO128' if mode=='oo' else 'GEMM_IO256'
        original = controls[control_name]
        spec=copy.deepcopy(original['spec'])
        uid=str(uuid.uuid4())
        label=f'DTC_TAG_PILOT_V1_{candidate.replace("-","_")}_{workload}'
        overlay=PACK/'config'/f'{candidate}.config'
        content=('-gpgpu_dtc_l1_io_pib_entries 128\n' if candidate=='T0' else
                 f'-gpgpu_dtc_l1_logical_sets {sets}\n-gpgpu_dtc_l1_logical_ways {ways}\n')
        if overlay.exists(): assert overlay.read_text()==content
        else:overlay.write_text(content)
        config_key='GEMM_IO256' if mode=='io' else 'GEMM_OO128'
        paths=[config_copies[config_key,i] for i in range(3)]+[overlay]
        effective=options(paths)
        diffs={k:dict(before=original['effective_options'].get(k),after=effective.get(k))
               for k in effective.keys()|original['effective_options'].keys()
               if effective.get(k)!=original['effective_options'].get(k)}
        allowed={'-gpgpu_dtc_l1_io_pib_entries'} if mode=='io' else {
                 '-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'}
        assert set(diffs)<=allowed
        for k,v in {'-gpgpu_dtc_l1_mode':2 if mode=='io' else 3,
                    '-gpgpu_dtc_l1_finite_service':1,'-gpgpu_dtc_l1_physical_lines':640,
                    '-gpgpu_dtc_l1_tag_banks':4,'-gpgpu_dtc_l1_tag_req_per_bank':1,
                    '-gpgpu_dtc_l1_tag_req_per_cycle':4,'-gpgpu_dtc_l1_allocation_width':4,
                    '-gpgpu_dtc_l1_lower_outstanding_cap':32768,
                    '-gpgpu_dtc_l1_logical_sets':sets,'-gpgpu_dtc_l1_logical_ways':ways,
                    '-gpgpu_n_clusters':64,'-gpgpu_n_cores_per_cluster':1,
                    '-gpgpu_shmem_size':98304,'-gpgpu_shmem_sizeDefault':98304,
                    '-gpgpu_adaptive_cache_config':0}.items():
            assert effective[k]==[str(v)],(label,k,effective[k])
        assert effective['-gpgpu_cache:dl1']==['S:32:128:4,L:T:m:L:L,A:512:8,16:0,32']
        assert effective['-gpgpu_clock_domains']==['1410.0:1410.0:1410.0:850.0']
        # Defaults are also frozen from the accepted full option echo; overrides
        # below are configuration values, not a new simulator implementation.
        expected_echo=copy.deepcopy(original['echo_options'])
        expected_echo.update(effective)
        assert expected_echo['-gpgpu_mem_unit_ports']==['1']
        assert expected_echo['-gpgpu_dtc_l1_ref_count_bits']==['13']
        assert expected_echo['-gpgpu_dtc_l1_'+mode+'_pib_entries']==['128']
        spec.update(label=label,attempt_uuid=uid,arm='IO128' if mode=='io' else candidate,
                    phase='T0_MATCHED_DEPTH' if mode=='io' else 'T1_DISCOVERY',candidate=candidate,
                    classification='EXPLORATORY_DTC_TAG_PIB_NOT_MAIN_FIGURE_NOT_NATIVE_NOT_EQUAL_AREA',
                    orchestrator_framework=AUTH_HEAD,configuration_parent_uuid=original['uuid'],
                    original_oo_uuid=controls[workload+'_OO128']['uuid'],
                    original_cplus_uuid=controls[workload+'_CPLUS']['uuid'],
                    discovery=True,holdout=False,finite_service=True,dtc_mode=mode,
                    configs=[dict(path=str(x),sha256=sha(x)) for x in paths],
                    expected_effective_options=effective,expected_option_echo=expected_echo,
                    expected_cores=64,expected_logical_sets=sets,expected_logical_ways=ways,
                    expected_active_pib=128,expected_ordinary_kib=16,expected_shared_kib=96,
                    expected_physical_lines=640,
                    wall_timeout_seconds=28800 if workload=='GEMM' else 7200,
                    no_retry=True)
        specfile=PACK/'specs'/f'{label}.json'
        write(specfile,spec)
        plan.append(dict(priority=priority,label=label,candidate=candidate,workload=workload,
                         attempt_uuid=uid,discovery=True,holdout=False,spec_path=str(specfile),
                         spec_sha256=sha(specfile),logical_sets=sets,logical_ways=ways,
                         physical_lines=640,active_pib=128,core=CORE_SHA,binary_sha256=BINARY_SHA,
                         build_framework=BUILD_FW,trace_list_sha256=spec['trace_list_sha256'],
                         ordered_kernels_sha256=sha(PACK/'ORDERED_KERNELS.json'),
                         cpu_proof_sha256=sha(PACK/'inputs/KERNEL_BODY_AUDIT.tsv'),
                         expected_active_instructions=spec['expected_instructions'],
                         kernel_count=len(spec['members']),kernel_ordinal_range=f'1..{len(spec["members"])}',
                         configuration_parent_uuid=original['uuid'],parent_stdout_sha256=original['stdout_sha256'],
                         original_oo_uuid=controls[workload+'_OO128']['uuid'],
                         original_oo_stdout_sha256=controls[workload+'_OO128']['stdout_sha256'],
                         original_cplus_uuid=controls[workload+'_CPLUS']['uuid'],
                         original_cplus_stdout_sha256=controls[workload+'_CPLUS']['stdout_sha256'],
                         effective_delta=json.dumps(diffs,sort_keys=True),
                         launch_gate='PUSH_FETCH_BACK_AND_M_VERIFIED_AND_LIVE_RESOURCE_AUTHORITY_PASS',
                         status='PREREGISTERED_NOT_LAUNCHED'))
        for k,v in sorted(diffs.items()):
            deltas.append(dict(candidate=candidate,workload=workload,parameter=k,
                               original_uuid=original['uuid'],old_value=' '.join(v['before']),
                               new_value=' '.join(v['after']),other_effective_options='UNCHANGED'))
    for name,sets,ways in [('original',32,4),('T1-A',32,8),('T1-B',64,4),('T1-C',64,8)]:
        import math
        n=sets*ways
        resources.append(dict(candidate=name,sets=sets,ways=ways,mappings=n,coverage_kib=n//8,
                              physical_data_kib=80,ordinary_data_kib=16,shared_kib=96,
                              io_pib=256,oo_pib=128,tag_banks=4,max_compares_per_lookup=ways,
                              tag_storage_example_bits=n*68+sets*math.ceil(math.log2(math.factorial(ways))),
                              storage_model='ILLUSTRATIVE_57BIT_ALIGNED_ADDRESS_PLUS10BIT_PHYS_PLUS_VALID_AND_LRU_INFORMATION_BOUND_NOT_SYNTHESIZED',
                              ref_count_bits=13,max_oo_references=4096,
                              tag_latency='1cycle_ASSUMED_NOT_RTL_QUALIFIED',area='UNAVAILABLE'))
    table(PACK/'CONTROLLED_DELTA.tsv',deltas)
    table(PACK/'RESOURCE_OVERHEAD.tsv',resources)
    table(PACK/'PRE_REGISTRATION.tsv',plan)
    policy=dict(status='FROZEN_BEFORE_NEW_PERFORMANCE',authorization=AUTH_HEAD,max_new_attempts=7,
                max_parallel=2,workloads=['GEMM','Gaussian'],holdouts_run=False,service_t2=False,
                tuning_after_results=False,preregistered_order=[r['label'] for r in plan],
                selection=dict(reference='accepted original OO128 same full input',
                               R_min_threshold=0.98,R_geomean_threshold=1.02,
                               tie_relative_geomean_difference=0.005,
                               tie_break=['fewer mappings','lower ways'],
                               no_candidate='NO_QUALIFIED_TAG_PROMOTION_IN_T1',
                               require_both_strict_pass=True),
                admission=dict(host_MemAvailable_min_gib=32,cgroup_headroom_min_gib=32,
                               disk_free_min_gib=10,memory_pressure_avg10_max=1,
                               io_pressure_avg10_max=25,swapped_pages_delta_max=0,
                               oom_event_delta_max=0,probe_interval_seconds=10,
                               external_simulators_allowed=0,old_lock_owners_allowed=0),
                resource_stop=dict(cgroup_headroom_min_gib=8,disk_free_min_gib=2,
                                   memory_pressure_avg10_max=10,consecutive_samples=3,
                                   signal_only_own_process_groups=True),
                failures='PRESERVE_NO_SCIENTIFIC_RETUNE_NO_AUTOMATIC_RETRY; correctness/identity gap stops candidate or full gate',
                after_T1='STOP_FOR_REVIEW_NO_AUTOMATIC_HOLDOUT',
                raw_root=str(ROOT),source_changes=False)
    write(PACK/'POLICY.json',policy)
    print(json.dumps(dict(status='PREREGISTERED_NOT_LAUNCHED',attempts=len(plan),inputs=input_checks)))


if __name__=='__main__':
    main()

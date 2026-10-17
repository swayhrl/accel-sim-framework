"""Freeze exactly two fixed T1-C holdouts from accepted original full inputs."""
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
    controls_ids = {'DWT2D_OO128':'95fd9a17-4e88-4063-998e-5713316ec3a1',
                    'DWT2D_CPLUS':'5f69ab62-9525-4a7c-8853-ad93455479ab',
                    'BICG_OO128':'8a5da6ac-ef65-4ca0-b1de-15a69d6ba613',
                    'BICG_CPLUS':'f91d33da-730a-4047-998c-566c4fc416c0'}
    expected_cycles = dict(DWT2D_OO128=237887,DWT2D_CPLUS=247588,
                           BICG_OO128=47533116,BICG_CPLUS=25353488)
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
    for workload in ['DWT2D','BICG']:
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
    for i,item in enumerate(controls['DWT2D_OO128']['spec']['configs']):
        dest=PACK/'config'/['FAST64_OO.config','FINITE_PRIMARY_COMMON.config','trace.config'][i]
        dest.write_bytes(Path(item['path']).read_bytes())
        config_copies['DWT2D_OO128',i]=dest
    candidates=[('T1-C','DWT2D',64,8,'oo'),('T1-C','BICG',64,8,'oo')]
    plan, deltas, resources = [], [], []
    for priority,(candidate,workload,sets,ways,mode) in enumerate(candidates):
        control_name = workload+'_OO128' if mode=='oo' else 'GEMM_IO256'
        original = controls[control_name]
        spec=copy.deepcopy(original['spec'])
        uid=str(uuid.uuid4())
        label=f'DTC_T1C_HOLDOUT_V1_{workload}'
        overlay=PACK/'config'/f'{candidate}.config'
        content=('-gpgpu_dtc_l1_io_pib_entries 128\n' if candidate=='T0' else
                 f'-gpgpu_dtc_l1_logical_sets {sets}\n-gpgpu_dtc_l1_logical_ways {ways}\n')
        if overlay.exists(): assert overlay.read_text()==content
        else:overlay.write_text(content)
        config_key='DWT2D_OO128'
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
                    phase='INDEPENDENT_FIXED_T1C_HOLDOUT',candidate=candidate,
                    classification='INDEPENDENT_FIXED_T1C_HOLDOUT_NOT_MAIN_FIGURE_NOT_NATIVE_NOT_EQUAL_AREA',
                    orchestrator_framework=AUTH_HEAD,configuration_parent_uuid=original['uuid'],
                    original_oo_uuid=controls[workload+'_OO128']['uuid'],
                    original_cplus_uuid=controls[workload+'_CPLUS']['uuid'],
                    discovery=False,holdout=True,finite_service=True,dtc_mode=mode,
                    configs=[dict(path=str(x),sha256=sha(x)) for x in paths],
                    expected_effective_options=effective,expected_option_echo=expected_echo,
                    expected_cores=64,expected_logical_sets=sets,expected_logical_ways=ways,
                    expected_active_pib=128,expected_ordinary_kib=16,expected_shared_kib=96,
                    expected_physical_lines=640,
                    wall_timeout_seconds=3600 if workload=='DWT2D' else 28800,
                    no_retry=True)
        spec.pop('supersedes_source_core',None)
        spec['correction']='New independent fixed T1-C holdout; only logical_sets/ways changed; no replacement of frozen results'
        specfile=PACK/'specs'/f'{label}.json'
        write(specfile,spec)
        plan.append(dict(priority=priority,label=label,candidate=candidate,workload=workload,
                         attempt_uuid=uid,discovery=False,holdout=True,spec_path=str(specfile),
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
                         launch_gate='PUSH_FETCH_BACK_RESOURCE_AUTHORITY_PASS_DWT2D_STRICT_BEFORE_BICG',
                         status='PREREGISTERED_NOT_LAUNCHED'))
        for k,v in sorted(diffs.items()):
            deltas.append(dict(candidate=candidate,workload=workload,parameter=k,
                               original_uuid=original['uuid'],old_value=' '.join(v['before']),
                               new_value=' '.join(v['after']),other_effective_options='UNCHANGED'))
    table(PACK/'CONTROLLED_DELTA.tsv',deltas)
    table(PACK/'PRE_REGISTRATION.tsv',plan)
    policy=json.loads((FW/'docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/POLICY.json').read_text())
    policy.update(status='FROZEN_BEFORE_ANY_NEW_CANDIDATE_PERFORMANCE',authorization='AUTHORIZATION.md',
                  max_new_attempts=2,max_parallel=1,workloads=['DWT2D','BICG'],
                  holdout_execution_authorized=True,service_t2=False,tuning_after_results=False,
                  preregistered_order=[r['label'] for r in plan],raw_root=str(ROOT),
                  after_holdouts='DWT2D_STRICT_PASS_THEN_BICG; STOP_AFTER_TWO_OR_LEGAL_FAILURE',
                  no_new_performance_threshold=True,
                  wall_timeouts_seconds=dict(DWT2D=3600,BICG=28800),
                  timeout_rationale='Frozen before results: DWT2D original OO335s ->3600s; BICG12471s ->28800s; no reset or retry',
                  independent_EP_L2='Reuse exact Lane T V2 fingerprint; all projects count toward resource limits')
    policy.pop('selection',None)
    policy.pop('holdouts_run',None)
    policy.pop('after_T1',None)
    write(PACK/'POLICY.json',policy)
    from strict_collect import strict as extended
    for workload in ['DWT2D','BICG']:
        c=controls[workload+'_OO128'];spec=copy.deepcopy(c['spec'])
        spec.update(attempt_uuid=c['uuid'],expected_effective_options=c['effective_options'],
                    expected_option_echo=c['echo_options'],candidate='ACCEPTED_ORIGINAL_OO128')
        result=extended(Path(c['run_dir']),spec)
        assert result['status']=='PASS_STRICT_HOLDOUT_SCOPE',(workload,result)
        write(PACK/'inputs'/(workload+'_OO128_ORDERED_STRICT_RECHECK.json'),result)
    write(PACK/'SOURCE_INPUT_IDENTITY.json',dict(
        status='PASS_FROZEN_SOURCE_AND_BOTH_COMPLETE_HOLDOUT_INPUTS_CPU_ONLY',
        source=json.loads((PACK/'SOURCE_IDENTITY.json').read_text()),
        frozen_lanes=json.loads((PACK/'FROZEN_LANES.json').read_text()),
        selected_input_checks=input_checks,
        controls={k:dict(uuid=v['uuid'],run_dir=v['run_dir'],stdout_sha256=v['stdout_sha256'],
                         start_sha256=v['start_sha256'],terminal_sha256=v['terminal_sha256'],
                         cycles=v['cycles'],instructions=v['instructions']) for k,v in controls.items()},
        cpu_body_proof='REUSED_ACCEPTED_12_ROWS_NO_629_RESCAN',new_full_simulator_attempts=0))
    print('PASS two fixed holdout specs, four original control identities, 12 ordered full kernels; no new simulator')


if __name__=='__main__':main()

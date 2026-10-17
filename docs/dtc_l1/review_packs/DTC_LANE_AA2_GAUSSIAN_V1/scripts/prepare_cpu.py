"""AA2 deterministic CPU preparation; no simulator launch capability.

The inherited four UUIDs do not create a new four-attempt allowance. Any
matching RUN_START is a stop, even if its terminal evidence is absent.
"""
from common import *


def scan_starts():
    roots=sorted(p for p in Path('/workspace').glob('dtc-*') if p.is_dir())
    found=[];examined=[]
    for root in roots:
        for directory,dirs,files in os.walk(root):
            dirs[:]=[d for d in dirs if not d.startswith(('build','source','frozen-header')) and d not in ['.git','__pycache__']]
            for filename in files:
                if filename not in ['RUN_START.json','RUN_TERMINAL.json','PID.json']:continue
                p=Path(directory)/filename
                data=p.read_bytes()
                examined.append(dict(path=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
                for name,uid,*_ in POINTS:
                    if uid.encode() in data or uid in str(p):
                        found.append(dict(point=name,uuid=uid,path=str(p),sha256=hashlib.sha256(data).hexdigest(),
                                          actual_RUN_START=filename=='RUN_START.json'))
    return dict(utc=now(),roots=[str(p) for p in roots],
          scope='All current /workspace/dtc-* raw roots; RUN_START/RUN_TERMINAL/PID metadata. Build/source caches pruned. No claim about disconnected hosts.',
          examined=examined,matches=found,matching_actual_RUN_STARTs=[r for r in found if r['actual_RUN_START']],
          status='STOP_UUID_ALREADY_STARTED' if any(r['actual_RUN_START'] for r in found) else 'PASS_NO_MATCHING_RUN_START_IN_REGISTERED_LOCAL_DTC_RAW_ROOTS')


def main():
    assert socket.gethostname()=='huangrulin-174' and os.getuid()==0
    assert git(FW,'branch','--show-current')=='hrl/iscas2027-dtc-lane-aa2-gaussian-factorial-174-v1'
    assert git(FW,'rev-parse','HEAD')==AA_SHA
    assert not (PACK/'PRE_REGISTRATION.tsv').exists()
    ROOT.mkdir(exist_ok=True)
    old=git_json(FW_REPO,AA_SHA,OLD_PACK+'/STOP_RECORD.json')
    assert old['actual_full_starts']==0 and old['canary_starts']==0 and old['launch_admitted'] is False
    oldplan=list(csv.DictReader(blob(FW_REPO,AA_SHA,OLD_PACK+'/PRE_REGISTRATION.tsv').decode().splitlines(),delimiter='\t'))
    assert [(r['point'],r['uuid']) for r in oldplan]==[(p[0],p[1]) for p in POINTS]
    scan=scan_starts();write(PACK/'UUID_START_CONFLICT_AUDIT.json',scan)
    write(PACK/'ATTEMPT_BUDGET.json',dict(ancestor_goal='DTC_LANE_AA_GAUSSIAN_INVALIDATION_FACTORIAL_174_V1',
          ancestor_commit=AA_SHA,ancestor_actual_starts=0,ancestor_reserved_UUIDs=4,
          cumulative_total_actual_start_ceiling=4,AA2_does_not_reset_allowance=True,
          reused_reserved_UUIDs=[dict(point=p[0],uuid=p[1]) for p in POINTS],
          observed_matching_RUN_STARTs=len(scan['matching_actual_RUN_STARTs']),
          AA2_actual_starts=0,canary_starts=0,one_start_per_uuid=True,
          old_raw='/workspace/dtc-lane-aa-gaussian-174-v1',new_raw=str(ROOT)))
    assert not scan['matching_actual_RUN_STARTs'],'STOP_UUID_ALREADY_STARTED'
    first=snapshot();write(ROOT/'CPU_PROBE_FIRST.json',first)
    # Resource-only probe. No DTC lock or execution authority is acquired.
    start=time.monotonic()
    while time.monotonic()-start<10:time.sleep(min(1,10-(time.monotonic()-start)))
    second=snapshot();write(ROOT/'CPU_PROBE_SECOND.json',second)
    checks=resource_checks(first,second)
    write(PACK/'CPU_RESOURCE_PREFLIGHT.json',dict(utc=now(),checks=checks,
         status='PASS_CPU_LIGHTWEIGHT_PREPARATION_ONLY' if all(checks.values()) else 'HOLD_RESOURCE',
         first_raw_sha256=sha(ROOT/'CPU_PROBE_FIRST.json'),second_raw_sha256=sha(ROOT/'CPU_PROBE_SECOND.json'),
         simulator_admission=False,includes_all_projects=True))

    provenance=[]
    for name in ['STOP_RECORD.json','PRE_REGISTRATION.tsv','SCIENTIFIC_SCOPE.md','FILES_SHA256.tsv']:
        provenance.append(copy_blob(FW_REPO,AA_SHA,OLD_PACK+'/'+name,PACK/'inputs/AA_V1'/name))
    for name in ['K1_SEMANTIC_CONTRACT.md','SOURCE_EVENT_MAP.md','OPEN_QUESTIONS.md','CPU_CHECKS.json']:
        provenance.append(copy_blob(FW_REPO,V_SHA,V_PACK+'/'+name,PACK/'inputs/V'/name))
    assert git(FW_REPO,'rev-parse','refs/remotes/origin/hrl/iscas2027-dtc-lane-v-semantic-audit-174-v1')==V_SHA
    assert git(CORE_REPO,'rev-parse','refs/remotes/origin/hrl/iscas2027-dtc-lane-x-invalidate-optin-core-174-v1')==CANDIDATE_CORE
    # The candidate is a real functional Core. It is not yet an AA2-admitted runtime.
    sourcefiles=[]
    for rel in ['src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/dtc-l1-invalidation.h',
                'src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','src/gpgpu-sim/gpu-sim.cc',
                'src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','CMakeLists.txt']:
        data=blob(CORE_REPO,CANDIDATE_CORE,rel)
        sourcefiles.append(dict(path=rel,blob=git(CORE_REPO,'rev-parse',CANDIDATE_CORE+':'+rel),
                                sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
    table(PACK/'CANDIDATE_SOURCE_SHA256.tsv',sourcefiles)
    diff=subprocess.check_output(['git','-C',str(CORE_REPO),'diff',BASE_CORE,CANDIDATE_CORE,'--','src'])
    (PACK/'CANDIDATE_CORE_DELTA.patch').write_bytes(diff)
    write(PACK/'CANDIDATE_CORE_IDENTITY.json',dict(utc=now(),core=CANDIDATE_CORE,base=BASE_CORE,
          remote_fetch_back_match=True,src_tree=git(CORE_REPO,'rev-parse',CANDIDATE_CORE+':src'),
          source_manifest_sha256=sha(PACK/'CANDIDATE_SOURCE_SHA256.tsv'),functional_delta=True,
          admissible_for_simulation=False,reason='Pending exact X publication, Y2 gate, Z2 contract, shared event observation and authority/resource admission',
          accepted_runtime_sha256='UNAVAILABLE',AA2_built_Core=False,core_mutations_by_AA2=False))

    # Select Gaussian, never the combined GEMM+Gaussian 511-member cohort.
    original=git_json(FW_REPO,T_SHA,T_PACK+'/inputs/Gaussian_OO128_SPEC.json')
    cohort=git_json(FW_REPO,T_SHA,T_PACK+'/ORDERED_KERNELS.json')
    ordered=cohort['Gaussian'];members=original['members']
    assert len(ordered)==len(members)==510
    assert sum(r['active_instructions'] for r in ordered)==283685120
    assert len(cohort['GEMM'])+len(ordered)==511
    listed=Path(original['trace_list'])
    assert sha(listed)==original['trace_list_sha256']=='6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9'
    (PACK/'inputs/Gaussian_kernelslist.g').write_bytes(listed.read_bytes())
    commands=[s.strip() for s in listed.read_text().splitlines() if s.strip() and not s.lstrip().startswith('#')]
    assert [s for s in commands if s.startswith('kernel-')]==[Path(m['path']).name for m in members]
    assert len(commands)==513 and all(s.startswith(('kernel-','MemcpyHtoD,')) for s in commands)
    write(PACK/'ORDERED_KERNELS.json',ordered)
    bod=blob(FW_REPO,T_SHA,T_PACK+'/inputs/KERNEL_BODY_AUDIT.tsv').decode()
    body=[r for r in csv.DictReader(bod.splitlines(),delimiter='\t') if r['workload'].lower()=='gaussian']
    assert len(body)==510
    table(PACK/'inputs/GAUSSIAN_BODY_AUDIT.tsv',body)
    actual=[]
    assert all(checks.values()),'HOLD_RESOURCE_BEFORE_LARGE_MEMBER_HASH_READ'
    total=0;hash_start=time.monotonic()
    for m,o in zip(members,ordered):
        assert Path(m['path']).stat().st_size==m['bytes']
        assert m['path']==o['member_path'] and m['sha256']==o['member_sha256']
        h=hashlib.sha256()
        with Path(m['path']).open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):
                h.update(b);total+=len(b)
                delay=total/(64*1024**2)-(time.monotonic()-hash_start)
                if delay>0:time.sleep(min(delay,1))
        assert h.hexdigest()==m['sha256'],m['path']
        actual.append(dict(ordinal=o['ordinal'],path=m['path'],bytes=m['bytes'],sha256=h.hexdigest()))
    table(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv',actual)
    write(PACK/'INPUT_PREFLIGHT.json',dict(status='PASS_ORIGINAL_GAUSSIAN_510_REHASHED',
          accepted_manifest_commit=T_SHA,accepted_manifest_path=T_PACK+'/inputs/Gaussian_OO128_SPEC.json',
          Gaussian_member_count=510,combined_GEMM_Gaussian_cohort_count_NOT_Gaussian_count=511,
          list_sha256=sha(listed),members_manifest_sha256=sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv'),
          ordered_manifest_sha256=sha(PACK/'ORDERED_KERNELS.json'),full_list_commands=513,HtoD_commands=3,
          active_thread_instructions=283685120,complete_ctas=sum(r['complete_ctas'] for r in ordered),
          ROI='FULL_ORIGINAL_LIST_NO_TRUNCATION_NO_SAMPLING_NO_TRACE_MODIFICATION',
          input_value_correctness='UNAVAILABLE',W_per_address_scan='UNAVAILABLE_ATTRIBUTION_GAP',
          member_bytes_rehashed=total,hash_bandwidth_limit_MiB_per_second=64,
          body_instruction_proof='REUSED_ACCEPTED_CPU_BODY_AUDIT_BOUND_TO_ALL_REHASHED_GAUSSIAN_MEMBERS'))

    # Public configs and default echoes stay byte-bound to accepted identities.
    template=git_json(FW_REPO,T_SHA,T_PACK+'/specs/DTC_TAG_PILOT_V1_T1_C_Gaussian.json')
    configs=[]
    for name in ['FAST64_OO.config','FINITE_PRIMARY_COMMON.config','trace.config']:
        destination=PACK/'config'/name
        provenance.append(copy_blob(FW_REPO,T_SHA,T_PACK+'/config/'+name,destination));configs.append(destination)
    for tag in ['32x4','64x8']:
        provenance.append(copy_blob(FW_REPO,AA_SHA,OLD_PACK+'/inputs/ORIGINAL_'+tag+'_OPTION_ECHO.tsv',PACK/'inputs'/('ORIGINAL_'+tag+'_OPTION_ECHO.tsv')))
    plans=[];full=[];deltas=[]
    for priority,(name,uid,k,sets,ways,calibration) in enumerate(POINTS):
        overlay=PACK/'config'/f'{name}.config'
        overlay.write_text(f'-gpgpu_dtc_l1_logical_sets {sets}\n-gpgpu_dtc_l1_logical_ways {ways}\n{K_OPTION} {k}\n')
        paths=configs+[overlay];effective=options(paths)
        expect=dict(template['expected_effective_options']);expect.update({
            '-gpgpu_dtc_l1_logical_sets':[str(sets)],'-gpgpu_dtc_l1_logical_ways':[str(ways)],K_OPTION:[str(k)]})
        assert effective==expect
        metadata={'-binary','-block','-cuda','-grid','-kernel','-nregs','-shmem'}
        echoes={key:value for key,value in template['expected_option_echo'].items() if key not in metadata}
        echoes.update(effective)
        spec=dict(point=name,attempt_uuid=uid,priority=priority,K=k,sets=sets,ways=ways,
              status='DRAFT_HOLD_NOT_EXECUTABLE_PREREGISTRATION',candidate_core=CANDIDATE_CORE,
              accepted_core='UNAVAILABLE_PENDING_Y2_AND_COMMON_OBSERVER_GATE',runtime_sha256='UNAVAILABLE',
              build_Framework='UNAVAILABLE',K_option=K_OPTION,K_option_value=k,
              configs=[dict(path=str(p),sha256=sha(p)) for p in paths],
              expected_effective_options=effective,expected_full_default_and_config_echo=echoes,
              trace_list=str(listed),trace_list_sha256=sha(listed),Gaussian_members=510,
              ordered_kernel_sha256=sha(PACK/'ORDERED_KERNELS.json'),
              member_manifest_sha256=sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv'),
              expected_active_thread_instructions=283685120,expected_CTAs=sum(r['complete_ctas'] for r in ordered),
              ROI='FULL_ORIGINAL_513_COMMAND_LIST_510_KERNELS',expected_SM=64,
              timeout_seconds=7200,actual_start_limit=1,global_AA_plus_AA2_start_limit=4,
              calibration_cycles=calibration,calibration_role='HISTORICAL_REFERENCE_ONLY_NOT_NEW_K0',
              event_phase='ldst_unit::invalidate source REQUEST before ordinary.invalidate request',
              event_summary='DTC_INVALIDATE_V1_SUMMARY',event_observer_contract='HOLD_NOT_SHARED_K0_K1_IN_CANDIDATE',
              required_source_event_count='NONNEGATIVE_ACTUAL_COUNT; ZERO_PRESERVED_NO_EVENT_REDEFINITION',
              invalidation_balance='changed=retained_at_event+reclaimed_at_event; sources sum=requests',
              numeric_load_correctness='UNAVAILABLE',W_full_address_scan='UNAVAILABLE_ATTRIBUTION_ONLY',
              launch_admitted=False,requires_complete_prereg_commit_push_fetch=True)
        write(PACK/'specs'/f'{name}.json',spec)
        plans.append(dict(point=name,uuid=uid,K=k,sets=sets,ways=ways,order=priority,
              spec_sha256=sha(PACK/'specs'/f'{name}.json'),actual_start_ceiling=1,timeout_seconds=7200,
              status=spec['status'],candidate_core=CANDIDATE_CORE,runtime_sha256='UNAVAILABLE'))
        full.append(dict(point=name,uuid=uid,K=k,sets=sets,ways=ways,actual_starts=0,
              status='HOLD_PENDING_ADMISSION',cycles='UNAVAILABLE',natural_exit='UNAVAILABLE',
              kernels='UNAVAILABLE',active_instructions='UNAVAILABLE',strict='NOT_RUN'))
        for key,value in sorted(effective.items()):
            deltas.append(dict(point=name,option=key,value=json.dumps(value),
                          role='K_FACTOR' if key==K_OPTION else 'TAG_FACTOR' if key in ['-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'] else 'FROZEN_COMMON'))
        receipt=dict(point=name,uuid=uid,status='NOT_RUN_HOLD',actual_starts=0,
             source_event_count='UNAVAILABLE_NOT_ZERO',invalidated_mappings='UNAVAILABLE_NOT_ZERO',
             live_refs_after_event='UNAVAILABLE',all_510_kernel_strict='UNAVAILABLE',
             note='Draft evidence only; no simulator output or successful strict run exists')
        write(ROOT/'run_receipts'/uid/'STRICT.json',receipt)
        write(PACK/'run_receipts'/uid/'STRICT.json',receipt)
    table(PACK/'PRE_REGISTRATION.tsv',plans);table(PACK/'FULL_MATRIX.tsv',full)
    table(PACK/'CONTROLLED_DELTA.tsv',deltas)
    write(PACK/'PROVENANCE.json',provenance)
    write(PACK/'PRE_REGISTRATION_STATUS.json',dict(status='CPU_DRAFT_NOT_LAUNCHABLE',
          retained_UUIDs=4,actual_starts=0,launch_admitted=False,executable_preregistration_complete=False,
          missing=['FINAL_X_RUNTIME','Y2_EXACT_CORE_PASS_AND_K0_EQUIVALENCE','Z2_PUBLISHED_V2',
                   'SHARED_EVENT_OBSERVER_CONTRACT','NO_FOREIGN_DTC_AUTHORITY','FRESH_RUN_ADMISSION'],
          no_simulator_or_coordinator_created=True))
    write(ROOT/'CPU_PREPARATION_END.json',snapshot())
    print('CPU draft prepared: four inherited UUIDs,510 Gaussian members,0 actual starts; NOT LAUNCHABLE.')


if __name__=='__main__':main()

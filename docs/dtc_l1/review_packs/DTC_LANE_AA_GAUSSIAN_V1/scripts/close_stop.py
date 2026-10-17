"""Capture the unbound scientific gate and close this CPU-only STOP package.

No simulator/coordinator launch, signal, old-lock operation, or Git mutation.
"""
from prepare_cpu import *


def main():
    names = dict(V='v-semantic-audit', W='w-trace-semantics',
                 X='x-implementation', Y='y-validation', Z='z-mechanism')
    needs = dict(V='Source-defined event contract and timing-model support domain',
                 W='Gaussian input, alias-risk and event-reachability evidence',
                 X='Independent new Core push/fetch-back, default-OFF CLI and binary identity',
                 Y='Independent validation PASS on exact new Core/binary',
                 Z='Typed metric dictionary, terminal/event counters and comparability definitions')
    dependencies=[]
    for lane, name in names.items():
        repo=Path(f'/workspace/worktrees/accel-sim-iscas2027-dtc-lane-{name}-174-v1')
        candidates=sorted(p for p in (repo/'docs/dtc_l1/review_packs').glob('DTC*') if p.is_dir())
        observed=[]
        for directory in candidates:
            for f in sorted(directory.iterdir()):
                if f.is_file() and f.suffix in ['.md','.json'] and f.stat().st_size<100000:
                    data=f.read_bytes()
                    dest=PACK/'inputs'/('LANE_'+lane)/f.name
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    with dest.open('xb') as out:out.write(data)
                    try:
                        result=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD:'+str(f.relative_to(repo))],capture_output=True,text=True,check=True)
                        blob=result.stdout.strip()
                        committed=git(repo,'hash-object',str(f))==blob
                    except subprocess.CalledProcessError:
                        blob='UNAVAILABLE_NOT_COMMITTED_AT_SNAPSHOT'
                        committed=False
                    observed.append(dict(path=str(f),snapshot=str(dest.relative_to(PACK)),
                         sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),
                         head_blob=blob,snapshot_matches_head_blob=committed))
        dependencies.append(dict(lane=lane,worktree=str(repo),requirement=needs[lane],
                     observed_head=git(repo,'rev-parse','HEAD'),
                     observed_status=git(repo,'status','--porcelain'),
                     candidate_review_pack_directories=[str(p) for p in candidates],
                     observed_files=observed,
                     binding_status='OBSERVED_STOP_OR_UNBOUND_NOT_A_PERFORMANCE_GATE_PASS',scientific_PASS=False))
    xidentity=json.loads((PACK/'inputs/LANE_X/SOURCE_AND_BINARY_IDENTITY.json').read_text())
    xdelivery=json.loads((PACK/'inputs/LANE_X/GIT_DELIVERY.json').read_text())
    assert xidentity['k1_implemented'] is False
    assert xidentity['new_option_registered'] is False
    assert xdelivery['terminal']=='SCIENTIFIC_STOP_SOURCE_EVENT_CONTRACT_MISMATCH'
    xremote=git(FW,'rev-parse','refs/remotes/origin/hrl/iscas2027-dtc-lane-x-implementation-174-v1')
    for record in dependencies[2]['observed_files']:
        rel=str(Path(record['path']).relative_to(Path(dependencies[2]['worktree'])))
        blob=git(FW,'rev-parse',xremote+':'+rel)
        data=subprocess.check_output(['git','-C',str(FW),'show',xremote+':'+rel])
        assert hashlib.sha256(data).hexdigest()==record['sha256']
        record['verified_remote_blob']=blob
    dependencies[2]['remote_fetch_back_sha']=xremote
    dependencies[2]['binding_status']='BOUND_SCIENTIFIC_STOP_K1_NOT_IMPLEMENTED'
    write(PACK/'DEPENDENCY_BINDINGS.json',dict(observed_utc=datetime.now(timezone.utc).isoformat(),lanes=dependencies))
    xcore=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-x-invalidate-optin-core-174-v1')
    xcore_remote=git(xcore,'rev-parse','refs/remotes/origin/hrl/iscas2027-dtc-lane-x-invalidate-optin-core-174-v1')
    assert xcore_remote==xidentity['built_core_sha']==xdelivery['core']['sha']
    assert git(xcore,'rev-parse',xcore_remote+':src')==git(xcore,'rev-parse',BASE_CORE+':src')
    source=[]
    for rel in ['src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h']:
        source.append(dict(path=str(CORE/rel),sha256=sha(CORE/rel)))
    write(PACK/'SOURCE_EVENT_OBSERVATION.json',dict(
        baseline_core=BASE_CORE,baseline_files=source,
        x_core_observed_head=git(xcore,'rev-parse','HEAD'),
        x_core_remote_fetch_back_sha=xcore_remote,
        x_core_observed_diff=git(xcore,'diff','--stat',BASE_CORE),
        x_core_status=git(xcore,'status','--porcelain'),
        baseline_source_path='gpu-sim.cc -> simt_core_cluster::cache_invalidate -> shader_core_ctx::cache_invalidate -> ldst_unit::invalidate -> m_L1D->invalidate',
        observation='Original flush=1 is bound. Source call sites alone do not prove accepted new DTC invalidation semantics or event count.',
        event_reachability='UNAVAILABLE',event_count='UNAVAILABLE',support_domain='UNAVAILABLE',
        inference_no_event=False, new_binary_identity='UNAVAILABLE'))

    # Read-only binding of historical strict receipts; never recast as new K0.
    refs=json.loads((PACK/'ACCEPTED_ORIGINAL_REFERENCES.json').read_text())
    for r in refs:
        strictfile=(PILOT/'inputs/Gaussian_OO128_STRICT_RECHECK.json' if r['tag']=='32x4'
                    else Path('/workspace/dtc-tag-pilot-174-v1/63f15c5a-a731-4c07-a3ce-c65312142a50.strict.json'))
        strict=json.loads(strictfile.read_text())
        base=strict.get('base',strict)
        assert base['stdout_sha256']==r['stdout_sha256']
        assert int(base['cycles'])==r['cycles']
        assert base['status']=='PASS_CHECKED_SCOPE'
        assert base['attempt_uuid']==r['uuid']
        write(PACK/'inputs'/f'ORIGINAL_{r["tag"]}_STRICT_BINDING.json',dict(
            source_path=str(strictfile),sha256=sha(strictfile),status=strict['status'],
            original_uuid=r['uuid'],original_stdout_sha256=r['stdout_sha256'],
            verified_cycles=r['cycles'],new_K0=False))

    metrics=[('gpu_tot_sim_cycle','GPU cycles','1','Final cumulative total; never sum cumulative kernel blocks'),
      ('gpu_tot_sim_insn','active-thread instructions','1','Final cumulative total must equal283685120'),
      ('gpu_tot_issued_cta','CTAs','1','Final cumulative total must match ordered manifest'),
      ('DTC_SERVICE_V1_samples','SM cycles','1','Must equal64*gpu_tot_sim_cycle'),
      ('DTC_SERVICE_V1_pib_integral','entry*SM cycles','DTC_SERVICE_V1_samples','All64SM cycle mean PIB occupancy'),
      ('DTC_SERVICE_V1_physical_integral','line*SM cycles','DTC_SERVICE_V1_samples','All64SM cycle mean physical occupancy'),
      ('DTC_SERVICE_V1_collected_sectors','collected32B sectors','1','Collection count; not independent lower-response fragments'),
      ('DTC_SERVICE_V1_fully_ready_to_complete_sum','warp cycles','DTC_SERVICE_V1_retired','Conditional mean; numerator=ready_to_collect_sum+collection_cycles+wb_wait'),
      ('DTC_SERVICE_V1_retired','fully-ready cacheable warps','1','Conditional service denominator'),
      ('DTC_SERVICE_V1_ready_to_collect_sum','warp cycles','DTC_SERVICE_V1_retired','Conditional ready-to-collect mean'),
      ('DTC_SERVICE_V1_collection_cycles','warp cycles','DTC_SERVICE_V1_retired','Conditional collection mean'),
      ('DTC_SERVICE_V1_wb_wait','warp cycles','DTC_SERVICE_V1_retired','Conditional writeback wait mean'),
      ('DTC_SERVICE_V1_map_loss_to_free_sum','line cycles','DTC_SERVICE_V1_map_loss_to_free_count','Completed mapping-loss-to-free intervals; censored intervals not silently included'),
      ('DTC_SERVICE_V1_map_loss_to_free_count','completed intervals','1','Denominator excludes incomplete intervals'),
      ('DTC_L1_oo_valid_hits','128B reference outcomes','accepted_refs','ready fraction; accepted_refs=valid_hits+pending_hits+new_misses'),
      ('DTC_L1_oo_pending_hits','128B reference outcomes','accepted_refs','pending fraction'),
      ('DTC_L1_oo_new_misses','128B allocations','accepted_refs','new fraction; accepted_refs must equal completion_dependency_count'),
      ('DTC_L1_oo_tag_evictions','evictions','1','Never substitute for invalidation mapping count'),
      ('DTC_L1_oo_lower_created','lower requests','1','128B lifecycle request identity; not DRAM payload'),
      ('source_defined_invalidate_event_count','events','1','Actual field UNAVAILABLE; numeric expected count must be bound before execution'),
      ('invalidate_mapping_count','mappings','1','Actual field UNAVAILABLE; no fabricated PASS'),
      ('live_ref_legality_after_invalidate','lifecycle invariant','1','Actual receipt UNAVAILABLE; generation and held-reference behavior required'),
      ('independent_sector_returns','32B response sectors','1','UNAVAILABLE distinct field'),
      ('numeric_load_values','values','1','UNAVAILABLE in SASS timing model'),
      ('L2_read_sectors','32B sectors','1','UNAVAILABLE until Lane Z typed stream/controller definition bound'),
      ('DRAM_read_payload','bytes','1','UNAVAILABLE until Lane Z atom/controller definition bound'),
      ('DRAM_write_payload','bytes','1','UNAVAILABLE until Lane Z atom/controller definition bound')]
    table(PACK/'METRIC_DICTIONARY.tsv',[dict(metric=m,unit=u,denominator=d,definition=n,
           status='PROPOSED_FROM_ACCEPTED_BASELINE_UNBOUND_LANE_Z',missing_policy='UNAVAILABLE_NOT_ZERO',
           finite11=m.startswith('DTC_SERVICE_V1_')) for m,u,d,n in metrics])
    policy=dict(status='FROZEN_CPU_RESERVATION_NOT_AN_EXECUTION_GRANT',full_attempt_ceiling=4,
        per_uuid_actual_start_limit=1,default_parallel=1,selected_max_parallel=1,
        optional_parallel2='NOT_ENABLED',wall_timeout_seconds_per_point=7200,
        timeout_origin='FIRST_ACTUAL_SIMULATOR_START_ABSOLUTE_MONOTONIC_DEADLINE',
        run_order=['K0_32x4','K0_64x8','K1_32x4','K1_64x8'],
        require_both_K0_strict_exact_calibration_before_any_K1=True,
        admission=dict(host='huangrulin-174',host_MemAvailable_min_gib=32,cgroup_headroom_min_gib=32,
            disk_free_min_gib=10,memory_full_PSI_avg10_max=1,io_full_PSI_avg10_max=25,
            probe_interval_seconds=10,swap_in_out_page_delta_max=0,oom_event_delta_max=0,
            all_U_recorded_process_incarnations_absent=True,U_lock_owners_allowed=0,
            unknown_simulator_or_DTC_coordinator_allowed=0,
            all_projects_count_for_RSS_cgroup_swap_PSI_disk_IO=True,
            per_sim_RSS_reservation_gib=4,per_sim_disk_reservation_gib=2),
        monitor_interval_seconds=30,resource_stop=dict(cgroup_headroom_min_gib=8,disk_free_min_gib=2,
            memory_full_PSI_avg10_max=10,consecutive_samples=3,signal_only_own_PID_start_ticks_bound_process_groups=True),
        failure_policy='PRESERVE_ALL_NEGATIVE_DEGRADED_TIMEOUT_DEADLOCK_AND_PARTIAL_RAW_NO_RETUNE_NO_SECOND_ACTUAL_START',
        wrapper_recovery='ORIGINAL_UUID_ABSOLUTE_TIMEOUT_ONLY_WITH_PROOF_OF_NO_SECOND_SIMULATOR_START',
        actual_new_full_starts=0,canary_starts=0)
    write(PACK/'EXECUTION_CONTRACT.json',policy)
    samples=[]
    for name in ['CPU_START_RESOURCES.json','CPU_END_RESOURCES.json']:
        r=json.loads((ROOT/name).read_text())
        current=int(r['cgroup']['memory.current'])
        lim=r['cgroup']['memory.max']
        samples.append(dict(phase=name,utc=r['utc'],host=r['host'],
           cgroup_current_bytes=current,cgroup_limit_bytes=lim,
           cgroup_headroom_bytes=int(lim)-current if lim!='max' else 'UNAVAILABLE_UNLIMITED',
           proc_RSS_sum_bytes=r['all_project_rss_bytes'],cgroup_swap_bytes=r['cgroup']['memory.swap.current'],
           pswpin=r['pswpin'],pswpout=r['pswpout'],disk_free_bytes=r['disk_free_bytes'],
           memory_PSI=r['pressure']['memory'].strip().replace('\n','; '),
           IO_PSI=r['pressure']['io'].strip().replace('\n','; '),
           cgroup_IO_stat=r['cgroup']['io.stat'].replace('\n','; '),
           snapshot_sha256=sha(ROOT/name),actual_AA_sims=0,admission='NOT_REQUESTED_SCIENTIFIC_GATE_STOP'))
    table(PACK/'EXECUTION_RESOURCES.tsv',samples)
    compare=[]
    for m,u,d,n in metrics:
        compare.append(dict(metric=m,unit=u,denominator=d,K0_32x4='UNAVAILABLE',K0_64x8='UNAVAILABLE',
            K1_32x4='UNAVAILABLE',K1_64x8='UNAVAILABLE',K_main_effect='UNAVAILABLE',
            Tag_main_effect='UNAVAILABLE',K_Tag_interaction='UNAVAILABLE',status='NO_NEW_ACCEPTED_POINTS'))
    table(PACK/'TERMINAL_MECHANISM_COMPARISON.tsv',compare)
    u=json.loads((PACK/'U_TERMINATION_PROOF.json').read_text())
    stop=dict(status='STOP_SCIENTIFIC_SCOPE_UNBOUND',recorded_utc=datetime.now(timezone.utc).isoformat(),
          launch_admitted=False,actual_full_starts=0,canary_starts=0,
          upstream_X_terminal='SCIENTIFIC_STOP_SOURCE_EVENT_CONTRACT_MISMATCH',
          upstream_X_implemented=False,
          unbound=['V_FINAL_SCIENTIFIC_ADMISSION','W_ALIAS_AND_REACHABILITY','X_ADMISSIBLE_K1_BINARY',
                   'Y_INDEPENDENT_PASS','Z_METRICS','MODEL_SUPPORT_DOMAIN','EVENT_COUNT','NEW_K0_BEHAVIOR_DIFFERENCE'],
          user_stop_rule='若没有合法事件或模型支持域未确定，STOP，不运行无意义/不合格性能矩阵。',
          no_legal_event_claim=False,zero_event_claim=False,
          U_all_recorded_incarnations_absent=u['all_recorded_incarnations_absent'],
          U_observed_locks_released=u['all_observed_old_locks_released'],
          other_lane_processes_modified=False,old_locks_acquired=False,background_launcher_created=False,
          outcome='CPU design reservation preserved; full execution preregistration incomplete; no performance conclusion.')
    write(PACK/'STOP_RECORD.json',stop)
    checks=dict(four_unique_UUIDs=True,only_authorized_four_design_points=True,
           complete_original_Gaussian_members_rehashed=True,ordered_510_active_instruction_manifest_bound=True,
           no_actual_simulator_starts=True,missing_dependencies_fail_closed=True,
           original_controls_not_substituted_for_new_K0=True,U_locks_never_acquired=True,
           new_binary_bound=False,scientific_domain_bound=False,event_reachability_proven=False,
           independent_Y_PASS=False,Z_definitions_bound=False,full_execution_preregistration_complete=False,
           new_K0_calibration=False,new_K1_receipts=False,performance_matrix_complete=False)
    write(PACK/'STRICT_AUDIT.json',dict(status='STOP_NOT_PERFORMANCE_PASS',checks=checks,
           required_new_run_fields_status='UNAVAILABLE_NO_RUN',natural_exit0='UNAVAILABLE',
           event_count='UNAVAILABLE',invalidate_mapping_count='UNAVAILABLE',live_ref_legality='UNAVAILABLE',
           independent_sector_return_count='UNAVAILABLE',ordinary_internal_MSHR_occupancy='UNAVAILABLE',
           numeric_load_values='UNAVAILABLE',per_uuid_receipts_root=str(ROOT/'receipts')))
    for f in sorted((ROOT/'receipts').glob('*/*')):
        dest=PACK/'run_receipts'/f.parent.name/f.name
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as out:out.write(f.read_bytes())
    rawfiles=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size)
              for p in sorted(ROOT.rglob('*')) if p.is_file()]
    table(PACK/'RAW_FILES_SHA256.tsv',rawfiles)
    rows=list(csv.DictReader((PACK/'PRE_REGISTRATION.tsv').open(),delimiter='\t'))
    lines=['# Lane AA: scientific STOP, zero new simulations','',
       '本轮状态 **STOP_SCIENTIFIC_SCOPE_UNBOUND**，实际 full Gaussian 启动 **0/4**，canary **0**。',
       '已远端回读并绑定Lane X的SCIENTIFIC_STOP_SOURCE_EVENT_CONTRACT_MISMATCH：K1未实现、新开关未注册，Core仅文档差分。Lane V给出待审语义合同，Lane W为DEFERRED_SAFE_STOP，地址别名与实际事件次数仍UNAVAILABLE；Y独立PASS/Z最终定义未绑定。模型支持域和新K1 binary不具准入条件，按用户门槛停止；没有声称事件为零，也没有性能结论。','',
       '已建立独立分支 `hrl/iscas2027-dtc-lane-aa-flush-factorial-174-v1` 和本 worktree；raw root `/workspace/dtc-lane-aa-gaussian-174-v1`。四点只完成 UUID/设计预留，完整可执行预注册尚未完成，缺项明确 UNAVAILABLE。','',
       '| Point | Reserved UUID | State |','| --- | --- | --- |']
    lines += [f'| {r["point"]} | {r["uuid"]} | NOT_STARTED |' for r in rows]
    lines += ['',
       '完整原 Gaussian list SHA `6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9`。全部510成员已现场重哈希，原有序CPU body audit绑定283,685,120 active-thread instructions，见 INPUT_PREFLIGHT.json、GAUSSIAN_MEMBERS_SHA256.tsv 和 ORDERED_KERNELS.json。未修改 trace/list。','',
       'U coordinator PID2132794/start_ticks898867525、两点 runner/process 的记录实例均已现场确认不存在；7个被观察的旧执行/归档锁无持有者，AA从未获取旧锁。U终态与其归档失败均原样保留，不能把归档失败标 PASS。现场证明见 U_TERMINATION_PROOF.json；这只解除 U运行互斥门槛，不解除科学门槛。','',
       '已绑定历史32×4周期3,798,174和64×8周期3,278,356的原stdout SHA及strict收据。两者仅为校准参考；尚无新K0。后续仅在完整准入且预注册commit/push/fetch-back后，先跑两个新K0并精确校准，任何不匹配停止全部K1，不retune。','',
       '默认并发上限固定1，每点7200秒、一次实际启动；未启用并发2。CPU前后资源快照包含所有项目RSS、cgroup、swap/PSI、磁盘和I/O；没有把这两个CPU快照当作10秒运行准入probe。EXECUTION_RESOURCES.tsv保留数值，RAW_FILES_SHA256.tsv绑定原始快照。','',
       'METRIC_DICTIONARY.tsv为基于接受基线的候选定义，Lane Z尚未绑定；缺失事件/映射/引用合法性字段保持UNAVAILABLE。COMPARISON_FORMULAS.md固定K、Tag主效应与difference-of-differences交互；FULL_MATRIX.tsv与TERMINAL_MECHANISM_COMPARISON.tsv四点均无测量值。STRICT_AUDIT.json明确不是性能PASS。','',
       '最终小文件提交、远端push/fetch-back、tree与clean状态由raw root中的FINAL_PUSH_FETCH_BACK.json闭合，避免Git提交自引用。STOP后不保留自动发射或重启U进程；不启动T2、GEMM、新Tag、其它输入或修改原44行/GM12/论文主图。']
    (PACK/'LATEST_REPORT.md').write_text('\n'.join(lines)+'\n')
    print('STOP_SCIENTIFIC_SCOPE_UNBOUND; zero actual starts; four reservations retained.')


if __name__=='__main__':
    main()

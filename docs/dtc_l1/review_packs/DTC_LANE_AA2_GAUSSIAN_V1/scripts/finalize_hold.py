"""Close the authorized CPU/authority STOP path. Does not dispatch simulations."""
from common import *
from prepare_cpu import scan_starts
from execution_guard import evaluate
from zoneinfo import ZoneInfo


def save(p,obj):
    Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def rewrite_table(p,rows):
    with Path(p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)


def main():
    # A stale conflict is not sufficient for closure; observe the actual same
    # incarnation and its live fd lock again, without acquiring or signaling it.
    current=proc(1425986)
    assert current and current['start_ticks']==584741606,'Foreign authority state changed; re-audit instead of reusing old HOLD'
    info=Path('/proc/1425986/fdinfo/9').read_text()
    assert 'lock:' in info and 'FLOCK' in info
    target=os.readlink('/proc/1425986/fd/9')
    write(PACK/'FINAL_AUTHORITY_WITNESS.json',dict(utc=now(),process=current,fd=9,fd_target=target,
        fdinfo=info,status='HOLD_FOREIGN_DTC_DISPATCH_AUTHORITY_AND_LOCK_STILL_PRESENT',
        AA2_old_lock_acquisitions=0,AA2_other_process_signals=0))
    write(ROOT/'FINAL_RESOURCE_SNAPSHOT.json',snapshot())
    scan=scan_starts();write(PACK/'FINAL_UUID_START_CONFLICT_AUDIT.json',scan)
    assert not scan['matching_actual_RUN_STARTs'],'STOP_RESERVED_UUID_NOW_HAS_A_RUN_START'
    pub=json.loads((PACK/'PUBLISHED_BINDINGS.json').read_text())
    y=json.loads((PACK/'Y2_GATE_BINDING.json').read_text())
    assert y['accepted_PASS_K1_OO_MODEL_SCOPE'] and y['accepted_K0_equivalence']
    runtime=next(b for b in pub['candidate_artifacts'] if b['path'].endswith('accel-sim.out'))
    library=next(b for b in pub['candidate_artifacts'] if b['path'].endswith('libcudart.so'))
    assert sha(runtime['path'])==runtime['sha256'] and sha(library['path'])==library['sha256']
    oldplans=list(csv.DictReader((PACK/'PRE_REGISTRATION.tsv').open(),delimiter='\t'))
    write(ROOT/'DRAFT_REGISTRATION_BEFORE_FINAL_BINDING.json',oldplans)
    plans=[];matrix=[]
    for plan,point in zip(oldplans,POINTS):
        name,uid,k,sets,ways,calibration=point
        path=PACK/'specs'/f'{name}.json';spec=json.loads(path.read_text())
        spec.update(runtime_path=runtime['path'],runtime_sha256=runtime['sha256'],
             runtime_library_path=library['path'],runtime_library_sha256=library['sha256'],
             build_Framework=pub['Framework_build_source'],source_Core_commit=CANDIDATE_CORE,
             Y2_published_commit=y['published_fetch_back_commit'],Y2_model_verdict=y['published_verdict'],
             accepted_core='UNAVAILABLE_FULL_EXECUTION_AUTHORITY_AND_OBSERVER_HOLD',
             status='DRAFT_HOLD_NOT_EXECUTABLE_PREREGISTRATION',
             effective_profile_sha256=sha(PACK/'effective_options'/f'{name}.tsv'),
             source_event_metric_dictionary_sha256=sha(PACK/'METRIC_DICTIONARY.tsv'),
             physical_conservation_contract_sha256=sha(PACK/'PHYSICAL_CONSERVATION_DELTA.md'),
             execution_guard_sha256=sha(PACK/'scripts/execution_guard.py'),
             production_runner_sha256='UNAVAILABLE_NOT_RELEASED_WHILE_AUTHORITY_HOLD',
             full_execution_admitted=False)
        save(path,spec)
        plan.update(spec_sha256=sha(path),runtime_sha256=runtime['sha256'])
        plans.append(plan)
        matrix.append(dict(point=name,uuid=uid,K=k,sets=sets,ways=ways,actual_starts=0,
            status='HOLD_FOREIGN_DTC_AUTHORITY_AND_LOCK',cycles='UNAVAILABLE',natural_exit='UNAVAILABLE',
            kernels='UNAVAILABLE',active_instructions='UNAVAILABLE',strict='NOT_RUN',
            Y2_model_scope='PASS_K1_OO_MODEL_SCOPE',observer_profile='REVIEW_UNRESOLVED',
            historical_calibration_cycles=calibration,historical_cycles_are_new_K0=False))
        receipt=json.loads((ROOT/'run_receipts'/uid/'STRICT.json').read_text())
        receipt.update(status='NOT_RUN_HOLD_EXECUTION_AUTHORITY',primary_reason='LIVE_FOREIGN_DTC_DISPATCH_AUTHORITY_AND_FD_LOCK',
                       secondary_reason='SHARED_OBSERVER_PROFILE_REVIEW_UNRESOLVED',spec_sha256=sha(path),
                       Y2_model_scope='PASS_K1_OO_MODEL_SCOPE',new_K0_calibration='NOT_RUN',
                       natural_exit='UNAVAILABLE',Core=CANDIDATE_CORE,runtime_sha256=runtime['sha256'])
        save(ROOT/'run_receipts'/uid/'STRICT.json',receipt);save(PACK/'run_receipts'/uid/'STRICT.json',receipt)
        rawrows=[dict(path='STRICT.json',sha256=sha(ROOT/'run_receipts'/uid/'STRICT.json'),status='EXISTS_METADATA_ONLY'),
                 dict(path='simulator.stdout',sha256='UNAVAILABLE',status='NOT_CREATED_NO_START'),
                 dict(path='simulator.stderr',sha256='UNAVAILABLE',status='NOT_CREATED_NO_START')]
        table(ROOT/'run_receipts'/uid/'RAW_SHA256.tsv',rawrows)
        table(PACK/'run_receipts'/uid/'RAW_SHA256.tsv',rawrows)
    rewrite_table(PACK/'PRE_REGISTRATION.tsv',plans);rewrite_table(PACK/'FULL_MATRIX.tsv',matrix)
    reg=json.loads((PACK/'PRE_REGISTRATION_STATUS.json').read_text())
    reg.update(status='DRAFT_CLOSED_WITH_AUTHORITY_HOLD_ZERO_STARTS',
       missing=['NO_FOREIGN_DTC_AUTHORITY_AND_FD_LOCK','SHARED_EVENT_OBSERVER_PROFILE_QUALIFICATION',
                'PRODUCTION_RUNNER_AND_COMPLETE_EXECUTABLE_PREREGISTRATION_PUSH_FETCH'],
       X_V_Z2_Y2_and_Gaussian_identity_bound=True,all_267_option_profiles_closed=True,
       executable_preregistration_complete=False,launch_admitted=False,actual_starts=0)
    save(PACK/'PRE_REGISTRATION_STATUS.json',reg)
    guard=evaluate();assert guard['status']=='HOLD_FAIL_CLOSED_NO_SIMULATOR_LAUNCH'
    assert guard['checks']['Y2_exact_Core_option_PASS'] and guard['checks']['Y2_K0_equivalence_gate']
    assert not guard['checks']['current_authority_and_resources']
    write(PACK/'FINAL_ADMISSION.json',guard)
    q=subprocess.run([__import__('sys').executable,'-B',str(PACK/'scripts/execution_guard.py'),'--execute'],
                      capture_output=True,text=True,cwd=ROOT)
    assert q.returncode==3
    write(ROOT/'GUARD_CHECK_FINAL.json',dict(expected_exit=3,actual_exit=q.returncode,
        script_sha256=sha(PACK/'scripts/execution_guard.py'),stdout=json.loads(q.stdout),stderr=q.stderr,
        simulator_starts=0,status='PASS_EXPECTED_GUARD_FAIL_CLOSED_ONLY'))
    write(PACK/'SOURCE_IDENTITY.json',dict(Core=CANDIDATE_CORE,frozen_Core=BASE_CORE,
        X_review=pub['X_review_fetch_back_commit'],V_contract=V_SHA,Z2=pub['Z2_remote_fetch_back_commit'],
        Y2=y['published_fetch_back_commit'],runtime=runtime,library=library,
        Framework_build_source=pub['Framework_build_source'],AA_V1_ancestor=AA_SHA,
        source_model_scope='PASS_K1_OO_MODEL_SCOPE',full_execution_admitted=False,
        runtime_executed_on_Gaussian=False,second_Core_created=False))
    write(PACK/'STOP_RECORD.json',dict(utc=now(),status='STOP_WITH_FOUR_HOLD_CELLS_NO_STARTS',
        primary_reason='LIVE_FOREIGN_DTC_DISPATCH_AUTHORITY_AND_FD_LOCK',
        foreign_pid=1425986,foreign_start_ticks=584741606,
        observer_review='AA2-OBS-001_UNRESOLVED_NOT_SILENTLY_WAIVED',
        X_real_K1_bound=True,V_Z2_Y2_bound=True,Y2_scope_PASS=True,
        W_full_address_scan='UNAVAILABLE_ATTRIBUTION_GAP_NOT_EXECUTION_DENIAL_REASON',
        combined_AA_AA2_actual_starts=0,global_actual_start_cap=4,canary_starts=0,
        all_four_new_points='NOT_RUN_HOLD',old_Goal_restarted=False,old_reports_modified=False,
        background_launcher_created=False,other_processes_signaled=False,old_locks_acquired=False,
        performance_conclusions=False,complete_executable_preregistration=False))
    write(PACK/'STRICT_AUDIT.json',dict(status='HOLD_NOT_A_PERFORMANCE_PASS',
        Gaussian_input_identity='PASS_510_MEMBER_REHASH_AND_ORDERED_ACTIVE_INSTRUCTIONS',
        unique_inherited_UUIDs='PASS_NO_ACTUAL_RUN_START_IN_INITIAL_AND_FINAL_REGISTERED_LOCAL_SCOPE',
        exact_X_Runtime_library_SHA_and_loader='PASS_CPU_IDENTITY_ONLY',
        default_option_profiles='PASS_230_CORE_CPU_PLUS23_UNCHANGED_RUNTIME_PLUS14_UNCHANGED_FRAMEWORK',
        omitted_explicit_zero='PASS_CPU_ONLY',Y2='PASS_K1_OO_MODEL_SCOPE_EXACT_CORE_AND_OPTION',
        physical_counter_contract='PASS_OWN_CPU_POSITIVE_AND_NEGATIVE_WITNESS_ONLY',
        current_execution_authority='HOLD_FOREIGN_PROCESS_AND_FD_LOCK',
        full_new_K0_calibration='NOT_RUN',new_K1_events='UNAVAILABLE_NOT_RUN',
        natural_exit_510_CTA_active_ref_credit_physical_ordinary_sector_finite='NOT_RUN',
        architectural_values='UNPROVEN',same_observer_profile='REVIEW_UNRESOLVED',
        actual_full_starts=0,full_matrix_performance_PASS=False))
    tooling=[dict(path=str(f.relative_to(PACK)),sha256=sha(f),role='CPU_PREPARATION_OR_GUARD_NOT_RELEASED_PRODUCTION_RUNNER')
             for f in sorted((PACK/'scripts').glob('*')) if f.is_file()]
    table(PACK/'TOOLING_SHA256.tsv',tooling)
    raw=[dict(path=str(f.relative_to(ROOT)),sha256=sha(f),bytes=f.stat().st_size)
         for f in sorted(ROOT.rglob('*')) if f.is_file()]
    table(PACK/'RAW_FILES_SHA256.tsv',raw)
    date=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    lines=['# AA2 Gaussian: execution HOLD, zero full starts','',
      f'收口时间（北京时间）：{date}。状态 **STOP_WITH_FOUR_HOLD_CELLS_NO_STARTS**，AA V1+AA2实际full starts仍 **0/4**，canary0。',
      '当前决定性阻塞是存活旧DTC自动派发authority及其FLOCK；不因U早已结束或内存/IO探针数值通过而绕过。完整可执行预注册未发布，四份spec仍明确为DRAFT_HOLD。','',
      '| Point | Inherited UUID | Final state |','| --- | --- | --- |']
    lines += [f'| {p[0]} | {p[1]} | HOLD / NOT_RUN |' for p in POINTS]
    lines += ['',
      '已从远端回读绑定真正K1 Core `'+CANDIDATE_CORE+'`、X trace executable SHA `'+runtime['sha256']+'` 与实际shared library SHA `'+library['sha256']+'`。CPU parser探针复制到AA2，ldd确认加载同一X库，未执行accel-sim.out。Framework build source为`'+pub['Framework_build_source']+'`，与AA2 orchestration分开记载。不是历史f8b34dd7文档STOP Core。','',
      'V `'+V_SHA+'`、Z2 V2合同（SHA `'+pub['Z2_contract_sha256']+'`）及Y2发布 `'+y['published_fetch_back_commit']+'` 均已绑定。Y2裁决为 **PASS_K1_OO_MODEL_SCOPE**，生产option默认/OFF/ON和CPU K0等价检查通过；资格仅限披露的OO逻辑/API及生产语句夹具，不含完整GPU/NoC、真实operand collector、数值load或PPA。没有把旧Y1 FAIL_CLOSED改写成新Core裁决。','',
      '原Gaussian list SHA `6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9`。Gaussian明确510成员、513命令（3 HtoD）、283,685,120 active-thread instructions；全部510成员重新SHA256，约877MB读取限64MiB/s。511仅是T中GEMM+Gaussian合计，不当成Gaussian成员数。两个时点的UUID扫描未发现预留UUID实际RUN_START。','',
      '有效配置固定OO128、physical640×128B、ordinary16KiB、shared96KiB、64SM、原4bank/finite服务、cap32768、1410MHz和flush_l1=1，唯一预设变化为K与Tag。四点各有267项预期profile：230项用精确X库CPU parser回读，23项runtime和14项Framework字段由接受echo与逐字未变注册源码绑定。省略K0和显式0的完整Core profile相等。剔除旧echo抽取器误收的7项trace header元数据，旧AA/T证据未改。完整实际simulator echo仍须在未来full strict中再次核对。','',
      '旧authority **PID1425986/start_ticks584741606** 仍存活；`fdinfo/9`明确FLOCK，target为`/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock`。它的脚本具有未来派发路径。全局/proc/locks未显示该锁，补充fdinfo后不能声称已释放。见FINAL_AUTHORITY_WITNESS.json与LOCK_FDINFO_SUPPLEMENT.json。AA2未获取旧锁、发送信号、删除其它文件或建立新模拟authority。','',
      '两次10秒资源探针中host/cgroup内存、disk、memory/IO PSI、swap和OOM差分均通过；其它项目sim/RTL/编辑器等全部计入。执行权检查仍关闭，未核DTC控制helper也保留，不用数值资源余量代替科学与authority准入。EXECUTION_RESOURCES.tsv和raw快照保留实值，最后快照不冒充新的10秒准入probe。','',
      'X仅在K1路径观测并打印source-event summary，K0缺字段保持UNAVAILABLE；X/Y2的零额外模拟cycle模型、host bookkeeping成本及共同observer合同不能混称。AA2-OBS-001保留具体条款审查，不请求第二套Core或增加计数器来修平。W完整地址扫描为UNAVAILABLE机制归因缺口，按用户AA2指令记录W_SCOPE_CLAUSE_REVIEW.md，不作为本次不执行的原因，也不声称已测复用或值正确。','',
      '已在新性能之前固定物理守恒完整项：new_misses=allocated+immediate_reclaims+final_ref_reclaims+source_reclaimed_at_event。K1 Ref0 source回收不进入旧immediate counter，持live Ref者最终释放已进入final_ref，不能重复扣减。独立CPU生产header正反例通过，属于计数合同校核，不代替Y2或full-run strict。','',
      '未有新K0，历史3798174/3278356仅校准参考；以后须两新K0先于任意K1且精确通过，差异即STOP，不retune或补跑。每点7200秒、一次实际启动，合计AA+AA2仍最多4；不重置预算。所有full natural exit、510kernel/CTA/instructions、Ref/credit/PIB/physical/ordinary/sector、finite及真实event验收目前NOT_RUN。四格、主效应/交互、类型化机制字段均UNAVAILABLE，完整保留HOLD。','',
      '小文件最终commit/push/fetch-back、全部文件blob比对和clean由AA2 raw root的FINAL_PUSH_FETCH_BACK.json闭合。旧AA83文件逐字未变，旧raw/Goal未覆盖、未重启。CPU guard的--execute按预期退出3，无simulator启动；本包没有生产runner或后台自动派发。STOP后不启动T2、新Tag、新Core、其它输入、GM12、主配置晋升或论文修改。']
    (PACK/'LATEST_REPORT.md').write_text('\n'.join(lines)+'\n')
    print('Closed four HOLD cells;0/4 actual starts; published X/V/Z2/Y2 bound; live foreign authority unchanged.')


if __name__=='__main__':main()

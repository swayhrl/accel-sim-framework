"""Publish no new experiments: retain original accounting and project the32 cells."""
from pathlib import Path
import sys,json,time,collections,subprocess
P=Path(__file__).resolve().parent;ROLL=P.parent/'MS20261020_E2_MAIN_ROLLING_r1'
sys.path.insert(0,str(ROLL));import publish_state as ps
c=ps.c;coord=c.Coordinator();s=coord.snapshot();data=json.loads((c.SHARED/'RUN_REGISTRY.json').read_text())
initial=json.loads((ROLL/'POST_SPACE_INDEPENDENT_ADMISSION_PASS.json').read_text())
assert s['actual_starts']==20 and s['remaining_start_capacity']==20
assert s['t0_unix']==initial['T0']==1792414193 and s['controller']['state']=='STOPPED'
assert not any(r['status'] in c.ACTIVE for group in ['runs','resource_leases'] for r in data[group].values())
assert s['scientific_holds']==initial['scientific_holds']
assert {a['attempt_id']:c.retained_tree_bytes(Path(a['result_directory'])) for a in s['attempts'][:14]}==initial['retained_bytes_by_attempt']
for e in initial['failures']:
    a=next(a for a in s['attempts'] if a['attempt_id']==e['attempt_id'])
    assert a['state']==e['state'] and a['receipt_sha256']==e['original_receipt']['sha256']
    assert c.digest(a['receipt_path'])==a['receipt_sha256']
assert s['accepted_results']['E013_33cffb17']==initial['accepted_results']['E013_33cffb17']
assert s['accepted_pairs']['V2_MAIN_convolutionSeparable_S_F_MAIN61']==initial['accepted_pairs']['V2_MAIN_convolutionSeparable_S_F_MAIN61']
new=s['attempts'][14:];assert len(new)==6 and all(a['state']=='COMPLETE_VALID' and a['actual_start'] for a in new)
usage=c.output_usage();assert usage['old_bytes']==initial['output_usage']['old_bytes']
growth=usage['new_bytes']-initial['output_usage']['new_bytes'];assert growth==589725365
buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']}
assert buckets['contingency']==8 and sum(buckets.values())==20 and buckets['seven_workload_common_S_F']==12
accepted={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED'};assert len(accepted)==4
by_condition=collections.defaultdict(list)
for a in s['attempts']:
    f=Path(a['result_directory'])/'input_spec.json'
    if not f.exists():continue
    spec=json.loads(f.read_text())
    if 'condition_id' not in spec:continue
    by_condition[spec['condition_id']].append(dict(attempt_id=a['attempt_id'],state=a['state'],profile=a.get('profile'),binary_sha256=a['identity']['binary_sha256'],actual_start=a.get('actual_start'),budget_bucket=c.policy_v2.charged_bucket(a,s['reservations'])))
rows=[]
for row in s['full_system_matrix']['matrix']['conditions']:
    matches=by_condition.get(row['condition_id'],[])
    decision='ALREADY_CHARGED_OR_TERMINAL_NO_AUTOMATIC_REPLAY' if matches else 'BTREE_INPUT_HOLD_NO_CURRENT_PRODUCER_AND_INPUT_QUALIFICATION' if row['workload']=='btree' else 'UNSTARTED_PROFILE_NOT_IN_CURRENT_E_QUALIFIED_S_F_QUEUES'
    rows.append(dict(condition_id=row['condition_id'],workload=row['workload'],profile=row['profile'],group=row['group'],priority=row['priority'],actual_attempts=matches,next_admission=decision,automatic_start_authorized=False))
assert sum(not r['actual_attempts'] for r in rows)==20
projection=dict(schema='E2_ORIGINAL32_EXECUTION_PROJECTION_AFTER_SPACE_RESUME_V1',at_unix=time.time(),matrix_unchanged=s['full_system_matrix'],conditions=rows,remaining_actual_start_capacity=20,budget_buckets=buckets,ready_never_started_qualified_queues_remaining=[],qualification_scope='Current main61 E proofs cover S/F of Conv/FWT/Vector/CFD/DWT/SAD. The remaining original32 cells are18 other profiles lacking current producer/profile qualification and Btree S/F on HOLD.',FWT_rerun_proposal=str(P.parent/'MS20261020_E2_EXIT_PERSISTENCE_REPAIR_r1/FWT_RERUN_REALLOCATION_PROPOSAL.json'),FWT_and_Vector_retry_automatic=False,no_reprioritisation_or_reallocation_adopted=True,next_concrete_boundary='No further currently qualified unstarted main condition. Preserve remaining20 for original32 conditions; each needs exact producer/profile/input/E qualification and frozen time/resource/result gates. FWT/Vector retries need an explicit internal allocation decision; no contingency extension.')
c.write_json(P/'REMAINING_ORIGINAL_MATRIX_PROJECTION.json',projection)
resources=c.local_resources();fs={name:subprocess.check_output(args,text=True) for name,args in [('df_bytes',['df','-B1','/workspace','/root/share']),('df_inodes',['df','-i','/workspace','/root/share'])]}
report=dict(schema='E2_POST_SPACE_THREE_FORMAL_PAIRS_FINAL_RECEIPT_V1',at_unix=time.time(),status='ALL_THREE_NEW_PAIRS_CURRENT_ACCEPTED',source_identity=s['final_source_identity'],original_T0=s['t0_unix'],actual_starts=20,remaining=20,budget_buckets=buckets,planned_used=12,contingency_remaining=0,accepted_pairs=accepted,new_attempts=new,output_usage=usage,actual_result_growth_this_resumption_bytes=growth,growth_by_new_pair_bytes={'cfd_097k':191906948,'dwt2d':210699839,'sad':187118578},old_first14_retained_sizes_unchanged=True,old_failures_INCOMPLETE_HOLD_and_Vector_identity_unchanged=True,controller=s['controller'],active_runs={},active_leases={},resources=resources,filesystem=fs,default_maximum_simulators=2,new_Goal_or_controller_created=False,source_main_or_archive_rebuilt=False,old_NATIVE17_repeated=False,other_project_policies_changed=False,additional_migration_requested=False,cumulative_result_accounting_not_reset=True,remaining_matrix_projection=str(P/'REMAINING_ORIGINAL_MATRIX_PROJECTION.json'))
c.write_json(P/'FINAL_SCIENTIFIC_RECEIPT.json',report)
lines=['# Lane E2：外部空间恢复后正式主配对终验','', '原174独立资源准入PASS后，复用原唯一控制器，依次完成CFD、DWT、SAD；三对六端全部独立接受，连同原Conv共四对CURRENT_ACCEPTED。每对已分别推送并通过中央inbox/events交付D，包含精确身份、周期、机制计数、原生退出证据及结果位置。','', '| 新配对 | S cycles | F cycles | S/F | 完整指令数/端 |','|---|---:|---:|---:|---:|']
for work in ['cfd_097k','dwt2d','sad']:
    pair=accepted['V2_MAIN_'+work+'_S_F_MAIN61'];r=json.loads(Path(pair['endpoints']['left']['path']).read_text())
    lines.append(f"| {work} | {pair['cycles_left']} | {pair['cycles_right']} | {pair['ratio_left_over_right']:.9f} | {r['summary']['instructions']} |")
lines += ['', '六端均真实exit0/wait status0，PID/start_ticks/boot身份与持久化原生回执闭合，全指令、64slice、硬件drain、requester/response/payload/WB等科学终验PASS。main61、原source/config/input/资格及构建身份保持，未重复17项原生测试。','',f"原T0={s['t0_unix']}；累计20/40，剩20；main已用12/32、contingency已用8/8。新结果累计{usage['new_bytes']:,} B，旧加新{usage['total_bytes']:,} B，本轮实际增长{growth:,} B。外部V3释放8,968,978,432 B未被当作结果生成量抵扣。",'',f"终验资源快照workspace可用{resources['disk_free_bytes']:,} B、Share可用{resources['share_disk_free_bytes']:,} B。原控制器STOPPED，无活动run/lease，无后台等待器。",'', 'FWT两端INCOMPLETE、Vector S COMPLETE_VALID、Vector F RESOURCE_LIMIT/exit-15、全部旧失败/撤回/HOLD及前14次保留体积/收据身份不变；没有重试或退回启动计数。','', '下一批边界：本轮具备资格且从未启动的主S/F队列已全部处理。剩余原32矩阵为Btree S/F（HOLD）及18个尚无当前producer/profile独立资格的消融/诊断条件。保留余20次；未采用新的预算重分配，旧FWT重跑建议仍仅是建议，Vector F也不自动重试。SGEMM继续仅独立探索候选，不能替换正式端点；C额外fixture不升级。逐条件记录见REMAINING_ORIGINAL_MATRIX_PROJECTION.json。']
(P/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(status=report['status'],actual_starts=20,remaining=20,usage=usage,growth=growth,resources=resources,unstarted_original_conditions=20,projection_counts=dict(collections.Counter(r['next_admission'] for r in rows)))))

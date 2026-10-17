"""Terminal-only six-arm comparison of two fixed holdouts; no selection or launches."""
from common import *
from typed_terminal_metrics import summarize
import shutil


def main():
    terminal=json.loads((ROOT/'AUTHORITY_TERMINAL.json').read_text())
    assert terminal['status']=='NATURAL_FOREGROUND_AUTHORITY_END' and not terminal['final']['active']
    authority=json.loads((ROOT/'AUTHORITY_ACTIVE.json').read_text());owner=proc(authority['pid'])
    assert not owner or owner['state']=='Z' or owner['start_ticks']!=authority['start_ticks']
    source_check()
    controls=json.loads((PACK/'ACCEPTED_CONTROLS.json').read_text())
    plan=list(csv.DictReader((PACK/'PRE_REGISTRATION.tsv').open(),delimiter='\t'))
    assert len(plan)==2
    sys=__import__('sys');sys.path.insert(0,str(PACK/'inputs'))
    import mechanism_consumer_cpu_174_v1 as lane_m
    matrix=[];mechanisms=[];evidence={};audit=[];raw=[];members={}
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text())
    prereg=json.loads((ROOT/'PRE_REG_FETCH_BACK.json').read_text())
    for point in plan:
        workload=point['workload'];oo=controls[workload+'_OO128'];cp=controls[workload+'_CPLUS']
        for arm,control in [('ORIGINAL_OO128',oo),('ORIGINAL_CPLUS',cp),('FIXED_T1C',None)]:
            uid=control['uuid'] if control else point['attempt_uuid']
            run=Path(control['run_dir']) if control else ROOT/'attempts'/(point['label']+'_'+uid)
            spec=control['spec'] if control else json.loads(Path(point['spec_path']).read_text())
            receipt=ROOT/(uid+'.strict.json')
            result=json.loads(receipt.read_text()) if not control and receipt.exists() else None
            accepted=bool(control) or bool(result and result['status']=='PASS_STRICT_HOLDOUT_SCOPE')
            status='ACCEPTED_ORIGINAL_CONTROL' if control else result['status'] if result else terminal['final']['terminal'].get(point['label'],'NOT_LAUNCHED_'+str(terminal['final']['halted'] or 'PENDING'))
            cycles=int(control['cycles']) if control else int(result['base']['cycles']) if accepted else None
            instructions=control['instructions'] if control else result['base']['instructions'] if accepted else ''
            if control:
                assert sha(run/'simulator.stdout')==control['stdout_sha256']
                assert sha(run/'RUN_START.json')==control['start_sha256']
                assert sha(run/'RUN_TERMINAL.json')==control['terminal_sha256']
                assert json.loads((run/'RUN_START.json').read_text())['spec']==spec
            elif result:
                (PACK/'strict').mkdir(exist_ok=True);shutil.copyfile(receipt,PACK/'strict'/receipt.name)
                if accepted:
                    assert all(v is True for v in result['checks'].values())
                    assert len(result['ordered_kernel_checks'])==len(ordered[workload])
                    assert all(v is True for row in result['ordered_kernel_checks'] for k,v in row.items() if k!='ordinal')
            if (run/'RUN_START.json').exists():
                start=json.loads((run/'RUN_START.json').read_text());end=json.loads((run/'RUN_TERMINAL.json').read_text())
                if not control:
                    assert start['spec']==spec and start['attempt_uuid']==uid
                    assert datetime.fromisoformat(prereg['utc'])<datetime.fromisoformat(start['launch_utc'])
                    assert sha(run/'immutable_runner.py')==start['runner_sha256']
                    for filename in ['simulator.stdout','simulator.stderr','resource.time']:
                        key={'simulator.stdout':'stdout_sha256','simulator.stderr':'stderr_sha256','resource.time':'resource_sha256'}[filename]
                        assert sha(run/filename)==end[key]
                    if accepted:assert end['exit_status']==0 and end['termination_reason']=='NATURAL_PROCESS_RETURN'
                    dest=PACK/'run_receipts'/uid;dest.mkdir(parents=True,exist_ok=True)
                    for filename in ['RUN_START.json','RUN_TERMINAL.json','PID.json','VALIDATION.json']:
                        if (run/filename).exists():shutil.copyfile(run/filename,dest/filename)
                    for file in sorted(run.rglob('*')):
                        if file.is_file():raw.append(dict(attempt_uuid=uid,path=str(file),bytes=file.stat().st_size,sha256=sha(file),symlink_target=os.readlink(file) if file.is_symlink() else 'NOT_A_SYMLINK'))
            if accepted:
                assert sha(spec['trace_list'])==spec['trace_list_sha256']
                for member in spec['members']:
                    assert member['path'] not in members or members[member['path']]==member
                    members[member['path']]=member
                for index,config in enumerate(spec['configs']):
                    assert sha(config['path'])==config['sha256']
                    if not control:assert sha(run/('config-'+str(index)+'.config'))==config['sha256']
                if not control:
                    actual=echo_options((run/'simulator.stdout').read_text());assert actual==spec['expected_option_echo']
                    differences={key for key in set(actual)|set(oo['echo_options']) if actual.get(key)!=oo['echo_options'].get(key)}
                    assert differences=={'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'}
                    assert sha(spec['runtime'])==BINARY_SHA
                mode='conventional' if arm=='ORIGINAL_CPLUS' else 'oo'
                row=summarize(arm,workload,mode,run,status,uid)
                if mode=='oo':assert row['accepted_reference_balance'] is True
                if arm=='FIXED_T1C':
                    old=next(m for m in mechanisms if m['workload']==workload and m['point']=='ORIGINAL_OO128')
                    for key in ['completion_dependency_count','fully_ready_cacheable_retired','collected_sectors']:assert row[key]==old[key]
                keys=['L2_read_sectors','L2_read_hits','L2_read_pending_hits','L2_read_misses','L2_read_sector_misses','L2_read_reservation_retries','L2_read_requested_payload_bytes','DRAM_n_rd','DRAM_n_rd_L2_A','DRAM_n_write','DRAM_n_wr_bk','DRAM_atom_bytes','DRAM_read_payload_bytes','DRAM_write_payload_bytes']
                config=spec['expected_option_echo'] if not control else control['echo_options']
                try:
                    parsed,proof=lane_m.extract(run,workload,'C+' if mode=='conventional' else 'OO128',uid,cycles,{},config)
                    row.update({key:parsed[key] for key in keys});row['L2_DRAM_comparability']='PASS_SAME_PATH_TYPED_DEFINITIONS'
                    evidence[uid]=proof
                except ValueError as exc:
                    row.update({key:'UNCOMPARABLE' for key in keys});row['L2_DRAM_comparability']='UNCOMPARABLE: '+str(exc)
                    evidence[uid]=dict(status='UNCOMPARABLE',reason=str(exc))
                row={k:('UNAVAILABLE' if v is None else v) for k,v in row.items()}
                mechanisms.append(row)
            matrix.append(dict(workload=workload,arm=arm,attempt_uuid=uid,status=status,
                cycles=cycles if accepted else '',active_instructions=instructions,
                accepted_original_oo_cycles=oo['cycles'],accepted_original_cplus_cycles=cp['cycles'],
                R_OO=oo['cycles']/cycles if accepted else '',R_CPLUS=cp['cycles']/cycles if accepted else '',
                cycles_change_vs_OO_pct=(cycles/oo['cycles']-1)*100 if accepted else '',
                cycles_change_vs_CPLUS_pct=(cycles/cp['cycles']-1)*100 if accepted else '',
                stdout_sha256=sha(run/'simulator.stdout') if (run/'simulator.stdout').exists() else 'NOT_LAUNCHED',
                strict_sha256=sha(receipt) if result else 'ORIGINAL_CONTROL' if control else 'UNAVAILABLE',raw_dir=str(run)))
            if not control:audit.append(dict(attempt_uuid=uid,workload=workload,status=status,formal_ratios_available=accepted,ordered_kernels=len(result['ordered_kernel_checks']) if result and accepted else 0))
    assert len(matrix)==6 and len(audit)==2 and len(members)==12
    for path,member in members.items():assert Path(path).stat().st_size==member['bytes'] and sha(path)==member['sha256']
    starts=list((ROOT/'attempts').glob('*/RUN_START.json'));assert len(starts)<=2
    allowed={point['attempt_uuid'] for point in plan}
    assert all(json.loads(f.read_text())['attempt_uuid'] in allowed for f in starts)
    table(PACK/'FULL_MATRIX.tsv',matrix)
    table(PACK/'TERMINAL_MECHANISM_COMPARISON.tsv',mechanisms)
    if raw:table(PACK/'RAW_FILES_SHA256.tsv',raw)
    write(PACK/'METRIC_COMPARABILITY_EVIDENCE.json',evidence)
    write(PACK/'STRICT_AUDIT.json',dict(utc=now(),status='COMPLETE_FIXED_TWO_HOLDOUTS_OR_LEGAL_STOP',
        prereg_commit=prereg['commit'],registered=2,actual_new_starts=len(starts),strict_pass=sum(p['formal_ratios_available'] for p in audit),
        source_input_identity_sha256=sha(PACK/'SOURCE_INPUT_IDENTITY.json'),member_hashes_verified=12,points=audit,
        no_performance_selection=True,no_new_candidates=True,no_new_mechanism=True,scientific_scope='SCIENTIFIC_SCOPE.md'))
    for name in ['PRE_REG_FETCH_BACK.json','EXECUTION_GATE.json','AUTHORITY_ACTIVE.json','AUTHORITY_TERMINAL.json','STATUS.json']:
        if (ROOT/name).exists():shutil.copyfile(ROOT/name,PACK/name)
    lines=['# Fixed T1-C independent holdout report','',
        '仅固定64sets×8ways OO128；两个原完整holdout输入，各一次启动。没有重新选型或新增硬性能门槛。','',
        '| 输入 | 新点状态 | 新周期 | R_OO | R_CPLUS | 对原OO周期变化 | 对原C+周期变化 |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for row in matrix:
        if row['arm']!='FIXED_T1C':continue
        if row['R_OO']:
            lines.append(f"| {row['workload']} | {row['status']} | {row['cycles']:,} | {row['R_OO']:.6f}× | {row['R_CPLUS']:.6f}× | {row['cycles_change_vs_OO_pct']:+.3f}% | {row['cycles_change_vs_CPLUS_pct']:+.3f}% |")
        else:lines.append(f"| {row['workload']} | {row['status']} | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |")
    lines+=['','完整六臂、失败/未启动项见FULL_MATRIX.tsv；新点strict/与run_receipts/逐UUID保存；机制与L2/DRAM单位和可比性见TERMINAL_MECHANISM_COMPARISON.tsv、METRIC_COMPARABILITY_EVIDENCE.json。资源另由summarize_terminal_resources.py生成EXECUTION_RESOURCES.tsv与RESOURCE_EXECUTION_SUMMARY.json。','',
        '原GEMM/Gaussian A/B/C只作发现证据，不参与新选择；本Goal不授予论文主配置替换权，不改原44行、GM12或v0.11-VI主图。所有负收益如实保留。独立sector返回、内部MSHR、数值load和PPA仍UNAVAILABLE；credit不转换DRAM字节，条件均值差不视为可加整机周期贡献。','',
        'A/M/T、原source/binary/parser/runtime和旧raw保持只读；只有Tag sets32→64、ways4→8有效变化。无T2、新observer、物理池调参、新候选或第三输入。两个点或合法STOP到此结束交审。','']
    with (PACK/'LATEST_REPORT.md').open('x') as f:f.write('\n'.join(lines))
    print('Terminal holdout matrix:',len(matrix),'rows;',sum(p['formal_ratios_available'] for p in audit),'strict new points')


if __name__=='__main__':main()

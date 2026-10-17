"""Close terminal identities, all registered outcomes and the fixed score; no runs."""
from decimal import Decimal, localcontext
from common import *


def main():
    prereg = json.loads((PACK/'PRE_REG_FETCH_BACK.json').read_text())
    assert prereg['status']=='PASS_FETCH_BACK_BEFORE_ANY_NEW_PERFORMANCE'
    with (PACK/'PRE_REGISTRATION.tsv').open() as stream:
        plan=list(csv.DictReader(stream,delimiter='\t'))
    assert len(plan)==7 and len({p['attempt_uuid'] for p in plan})==7
    assert sha(PACK/'PRE_REGISTRATION.tsv')==prereg['plan_sha256']
    for row in csv.DictReader((PACK/'PREREG_FILES_SHA256.tsv').open(),delimiter='\t'):
        path=PACK/row['path']
        assert sha(path)==row['sha256']
        original=subprocess.check_output(['git','-C',str(FW),'show',
            prereg['commit']+':'+str(path.relative_to(FW))])
        assert hashlib.sha256(original).hexdigest()==row['sha256']
    source_check()
    assert not git(CORE,'status','--porcelain')
    assert not git(MAIN,'status','--porcelain')
    assert subprocess.run(['git','-C',str(FW),'merge-base','--is-ancestor',AUTH_HEAD,'HEAD']).returncode==0
    status=json.loads((ROOT/'STATUS.json').read_text())
    terminal=json.loads((ROOT/'AUTHORITY_TERMINAL.json').read_text())
    assert terminal['final']==status and terminal['status']=='NATURAL_FOREGROUND_AUTHORITY_END'
    assert not status['active'] and not status['not_launched'] and status['halted'] is None
    assert len(status['terminal'])==7
    for name in ['AUTHORITY_ACTIVE_V2.json','BACKGROUND_MONITOR_ACTIVE_V1.json']:
        a=json.loads((ROOT/name).read_text()); p=proc(a['pid'])
        assert not p or p['state']=='Z' or p['start_ticks']!=a['start_ticks']
    controls=json.loads((PACK/'ACCEPTED_CONTROLS.json').read_text())
    old_rows=[]
    for name,c in controls.items():
        run=Path(c['run_dir'])
        for filename,key in [('RUN_START.json','start_sha256'),('RUN_TERMINAL.json','terminal_sha256'),('simulator.stdout','stdout_sha256')]:
            assert sha(run/filename)==c[key]
            old_rows.append(dict(control=name,path=str(run/filename),sha256=c[key]))
        assert json.loads((run/'RUN_START.json').read_text())['spec']==c['spec']
        for config in c['spec']['configs']:assert sha(config['path'])==config['sha256']
        assert sha(c['spec']['runtime'])==c['spec']['runtime_sha256']
    preservation=json.loads((ROOT/'PRESERVATION_CHECK_ACTIVE.json').read_text())
    for row in preservation['files']:assert sha(row['path'])==row['expected_sha256']
    snapshot=resource_snapshot()
    old_locks={Path(p['path']).name:p for p in snapshot['old_locks']}
    for name,inode in preservation['old_lock_inodes'].items():
        assert old_locks[name]['inode']==inode and not old_locks[name]['owners']
    lock_inode=(ROOT/'AUTHORITY.lock').stat().st_ino
    assert not any(line.split()[5].split(':')[-1]==str(lock_inode)
                   for line in Path('/proc/locks').read_text().splitlines())
    m=json.loads((PACK/'M_CONSUMPTION.json').read_text())
    assert m['status']=='PASS_INPUT_AND_HYPOTHESIS_GATE'
    for row in m['files']:
        data=subprocess.check_output(['git','-C',str(FW),'show',m['verified_remote_head']+':'+row['path']])
        assert hashlib.sha256(data).hexdigest()==row['sha256']
    matrix=list(csv.DictReader((PACK/'FULL_MATRIX.tsv').open(),delimiter='\t'))
    assert len(matrix)==7 and {r['attempt_uuid'] for r in matrix}=={r['attempt_uuid'] for r in plan}
    matrix={r['attempt_uuid']:r for r in matrix}
    actual_starts={str(p.parent) for p in (ROOT/'attempts').rglob('RUN_START.json')}
    expected_runs={str(ROOT/'attempts'/(p['label']+'_'+p['attempt_uuid'])) for p in plan}
    assert actual_starts==expected_runs
    unique_members={}; events=[]; point_checks=[]; raw=[]
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text())
    repair=json.loads((ROOT/'WRAPPER_REPAIR_FETCH_BACK.json').read_text())
    for point in plan:
        uid=point['attempt_uuid']; run=ROOT/'attempts'/(point['label']+'_'+uid)
        spec=json.loads(Path(point['spec_path']).read_text())
        assert sha(point['spec_path'])==point['spec_sha256']
        assert json.loads((run/'SPEC.json').read_text())==spec
        start=json.loads((run/'RUN_START.json').read_text())
        end=json.loads((run/'RUN_TERMINAL.json').read_text())
        strict=json.loads((ROOT/(uid+'.strict.json')).read_text())
        assert start['attempt_uuid']==end['attempt_uuid']==strict['attempt_uuid']==uid
        assert start['spec']==spec and end['exit_status']==0
        assert end['termination_reason']=='NATURAL_PROCESS_RETURN'
        launched=datetime.fromisoformat(start['launch_utc']); ended=datetime.fromisoformat(end['terminal_utc'])
        assert datetime.fromisoformat(prereg['utc'])<launched<ended
        if point['label'] not in ['DTC_TAG_PILOT_V1_T0_GEMM','DTC_TAG_PILOT_V1_T1_A_GEMM']:
            assert datetime.fromisoformat(repair['utc'])<launched
        events += [(launched,1),(ended,-1)]
        assert sha(run/'immutable_runner.py')==start['runner_sha256']
        assert sha(run/'simulator.stdout')==end['stdout_sha256']
        assert sha(run/'simulator.stderr')==end['stderr_sha256']
        assert sha(run/'resource.time')==end['resource_sha256']
        assert sha(run/'RUN_TERMINAL.json')==strict['base']['terminal_sha256']
        assert strict['status']==status['terminal'][point['label']]=='PASS_STRICT_EXPLORATORY_SCOPE'
        assert all(value is True for value in strict['checks'].values())
        kernels=strict['ordered_kernel_checks']
        assert len(kernels)==len(ordered[point['workload']])
        assert [k['ordinal'] for k in kernels]==list(range(1,len(kernels)+1))
        assert all(v is True for k in kernels for field,v in k.items() if field!='ordinal')
        assert int(strict['base']['instructions'])==spec['expected_instructions']
        assert matrix[uid]['cycles']==strict['base']['cycles']
        assert matrix[uid]['strict_sha256']==sha(ROOT/(uid+'.strict.json'))
        assert sha(PACK/'strict'/(uid+'.strict.json'))==matrix[uid]['strict_sha256']
        for index,config in enumerate(spec['configs']):
            assert sha(config['path'])==sha(run/('config-'+str(index)+'.config'))==config['sha256']
        text=(run/'simulator.stdout').read_text()
        actual=echo_options(text)
        assert actual==spec['expected_option_echo']
        parent=controls['GEMM_IO256' if point['candidate']=='T0' else point['workload']+'_OO128']
        differences={key for key in set(actual)|set(parent['echo_options'])
                     if actual.get(key)!=parent['echo_options'].get(key)}
        allowed=({'-gpgpu_dtc_l1_io_pib_entries'} if point['candidate']=='T0' else
                 {'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'})
        assert differences and differences<=allowed,(point['label'],differences)
        binary=Path(start['command'][start['command'].index('-trace')-1])
        assert sha(binary)==BINARY_SHA
        assert sha(spec['trace_list'])==spec['trace_list_sha256']
        for member in spec['members']:
            if member['path'] in unique_members:assert unique_members[member['path']]==member
            unique_members[member['path']]=member
        pid=json.loads((run/'PID.json').read_text())
        for pid_key,ticks_key in [('runner_pid','runner_start_ticks'),('process_pid','process_start_ticks')]:
            p=proc(pid[pid_key]);assert not p or p['state']=='Z' or p['start_ticks']!=pid[ticks_key]
        point_checks.append(dict(attempt_uuid=uid,label=point['label'],status='PASS',
            ordered_kernels=len(kernels),strict_checks=len(strict['checks']),
            effective_option_differences=sorted(differences),launch_utc=start['launch_utc'],
            terminal_utc=end['terminal_utc'],terminal_sha256=sha(run/'RUN_TERMINAL.json')))
        for file in sorted(run.rglob('*')):
            if file.is_file():raw.append(dict(attempt_uuid=uid,path=str(file),bytes=file.stat().st_size,
                sha256=sha(file),symlink_target=os.readlink(file) if file.is_symlink() else ''))
    assert len(unique_members)==511
    for path,member in unique_members.items():
        assert Path(path).stat().st_size==member['bytes'] and sha(path)==member['sha256']
    live=peak=0
    for _,delta in sorted(events):live+=delta;peak=max(peak,live);assert 0<=live<=2
    assert live==0
    with localcontext() as context:
        context.prec=40
        independently=[]
        scores=list(csv.DictReader((PACK/'DISCOVERY_SCORE.tsv').open(),delimiter='\t'))
        for score in scores:
            candidate=score['candidate']; ratios=[]
            for workload in ['GEMM','Gaussian']:
                row=next(v for v in matrix.values() if v['candidate']==candidate and v['workload']==workload)
                ratio=Decimal(controls[workload+'_OO128']['cycles'])/Decimal(row['cycles'])
                assert abs(float(ratio)-float(score['R_'+workload]))<1e-14
                ratios.append(ratio)
            gm=(ratios[0]*ratios[1]).sqrt();minimum=min(ratios)
            eligible=minimum>=Decimal('.98') and gm>=Decimal('1.02')
            assert (score['eligible']=='True')==eligible
            assert abs(float(gm)-float(score['R_g']))<1e-14
            independently.append(dict(candidate=candidate,R_min=str(minimum),R_g=str(gm),
                eligible=eligible,mappings=int(score['mappings']),ways=int(score['ways'])))
        eligible=[p for p in independently if p['eligible']]
        best=max(Decimal(p['R_g']) for p in eligible)
        tied=[p for p in eligible if (best-Decimal(p['R_g']))/best<Decimal('.005')]
        selected=min(tied,key=lambda p:(p['mappings'],p['ways']))['candidate']
        assert [s['candidate'] for s in scores if s['selected']=='True']==[selected]
    summary=json.loads((PACK/'EXPLORATION_SUMMARY.json').read_text())
    assert summary['selected']==selected and summary['strict_pass']==7
    audit=dict(utc=now(),status='PASS_TERMINAL_IDENTITY_AND_FIXED_SCORE_AUDIT',
        prereg_commit=prereg['commit'],authorization_commit=AUTH_HEAD,
        registered=7,unique_actual_starts=7,strict_pass=7,
        unique_selected_input_members_rehashed=511,reused_body_proof_no_629_rescan=True,
        ordered_kernel_checks=sum(p['ordered_kernels'] for p in point_checks),
        peak_execution_interval_concurrency=peak,all_registered_runs_terminal=True,
        no_live_own_authority_or_observer=True,authority_lock_released=True,
        original44_and_hold_tokens_unchanged=True,old_lock_inodes_and_nonownership_preserved=True,
        frozen_core_and_old_framework_heads_clean=True,source_and_original_controls_rehashed=True,
        preregistered_files_byte_identical_to_performance_preceding_commit=True,
        independent_decimal_score=independently,selected=selected,points=point_checks,
        scope='SAME TWO DISCOVERY INPUTS; NO HOLDOUT/T2/NEW CORE OR MECHANISM; NOT PPA/GM12/NATIVE PROOF')
    table(PACK/'FINAL_RAW_FILES_SHA256.tsv',raw)
    table(PACK/'FINAL_CONTROL_IDENTITIES.tsv',old_rows)
    write(PACK/'FINAL_IDENTITY_AUDIT.json',audit)
    print(json.dumps({k:audit[k] for k in ['status','strict_pass','ordered_kernel_checks','unique_selected_input_members_rehashed','selected']}))


if __name__=='__main__':main()

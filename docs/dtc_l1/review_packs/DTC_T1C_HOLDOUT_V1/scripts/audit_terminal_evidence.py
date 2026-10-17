"""Independent terminal closure of the preregistered two-point contract; no runs."""
from decimal import Decimal, localcontext
from common import *
from review_external_sources import main as review_foreign


def main():
    terminal=json.loads((ROOT/'AUTHORITY_TERMINAL.json').read_text())
    assert terminal['status']=='NATURAL_FOREGROUND_AUTHORITY_END'
    status=json.loads((ROOT/'STATUS.json').read_text())
    assert terminal['final']==status and not status['active']
    owner=json.loads((ROOT/'AUTHORITY_ACTIVE.json').read_text());current=proc(owner['pid'])
    assert not current or current['state']=='Z' or current['start_ticks']!=owner['start_ticks']
    source_check()
    assert git(Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64'),'rev-parse','HEAD')==BUILD_FW
    assert git(Path('/workspace/worktrees/gpgpu-sim-iscas2027-sg1-canonical'),'rev-parse','HEAD')=='6582b9d171330d88b17e8d5294c97704229e3823'
    assert not git(CORE,'status','--porcelain') and not git(MAIN,'status','--porcelain')
    prereg=json.loads((ROOT/'PRE_REG_FETCH_BACK.json').read_text())
    assert prereg['status']=='PASS_FETCH_BACK_BEFORE_ANY_NEW_HOLDOUT_PERFORMANCE'
    assert prereg['plan_sha256']==sha(PACK/'PRE_REGISTRATION.tsv')
    frozen=list(csv.DictReader((PACK/'PREREG_FILES_SHA256.tsv').open(),delimiter='\t'))
    assert len(frozen)==63
    for row in frozen:
        path=PACK/row['path'];assert sha(path)==row['sha256']
        blob=subprocess.check_output(['git','-C',str(FW),'show',prereg['commit']+':'+str(path.relative_to(FW))])
        assert hashlib.sha256(blob).hexdigest()==row['sha256']
    prior=json.loads((PACK/'PRESERVATION_BASELINE.json').read_text())
    for row in prior['files']:assert sha(row['path'])==row['expected_sha256']
    lines=Path('/proc/locks').read_text().splitlines();lock_rows=[]
    for name,inode in prior['old_lock_inodes'].items():
        path=Path('/workspace/dtc-service-closure-174-v1/r2-attempts')/name
        assert path.stat().st_ino==inode
        owners=[line for line in lines if line.split()[5].split(':')[-1]==str(inode)]
        assert not owners
        lock_rows.append(dict(path=str(path),inode=inode,owners=owners))
    own_inode=(ROOT/'AUTHORITY.lock').stat().st_ino
    assert not any(line.split()[5].split(':')[-1]==str(own_inode) for line in lines)
    controls=json.loads((PACK/'ACCEPTED_CONTROLS.json').read_text());control_files=[]
    original_ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text())
    for key,control in controls.items():
        run=Path(control['run_dir']);spec=control['spec']
        for filename,digest in [('simulator.stdout',control['stdout_sha256']),('RUN_START.json',control['start_sha256']),('RUN_TERMINAL.json',control['terminal_sha256'])]:
            assert sha(run/filename)==digest
            control_files.append(dict(control=key,path=str(run/filename),sha256=digest))
        assert json.loads((run/'RUN_START.json').read_text())['spec']==spec
        text=(run/'simulator.stdout').read_text();proofs=original_ordered[spec['workload']]
        marks=list(re.finditer(r'^kernel_name\s*=\s*(\S+)\s*$',text,re.M))
        assert [m.group(1) for m in marks]==[p['kernel'] for p in proofs]
        instructions=ctas=0
        for i,(mark,proof) in enumerate(zip(marks,proofs)):
            block=text[mark.start():marks[i+1].start() if i+1<len(marks) else len(text)]
            values={k:int(v) for k,v in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',block,re.M)}
            instructions+=proof['active_instructions'];ctas+=proof['complete_ctas']
            assert values['gpu_sim_insn']==proof['active_instructions']
            assert values['gpu_tot_sim_insn']==instructions and values['gpu_tot_issued_cta']==ctas
        assert values['gpu_tot_sim_cycle']==control['cycles'] and instructions==control['instructions']
        assert sha(spec['runtime'])==spec['runtime_sha256']
        for config in spec['configs']:assert sha(config['path'])==config['sha256']
    plan=list(csv.DictReader((PACK/'PRE_REGISTRATION.tsv').open(),delimiter='\t'))
    assert len(plan)==2 and [p['workload'] for p in plan]==['DWT2D','BICG']
    assert len({p['attempt_uuid'] for p in plan})==2
    starts=list((ROOT/'attempts').rglob('RUN_START.json'))
    assert len(starts)<=2
    assert all(json.loads(p.read_text())['attempt_uuid'] in {p['attempt_uuid'] for p in plan} for p in starts)
    matrix=list(csv.DictReader((PACK/'FULL_MATRIX.tsv').open(),delimiter='\t'))
    assert len(matrix)==6
    assert {(r['workload'],r['arm']) for r in matrix}=={(w,a) for w in ['DWT2D','BICG'] for a in ['ORIGINAL_OO128','ORIGINAL_CPLUS','FIXED_T1C']}
    intervals=[];point_proof=[];members={};raw_files=list(csv.DictReader((PACK/'RAW_FILES_SHA256.tsv').open(),delimiter='\t'))
    for row in raw_files:assert Path(row['path']).stat().st_size==int(row['bytes']) and sha(row['path'])==row['sha256']
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text())
    for point in plan:
        uid=point['attempt_uuid'];run=ROOT/'attempts'/(point['label']+'_'+uid)
        spec=json.loads(Path(point['spec_path']).read_text());assert sha(point['spec_path'])==point['spec_sha256']
        row=next(r for r in matrix if r['workload']==point['workload'] and r['arm']=='FIXED_T1C')
        assert row['attempt_uuid']==uid
        if not (run/'RUN_START.json').exists():
            assert status['halted'] and not row['R_OO'] and not row['R_CPLUS'];continue
        start=json.loads((run/'RUN_START.json').read_text());end=json.loads((run/'RUN_TERMINAL.json').read_text())
        assert start['spec']==spec==json.loads((run/'SPEC.json').read_text())
        assert start['attempt_uuid']==end['attempt_uuid']==uid
        begin=datetime.fromisoformat(start['launch_utc']);finish=datetime.fromisoformat(end['terminal_utc'])
        assert datetime.fromisoformat(prereg['utc'])<begin<finish
        intervals.extend([(begin,1),(finish,-1)])
        assert sha(run/'immutable_runner.py')==start['runner_sha256']
        for filename,key in [('simulator.stdout','stdout_sha256'),('simulator.stderr','stderr_sha256'),('resource.time','resource_sha256')]:assert sha(run/filename)==end[key]
        binary=Path(start['command'][start['command'].index('-trace')-1]);assert sha(binary)==BINARY_SHA
        for index,config in enumerate(spec['configs']):assert sha(config['path'])==sha(run/('config-'+str(index)+'.config'))==config['sha256']
        assert sha(spec['trace_list'])==spec['trace_list_sha256']
        for member in spec['members']:
            assert member['path'] not in members or members[member['path']]==member
            members[member['path']]=member
        strictfile=ROOT/(uid+'.strict.json');strict=json.loads(strictfile.read_text()) if strictfile.exists() else None
        if strict and strict['status']=='PASS_STRICT_HOLDOUT_SCOPE':
            assert end['exit_status']==0 and end['termination_reason']=='NATURAL_PROCESS_RETURN'
            assert all(value is True for value in strict['checks'].values())
            kernels=strict['ordered_kernel_checks'];assert len(kernels)==len(ordered[point['workload']])
            assert [k['ordinal'] for k in kernels]==list(range(1,len(kernels)+1))
            assert all(v is True for k in kernels for key,v in k.items() if key!='ordinal')
            assert sha(PACK/'strict'/strictfile.name)==sha(strictfile)==row['strict_sha256']
            assert sha(run/'RUN_TERMINAL.json')==strict['base']['terminal_sha256']
            assert row['cycles']==strict['base']['cycles'] and int(row['active_instructions'])==spec['expected_instructions']
            actual=echo_options((run/'simulator.stdout').read_text());assert actual==spec['expected_option_echo']
            parent=controls[point['workload']+'_OO128']['echo_options']
            assert {k for k in actual.keys()|parent.keys() if actual.get(k)!=parent.get(k)}=={'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'}
        else:assert not row['R_OO'] and not row['R_CPLUS']
        point_proof.append(dict(attempt_uuid=uid,status=row['status'],launch_utc=start['launch_utc'],terminal_utc=end['terminal_utc'],timeout_seconds=spec['wall_timeout_seconds']))
        pids=json.loads((run/'PID.json').read_text())
        for key,ticks in [('runner_pid','runner_start_ticks'),('process_pid','process_start_ticks')]:
            current=proc(pids[key]);assert not current or current['state']=='Z' or current['start_ticks']!=pids[ticks]
    for path,member in members.items():assert Path(path).stat().st_size==member['bytes'] and sha(path)==member['sha256']
    live=peak=0
    for _,delta in sorted(intervals):live+=delta;peak=max(peak,live);assert 0<=live<=1
    assert live==0
    if len(starts)==2:
        second=ROOT/'attempts'/(plan[1]['label']+'_'+plan[1]['attempt_uuid'])
        first=json.loads((ROOT/(plan[0]['attempt_uuid']+'.strict.json')).read_text())
        assert first['status']=='PASS_STRICT_HOLDOUT_SCOPE'
        gate=json.loads((ROOT/'SERIAL_HOLDOUT_GATE_RECEIPT.json').read_text())
        assert gate['dwt_strict_sha256']==sha(ROOT/(plan[0]['attempt_uuid']+'.strict.json'))
        assert gate['bicg_start_utc']==json.loads((second/'RUN_START.json').read_text())['launch_utc']
    with localcontext() as context:
        context.prec=40
        for row in matrix:
            if not row['cycles']:continue
            cycles=Decimal(row['cycles'])
            for suffix,key in [('OO','accepted_original_oo_cycles'),('CPLUS','accepted_original_cplus_cycles')]:
                old=Decimal(row[key]);assert old==Decimal(controls[row['workload']+('_OO128' if suffix=='OO' else '_CPLUS')]['cycles'])
                assert abs(Decimal(row['R_'+suffix])-old/cycles)<Decimal('1e-12')
                assert abs(Decimal(row['cycles_change_vs_'+suffix+'_pct'])-(cycles/old-1)*100)<Decimal('1e-10')
    review_foreign()
    foreign=json.loads((ROOT/'EXTERNAL_RESOURCE_IDENTITIES.json').read_text());assert not foreign['unresolved']
    report=dict(utc=now(),status='PASS_TERMINAL_CONTRACT_AND_IDENTITY_AUDIT',prereg_commit=prereg['commit'],
        preregistered_files_unchanged=63,registered=2,actual_starts=len(starts),maximum_new_DTC_concurrency=peak,
        points=point_proof,selected_input_members_rehashed=len(members),original_control_files_rehashed=control_files,
        old_44_and_hold_tokens_unchanged=True,old_locks=lock_rows,own_authority_lock_released=True,
        Core_and_old_framework_clean=True,source_and_full_default_echo_closed=True,
        ratios_and_signed_percentages_independently_checked=True,no_new_performance_threshold=True,
        conservative_scope_hold_preserved=bool(status['halted']),foreign_identity_review_sha256=sha(ROOT/'EXTERNAL_RESOURCE_IDENTITIES.json'),
        scientific_scope='TWO FIXED HOLDOUTS ONLY; NO PROMOTION/GM12/T2/NEW MODEL; INCOMPLETE POINT HAS NO FORMAL RATIO')
    write(PACK/'FINAL_CONTRACT_AUDIT.json',report)
    print(report['status'],'actual starts',len(starts),'peak DTC',peak,'members',len(members))


if __name__=='__main__':main()

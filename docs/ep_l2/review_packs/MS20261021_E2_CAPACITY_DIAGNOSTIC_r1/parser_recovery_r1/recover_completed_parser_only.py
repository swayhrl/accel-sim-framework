"""Explicit decoder-only intake for already completed E application evidence.

DRAFT: no invocation during preparation. Never calls execute/reserve_application,
start_application/finish_application, native simulator, compiler or controller.
The old FAILED attempt/receipt/Q/parser/raw are immutable. New acceptance is a
separate pointer to a new child receipt after complete independent validation.
"""
from pathlib import Path
import argparse,copy,fcntl,hashlib,json,os,re,shutil,sys,time
P=Path(__file__).resolve().parent;PACK=P.parent;ROOT=PACK.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner,capacity_policy,durable_exit as d
INTAKE=P/'PARSER_RECOVERY_INTAKE.json'
GROWTH=64*2**20;MEMORY=8*c.GIB

def require(ok,message):
    if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve(strict=True)),sha256=c.digest(p))
def pinned(r):
    p=Path(r['path']).resolve(strict=True);require(c.digest(p)==r['sha256'],'pinned evidence changed: '+str(p));return p

def stable_q(q):
    out=copy.deepcopy(q)
    for key in ('terminal_parser','parser_seal','qualified_unix','scope_note','parser_only_revision'):out.pop(key,None)
    out['capacity_diagnostic'].pop('parser_seal',None)
    return out

def stable_spec(spec):
    return {k:v for k,v in spec.items() if k not in ('qualification_id','parser','input_audit')}

def stable_audit(audit):
    return {k:v for k,v in audit.items() if k not in ('qualification_sha256','parser')}

def historical(item):
    # Hold resolution and parser recovery history are separately accounted.
    return copy.deepcopy({k:item.get(k) for k in ('t0_unix','actual_starts','maximum_actual_starts','attempts',
      'accepted_pairs','full_system_matrix','reservations','final_source_identity','capacity_diagnostic_runtime')})

def safe_boundary(coord):
    snap=coord.snapshot();require(snap['controller']['state']=='STOPPED','original controller must naturally STOP')
    prior=snap['controller'].get('process')
    if prior:
        try:live=c.process_identity(prior['pid'])==prior
        except (FileNotFoundError,ProcessLookupError):live=False
        require(not live,'original controller process still exists; wait for full exit')
    data=read(c.SHARED/'RUN_REGISTRY.json')
    require(not any(a['state'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED') for a in snap['attempts']),
            'active or uncertain E application blocks parse-only recovery')
    require(not any(r.get('experiment_id')==c.CAMPAIGN and r['status'] in c.ACTIVE
                    for group in ('runs','resource_leases') for r in data[group].values()),
            'active campaign lease blocks safe recovery boundary')
    with (c.HANDOFF/'CONTROLLER.lock').open('rb') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_UN)
    return snap

def native_proof(attempt,old,origin):
    require(old['status']=='FAILED' and old['execution_stage']=='TERMINAL_VALIDATION' and
            old['exit_code']==0 and 'independent terminal parser failed' in old['detail'],
            'recovery limited to exact completed-native terminal-parser failure')
    require(attempt['state']=='FAILED' and attempt['actual_start'] is True,'original charged failed attempt required')
    native=read(origin/'NATIVE_EXIT.json');ready=read(origin/'NATIVE_EXECUTION_READY.json')
    require(c.digest(origin/'NATIVE_EXIT.json')==old['native_exit_receipt_sha256'] and
            native==old['native_exit_evidence'],'original native exit changed')
    require(native['exit_code']==native['wait_status']==0 and native['stop_reason'] is None and
            native['exited_normally'] is True and native['signaled'] is False and native['released_to_native'],
            'actual native must have an unguarded normal exit0/wait0')
    require(native['native_process']==attempt['process']==old['process']==ready['native_process'] and
            native['guardian_process']==attempt['exit_collector_process']==ready['guardian_process'],
            'original native/guardian PID/start_ticks/boot identity differs')
    require(native['binding']['attempt_id']==attempt['attempt_id'] and native['binding']['run_key']==attempt['run_key'] and
            native['binding']['identity']==attempt['identity']==old['identity'],
            'original native startup/exit scientific identity differs')
    require(ready['binding']==native['binding'] and ready['command']==native['command'],
            'native startup and exit bind different execution')
    require(c.digest(origin/'raw.log')==old['raw_log_sha256'],'completed original raw changed')
    require(Path(native['command'][0]).resolve()==origin/'accel-sim.out' and
            c.digest(origin/'accel-sim.out')==attempt['identity']['binary_sha256'],'original executed binary snapshot changed')
    for index,asset in enumerate(old['input_audit']['configs']):
        require(c.digest(origin/('config-'+str(index)+'.config'))==asset['sha256'],'original executed config snapshot changed')
    for asset in old['input_audit']['auxiliary_assets']:
        require(c.digest(origin/asset['name'])==asset['sha256'],'original executed auxiliary snapshot changed')
    return native

def parse_under_original_test_lease(coord,spec,recovery,raw):
    """Only the new Python decoder executes; exact original resource guards."""
    lease=coord.reserve_work('E','test',1,MEMORY,GROWTH,recovery,result_growth_bytes=GROWTH)
    recovery.mkdir();stage=recovery/'parser_validation';stage.mkdir();(stage/'tmp').mkdir();(stage/'cache').mkdir()
    c.write_json(recovery/'input_spec.json',spec);c.write_json(stage/'input_spec.json',spec)
    limits=capacity_policy.effective_limits(coord.snapshot())
    bounds={k:lease[k] for k in ('policy_id','disk_floor_bytes','monitor_reserve_bytes','monitor_interval_seconds','termination_grace_seconds')}
    bounds.update(memory_bytes=MEMORY,maximum_result_bytes=GROWTH,timeout_seconds=300,
       **{k:limits[k] for k in ('intake_deadline_unix','additional_results_max_bytes','old_plus_new_results_max_bytes')})
    env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',
       TMPDIR=str(stage/'tmp'),TMP=str(stage/'tmp'),TEMP=str(stage/'tmp'),XDG_CACHE_HOME=str(stage/'cache'))
    command=[sys.executable,spec['parser']['path'],'--raw',str(raw),'--out',str(recovery/'terminal_summary.json')]
    process=None;bound=False;unresolved=False;constructing=False
    try:
        with (stage/'parser.log').open('xb') as log:
            constructing=True
            process=d.NativeProcess(command,stage,log,env,bounds,dict(kind='PARSER_ONLY_RECOVERY_NO_APPLICATION',
                source_identity=spec['identity'],old_raw=ref(raw),new_qualification_id=spec['qualification_id']))
            constructing=False
            coord.bind_work_process(lease['lease_id'],'E',process.pid);bound=True;process.release()
            until=time.monotonic()+315
            while process.poll() is None:
                if d.STOP.is_set() or time.monotonic()>until or c.retained_tree_bytes(recovery)>=GROWTH:
                    os.kill(process.collector.pid,15)
                if time.monotonic()>until+15:raise d.ExitEvidenceMissing('decoder durable closure unavailable')
                time.sleep(.1)
            ev=process.exit_evidence();process.collector.wait(timeout=5)
        require(ev['exit_code']==ev['wait_status']==0 and ev['stop_reason'] is None,
                'new decoder failed; preserve original failure and this recovery evidence')
        return read(recovery/'terminal_summary.json'),ref(stage/'NATIVE_EXIT.json')
    finally:
        unresolved|=constructing
        if process is not None:
            if process.poll() is None:
                os.kill(process.collector.pid,15)
                try:process.wait(timeout=15)
                except Exception:unresolved=True
            try:unresolved|=process.poll() is None
            except Exception:unresolved=True
        if not unresolved:
            coord.release_work(lease['lease_id'],'E','Parser-only recovery decoder finished; zero application starts',no_child_started=not bound)


def recover(row,intake_sha,coord,proof):
    snap=safe_boundary(coord);history=historical(snap);prior_accepted=copy.deepcopy(snap['accepted_results'])
    attempt=next(a for a in snap['attempts'] if a['attempt_id']==row['attempt_id'])
    oldpath=pinned(row['original_receipt']);require(str(oldpath)==attempt['receipt_path'] and
        row['original_receipt']['sha256']==attempt['receipt_sha256'],'original failed receipt is not canonical')
    old=read(oldpath);origin=Path(attempt['result_directory']).resolve();require(oldpath.parent==origin,'original receipt directory changed')
    native=native_proof(attempt,old,origin)
    oldspec=read(origin/'input_spec.json');oldqid=oldspec['qualification_id'];require(oldqid==attempt['qualification_id']==old['qualification_id'],'original Q differs')
    qrow=snap['qualifications'][oldqid];pinned(qrow);oldq=qrow['qualification']
    newqp=pinned(row['new_qualification']);newq=read(newqp)
    require(stable_q(newq)==stable_q(oldq),'scientific/build/native/input/profile/gate qualification changed beyond decoder revision')
    require(newq['terminal_parser']!=oldq['terminal_parser'] and newq['parser_seal']!=oldq['parser_seal'],
            'explicit new parser path/hash/seal revision required')
    require(newq['capacity_diagnostic']['parser_seal']==newq['parser_seal'],'nested parser seal not revised consistently')
    pinned(newq['terminal_parser']);pinned(newq['parser_seal'])
    newqid=c.digest(newqp);require(newqid!=oldqid,'do not overwrite/reuse original qualification')
    require(proof['scientific_semantics_unchanged'] is True and proof['status']=='PARSER_ONLY_ORDERING_FIX_VERIFIED' and
            proof['reviewed_by']=='E','explicit source-order-only owner review required')
    # Registration uses existing version-specific native/build/producer checks;
    # no old held Q is unheld to inspect the new separately registered decoder Q.
    require(coord.register_qualification(newqp)==newqid,'new qualification registration mismatch')
    newspec=copy.deepcopy(oldspec);newspec.update(qualification_id=newqid,parser=newq['terminal_parser'])
    require(stable_spec(newspec)==stable_spec(oldspec),'new decoder spec changed scientific input/config/identity')
    newaudit=runner.inspect(newspec,coord,launch_check=False)
    require(stable_audit(newaudit)==stable_audit(old['input_audit']),
            'independent source/config/trace/input/termination audit changed beyond Q/parser hashes')
    require(newaudit['parser']==newq['terminal_parser'] and newaudit['qualification_sha256']==newqid,'new audit not exact revised Q/parser')
    newspec['input_audit']=newaudit
    name=row['recovery_subdirectory'];require(re.fullmatch(r'parser_recovery_[A-Za-z0-9_.-]+',name) is not None,'safe unique parser recovery child required')
    recovery=origin/name;require(not recovery.exists(),'retain previous recovery; review a separate revision explicitly')
    summary,parser_exit=parse_under_original_test_lease(coord,newspec,recovery,origin/'raw.log')
    # Preserve actual application-native evidence bytes for existing accept_pair/report.
    for name in ('NATIVE_EXIT.json','NATIVE_EXECUTION_READY.json'):
        shutil.copyfile(origin/name,recovery/name);require(c.digest(recovery/name)==c.digest(origin/name),'native proof copy differs')
    (recovery/'raw.log').symlink_to(origin/'raw.log') # reference only: no raw bytes/inode overwritten or duplicated
    c.write_json(recovery/'input_audit.json',newaudit)
    native_again=native_proof(attempt,old,origin);require(native_again==native,'native evidence changed during decoder recovery')
    actual=runner.runtime_metrics(origin/'raw.log',newaudit['effective_options'])
    require(summary['cycles']==actual['cycle'] and summary['instructions']==actual['insn']==newaudit['expected_full_instructions'],
            'new decoder/native/full-instruction mismatch')
    require(summary['slices']==64 and summary['kernel_completion']['expected']==oldspec['expected_kernel_count'] and
            summary['kernel_completion']['launched_uids']==summary['kernel_completion']['completed_uids'] and
            len(summary['kernel_completion']['completed_uids'])==oldspec['expected_kernel_count'],
            'complete kernel or64slice closure failed')
    registered=coord.snapshot()['qualifications'][newqid]
    validation=runner.validate_terminal_summary(summary,newspec,registered,newaudit);require(validation['status']=='PASS','independent terminal closure failed')
    require(runner.inspect(newspec,coord,launch_check=False)==newaudit,'new qualification/source/input changed during decoder validation')
    recovered=copy.deepcopy(old);recovered.update(status='COMPLETE_VALID',detail='Independent complete parse-only recovery; original charged FAILED attempt retained',
       execution_stage='PARSER_ONLY_RECOVERY_COMPLETE',qualification_id=newqid,input_audit=newaudit,summary=summary,
       mechanism_metrics=summary.get('mechanism_metrics',{}),validation=validation,independent_acceptance='PASS',complete_input_verified=True,
       parser_recovery=dict(original_qualification_id=oldqid,new_qualification_id=newqid,original_failure=row['original_receipt'],
           original_attempt_state=attempt['state'],original_raw=ref(origin/'raw.log'),original_native_binding=native['binding'],
           revised_parser=newq['terminal_parser'],parser_execution_exit=parser_exit,intake_sha256=intake_sha,
           simulator_rerun=False,new_application_charges=0,scope='Only decoder record-order handling and Q/parser metadata changed'))
    receipt=recovery/'run_status.json';c.write_json(receipt,recovered)
    key='qualification:'+oldqid;hold=copy.deepcopy(coord.snapshot().get('scientific_holds',{}).get(key))
    require(hold is not None and hold['qualification_id']==oldqid,'exact old parser qualification HOLD not present')
    c.write_json(recovery/'ORIGINAL_HOLD.json',hold)
    review=dict(reviewed_by='E',qualification_id=oldqid,status='RESOLVED_WITH_EXPLICIT_EVIDENCE',hold_at_unix=hold['at_unix'],
      reason='Independent new decoder order revision fully validates the same completed native evidence; old FAILED/Q/parser evidence retained, no app replay',
      evidence=[ref(receipt),ref(newqp),ref(P/'PARSER_RECOVERY_INTAKE.json'),ref(recovery/'ORIGINAL_HOLD.json'),*proof['evidence']])
    resolution=recovery/'HOLD_RESOLUTION_REVIEW.json';c.write_json(resolution,review)
    with coord.locked() as (data,item):
        require(item['controller']['state']=='STOPPED' and historical(item)==history,'scientific history/controller changed before recovery acceptance')
        require(item['accepted_results']==prior_accepted,'preexisting accepted endpoint mutated during decoder recovery')
        require(not any(r.get('experiment_id')==c.CAMPAIGN and r['status'] in c.ACTIVE for group in ('runs','resource_leases') for r in data[group].values()),'active campaign process at recovery commit')
        require(c.digest(oldpath)==attempt['receipt_sha256'] and c.digest(origin/'raw.log')==old['raw_log_sha256'],'original completed evidence changed before commit')
        require(attempt['attempt_id'] not in item['accepted_results'],'accepted pointer already exists; never overwrite')
        coord.require_no_hold(item,newqid)
        pointer=dict(path=str(receipt),sha256=c.digest(receipt),run_key=attempt['run_key'],identity=attempt['identity'],
           qualification_id=newqid,parser_only_recovered=True,original_failed_receipt=row['original_receipt'])
        item['accepted_results'][attempt['attempt_id']]=pointer
        item.setdefault('parser_recovery_history',[]).append(dict(at_unix=time.time(),attempt_id=attempt['attempt_id'],
           original_attempt=copy.deepcopy(attempt),original_receipt=row['original_receipt'],original_hold=hold,
           new_qualification_id=newqid,new_receipt=ref(receipt),resolution_review=ref(resolution),
           actual_starts_unchanged=item['actual_starts'],T0_unchanged=item['t0_unix'],new_applications=0))
    # Keep the old Q hold active until every requested endpoint in this cohort
    # has independently passed. OFF and ON may share the SAME old Q/HOLD.
    after=coord.snapshot();require(historical(after)==history,'recovery altered charged attempts/old scientific history')
    require(after['accepted_results'][attempt['attempt_id']]==pointer,'new accepted pointer changed')
    result=dict(status='PARSER_ONLY_RECOVERY_ACCEPTED_OLD_HOLD_PENDING_COHORT_REVIEW',attempt_id=attempt['attempt_id'],
       accepted_result=pointer,original_failure=row['original_receipt'],actual_starts=after['actual_starts'],new_application_starts=0,
       scientific_history_unchanged=True,revised_Q=newqid,pending_old_hold_resolution=oldqid,
       resolution_review=ref(resolution),original_hold_at_unix=hold['at_unix'],new_receipt=ref(receipt))
    c.write_json(recovery/'RECOVERY_COMMIT_RECEIPT.json',result);return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--execute-sealed-intake',action='store_true',required=True);ap.add_argument('--intake-sha256',required=True);a=ap.parse_args()
    require(re.fullmatch('[0-9a-f]{64}',a.intake_sha256) is not None and c.digest(INTAKE)==a.intake_sha256,'exact root recovery intake pin required')
    intake=read(INTAKE);require(intake['schema']=='E2_COMPLETED_NATIVE_PARSER_ONLY_RECOVERY_INTAKE_V1' and
      intake['approved_by']=='E' and intake['new_application_starts']==0,'explicit E decoder-only recovery scope required')
    proof=read(pinned(intake['owner_review']))
    for evidence in proof['evidence']:pinned(evidence)
    c.tooling_binding();coord=c.Coordinator();safe_boundary(coord)
    results=[recover(row,a.intake_sha256,coord,proof) for row in intake['attempts']]
    # One exact resolution per original Q after all requested endpoint decodes
    # pass; two failed endpoints can share a single overwritten-current HOLD.
    for oldqid in sorted({r['pending_old_hold_resolution'] for r in results}):
        cohort=[r for r in results if r['pending_old_hold_resolution']==oldqid]
        current=coord.snapshot()['scientific_holds']['qualification:'+oldqid]
        require(all(r['original_hold_at_unix']==current['at_unix'] for r in cohort),'old Q HOLD changed before explicit cohort resolution')
        review=read(pinned(cohort[0]['resolution_review']))
        review['evidence'] += [r['new_receipt'] for r in cohort[1:]]
        review['reason'] += '; all requested endpoints sharing this exact Q independently passed; original hold history retained'
        target=Path(cohort[0]['new_receipt']['path']).parent/'COHORT_HOLD_RESOLUTION_REVIEW.json'
        c.write_json(target,review);coord.resolve_scientific_hold(oldqid,target)
        for result in cohort:
            result.update(status='PARSER_ONLY_RECOVERY_ACCEPTED_ORIGINAL_FAILURE_RETAINED',resolved_old_hold=oldqid,cohort_resolution_review=ref(target))
            c.write_json(Path(result['new_receipt']['path']).parent/'RECOVERY_COMMIT_RECEIPT.json',result)
    print(json.dumps(dict(status='COHORT_COMPLETE',results=results,new_application_starts=0)),flush=True)

if __name__=='__main__':main()

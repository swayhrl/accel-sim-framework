"""DRAFT independent E native replay; requires a real root-sealed formal intake.

Not executed during preparation. No production build, application start,
qualification registration, second controller, automatic retry or Git action.
The original Coordinator owns the one E test lease; NativeProcess persists the
actual ELF child's direct-parent exit. See INTAKE_SCHEMA.md before use.
"""
from pathlib import Path
import argparse, copy, fcntl, hashlib, json, math, os, re, signal, subprocess, sys, time

P=Path(__file__).resolve().parent
PACK=P.parent
ROOT=PACK.parents[3]
INTAKE=PACK/'E_NATIVE_INTAKE.json'
AUTH='49343880865edb22a17523790fc32dd55975966c'
GIB=2**30
MEMORY=8*GIB
GROWTH=512*2**20
METADATA=16*2**20
TOTAL_SECONDS=1800
MAIN61='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'

def require(ok,message):
    if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text())
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for data in iter(lambda:f.read(4*2**20),b''):h.update(data)
    return h.hexdigest()
def reference(p):return dict(path=str(Path(p).resolve(strict=True)),sha256=digest(p))
def checked_ref(value):
    require(isinstance(value,dict) and isinstance(value.get('path'),str),'real content reference required')
    require(re.fullmatch('[0-9a-f]{64}',value.get('sha256','')) is not None,'real SHA256 pin required')
    p=Path(value['path']).resolve(strict=True)
    require(p.is_file() and digest(p)==value['sha256'],'missing/changed pinned input: '+str(p))
    return p
def elf(p):
    p=Path(p).resolve(strict=True)
    with p.open('rb') as f:require(f.read(4)==b'\x7fELF','command must directly execute an actual ELF: '+str(p))
    require(os.access(p,os.X_OK),'ELF is not executable')
    return p
def stamp(p):
    s=Path(p).stat();return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def render(values,out,stage):
    require(isinstance(values,list) and all(isinstance(v,str) for v in values),'literal argv list required')
    result=[v.replace('{OUTPUT}',str(out)).replace('{STEP}',str(stage)) for v in values]
    require(not any('{' in v or '}' in v for v in result),'unsupported command substitution')
    require(not any(v.startswith(('-trace','--trace')) or v in ('--full-application','--application','--workload','--app') for v in result),'full-application/trace execution prohibited')
    return result
def fingerprint_history(s):
    return copy.deepcopy({k:s[k] for k in ('t0_unix','actual_starts','attempts','accepted_results','accepted_pairs','full_system_matrix','scientific_holds') if k in s})
def own_group_members(pgid,d):
    rows=[]
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:
            text=(path/'stat').read_text();v=text[text.rfind(')')+2:].split()
            if int(v[2])==pgid and int(v[3])==pgid:rows.append(d.identity(int(path.name)))
        except (FileNotFoundError,ProcessLookupError,PermissionError):pass
    return rows
def drain_owned_group(pgid,d):
    remaining=own_group_members(pgid,d)
    if not remaining:return []
    # The exact recorded native PID was session/PGID leader. This group is our
    # owned descendant tree; never select a process by binary name or project.
    os.killpg(pgid,signal.SIGTERM);until=time.monotonic()+3
    while time.monotonic()<until and own_group_members(pgid,d):time.sleep(.05)
    if own_group_members(pgid,d):os.killpg(pgid,signal.SIGKILL)
    return remaining
def check_source(index):
    source=index['source_identity']
    for key in ('core_source_commit','framework_source_commit','vendor_pybind11_commit','binary_sha256'):
        n=64 if key=='binary_sha256' else 40
        require(re.fullmatch('[0-9a-f]{'+str(n)+'}',source.get(key,'')) is not None,'real new source identity required')
    require(source['binary_sha256']!=MAIN61,'main61 runtime qualification cannot be inherited')
    for field,key in [('core','core_source_commit'),('runtime_framework','framework_source_commit')]:
        repo=Path(index[field]).resolve(strict=True)
        head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
        dirty=subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True)
        require(head==source[key] and not dirty,'formal runtime source identity/cleanliness changed')
    return source
def verify_formal(index):
    require(index.get('schema')=='E2_CAPACITY_FORMAL_NATIVE_INTAKE_V1','wrong native intake schema')
    require(index.get('status')=='FORMAL_PRODUCER_READY_E_INDEPENDENT_NATIVE_PENDING','candidate intake prohibited')
    require(index.get('sealed_by') in ('E','E2') and index.get('authority_commit')==AUTH,'root E sealed approval required')
    require(index.get('production_main_or_archive_build_requested') is False,'E must not build production main/archive')
    source=check_source(index);producer=index['formal_producer']
    require(producer.get('formal_release_reviewed_by_E') is True,'formal producer release not reviewed')
    release=checked_ref(producer['release']);commit=producer['commit']
    require(re.fullmatch('[0-9a-f]{40}',commit) is not None,'formal producer Git commit required')
    repo=Path(subprocess.check_output(['git','-C',str(release.parent),'rev-parse','--show-toplevel'],text=True).strip())
    remote=read(checked_ref(producer['remote_readback']))
    require(remote.get('remote_commit')==commit and bool(remote.get('verified_paths')),'producer byte readback missing')
    require(subprocess.check_output(['git','-C',str(repo),'show',commit+':'+release.relative_to(repo).as_posix()])==release.read_bytes(),'release differs from exact published Git blob')
    checked_ref(index['main']);checked_ref(index['archive'])
    require(index['main']['sha256']==source['binary_sha256'],'main pin differs from formal source')
    refs=[producer['release'],producer['remote_readback'],index['main'],index['archive'],*index['build_pins']]
    require(bool(index['build_pins']),'formal build/link/source evidence pins required')
    for row in index['test_elfs'].values():
        require(row['role'] in ('NEW_PRODUCTION_NATIVE_FIXTURE','OLD_OFF_COMPARISON_REFERENCE'),'unsupported ELF role')
        checked_ref(row);elf(row['path']);checked_ref(row['link_provenance'])
        require(row.get('source_pins'),'fixture source pins missing')
        require(row.get('bounded_fixture_source_reviewed_by_E') is True,'E must review the actual bounded fixture source')
        fixture_sources=[Path(r['path']).resolve() for r in row['source_pins'] if Path(r['path']).suffix in ('.cc','.cpp','.c')]
        require(any(p.is_relative_to(Path(index['core'])/'tests/ep_l2') or
                    (p.is_relative_to(PACK) and p.name.startswith('test')) for p in fixture_sources),
                'native ELF must name a bounded test fixture source, not simulator main')
        refs += [row,row['link_provenance'],*row['source_pins']]
        if row['role']=='NEW_PRODUCTION_NATIVE_FIXTURE':require(row['source_identity']==source,'fixture source differs from new producer')
        else:require(row.get('reference_only') is True,'old OFF reference must be explicitly labeled and never inherited')
        require(row['sha256'] not in (source['binary_sha256'],MAIN61),'full-application binary is not a native fixture')
    require(index['cases'] and len({r['id'] for r in index['cases']})==len(index['cases']),'finite unique real cases required')
    for row in index.get('compile_steps',[]):
        require(row.get('kind') in ('COMPILE_E_TEST','LINK_E_TEST'),'E can only compile/link its independent test fixture')
        checked_ref(row['compiler']);elf(row['compiler']['path'])
        require(row['source_pins'],'explicit E fixture sources required')
        for item in row['source_pins']:
            src=checked_ref(item)
            require(src.is_relative_to(PACK) and src.suffix in ('.cc','.cpp','.c','.h'),'only E-owned independent test source can be compiled')
        refs += [row['compiler'],*row['source_pins'],*row.get('input_pins',[])]
        require(row['timeout_seconds'] in (120,300),'bounded compile/link timeout required')
        require(row['output_relative_path'].endswith(('.o','.native')),'only new E fixture object or .native output allowed')
        require(row['output_relative_path'] not in ('accel-sim.out','libgpgpusim.a'),'production build prohibited')
    for row in index['cases']:
        require(row['timeout_seconds'] in (120,300),'case timeout must be explicitly120 or300 seconds')
        require(type(row['expected_exit']) is int and -64<=row['expected_exit']<=255,'exact expected native exit required')
        require(row.get('required_terminal') and all(isinstance(x,str) and x for x in row['required_terminal']),'explicit native assertion markers required')
        require(row.get('full_application') is False,'every case is bounded native only')
        require(('elf_id' in row)!=('generated_elf_id' in row),'one exact native ELF selector required')
    for item in refs:checked_ref(item)
    return source,refs
def terminal_checks(raw,required):
    # One bounded streaming pass computes the raw identity and exact literal
    # checks. No checker process can substitute for the native ELF exit status.
    needles={s:s.encode() for s in required};found={s:False for s in required}
    h=hashlib.sha256();tail=b'';overlap=max((len(v) for v in needles.values()),default=1)-1
    with Path(raw).open('rb') as f:
        for data in iter(lambda:f.read(2**20),b''):
            h.update(data);window=tail+data
            for text,value in needles.items():found[text]|=value in window
            tail=window[-overlap:] if overlap else b''
    return found,h.hexdigest()

def execute(sealed_sha):
    started=time.monotonic();require(re.fullmatch('[0-9a-f]{64}',sealed_sha) is not None,'exact sealed intake SHA required')
    require(INTAKE.is_file() and digest(INTAKE)==sealed_sha,'root-sealed E_NATIVE_INTAKE.json absent/changed')
    index=read(INTAKE);source,refs=verify_formal(index)
    sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
    import coordinator as c,capacity_policy,durable_exit as d
    c.tooling_binding();coord=c.Coordinator();before=coord.snapshot();history=fingerprint_history(before)
    limits=capacity_policy.effective_limits(before)
    require(before['actual_starts']==36 and before['controller']['state']=='STOPPED','independent replay starts at charged36/stopped boundary')
    prior_controller=before['controller'].get('process')
    if prior_controller:
        try:still_same=c.process_identity(prior_controller['pid'])==prior_controller
        except (FileNotFoundError,ProcessLookupError):still_same=False
        require(not still_same,'old controller process is still alive; do not overlap')
    require(not any(a['state'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED') for a in before['attempts']),'live or uncertain application exists')
    # Audit the already-existing original lock only. Do not enter
    # unique_controller(), change controller state, or create another lock.
    with (c.HANDOFF/'CONTROLLER.lock').open('rb') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        fcntl.flock(lock.fileno(),fcntl.LOCK_UN)
    require(limits['additional_results_max_bytes']==10*GIB and limits['old_plus_new_results_max_bytes']==24*GIB,'approved cumulative output policy not adopted')
    out=Path(index['output_directory']).resolve()
    require(out.is_relative_to(c.OUTPUT) and out.parent.exists() and not out.exists(),'unique new accounted native result directory required')
    require(not (out.parent.is_symlink()) and out.parent.stat().st_dev==Path('/workspace').stat().st_dev,'physical workspace output required')
    pins={str(checked_ref(r)):dict(reference=copy.deepcopy(r),stamp=stamp(r['path'])) for r in refs}
    steps=index.get('compile_steps',[])
    ids=[r['id'] for r in steps]+[r['id'] for r in index['cases']]
    require(len(ids)==len(set(ids)) and all(v not in ('.','..') and re.fullmatch('[A-Za-z0-9_.-]+',v) for v in ids),'safe distinct stage IDs required')
    lease=None;current=None;constructing=False;current_bound=False;bound_any=False;lease_released=False;rows=[];generated={};suite_error=None
    def original_history():require(fingerprint_history(coord.snapshot())==history,'historical scientific state/count/anchors changed')
    def stable_pins(full=False):
        require(digest(INTAKE)==sealed_sha,'sealed intake changed')
        check_source(index)
        for name,row in pins.items():
            require(stamp(name)==row['stamp'],'pinned file replaced/modified during replay: '+name)
            if full:require(digest(name)==row['reference']['sha256'],'pinned bytes changed')
    def stage_run(row,command,kind,artifact_identity):
        nonlocal current,constructing,current_bound,bound_any
        require(not d.STOP.is_set(),'parent stop requested; no further native work')
        remaining=math.floor(TOTAL_SECONDS-(time.monotonic()-started))
        require(remaining>0,'1800s bounded suite exhausted')
        original_history();stable_pins()
        retained=c.retained_tree_bytes(out);left=GROWTH-retained-METADATA
        require(left>0,'512MiB native output allowance exhausted')
        current_dir=out/row['id'];current_dir.mkdir();(current_dir/'tmp').mkdir();(current_dir/'cache').mkdir()
        bounds={k:lease[k] for k in ('policy_id','disk_floor_bytes','monitor_reserve_bytes','monitor_interval_seconds','termination_grace_seconds')}
        bounds.update(memory_bytes=MEMORY,maximum_result_bytes=left,
            timeout_seconds=min(row['timeout_seconds'],remaining),
            **{k:limits[k] for k in ('intake_deadline_unix','additional_results_max_bytes','old_plus_new_results_max_bytes')})
        # Every bounds/binding/report copy is independent. Never mutate a saved
        # request or earlier result while preparing the next native case.
        bounds=copy.deepcopy(bounds)
        binding=dict(schema='E2_INDEPENDENT_NATIVE_CASE_BINDING_V1',intake_sha256=sealed_sha,
            lease_id=lease['lease_id'],case_id=row['id'],kind=kind,source_identity=copy.deepcopy(source),
            executed_artifact=copy.deepcopy(artifact_identity),full_application=False)
        env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',
            TMPDIR=str(current_dir/'tmp'),TMP=str(current_dir/'tmp'),TEMP=str(current_dir/'tmp'),XDG_CACHE_HOME=str(current_dir/'cache'))
        raw=current_dir/'raw.log';current=None;current_bound=False;constructing=True
        with raw.open('xb') as log:
            current=d.NativeProcess(command,current_dir,log,env,copy.deepcopy(bounds),copy.deepcopy(binding))
            constructing=False
            identity=coord.bind_work_process(lease['lease_id'],'E',current.pid);bound_any=True;current_bound=True
            require(identity==current.ready['native_process'],'lease/native identity mismatch')
            current.release()
            until=time.monotonic()+bounds['timeout_seconds']+15;parent_stop=None
            while current.poll() is None:
                if (d.STOP.is_set() or time.monotonic()>=until or c.retained_tree_bytes(out)>=GROWTH-METADATA) and parent_stop is None:
                    parent_stop='PARENT_STOP_OR_TOTAL_OUTPUT_OR_BOUNDED_SUPERVISION_TIMEOUT'
                    os.kill(current.collector.pid,signal.SIGTERM)
                if parent_stop and time.monotonic()>=until+10:
                    raise d.ExitEvidenceMissing('bounded collector closure missing; preserve lease and evidence')
                time.sleep(.1)
            native=current.exit_evidence();current.collector.wait(timeout=5)
        descendants=drain_owned_group(current.pid,d)
        checks,raw_sha=terminal_checks(raw,row.get('required_terminal',['']))
        actual_ok=(native['exit_code']==row['expected_exit'] and native['stop_reason'] is None and
                   native['released_to_native'] is True and not descendants and parent_stop is None and all(checks.values()))
        require(read(current_dir/'NATIVE_EXECUTION_REQUEST.json')['bounds']==bounds,'persisted request bounds differ')
        result=dict(schema='E2_INDEPENDENT_NATIVE_CASE_RESULT_V1',case_id=row['id'],kind=kind,
            status='EXPECTATIONS_MATCH' if actual_ok else 'FAILED',actual_exit=native['exit_code'],actual_wait_status=native['wait_status'],
            expected_exit=row['expected_exit'],native_process=copy.deepcopy(native['native_process']),
            guardian_process=copy.deepcopy(native['guardian_process']),native_exit=copy.deepcopy(native),
            native_exit_receipt=reference(current_dir/'NATIVE_EXIT.json'),raw=dict(path=str(raw),sha256=raw_sha),
            required_checks=checks,bounds=copy.deepcopy(bounds),binding=copy.deepcopy(binding),
            stopped_by_parent=parent_stop,descendants_found_after_native_exit=descendants,
            full_application=False,application_start_charges_added=0,scientific_qualification='PENDING_E_ASSERTION_AND_SOURCE_REVIEW')
        d.durable_json(current_dir/'CASE_RESULT.json',copy.deepcopy(result));rows.append(copy.deepcopy(result));current=None
        require(c.retained_tree_bytes(out)<GROWTH,'native result directory exceeded512MiB')
        require(actual_ok,'native case did not match exact exit and required checks: '+row['id'])
        return result,current_dir
    try:
        lease=coord.reserve_work('E','test',1,MEMORY,GROWTH,out,result_growth_bytes=GROWTH)
        out.mkdir();d.durable_json(out/'SEALED_INTAKE.json',copy.deepcopy(index));d.durable_json(out/'TEST_LEASE.json',copy.deepcopy(lease))
        d.durable_json(out/'PRE_NATIVE_STATE.json',dict(actual_starts=before['actual_starts'],T0=before['t0_unix'],source_identity=source,
            intake_sha256=sealed_sha,output_usage=c.output_usage(),limits=copy.deepcopy(limits)))
        with d.controller_signals():
            for row in steps:
                stage=out/row['id'];command=[str(elf(checked_ref(row['compiler'])))]+render(row['args'],out,stage)
                require(command.count('-o')==1,'one explicit E test output required')
                target=Path(command[command.index('-o')+1]).resolve()
                expected=(stage/row['output_relative_path']).resolve()
                require(target==expected and target.is_relative_to(stage) and not target.exists(),'compile/link target must be a unique owned test artifact')
                require(not any(v in ('-shared','-j','--build') or v.startswith('-j') for v in command[1:]),'production/build-system or parallel build command prohibited')
                if row['kind']=='COMPILE_E_TEST':require('-c' in command,'test compile step must compile only')
                source_args=[str(checked_ref(r)) for r in row['source_pins'] if Path(r['path']).suffix in ('.cc','.cpp','.c')]
                if row['kind']=='COMPILE_E_TEST':require(all(v in command for v in source_args),'compile source pins differ from literal command')
                else:
                    generated_args=[r['reference']['path'] for r in generated.values()]
                    require(any(v in command for v in source_args+generated_args),'link command lacks the actual E fixture source/object')
                # Linking is allowed to READ the formal archive, never write it.
                compile_row=dict(row,expected_exit=0,required_terminal=row.get('required_terminal',[]))
                result,directory=stage_run(compile_row,command,row['kind'],dict(compiler=copy.deepcopy(row['compiler']),sources=copy.deepcopy(row['source_pins']),output_path=str(target)))
                require(target.is_file(),'compiler exited without declared test artifact')
                generated[row['id']]=dict(reference=reference(target),source_identity=copy.deepcopy(source),compile_case_receipt=reference(directory/'CASE_RESULT.json'))
                if row['kind']=='LINK_E_TEST':elf(target)
                d.durable_json(directory/'GENERATED_ARTIFACT.json',copy.deepcopy(generated[row['id']]))
            for row in index['cases']:
                if 'elf_id' in row:
                    artifact=copy.deepcopy(index['test_elfs'][row['elf_id']]);exe=elf(checked_ref(artifact))
                else:
                    made=generated[row['generated_elf_id']];artifact=copy.deepcopy(made);exe=elf(checked_ref(made['reference']))
                require(exe!=Path(index['main']['path']).resolve(),'production main path is not a native fixture')
                require(digest(exe) not in (source['binary_sha256'],MAIN61),'application binary cannot be run as a native test')
                command=[str(exe)]+render(row['args'],out,out/row['id'])
                stage_run(row,command,'DIRECT_NATIVE_TEST_ELF',artifact)
        stable_pins(full=True);original_history()
    except BaseException as exc:
        suite_error=dict(type=type(exc).__name__,detail=str(exc));
        if current is not None and current.poll() is None:
            os.kill(current.collector.pid,signal.SIGTERM)
            try:current.wait(timeout=15)
            except Exception as closure:suite_error['closure_error']=str(closure)
    finally:
        if lease is not None:
            unresolved=constructing
            if current is not None:
                unresolved|=not current_bound
                try:
                    unresolved|=current.poll() is None
                    if not unresolved:unresolved|=bool(own_group_members(current.pid,d))
                except Exception:unresolved=True
            if not unresolved:
                try:
                    coord.release_work(lease['lease_id'],'E','Bounded independent native replay finished; no app charges; '+('FAILED' if suite_error else 'expectations matched'),no_child_started=not bound_any)
                    lease_released=True
                except Exception as release_error:
                    suite_error=suite_error or dict(type='LeaseReleaseError',detail=str(release_error))
            if out.exists():
                after=coord.snapshot();unchanged=fingerprint_history(after)==history
                report=dict(schema='E2_CAPACITY_INDEPENDENT_NATIVE_REPLAY_RESULT_V1',
                    status='NATIVE_EXPECTATIONS_MATCH_PENDING_SCIENTIFIC_QUALIFICATION' if suite_error is None and unchanged and lease_released else 'FAILED_OR_INCOMPLETE',
                    intake=dict(path=str(INTAKE),sha256=sealed_sha),source_identity=copy.deepcopy(source),lease_id=lease['lease_id'],lease_released=lease_released,
                    retained_active_lease_for_unresolved_native=not lease_released,error=suite_error,cases=copy.deepcopy(rows),generated_test_artifacts=copy.deepcopy(generated),
                    elapsed_seconds=time.monotonic()-started,output_directory=str(out),retained_result_bytes=c.retained_tree_bytes(out),
                    original_scientific_history_unchanged=unchanged,T0=after['t0_unix'],actual_starts=after['actual_starts'],
                    full_applications_started=0,new_native_application_qualification_granted=False,output_usage=c.output_usage(),at_unix=time.time())
                d.durable_json(out/'NATIVE_REPLAY_RESULT.json',copy.deepcopy(report))
                print(json.dumps({k:report[k] for k in ('status','lease_released','actual_starts','elapsed_seconds','output_directory')}),flush=True)
        if suite_error is not None:raise RuntimeError(json.dumps(suite_error))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--execute-sealed-intake',action='store_true',required=True)
    ap.add_argument('--intake-sha256',required=True)
    args=ap.parse_args();execute(args.intake_sha256)

if __name__=='__main__':main()

"""Independent Oracle registry/closed-result adapter primitives.

Import is inert. No registration or model entrypoint is exposed. Main must
freeze/integrate this source and provide the exact request/row/source pins.
"""
import copy, fcntl, hashlib, json, os, pathlib, re, time
P=pathlib.Path

def require(ok, reason):
    if not ok:raise RuntimeError(reason)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())

def bounded_snapshot(registry_path, epoch_path, lock_path, timeout_seconds=2.0):
    """Read-only SH entry. NEVER invoke under any EX mutator callback."""
    with P(lock_path).open('rb') as lock:
        until=time.monotonic()+timeout_seconds
        while True:
            try:fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB);break
            except BlockingIOError:
                require(time.monotonic()<until,'REGISTRY_BUSY_HOLD_NO_START');time.sleep(.02)
        r=read(registry_path);e=read(epoch_path)
        require(e['epoch']==2 and e['state']=='NATIVE_SCIENCE_ACTIVE','EPOCH2_REQUIRED')
        require(e['native_registry_sha256']==sha(registry_path),'REGISTRY_EPOCH_SHA')
        return r,e

def mutate_from_passed_snapshot(registry, allowed_request_ids, callback):
    """Pure mutation projection to call inside Main's actual EX writer.

    No bounded_snapshot / registered / canonical / runtime resource query is
    called transitively. Every helper needed by callback must accept this passed
    snapshot. The actual independent review must inspect callback callgraph too.
    """
    require(allowed_request_ids and len(set(allowed_request_ids))==len(allowed_request_ids),'EXACT_REQUEST_ALLOWLIST')
    before=copy.deepcopy(registry);current=copy.deepcopy(registry)
    callback(current)
    old=before['registered_future_requests'];new=current['registered_future_requests']
    require(set(old)<=set(new),'REQUEST_HISTORY_DELETION')
    require(set(new)-set(old)<=set(allowed_request_ids),'UNAUTHORIZED_REQUEST_APPEND')
    require(all(new[k]==v for k,v in old.items()if k not in allowed_request_ids),'FOREIGN_REQUEST_MUTATION')
    # Derived global remaining may be recomputed by the outer writer, not used
    # to overwrite any individual old request's remaining/history.
    require({k:v for k,v in before.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']}==
            {k:v for k,v in current.items()if k not in ['registered_future_requests','new_scientific_budget_remaining']},'FOREIGN_REGISTRY_HISTORY_MUTATION')
    for key in allowed_request_ids:
        if key not in new:continue
        q=new[key];require(type(q['budget'])is int and q['budget']>=0,'BUDGET_TYPE')
        require(isinstance(q['consumed'],dict),'ONE_USE_CONSUMED_MAP')
        require(q['remaining']==q['budget']-len(q['consumed']),'BUDGET_CONSERVATION')
        require(set(q['consumed'])<=set(q['admitted_specs']),'UNREGISTERED_MODEL_IDENTITY')
        require(len({x['uuid']for x in q['consumed'].values()})==len(q['consumed']),'DUPLICATE_UUID')
        if key in old:
            p=old[key]
            require(q['budget']==p['budget']and q['admitted_specs']==p['admitted_specs'],'NO_BUDGET_EXTENSION_OR_INPUT_CHANGE')
            require(set(p['consumed'])<=set(q['consumed']),'CONSUMED_IDENTITY_REFUND')
            for c,row in p['consumed'].items():
                # A genuine later execution receipt may be appended; original
                # consumed identity and every existing field stay immutable.
                require(all(q['consumed'][c].get(k)==v for k,v in row.items()),'CONSUMED_IDENTITY_OVERWRITE')
    return current

def closed_engineering_negative(intent, done, output):
    """Typed before-PID negative inventory; never fabricates runtime evidence."""
    output=P(output)
    require(done['uuid']==intent['uuid']and done['new_attempt_consumed']==1,'CLOSED_UUID_REQUIRED')
    require(not done['native_simulator_observed'],'NOT_A_BEFORE_PID_ENGINEERING_NEGATIVE')
    require(done.get('launcher_wait_returncode')not in[None,0]or done.get('stop_reason'),'GENUINE_FAILURE_REQUIRED')
    forbidden=['NATIVE_SIMULATOR_PID_AND_MAPS.json','NATIVE_SIMULATOR_VERIFIED_LATE_MAPS.json']
    require(not any((output/x).exists()for x in forbidden),'PID_EVIDENCE_EXISTS_USE_ACTUAL_LIFECYCLE_CLASSIFICATION')
    entries=[]
    for path in sorted(output.iterdir()):
        if path.is_file():entries.append(dict(path=str(path),name=path.name,bytes=path.stat().st_size,sha256=sha(path)))
    require(entries,'EMPTY_NEGATIVE_EVIDENCE')
    return dict(schema='DTC_CONTROLLED_ORACLE_BEFORE_PID_ENGINEERING_NEGATIVE_V1',uuid=intent['uuid'],
                classification='ENGINEERING_NEGATIVE_BEFORE_PID_PRESERVE_NO_RETRY',cycles=None,
                native_simulator_observed=False,manifest_entries=entries,
                fabricated_PID_trace_guard_counters=False,SOURCE_KEEP=True,model_retries=0)

def verify_typed_restore(source_manifest, archive_receipt, native_restore_root):
    """Typed restore supplemental check; outer archive verifier still mandatory."""
    root=P(native_restore_root)
    require(root.stat().st_dev==2128,'RESTORE_MUST_BE_NATIVE_EXT4')
    require(archive_receipt['SOURCE_KEEP']is True,'SOURCE_KEEP_REQUIRED')
    entries=source_manifest['entries'];require(entries,'EMPTY_SOURCE_MANIFEST')
    checks=[]
    for row in entries:
        relative=P(row.get('relative_path',row.get('name','')))
        require(str(relative)not in['','.']and not relative.is_absolute()and'..'not in relative.parts,'RESTORE_RELATIVE_PATH')
        p=root/relative
        require(p.is_file()and not p.is_symlink(),'RESTORE_TYPE_FILE_REQUIRED')
        require(p.stat().st_size==row['bytes']and sha(p)==row['sha256'],'TYPED_NATIVE_RESTORE_SHA')
        checks.append(str(relative))
    return dict(typed_files=len(checks),native_device=root.stat().st_dev,all_sha_pass=True,
                archive_index_chunk_COMMIT_verification_still_required=True)

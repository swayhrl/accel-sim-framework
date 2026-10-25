"""Finite audited queue, not a daemon or scientific controller."""
import os,sys,json,time,pathlib,hashlib,gzip,fcntl,traceback
import copy_engine as c
P=pathlib.Path;TASK=c.TASK;NAS=c.NAS.parent
STATE=TASK/'control'/'STATE.json';LEDGER=TASK/'control'/'LEDGER.jsonl'
stage={};last_state=0

def persist(path,x):
    path=P(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.own-writing')
    with temp.open('wb') as f:f.write(c.canon(x));f.flush();os.fsync(f.fileno())
    os.replace(temp,path)

def update(force=False,**kw):
    global last_state
    stage.update(kw);stage['unix']=time.time();stage['driver_pid']=os.getpid()
    stage['driver_start_ticks']=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
    if force or time.monotonic()-last_state>=5:persist(STATE,stage);last_state=time.monotonic()

def event(x):
    if x.get('event')=='RANGE_VERIFIED':update(phase='TRANSFER_RANGE_VERIFIED',file=x['file'],verified_end=x['verified_end'],current_asset_new_transferred_bytes=x['new_payload_bytes'])
    print(json.dumps(x),flush=True)

c.emit=event
BaseResources=c.Resources
class DriverResources(BaseResources):
    def __call__(self,force=False):
        x=super().__call__(force);update(SSD_available_bytes=x['SSD_available_bytes'],SSD_required_bytes=x['SSD_required_bytes'],current_host_io=x['IO'],archive_transfer_rate_policy=x.get('archive_transfer_rate_policy'));return x
c.Resources=DriverResources

def append(x):
    LEDGER.parent.mkdir(parents=True,exist_ok=True)
    with LEDGER.open('ab') as f:f.write(c.canon(x));f.flush();os.fsync(f.fileno())

def prepare(scope):
    control=TASK/'manifests'/(scope['asset_id']+'.json')
    if control.exists():return c.read(control),dict(reused_prepared_manifest=True)
    c.Resources()(True)
    lock=(c.BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    request=dict(scope=scope,source_role='TARGET' if scope['source_alias']=='hrl-174-new' else 'SOURCE',true164_bundle=str(NAS/'assets'/scope['asset_id']).replace('/root/share/mnt164','/home/shared',1))
    p=c.source_boot('prepare',request);prepared=None
    try:
        for line in p.stdout:
            x=json.loads(line)
            if x['event']=='PREPARED':prepared=x
            else:update(force=True,phase='SOURCE_PREHASH',file=x.get('file'),current_file_hashed_bytes=x.get('current_file_bytes'),current_asset_new_hashed_bytes=x.get('new_hashed_bytes'))
        rc=p.wait(timeout=30);err=p.stderr.read().decode(errors='replace');c.need(rc==0 and prepared is not None,'SOURCE_PREPARE_HOLD '+err[-2000:])
    finally:
        if p.poll() is None:p.terminate();p.wait(timeout=10)
        p.stdout.close();p.stderr.close();lock.close()
    persist(control,prepared['manifest']);persist(TASK/'prehash'/(scope['asset_id']+'.json'),{k:v for k,v in prepared.items() if k!='manifest'})
    return prepared['manifest'],{k:v for k,v in prepared.items() if k!='manifest'}

def restore_and_retire_own_test(bundle,m):
    root=TASK/'recovery'/(m['primary_asset_id']+'_VERIFY_v1');control=TASK/'restore'/(m['primary_asset_id']+'.json')
    if control.exists():return c.read(control)
    if m['source_data_bytes']>240*c.MIB:
        out=dict(status='FULL_NATIVE_RESTORE_NOT_PERFORMED_EXCEEDS_BOUND',original_bytes=m['source_data_bytes'],bounded_complete_restore_limit_bytes=240*c.MIB,native164_restore_claimed=False,complete_source_and_true164_full_SHA='VERIFIED',recovery='RESTORE.sh plus complete original numeric metadata in SOURCE_MANIFEST.json')
    else:
        try:
            update(force=True,phase='INDEPENDENT_NATIVE_RESTORE');out=c.restore_native(bundle/'tree',m,root)
            v=c.v9();c.publish_bytes(bundle/'NATIVE_TARGET_RESTORE_PROOF.json',c.canon(out),v)
            # Original source files are not part of this temporary cleanup.
            # Complete proof is durable on true164 before exact new test-copy
            # removal. Recheck fstat and readers; no recursive source deletion.
            own=[dict(x['identity'],path=str(root/x['relative_path'])) for x in out['rows']]
            c.rr.selected_readers_writers(own,[])
            persist(TASK/'restore'/(m['primary_asset_id']+'.CLEANUP_INTENT.json'),dict(scope=str(root),rows=out['rows'],persistent_proof_sha256=c.digest(c.canon(out))))
            before=os.statvfs(root).f_bavail*os.statvfs(root).f_frsize;allocated=0
            for x in out['rows']:
                p=c.safe(root,x['relative_path']);now=c.identity(p);c.need(c.same_source(now,x['identity']),'OWN_TEST_COPY_CHANGED');allocated+=p.stat().st_blocks*512;p.unlink()
            for x in out.get('symlinks',[]):
                p=c.safe(root,x['relative_path']);c.need(p.is_symlink() and os.readlink(p)==x['target'] and c.same_source(c.identity(p),x['identity']),'OWN_TEST_SYMLINK_CHANGED');p.unlink()
            for x in sorted(out.get('directories',[]),key=lambda x:len(P(x['relative_path']).parts),reverse=True):
                p=root if x['relative_path']=='.' else c.safe(root,x['relative_path'])
                if p.exists() and not any(p.iterdir()):p.rmdir()
            after=os.statvfs(TASK).f_bavail*os.statvfs(TASK).f_frsize
            out.update(temporary_native_test_copy_retired=True,temporary_regular_allocated_bytes_removed=allocated,shared_SSD_df_before_cleanup=before,shared_SSD_df_after_cleanup=after,Source_released_bytes=0)
        except RuntimeError as e:
            if root.exists():raise
            out=dict(status='FULL_NATIVE_RESTORE_HOLD',reason=str(e),original_bytes=m['source_data_bytes'],complete_source_and_true164_full_SHA='VERIFIED',native164_restore_claimed=False)
    persist(control,out);c.publish_bytes(bundle/'NATIVE_RESTORE_STATUS.json',c.canon(out),c.v9());return out

def main():
    queue=json.loads(gzip.decompress((TASK/'control/FROZEN_SCOPES.json.gz').read_bytes()))['scopes']
    pilot=min((x for x in queue if x['kind']=='DTC_RAW'),key=lambda x:x['expected_bytes'])
    traces=sorted((x for x in queue if x['kind']=='TRACE'),key=lambda x:(0 if x['queue']['source_endpoint']=='ORIGINAL174_SSD_BACKED_OVERLAY' else 1,0 if x['priority']=='P0' else 1,-x['expected_bytes']))
    other=[x for x in queue if x['kind']!='TRACE' and x['asset_id']!=pilot['asset_id']]
    ordered=[pilot]+traces+other
    c.need(len(ordered)==115 and len({x['asset_id'] for x in ordered})==115,'FROZEN_QUEUE_IDENTITY_MISMATCH')
    previous={}
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            x=json.loads(line)
            if x['status']=='ARCHIVED_CONTENT_VERIFIED':previous[x['asset_id']]=x
    complete=len(previous);holds=0;transferred=sum(x.get('new_transferred_bytes',0) for x in previous.values())
    update(force=True,phase='QUEUE_START',total_assets=115,completed_assets=complete,held_assets=0,total_new_transferred_bytes=transferred)
    for index,scope in enumerate(ordered):
        if scope['asset_id'] in previous:continue
        update(force=True,asset_id=scope['asset_id'],asset_kind=scope['kind'],queue_index=index+1,asset_expected_bytes=scope['expected_bytes'],phase='ASSET_ADMISSION',file=None,verified_end=0,current_asset_new_hashed_bytes=0,current_file_hashed_bytes=0,current_asset_new_transferred_bytes=0)
        started=time.time()
        try:
            m,prep=prepare(scope);bundle=P(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));update(force=True,phase='TRUE164_RANGE_TRANSFER')
            result=c.migrate(m)
            persist(TASK/'receipts'/(scope['asset_id']+'.json'),result)
            restoration=restore_and_retire_own_test(bundle,m)
            record=dict(status='ARCHIVED_CONTENT_VERIFIED',asset_id=scope['asset_id'],kind=scope['kind'],original_bytes=scope['expected_bytes'],regular_files=len(m['members']),new_transferred_bytes=result.get('new_payload_bytes',0),reused_range_bytes=result.get('reused_verified_range_bytes',0),true164_bundle=m['new_true164_bundle'],commit_sha256=c.digest((bundle/'COMMIT.json').read_bytes()),manifest_sha256=c.digest(c.canon(m)),native_restore_status=restoration['status'],source_disposition='SOURCE_KEEP_EXCEPT_FOUR_PREVIOUSLY_AUTHORIZED_RETIRED_FILES',Source_released_bytes=0,elapsed_seconds=time.time()-started,unix=time.time())
            append(record);complete+=1;transferred+=record['new_transferred_bytes'];update(force=True,phase='ASSET_COMMITTED',completed_assets=complete,total_new_transferred_bytes=transferred)
            if index==0:
                qualification=dict(status='QUALIFIED_ZERO_SHARE_PATH',pilot_asset=scope['asset_id'],manifest_sha256=record['manifest_sha256'],commit_sha256=record['commit_sha256'],true164_bundle=m['new_true164_bundle'],Source_new_payload_writes=0,Share_new_payload_writes=0,Source_sender='readonly files to verified direct SSH socket',Target_receiver='bounded memory to genuine164 only',native_restore=restoration['status'],old_Share40GiB_policy_changed=False,SSD_RAM_identity_and_live_science_gates='independently enforced on both ends',raw_chunk_max_bytes=c.CHUNK,staging_max_bytes=256*c.MIB,single_stream=True,sender_rate_bytes_per_second=c.RATE,aggregate_data_rate_limit_bytes_per_second=30*c.MIB)
                persist(TASK/'control/ZERO_SHARE_QUALIFICATION.json',qualification);c.publish_bytes(NAS/'control/ZERO_SHARE_QUALIFICATION.json',c.canon(qualification),c.v9())
        except Exception as e:
            holds+=1;record=dict(status='HOLD_EXACT_ASSET',asset_id=scope['asset_id'],kind=scope['kind'],reason=str(e),traceback=traceback.format_exc(),elapsed_seconds=time.time()-started,unix=time.time(),source_disposition='KEEP',new_scientific_starts=0)
            append(record);update(force=True,phase='ASSET_HOLD',last_hold=record,held_assets=holds)
            print(json.dumps(record),flush=True)
            if index==0:raise RuntimeError('ZERO_SHARE_PILOT_NOT_QUALIFIED '+str(e))
            if isinstance(e,BlockingIOError) or any(x in str(e) for x in ['RESOURCE_HOLD','OTHER_EXISTING_ARCHIVE_LOCK_HELD','CURRENT_SCIENCE_','SOURCE_LIVE_DTC_OWNER','UNKNOWN_SOURCE_ACTIVE_WRITE_RESERVATION','SOURCE_POLICY_IDENTITY_HOLD','NOT_TRUE164_TARGET_HOLD','ENDPOINT_IDENTITY_HOLD']):
                # Do not turn a transient common gate into115 repeated failed
                # attempts. Preserve the finite runner state for same-identity
                # resource repair or authorized verified-copy retirement.
                update(force=True,phase='COMMON_RESOURCE_HOLD',completed_assets=complete,held_assets=holds);return
    update(force=True,phase='FINITE_QUEUE_PASS_ENDED',completed_assets=complete,held_assets=holds,total_new_transferred_bytes=transferred)

if __name__=='__main__':
    # Extra process exclusion only; existing transfer locks and transaction
    # identities remain authoritative. Never replace or unlink lock files.
    driver_lock=(TASK/'control/DRIVER.lock').open('a+b')
    fcntl.flock(driver_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:
        main()
        update(force=True,driver_exit_observed=True,driver_exit_code=0)
    except Exception as e:
        update(force=True,phase='DRIVER_HOLD',driver_exit_observed=True,driver_exit_code=1,error=str(e),traceback=traceback.format_exc());raise

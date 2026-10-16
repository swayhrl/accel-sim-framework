"""Receive one bounded PolyBench archive range; never releases source.

Default is read-only validation. Verified ranges append to one exclusively
owned partial archive. Only complete, gap-free whole SHA256 permits finalizing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time
from archive_receiver import ARCHIVE, BRIDGE, LIMIT, SHARE_FLOOR, require, beneath, mkdirs, sha, atomic_json, check_resources, now

SPEC = dict(id='polybench_9feffb121c30', size=17943970556, payload=524288000,
    sha256='9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca',
    source='/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz',
    final='Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz')

def validate_scope(scope,proof):
    require(re.fullmatch('[0-9a-f]{40}',proof.get('commit','')) is not None and proof.get('github_readback_verified') is True,
            'source GitHub scope proof missing')
    require(scope['source_archive_path']==SPEC['source'] and scope['source_archive_size_bytes']==SPEC['size']
            and scope['source_archive_sha256']==SPEC['sha256'], 'wrong whole archive scope')
    require(scope['source_action']=='SOURCE_KEEP' and scope['source_release_authorized'] is False and
            scope['owner_authorization']=='COPY_OK_ONLY' and scope['owner'] and
            scope['no_active_readers_or_writers'] is True and scope['original_archive_retained'] is True and
            scope['both_closeout_stage_roots_retained'] is True, 'source copy scope is not qualified')

def validate(data, scope, proof):
    validate_scope(scope,proof)
    require(data.get('schema') == 'STORAGE_OPS_V7_ARCHIVE_RANGE_READY', 'wrong range schema')
    require(re.fullmatch('[0-9a-f]{40}', proof.get('commit','')) is not None and
            proof.get('github_readback_verified') is True, 'source scope GitHub proof missing')
    require(data['source_receipt_commit'] == proof['commit'] and
            data['source_scope_sha256'] == proof['receipt_sha256'], 'source scope publication mismatch')
    for obj in [data, scope]:
        require(obj['source_archive_path'] == SPEC['source'] and obj['source_archive_size_bytes'] == SPEC['size']
                and obj['source_archive_sha256'] == SPEC['sha256'], 'wrong frozen archive')
        require(obj['source_action'] == 'SOURCE_KEEP' and obj['source_release_authorized'] is False,
                'range transfer cannot authorize original science release')
    require(scope['owner_authorization'] == 'COPY_OK_ONLY' and scope['owner'] and
            scope['no_active_readers_or_writers'] is True and scope['original_archive_retained'] is True and
            scope['both_closeout_stage_roots_retained'] is True, 'copy scope/consumer protection incomplete')
    require(data['source_archive_identity'] == scope['source_archive_identity'] and
            data['source_archive_identity_rechecked_before_after_stage'] is True,
            'original archive stability evidence missing')
    identity = data['source_archive_identity']
    require(identity['device'] == 156 and identity['nlink'] == 1 and identity['size_bytes'] == SPEC['size']
            and identity['inode'] > 0, 'source namespace/identity mismatch')
    count = (SPEC['size'] + SPEC['payload'] - 1) // SPEC['payload']
    index = data['chunk_index']
    require(type(index) is int and 0 <= index < count and data['chunk_count'] == count, 'range ordinal/count')
    offset = index * SPEC['payload']; length = min(SPEC['payload'], SPEC['size'] - offset)
    require(data['offset_bytes'] == offset and data['length_bytes'] == length <= LIMIT, 'overlap/gap/oversize range')
    batch = 'PB_CHUNK_' + str(index).zfill(3)
    require(data['batch_id'] == batch and data['project'] == 'Decoupled-L2', 'wrong archive batch/project')
    require(data['bridge_root'] == str(BRIDGE) and data['destination_archive_root'] == str(ARCHIVE)
            and data['final_destination_relative_path'] == SPEC['final'], 'range root/map mismatch')
    require(data['bridge_path'] == str(BRIDGE / batch / 'files' / 'payload.bin'), 'unsafe range bridge path')
    require(re.fullmatch('[0-9a-f]{64}', data['source_range_sha256']) is not None and
            data['source_range_sha256'] == data['bridge_sha256'] and
            data['bridge_reopened_sha256_verified'] is True, 'range source/bridge hash mismatch')
    return batch, offset, length

def range_sha(path, offset, length):
    require(path.resolve() == path and not path.is_symlink(), 'noncanonical archive range path')
    h=hashlib.sha256()
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
        require(os.fstat(stream.fileno()).st_size >= offset+length, 'archive range is truncated')
        stream.seek(offset); left=length
        while left:
            raw=stream.read(min(left,4*1024**2));require(raw,'short archive range read')
            h.update(raw);left-=len(raw)
    return h.hexdigest()

def write_owned_state(path, state):
    require(state['owner']=='Storage-Ops' and state['archive_id']==SPEC['id'], 'wrong journal owner')
    if path.exists():
        old=json.loads(path.read_text());require(old['owner']==state['owner'] and old['archive_id']==state['archive_id'], 'unowned journal')
    require(path.resolve()==path, 'journal symlink')
    tmp=path.with_name(path.name+'.tmp-'+str(os.getpid()))
    with tmp.open('x') as f:json.dump(state,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def receive(data, digest, scope, proof, resume=False, rate=30*1024**2):
    import fcntl
    batch,offset,length=validate(data,scope,proof)
    ready_path=BRIDGE/(batch+'_READY.json')
    require(hashlib.sha256(ready_path.read_bytes()).hexdigest()==digest,'range READY changed before receive')
    resources=check_resources()
    lock=os.open(BRIDGE/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW)
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        final=ARCHIVE/SPEC['final'];partial=final.with_name(final.name+'.storageops-owned-partial')
        folder=ARCHIVE/'infrastructure/archive_range_journals';mkdirs(ARCHIVE,folder)
        journal=folder/(SPEC['id']+'.json')
        receipt_folder=ARCHIVE/'infrastructure/archive_range_receipts'/SPEC['id'];mkdirs(ARCHIVE,receipt_folder)
        receipt_path=receipt_folder/(batch+'_DEST_VERIFIED.json')
        if receipt_path.exists():
            existing=json.loads(receipt_path.read_text())
            require(existing['source_ready_sha256']==digest,'different manifest for existing range')
            path=final if final.exists() else partial
            require(range_sha(path,offset,length)==data['source_range_sha256'],'verified range changed')
            marker=BRIDGE/(batch+'_DEST_VERIFIED.json')
            if not marker.exists():atomic_json(marker,existing)
            else:require(json.loads(marker.read_text())==existing,'range receipt conflict')
            return dict(existing,new_received_range_bytes=0,idempotent_existing_range_verified=True)
        bridge=beneath(BRIDGE,data['bridge_path']);h,bridge_stat=sha(bridge)
        require(h==data['source_range_sha256'] and bridge_stat['size']==length,'bridge range changed')
        require(bridge_stat['nlink']==1 and bridge_stat['dev']==BRIDGE.stat().st_dev,'unqualified bridge link/filesystem')
        require(set(BRIDGE.glob('*/files'))=={bridge.parent},'another forward/reverse bridge batch is active')
        require(resources['share_available_bytes']>=SHARE_FLOOR,'Share below original floor')
        require(resources['archive_available_bytes']>=SPEC['size']-offset,'archive capacity below remaining file')
        if journal.exists():
            beneath(ARCHIVE,journal)
            state=json.loads(journal.read_text())
            require(state['owner']=='Storage-Ops' and state['archive_id']==SPEC['id'] and
                    state['source_scope_sha256']==proof['receipt_sha256'] and
                    state['source_archive_identity']==data['source_archive_identity'] and
                    state['final_path']==str(final) and state['whole_sha256']==SPEC['sha256'], 'archive journal scope mismatch')
        else:
            require(offset==0 and not resume and not os.path.lexists(final) and not os.path.lexists(partial),
                    'unowned existing destination or missing predecessor journal')
            state=dict(owner='Storage-Ops',archive_id=SPEC['id'],final_path=str(final),whole_sha256=SPEC['sha256'],
                source_scope_sha256=proof['receipt_sha256'],source_archive_identity=data['source_archive_identity'],
                verified_ranges=[],next_offset=0,created_at_utc=now(),all_destinations_absent_before_start=True)
            mkdirs(ARCHIVE,final.parent);write_owned_state(journal,state)
        recovered=state['next_offset']==offset+length and len(state['verified_ranges'])==data['chunk_index']+1
        if recovered:
            require(state['verified_ranges'][-1]['source_ready_sha256']==digest and
                    range_sha(partial,offset,length)==data['source_range_sha256'], 'owned completed range mismatch')
        else:
            require(state['next_offset']==offset and len(state['verified_ranges'])==data['chunk_index'], 'out-of-order archive range')
        require(not os.path.lexists(final),'canonical final already exists; refuse overwrite')
        if not partial.exists():
            require(offset==0,'owned partial archive missing')
            fd=os.open(partial,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
        beneath(ARCHIVE,partial)
        size=partial.stat().st_size
        require(recovered or size==offset or (resume and offset<=size<=offset+length), 'partial tail needs explicit owned --resume')
        # Only an unverified tail in this task-owned archive may be replaced.
        if not recovered:
            started=time.monotonic();copied=0
            with os.fdopen(os.open(partial,os.O_RDWR|os.O_NOFOLLOW),'r+b') as output:
                output.truncate(offset);output.seek(offset)
                with bridge.open('rb') as source:
                    while copied<length:
                        raw=source.read(min(4*1024**2,length-copied));require(raw,'short bridge payload')
                        output.write(raw);copied+=len(raw)
                        if rate:
                            delay=copied/rate-(time.monotonic()-started)
                            if delay>0:time.sleep(delay)
                output.flush();os.fsync(output.fileno())
        require(sha(bridge)[1]==bridge_stat,'bridge identity changed during range copy')
        require(partial.stat().st_size==offset+length and range_sha(partial,offset,length)==data['source_range_sha256'],
                'closed/reopened SSHFS range mismatch')
        record=dict(index=data['chunk_index'],offset_bytes=offset,length_bytes=length,sha256=data['source_range_sha256'],source_ready_sha256=digest)
        require(hashlib.sha256(ready_path.read_bytes()).hexdigest()==digest,'range READY changed during receive')
        if not recovered:
            state['verified_ranges'].append(record);state['next_offset']=offset+length
            write_owned_state(journal,state)
        result=dict(schema='STORAGE_OPS_V7_ARCHIVE_RANGE_DEST_VERIFIED',status='RANGE_DEST_VERIFIED',batch_id=batch,
            project='Decoupled-L2',verified_at_utc=now(),source_ready_sha256=digest,source_scope_publication=proof,
            source_archive_path=SPEC['source'],source_archive_size_bytes=SPEC['size'],source_archive_sha256=SPEC['sha256'],
            chunk_index=data['chunk_index'],chunk_count=data['chunk_count'],offset_bytes=offset,length_bytes=length,
            source_range_sha256=h,bridge_sha256=h,destination_range_sha256=h,bridge_path=str(bridge),bridge_identity=bridge_stat,
            partial_archive_path=str(partial),final_archive_path=str(final),received_verified_component_bytes=state['next_offset'],
            whole_archive_dest_verified=False,source_action='SOURCE_KEEP',original_source_released_bytes=0,
            source_release_authorized=False,new_received_range_bytes=0 if recovered else length,
            recovered_owned_journal_without_data_transfer=recovered,verification_level='SSHFS_READBACK_VERIFIED',native_164_verified=False)
        atomic_json(receipt_path,result);atomic_json(BRIDGE/(batch+'_DEST_VERIFIED.json'),result)
        return result
    finally:
        os.close(lock)

def finalize(scope, proof):
    import fcntl
    validate_scope(scope,proof)
    check_resources();lock=os.open(BRIDGE/'.TARGET_RECEIVER.lock',os.O_RDWR|os.O_NOFOLLOW)
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        require(not any(BRIDGE.glob('*/files')),'one active bridge batch still exists')
        state_path=ARCHIVE/'infrastructure/archive_range_journals'/(SPEC['id']+'.json')
        state=json.loads(state_path.read_text());final=ARCHIVE/SPEC['final'];partial=final.with_name(final.name+'.storageops-owned-partial')
        require(state['owner']=='Storage-Ops' and state['source_scope_sha256']==proof['receipt_sha256'] and
                state['next_offset']==SPEC['size'],'whole archive coverage incomplete')
        count=(SPEC['size']+SPEC['payload']-1)//SPEC['payload']
        require(len(state['verified_ranges'])==count,'wrong complete range count')
        for i,r in enumerate(state['verified_ranges']):
            require(r['index']==i and r['offset_bytes']==i*SPEC['payload'] and
                    r['length_bytes']==min(SPEC['payload'],SPEC['size']-r['offset_bytes']), 'gap/overlap in archive journal')
        require(state['all_destinations_absent_before_start'] is True and state['final_path']==str(final)
                and state['whole_sha256']==SPEC['sha256'],'unowned finalization')
        existing=final.exists()
        require(not existing or not os.path.lexists(partial),'both final and partial exist; never overwrite')
        source=final if existing else partial
        require(source.stat().st_size==SPEC['size'] and range_sha(source,0,SPEC['size'])==SPEC['sha256'],
                'full closed/reopened archive SHA256 mismatch')
        if not existing:os.rename(partial,final)
        receipt_path=ARCHIVE/'infrastructure/project_receipts/POLYBENCH_WHOLE_ARCHIVE_DEST_VERIFIED.json'
        marker=BRIDGE/'POLYBENCH_WHOLE_ARCHIVE_DEST_VERIFIED.json'
        if receipt_path.exists():
            previous=json.loads(receipt_path.read_text())
            require(previous['destination_sha256']==SPEC['sha256'] and previous['size_bytes']==SPEC['size'], 'whole receipt mismatch')
            if not marker.exists():atomic_json(marker,previous)
            else:require(json.loads(marker.read_text())==previous,'whole bridge receipt mismatch')
            return dict(previous,idempotent_existing_whole_archive_verified=True,new_primary_archived_bytes=0)
        result=dict(schema='STORAGE_OPS_V7_WHOLE_ARCHIVE_DEST_VERIFIED',status='WHOLE_ARCHIVE_DEST_VERIFIED',
            verified_at_utc=now(),project='Decoupled-L2',source_path=SPEC['source'],destination_path=str(final),
            size_bytes=SPEC['size'],source_sha256=SPEC['sha256'],destination_sha256=SPEC['sha256'],
            components=count,component_receipts_root=str(ARCHIVE/'infrastructure/archive_range_receipts'/SPEC['id']),
            primary_archived_bytes=SPEC['size'],source_action='SOURCE_KEEP',source_released_bytes=0,
            verification_level='SSHFS_READBACK_VERIFIED',native_164_verified=False,source_scope_publication=proof,
            restore_status='PENDING_INDEPENDENT_BOUNDED_REVERSE_AND_STAGE_MEMBER_RECOVERY')
        mkdirs(ARCHIVE,receipt_path.parent)
        atomic_json(receipt_path,result);atomic_json(marker,result)
        return result
    finally:os.close(lock)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest');p.add_argument('--expected-ready-sha256')
    p.add_argument('--source-scope-proof',required=True);p.add_argument('--receive',action='store_true')
    p.add_argument('--resume',action='store_true');p.add_argument('--finalize',action='store_true');args=p.parse_args()
    proof=json.loads(Path(args.source_scope_proof).read_text());scope_raw=(BRIDGE/'POLYBENCH_SOURCE_COPY_SCOPE.json').read_bytes()
    require(hashlib.sha256(scope_raw).hexdigest()==proof['receipt_sha256'],'source copy scope changed');scope=json.loads(scope_raw)
    validate_scope(scope,proof)
    if args.finalize:
        require(not args.receive and not args.manifest,'finalize is a separate sole pipeline phase');print(json.dumps(finalize(scope,proof)));return
    require(args.manifest and args.expected_ready_sha256,'explicit pinned range READY required')
    raw=Path(args.manifest).read_bytes();digest=hashlib.sha256(raw).hexdigest();require(digest==args.expected_ready_sha256,'range READY changed')
    data=json.loads(raw);batch,offset,length=validate(data,scope,proof)
    result=receive(data,digest,scope,proof,args.resume) if args.receive else dict(mode='READ_ONLY_RANGE_PLAN',batch_id=batch,offset_bytes=offset,length_bytes=length,data_written=0,source_action='SOURCE_KEEP')
    require(hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest()==digest,'range READY changed during execution')
    print(json.dumps(result))

if __name__=='__main__':main()

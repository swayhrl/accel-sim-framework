"""Complete an already-copied exact stage after a post-copy gate HOLD.

Never creates, truncates, retries or removes a payload. Fresh source/request,
per-range close/reopen SHA, all identities and both resource gates are required.
The original qualified runner still publishes the resulting immutable READY.
"""
import fcntl
import hashlib
import os
from pathlib import Path
import stat

import tls_v10_p9_exact_window_runner as r
import tls_v10_p9_grouped_source_range as sender

def verify_complete_stage(directory, rows, expected_shas):
    r._require(directory.resolve(strict=True) == directory, 'stage parent symlink')
    r._require({x.name for x in directory.iterdir()} ==
               {'range-%04d.bin' % i for i in range(len(rows))}, 'stage membership mismatch')
    entries=[]
    for i,row in enumerate(rows):
        path=directory/('range-%04d.bin'%i)
        before=os.lstat(path)
        r._require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
                   before.st_size==row['length'] and before.st_mode&0o777==0o600 and
                   before.st_uid==os.getuid() and before.st_gid==os.getgid(),
                   'incomplete/foreign staged payload')
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            r._require(sender._fingerprint(os.fstat(fd))==sender._fingerprint(before), 'stage open drift')
            h=hashlib.sha256()
            while True:
                chunk=os.read(fd,r.MIB)
                if not chunk:break
                h.update(chunk)
            r._require(sender._fingerprint(os.fstat(fd))==sender._fingerprint(before) and
                       sender._fingerprint(os.lstat(path))==sender._fingerprint(before), 'stage changed during read')
        finally:os.close(fd)
        r._require(h.hexdigest()==expected_shas[i], 'stage/source range SHA mismatch')
        entries.append({'relative_path':row['relative_path'],'offset':row['offset'],
                        'length':row['length'],'source_identity':row['source_identity'],
                        'source_full_sha256':row['original_sha256'],'chunk_sha256':h.hexdigest(),
                        'bridge_path':str(path),'bridge_identity':sender._fingerprint(before)})
    r._require(sum(e['bridge_identity']['allocated'] for e in entries)<=256*r.MIB,'stage allocation cap')
    return entries

def finish(controller):
    ctx=controller.ctx
    binding=r._json(controller.binding_path.read_bytes())
    r._require(binding['window_id']=='TLS_V10_P9_PUBLIC_B0010' and
               binding.get('one_shot_coordination_commit')=='3a7ea422d3f4301688bd3cb7bcf4431b97f08e90',
               'only the exact one-shot B0010 adoption')
    return _finish(controller)

CANONICAL_AMENDMENT='9f1a21a909e437f1e34233b22595d0f7359f3dd3'

def check_followup_binding(binding, source_notice, target_adoption):
    match=r.WINDOW_RE.fullmatch(binding.get('window_id',''))
    r._require(match is not None and 11<=int(match[1])<=33 and
               binding.get('plan_batch_index')==int(match[1])-1 and
               binding.get('txid')==r.old.TXID and binding.get('selector_sha256')==r.old.SELECTOR and
               binding.get('source_root')==r.old.SOURCE_ROOT and
               binding.get('canonical_manifest_sha256')==r.old.MANIFEST_SHA256,
               'not original frozen P9 followup11..33')
    r._require(source_notice.get('canonical_approval_commit')==CANONICAL_AMENDMENT and
               source_notice.get('source_adopts_exact_commit') is True and
               target_adoption.get('canonical_approval_commit')==CANONICAL_AMENDMENT and
               target_adoption.get('status')=='S_AND_T_SAME_CANONICAL_USER_APPROVAL_COMMIT_ADOPTED',
               'joint canonical user amendment missing')

def finish_followup(controller):
    ctx=controller.ctx;binding=r._json(controller.binding_path.read_bytes())
    sn='TLS_V10_USER_NATIVE_RESTORE_AMENDMENT_20261019_SOURCE_NOTICE.json'
    sr=r._source_git_raw(ctx.source_repo,'f893eb33bd77b6452944c38a4b0ff42d1fd42404',ctx.receipt_dir/sn)
    r._require(sr==(ctx.receipt_dir/sn).read_bytes(),'Source canonical amendment raw drift')
    tn='TLS_V10_TARGET_SAME_COMMIT_LOCATION_ADOPTION_V1.json'
    tr=r._git_raw(ctx.target_repo,'12461d1c26cd4310f63b136e60c5315a318fbc8a',r.TARGET_RECEIPTS+tn)
    r._require(tr==(ctx.bridge/tn).read_bytes(),'Target canonical amendment raw drift')
    check_followup_binding(binding,r._json(sr),r._json(tr))
    return _finish(controller)

def _finish(controller):
    ctx=controller.ctx;binding=r._json(controller.binding_path.read_bytes())
    pass_path,ready_path,bridge_ready=r._window_paths(ctx,binding['window_id'])
    r._require(not ready_path.exists() and not bridge_ready.exists(),'READY already exists')
    lock=os.open(ctx.bridge/'.TLS_V10_SOURCE_SENDER.lock',os.O_RDWR|os.O_NOFOLLOW)
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        inspected=controller._inspect(stage_must_be_absent=False)
        pinned=r._json(pass_path.read_bytes())
        for key in ['binding_sha256','request_sha256','target_receiver_preflight_sha256','fresh_range_sha256']:
            r._require(pinned[key]==inspected[key],'prepare/stage identity drift: '+key)
        r._require(pinned['runner_code_sha256']==r.sha(Path(r.__file__).read_bytes()) and
                   pinned['status']=='PASS_NOT_READY_NO_STAGE','prepare code/state drift')
        rows=inspected['request']['ranges']
        # Existing complete payloads only; physical reserve was already spent.
        entries=verify_complete_stage(inspected['stage_root'],rows,inspected['fresh_range_sha256'])
        physical=sum(e['bridge_identity']['allocated'] for e in entries)
        before=controller._gate(inspected,staged_physical=physical)
        after_inspected=controller._inspect(stage_must_be_absent=False)
        r._require(after_inspected['fresh_range_sha256']==inspected['fresh_range_sha256'],'post-source SHA drift')
        r._require(verify_complete_stage(inspected['stage_root'],rows,after_inspected['fresh_range_sha256'])==entries,
                   'post-stage identity drift')
        after=controller._gate(after_inspected,staged_physical=physical)
        ready={'schema':'TLS_V10_OLD174_GROUPED_RAW_READY_V1','status':'READY_SOURCE_KEEP',
               'window_id':binding['window_id'],'group':r.old.GROUP,'txid':r.old.TXID,
               'selector_sha256':r.old.SELECTOR,'canonical_manifest_sha256':r.old.MANIFEST_SHA256,
               'target_window_git_commit':binding['target_request_git_commit'],
               'target_window_sha256':inspected['request_sha256'],
               'prior_cleanup_sha256':binding['prior_cleanup_sha256'],
               'target_root_native164':r.old.TARGET_ROOT,'source_repo':r.old.SOURCE_REPO,
               'source_branch':r.old.SOURCE_BRANCH,'source_root':str(ctx.source_root),
               'source_frozen_commit':inspected['request']['source_frozen_commit'],
               'source_namespace':r.old.SOURCE_NAMESPACE,'source_dev':r.old.SOURCE_DEV,
               'policy_id':r.policy.POLICY_ID,'source_gate_sha256':r.sha(pass_path.read_bytes()),
               'source_sender_code_sha256':r.sha(Path(r.__file__).read_bytes()),
               'source_range_primitive_sha256':r.sha(Path(sender.__file__).read_bytes()),
               'source_protocol_adoption_sha256':r.sha(r.ADOPTION.read_bytes()),
               'gate_before_stage':before,'gate_after_stage':after,'entries':entries,
               'range_count':len(entries),'raw_bytes':sum(e['length'] for e in entries),
               'bridge_payload_allocated_bytes':physical,'source_originals':'SOURCE_KEEP',
               'source_files_unlinked':0,'complete_group_archived':False,'complete_group_native_restored':False,
               'post_stage_recovery_code_sha256':r.sha(Path(__file__).read_bytes()),
               'recovery_payload_bytes_rewritten':0,'recovery_reason':'copied stage preserved after post-copy gate HOLD; fresh complete verification and both actual gates now passed'}
        return {'path':str(ready_path),'sha256':r._no_clobber_json(ready_path,ready)}
    finally:os.close(lock)

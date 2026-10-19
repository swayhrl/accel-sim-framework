#!/usr/bin/env python3
"""Bind fresh visible controls/FLOCKs to fixed, reviewed output-only identities."""
from common import *
from audit_site import proc
import argparse

OLD=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')
CONT='continuations/USER_RECHECK_20261018T030133Z/AUTHORITY_AND_FLOCK_AUDIT.json'


def review(snapshot_data,own_owner=None,ownership=None):
    historic=json.loads(blob(FW_REPO,AA5,AA5_PACK+'/'+CONT))
    known={p['pid']:p for p in historic['reviewed_other_controls']}
    sources=[]
    source_names=set()
    for h in historic['source_review']:
        path=Path(h['path'])
        actual=sha(path)
        assert actual==h['sha256'], 'Output-only source changed; no authority closure: '+str(path)
        source_names.add(path.name)
        sources.append(dict(path=str(path),expected_sha256=h['sha256'],actual_sha256=actual,
            classification='PUBLISHED_AA5_REVIEW_PLUS_CURRENT_SHA_MATCH_OUTPUT_ONLY_CALLEES',
            source_review_commit=AA5,execution_review=h['execution_review']))
    controls=[];unknown=[];foreign=[];own=[];pending=[]
    processes=snapshot_data['processes']
    for p in processes:
        args=p.get('argv',[])
        if p['is_simulator']:
            classification=ownership.classify(p) if ownership else 'UNKNOWN'
            if classification=='CONFIRMED':
                own.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],classification='OWN_PTRACE_EVENT_CONFIRMED_INSTANCE'));continue
            if classification=='PENDING':
                pending.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],classification='PENDING_QUARANTINED_NO_AUTHORITY_PASS'));continue
            if own_owner and p['pid']==own_owner.get('child_pid') and p['start_ticks']==own_owner.get('child_start_ticks'):
                own.append(dict(pid=p['pid'],classification='OWN_REGISTERED_AG_SIMULATOR'));continue
            # External EP-L2 is an independently authorized project; its actual
            # CPU/RSS/IO remains in the all-process/cgroup resource population.
            if p['exe'].startswith('/workspace/ep_l2_'):
                foreign.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],exe=p['exe'],classification='EXTERNAL_EP_L2_RESOURCE_COUNTED'))
            else:
                unknown.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],argv=args,classification='UNCLASSIFIED_OR_DTC_SIMULATOR_STOP'))
            continue
        if not args:
            continue
        actual=[a for a in args if '\n' not in a and len(a)<4096]
        scripts=[]
        for a in actual:
            if not a.endswith(('.py','.sh')):continue
            q=Path(a) if a.startswith('/') else Path(p['cwd'])/a
            if q.is_file() and '/dtc_l1/' in str(q):scripts.append(q)
        oldmatch=p['cwd']==str(OLD) or any(a==str(OLD) or a.startswith(str(OLD)+'/') for a in actual)
        if not oldmatch and not scripts:
            continue
        if any(str(PACK) in str(q) for q in scripts):
            own.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],classification='OWN_AG_CPU_OR_REGISTERED_RUNNER'))
            continue
        if p['pid'] in known and p['start_ticks']==known[p['pid']]['start_ticks'] and args==known[p['pid']]['argv']:
            controls.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],classification='EXACT_PUBLISHED_OUTPUT_ONLY_CONTROLLER',future_simulator_dispatch=False))
        elif scripts and all(q.name in source_names for q in scripts):
            controls.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],classification='HASH_REVIEWED_OUTPUT_ONLY_HELPER',future_simulator_dispatch=False))
        else:
            unknown.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],argv=args,scripts=list(map(str,scripts)),classification='UNKNOWN_DTC_CONTROL_STOP'))
    bypid={p['pid']:p for p in processes};reviewed={p['pid'] for p in controls}
    external=json.loads((PACK/'EXTERNAL_PROJECT_LOCK_BINDING.json').read_text())
    ext_live=proc(external['pid'])
    ext_ok=bool(ext_live and ext_live['start_ticks']==external['start_ticks'] and
        ext_live['cwd']==external['cwd'] and
        [v for v in Path('/proc',str(external['pid']),'cmdline').read_bytes().split(b'\0') if v]==[v.encode() for v in external['argv']] and
        sha(external['script'])==external['script_sha256'])
    locks=[]
    for lock in snapshot_data['FLOCKs']:
        if not any(k in lock['path'].lower() for k in ['dtc','fast64','lane']):continue
        p=bypid.get(lock['pid']);output=lock['pid'] in reviewed
        if p and p['comm']=='sleep' and p['ppid'] in reviewed:output=True
        own_ok=bool(own_owner and lock['path']==str(RAW/'AG_execution.lock') and lock['pid']==own_owner.get('pid') and lock['start_ticks']==own_owner.get('start_ticks'))
        external_ok=bool(ext_ok and lock['pid']==external['pid'] and lock['start_ticks']==external['start_ticks'] and lock['path']==external['lock'])
        locks.append(dict(**lock,output_only_collector=output,own_AG_execution=own_ok,external_EP_L2_resource_counted=external_ok))
    identities=snapshot_data['known_identity_checks']
    checks=dict(AA5_original_PID_instances_terminal=not any(r['same_instance_live'] for r in identities if r['role']=='AA5'),
        retired_auto_dispatcher_instance_absent=not any(r['same_instance_live'] for r in identities if r['role']=='OLD_AUTODISPATCHER'),
        retired_deferred_parent_absent=proc(3291777) is None,
        no_unknown_DTC_dispatch_authority_or_simulator=not unknown,
        all_DTC_FLOCK_holders_source_reviewed_or_own_AG=all(r['output_only_collector'] or r['own_AG_execution'] or r['external_EP_L2_resource_counted'] for r in locks),
        no_retired_Core41_auto_dispatch_FLOCK=not any('autodispatch_v1.lock' in r['path'] for r in locks))
    return dict(status=('PENDING_QUARANTINED_NO_AUTHORITY_PASS' if pending or (ownership and ownership.pending) else 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY') if all(checks.values()) else 'STOP_AUTHORITY_NOT_CLOSED',
        pending_quarantined=pending,
        utc=now(),checks=checks,reviewed_controls=controls,unknown_controls=unknown,foreign_projects=foreign,
        own_AG_processes=own,remaining_DTC_FLOCKs=locks,source_review=sources,
        AA5_published_commit=AA5,AA5_actual_starts=1,AA5_complete_strict_passes=0,
        foreign_signals=0,foreign_lock_acquisitions=0,old_files_modified=0)


def main(label):
    path=RAW/'site-audits'/label/'SECOND.json'
    snapshot_data=json.loads(path.read_text())
    result=review(snapshot_data)
    write(PACK/'AUTHORITY_AND_FLOCK_REVIEW.json',dict(**result,source_snapshot=str(path),source_snapshot_sha256=sha(path)))
    print(json.dumps(dict(status=result['status'],checks=result['checks'],unknown_controls=result['unknown_controls'],DTC_FLOCKs=len(result['remaining_DTC_FLOCKs']))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);main(p.parse_args().label)

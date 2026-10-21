#!/usr/bin/env python3
"""E2 foreground approved-record relay. Dry-run unless --publish is explicit.

Verifies labels and immutable metadata references, not the user's identity,
meaning of approval, scientific qualification or permission to run an experiment.
"""
from pathlib import Path
import argparse, contextlib, fcntl, importlib.util, io, json, os, re, sys, uuid
import coordination as transport

ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
PROTOCOL=ROOT/'docs/ep_l2/lane_collaboration_v1'
ALIAS_ROOTS=(Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/events'),Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/inbox'),Path('/workspace/ep_l2_ms20261019_shared'))
PACKET_SCHEMA='E2_APPROVED_RELAY_PACKET_V1'
APPROVAL_SCHEMA='E2_APPROVED_RELAY_AUTHORIZATION_V1'
PACKET_FIELDS={'schema','dispatch_id','recipients','task_ids','scope','subject','body','refs'}
APPROVAL_FIELDS={'schema','user_message_verbatim','approved_packet_path','approved_packet_sha256','approved_recipients','approved_task_ids','approved_scope','approval_kind'}
require=transport.require


def remote_head(client):
    branch=client.contract['lanes']['E2']['branch'];lines=transport.git(client.root,'ls-remote','--exit-code','origin','refs/heads/'+branch).decode().splitlines()
    require(len(lines)==1,'remote E2 branch readback missing/ambiguous');head,name=lines[0].split()
    require(transport.HEX40.fullmatch(head) and name=='refs/heads/'+branch,'invalid remote branch readback');return head


def published_metadata(client,ref,head):
    client.validate_ref(ref)
    require(ref['repo']==client.contract['repository']['full_name'] and ref['path'].startswith('docs/ep_l2/') and ref['path'].endswith('.json'),'relay accepts same-repository EP-L2 JSON metadata only')
    transport.git(client.root,'merge-base','--is-ancestor',ref['commit'],head)
    raw=client.blob(ref['commit'],ref['path'],65536);require(transport.sha(raw)==ref['sha256'],'published metadata SHA mismatch')
    return json.loads(raw)


def prepare(client,packet_ref,approval_ref):
    require(client.lane=='E2' and client.root.resolve()==ROOT.resolve(),'relay is only for the original E2 worktree')
    head=remote_head(client);packet=published_metadata(client,packet_ref,head);approval=published_metadata(client,approval_ref,head)
    require(isinstance(packet,dict) and set(packet)==PACKET_FIELDS and packet['schema']==PACKET_SCHEMA,'unknown packet schema/fields')
    require(isinstance(approval,dict) and set(approval)==APPROVAL_FIELDS and approval['schema']==APPROVAL_SCHEMA,'unknown approval schema/fields')
    require(re.fullmatch(r'[a-z0-9_-]{1,64}',packet['dispatch_id']) is not None,'invalid dispatch ID')
    recipients=packet['recipients'];tasks=packet['task_ids']
    require(isinstance(recipients,list) and recipients and len(recipients)==len(set(recipients)) and set(recipients)<=set(client.contract['lanes'])-{'E2'},'invalid approved recipients')
    require(isinstance(tasks,list) and 0<len(tasks)<=32 and all(isinstance(x,str) and 0<len(x)<=120 for x in tasks) and len(tasks)==len(set(tasks)),'invalid approved task IDs')
    require(isinstance(packet['scope'],str) and 0<len(packet['scope'])<=2000 and isinstance(packet['subject'],str) and 0<len(packet['subject'])<=200,'invalid packet scope/subject')
    require(isinstance(approval['user_message_verbatim'],str) and 0<len(approval['user_message_verbatim'])<=16000,'approval requires the transcribed original user words')
    require(approval['approval_kind'] in ('COORDINATION_RELAY_ONLY','USER_APPROVED_TASK_PACKET'),'unknown approval kind')
    require(approval['approved_packet_path']==packet_ref['path'] and approval['approved_packet_sha256']==packet_ref['sha256'],'approval binds a different packet')
    require(approval['approved_recipients']==recipients and approval['approved_task_ids']==tasks and approval['approved_scope']==packet['scope'],'recipient/task/scope differs from recorded approval')
    require(isinstance(packet['refs'],list) and len(packet['refs'])<=30,'packet references exceed event allowance')
    for ref in packet['refs']:client.validate_ref(ref)
    body=dict(dispatch_id=packet['dispatch_id'],approval_kind=approval['approval_kind'],approved_scope=packet['scope'],approved_task_ids=tasks,packet_body=packet['body'],record_validation='EXACT_REFERENCE_AND_FIELD_MATCH_ONLY_NOT_HUMAN_AUTHENTICATION_OR_SCIENTIFIC_AUTHORITY')
    refs=[packet_ref,approval_ref]+packet['refs']
    require(len(json.dumps(body,ensure_ascii=False))<=client.limits['max_body_characters'],'relay body exceeds bounded event size')
    return dict(dispatch_id=packet['dispatch_id'],packet_ref=packet_ref,approval_ref=approval_ref,recipients=recipients,task_ids=tasks,subject='Approved relay: '+packet['subject'],body=body,refs=refs)


def publisher():
    path=ROOT/'docs/ep_l2/review_packs/MS20261020_E2_TAKEOVER_r1/publish.py'
    spec=importlib.util.spec_from_file_location('original_e2_publisher',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def publish_exact(pub,title,paths):
    """Reuse original publisher; resume an already committed failed push safely."""
    names=[str(Path(p).resolve().relative_to(ROOT)) for p in paths]
    require(all(n.startswith('docs/ep_l2/lane_collaboration_v1/') for n in names),'publication escaped relay metadata')
    require(set(pub.git('diff','--cached','--name-only').decode().splitlines())<=set(names),'unrelated staged work; serialize original E2 publication first')
    pub.git('add','-f',*names)
    if pub.git('diff','--cached','--name-only').strip():
        with contextlib.redirect_stdout(io.StringIO()):return pub.publish(title,paths)
    # Previous invocation may have committed then failed during push/readback.
    head=pub.git('rev-parse','HEAD').decode().strip();branch='hrl/ep-l2-ms20261019-e-eval-v1'
    pub.git('push','origin','HEAD:refs/heads/'+branch);pub.git('fetch','origin',branch)
    require(pub.git('rev-parse','FETCH_HEAD').decode().strip()==head,'remote head diverged; pending state retained')
    for name in names:require(pub.git('show',head+':'+name)==transport.small_bytes(ROOT/name,transport.MAX_STATE_BYTES),'remote metadata differs')
    return dict(remote_commit=head,verified_paths=names,resumed_committed_publication=True)


def mirror_aliases(plan,event_ref):
    mirrors=[]
    for lane in plan['recipients']:
        alias=dict(schema='E2_APPROVED_RELAY_ALIAS_V1',dispatch_id=plan['dispatch_id'],recipient=lane,event=event_ref,packet=plan['packet_ref'],approval=plan['approval_ref'],approved_task_ids=plan['task_ids'],delivery='PUBLISHED_EVENT_AND_LOCAL_POINTER_ONLY_NOT_ACK_OR_SCIENTIFIC_ACCEPTANCE')
        raw=transport.encoded(alias)
        for root in ALIAS_ROOTS:
            require(root.is_dir(),'original recipient directory missing; no replacement created')
            target=transport.safe_target(root,'E2_TO_'+lane+'_APPROVED_RELAY_'+plan['dispatch_id']+'.json');transport.immutable(target,raw)
            mirrors.append(dict(path=str(target),sha256=transport.sha(raw)))
    return mirrors


def dispatch(client,plan,pub,publish=False):
    require(prepare(client,plan['packet_ref'],plan['approval_ref'])==plan,'dispatch plan differs from independently verified approved metadata')
    if not publish:return dict(status='DRY_RUN_NO_MESSAGES_OR_WRITES',dispatch=plan,ack_claimed=False,wakes_idle_lane=False)
    directory=transport.safe_target(PROTOCOL,'dispatches/'+plan['dispatch_id']);directory.mkdir(parents=True,exist_ok=True)
    lock=directory/'.relay.lock';fd=os.open(lock,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'a+b') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX);journal=directory/'PENDING.json'
        state=transport.json_read(journal) if journal.exists() else dict(schema='E2_APPROVED_RELAY_JOURNAL_V1',plan=plan,phase='PENDING',created_at_utc=transport.utc())
        require(state['plan']==plan,'dispatch ID already binds a different immutable packet/approval')
        if state['phase']=='COMPLETE':
            proof=state['receipt_publication'];published_metadata(client,dict(repo=client.contract['repository']['full_name'],commit=proof['remote_commit'],path=str((directory/'RECEIPT.json').relative_to(ROOT)),sha256=transport.sha(transport.small_bytes(directory/'RECEIPT.json',65536)),role='request_context'),remote_head(client))
            receipt=transport.json_read(directory/'RECEIPT.json',65536);require(mirror_aliases(plan,receipt['event'])==receipt['mirrors'],'mirror recovery differs from published receipt')
            return dict(status='ALREADY_DELIVERED_NO_NEW_EVENT',dispatch_id=plan['dispatch_id'],receipt_publication=proof,ack_claimed=False,wakes_idle_lane=False)
        transport.atomic(journal,transport.encoded(state))
        try:
            emitted=client.emit('REQUEST',plan['recipients'],plan['subject'],plan['body'],plan['refs'],'E2:APPROVED_RELAY:'+plan['dispatch_id'],dict(correlation_id=plan['dispatch_id'],work_key='APPROVED_RELAY:'+plan['dispatch_id']))
            event=emitted['event'];eventpath=client.path('events',event_id=event['event_id']);eventsha=transport.sha(transport.small_bytes(eventpath,65536))
            state['event_id']=event['event_id'];state['event_sha256']=eventsha
            if 'event_publication' not in state:
                state['phase']='EVENT_PREPARED';transport.atomic(journal,transport.encoded(state))
                state['event_publication']=publish_exact(pub,'ep-l2 E2: relay recorded user approval '+plan['dispatch_id'],[eventpath,client.path('cursor'),journal])
                state['phase']='EVENT_PUBLISHED';transport.atomic(journal,transport.encoded(state))
            event_ref=dict(repo=client.contract['repository']['full_name'],commit=state['event_publication']['remote_commit'],path=str(eventpath.relative_to(ROOT)),sha256=eventsha,role='request_context')
            # Independent remote source readback before any legacy alias is delivered.
            client.source_event('E2',event['event_id'],event_ref['commit'],eventsha)
            mirrors=mirror_aliases(plan,event_ref)
            state['phase']='MIRRORED';state['mirrors']=mirrors;transport.atomic(journal,transport.encoded(state))
            receipt=dict(schema='E2_APPROVED_RELAY_DISPATCH_RECEIPT_V1',status='EVENT_PUBLISHED_AND_LOCAL_ALIASES_DELIVERED_NO_ACK_CLAIM',created_at_utc=state['created_at_utc'],dispatch_id=plan['dispatch_id'],packet=plan['packet_ref'],approval=plan['approval_ref'],event=event_ref,recipients=plan['recipients'],approved_task_ids=plan['task_ids'],mirrors=mirrors,peer_ack_claimed=False,peer_execution_claimed=False,idle_window_wakeup_available=False)
            receiptpath=directory/'RECEIPT.json';transport.immutable(receiptpath,transport.encoded(receipt))
            state['receipt_publication']=publish_exact(pub,'ep-l2 E2: approved relay delivery receipt '+plan['dispatch_id'],[receiptpath,journal])
            state['phase']='COMPLETE';transport.atomic(journal,transport.encoded(state))
            transport.atomic(directory/'REMOTE_READBACK.json',transport.encoded(state['receipt_publication']))
            return dict(status='DELIVERED_NOT_ACKNOWLEDGED',dispatch_id=plan['dispatch_id'],receipt_publication=state['receipt_publication'],ack_claimed=False,wakes_idle_lane=False)
        except Exception as error:
            # Preserve the last durable stage and immutable failures; never reset.
            transport.immutable(directory/('ERROR_'+uuid.uuid4().hex+'.json'),transport.encoded(dict(status='PENDING_RETRY_REQUIRED',phase=state['phase'],at_utc=transport.utc(),error=str(error)[:2000])))
            raise


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--packet-ref',required=True);ap.add_argument('--approval-ref',required=True);ap.add_argument('--publish',action='store_true');args=ap.parse_args(argv)
    require(len(args.packet_ref)<=4096 and len(args.approval_ref)<=4096,'reference argument bound')
    client=transport.Client(transport.json_read(PROTOCOL/'CONTRACT.json',65536),'E2')
    plan=prepare(client,json.loads(args.packet_ref),json.loads(args.approval_ref))
    result=dispatch(client,plan,publisher() if args.publish else None,args.publish);print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(status='RELAY_REJECTED_OR_PENDING',error=str(error),ack_claimed=False),ensure_ascii=False),file=sys.stderr);raise SystemExit(2)

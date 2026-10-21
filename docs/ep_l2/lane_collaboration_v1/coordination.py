#!/usr/bin/env python3
"""Bounded, foreground lane messages. No experiment, resource or command executor.

Run from your own Framework worktree/branch. Git publication/fetch/readback is
explicit outside this CLI. Local uncommitted messages are preview-only; ACKs
require the exact source event in a pinned Git commit on its owner branch.
"""
from pathlib import Path, PurePosixPath
from contextlib import contextmanager
from datetime import datetime, timezone
import argparse, copy, fcntl, hashlib, json, os, re, socket, stat, subprocess, sys, tempfile, uuid

PROTOCOL='docs/ep_l2/lane_collaboration_v1'
MAX_STATE_BYTES=1024*1024
MAX_STATE_EVENTS=4096
MAX_SCAN=512
HEX40=re.compile(r'[0-9a-f]{40}\Z')
HEX64=re.compile(r'[0-9a-f]{64}\Z')
EVENT_ID=re.compile(r'(A2|B|C|D|E2|F)-[0-9]{8}-[0-9a-f]{12}\Z')


def require(ok, message):
    if not ok:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def utc():return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


def small_bytes(path, maximum):
    """No symlinks; size checked before and after the bounded read."""
    path=Path(path)
    require(stat.S_ISREG(path.lstat().st_mode),'metadata must be a regular file: '+str(path))
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        st=os.fstat(fd);require(stat.S_ISREG(st.st_mode),'metadata changed file type');require(st.st_size<=maximum,'oversized metadata: '+str(path))
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(maximum+1)
        require(len(raw)<=maximum,'metadata grew over bound: '+str(path));return raw
    finally:os.close(fd)


def json_read(path,maximum=MAX_STATE_BYTES):return json.loads(small_bytes(path,maximum))


def relative_path(value):
    require(isinstance(value,str) and 0<len(value)<=512 and '\\' not in value,'invalid repo-relative path')
    path=PurePosixPath(value)
    require(not path.is_absolute() and str(path)==value and all(x not in ('..','.git','.') for x in path.parts),'unsafe repo-relative path')
    require(not any(ord(c)<32 for c in value),'control character in path');return value


def safe_target(root,relative):
    relative_path(relative);require(not Path(root).is_symlink(),'transport root is a symlink');root=Path(root).resolve();target=root/relative
    for parent in [target,*target.parents]:
        if parent==root:break
        require(not parent.is_symlink(),'symlink in transport path: '+str(parent))
    require(target.resolve().is_relative_to(root),'transport path escapes root');return target


def immutable(path,raw):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    try:fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    except FileExistsError:
        require(small_bytes(path,max(len(raw),65536))==raw,'conflicting immutable event: '+str(path));return False
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return True


def atomic(path,raw):
    path=Path(path);require(not path.is_symlink(),'symlink state path');path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.transport-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)


def git(root,*args):
    # Fixed argument arrays only. Never shell=True, a message command or git write.
    result=subprocess.run(['git','-C',str(root),*args],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
    require(result.returncode==0,'read-only Git query failed: '+str(args[0]));return result.stdout


def repo_name(url):
    url=url.strip()
    if url.startswith('git@github.com:'):value=url[len('git@github.com:'):]
    else:
        from urllib.parse import urlsplit
        parsed=urlsplit(url);require(parsed.hostname=='github.com' and parsed.scheme in ('https','ssh'),'origin is not configured GitHub repository')
        value=parsed.path.lstrip('/')
    return value.removesuffix('.git').rstrip('/')


class Client:
    def __init__(self,contract,lane,worktree=None):
        self.contract=contract;self.lane=lane
        require(contract['schema']=='EPL2_LANE_COLLABORATION_CONTRACT_V1','unknown contract schema')
        require(lane in contract['lanes'],'unknown/inactive owner; support lanes require an explicit contract revision')
        self.limits=contract['limits'];self.maximum=self.limits['max_event_bytes']
        require(0<self.maximum<=65536 and 0<self.limits['max_events_per_check']<=128,'unsafe configured bounds')
        cwd_root=Path(git(Path.cwd(),'rev-parse','--show-toplevel').decode().strip()).resolve()
        self.root=Path(worktree).resolve() if worktree else cwd_root
        require(self.root==cwd_root,'writes/reads must use actual current worktree; arbitrary foreign target forbidden')
        require(lane!='F' or worktree is not None,'cross-host F requires explicit actual --worktree')
        branch=git(self.root,'branch','--show-current').decode().strip()
        require(branch==contract['lanes'][lane]['branch'],'owner does not match actual current branch')
        require(repo_name(git(self.root,'remote','get-url',contract['repository']['git_remote']).decode())==contract['repository']['full_name'],'origin repository differs')
        self.base=safe_target(self.root,contract['protocol_path'])
        self.mailbox=Path(contract['local_mailbox_root'])
        require(self.mailbox.is_absolute(),'mailbox must be explicit absolute shared location')
        self.binding=dict(owner=lane,branch=branch,worktree=str(self.root),hostname=socket.gethostname())

    def path(self,kind,**kwargs):return safe_target(self.base,self.contract['paths'][kind].format(owner=self.lane,**kwargs))
    def cache(self,kind,**kwargs):return safe_target(self.mailbox,self.contract['paths'][kind].format(owner=self.lane,consumer=self.lane,**kwargs))

    @contextmanager
    def lock(self):
        # Isolated transport lock; never touches REGISTRY.lock or a lease.
        path=safe_target(self.mailbox,self.lane+'/state/transport.lock');path.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'a+b') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX)
            try:yield
            finally:fcntl.flock(stream,fcntl.LOCK_UN)

    def state(self):
        p=self.path('cursor')
        if not p.exists():return dict(owner=self.lane,campaign_id=self.contract['campaign_id'],seen_event_ids={},seen_dedup_keys={},last_sequence_by_sender={},last_emitted_sequence=0,outgoing_dedup={})
        value=json_read(p)
        require(value['owner']==self.lane and value['campaign_id']==self.contract['campaign_id'],'foreign cursor ownership')
        require(all(k in value for k in self.contract['cursor_required']),'incomplete cursor')
        require(len(value['seen_event_ids'])<=MAX_STATE_EVENTS and len(value.get('outgoing_dedup',{}))<=MAX_STATE_EVENTS,'cursor bound exhausted')
        return value

    def save_state(self,value):
        require(len(value['seen_event_ids'])<=MAX_STATE_EVENTS and len(value['outgoing_dedup'])<=MAX_STATE_EVENTS,'cursor capacity exhausted; explicit archival review required')
        raw=encoded(value);require(len(raw)<=MAX_STATE_BYTES,'cursor bytes bound exhausted');atomic(self.path('cursor'),raw)

    def validate_ref(self,ref):
        require(isinstance(ref,dict) and set(ref)==set(self.contract['reference_required']),'invalid reference fields')
        require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',ref['repo']) is not None,'invalid reference repository')
        require(HEX40.fullmatch(ref['commit']) and HEX64.fullmatch(ref['sha256']),'reference needs full commit and SHA256')
        relative_path(ref['path']);require(isinstance(ref['role'],str) and 0<len(ref['role'])<=100,'invalid reference role')

    def validate_event(self,value):
        require(isinstance(value,dict) and set(value)>=set(self.contract['event_required']),'incomplete event')
        require(set(value)<=set(self.contract['event_required']+self.contract['event_optional']),'unknown event fields')
        require(value['schema']==self.contract['event_schema'] and value['campaign_id']==self.contract['campaign_id'],'different event contract/campaign')
        owner=value['owner'];require(owner in self.contract['lanes'],'foreign/inactive event owner')
        require(EVENT_ID.fullmatch(value['event_id']) and value['event_id'].startswith(owner+'-'),'invalid owner/event filename')
        require(type(value['sequence']) is int and 0<value['sequence']<10**8,'invalid sequence')
        require(int(value['event_id'].split('-')[1])==value['sequence'],'event ID/sequence mismatch')
        require(value['kind'] in self.contract['kinds'],'unknown event kind')
        recipients=value['recipients'];require(isinstance(recipients,list) and recipients and len(recipients)==len(set(recipients)) and set(recipients)<=set(self.contract['lanes']),'invalid recipients')
        require(isinstance(value['subject'],str) and 0<len(value['subject'])<=240,'subject too long/empty')
        require(isinstance(value['body'],(dict,list,str)) and len(json.dumps(value['body'],ensure_ascii=False))<=self.limits['max_body_characters'],'body bound/type')
        require(isinstance(value['dedup_key'],str) and value['dedup_key'].startswith(owner+':') and len(value['dedup_key'])<=240,'owner-qualified dedup key required')
        require(isinstance(value['refs'],list) and len(value['refs'])<=self.limits['max_refs_per_event'],'reference count bound')
        require(value['kind']!='DELIVERY' or value['refs'],'DELIVERY needs an immutable artifact reference')
        for name in ('correlation_id','work_key'):
            if name in value:require(isinstance(value[name],str) and 0<len(value[name])<=240,'invalid correlation/work key')
        for ref in value['refs']:self.validate_ref(ref)
        require(isinstance(value['created_at_utc'],str) and value['created_at_utc'].endswith('Z'),'UTC timestamp required')
        datetime.fromisoformat(value['created_at_utc'].replace('Z','+00:00'))
        if value['kind']=='ACK':
            target=value.get('ack_for');require(isinstance(target,dict) and set(target)=={'owner','event_id','event_sha256','source_commit'},'ACK requires exact original reference')
            require(target['owner'] in self.contract['lanes'] and EVENT_ID.fullmatch(target['event_id']) and target['event_id'].startswith(target['owner']+'-'),'invalid ACK target')
            require(HEX64.fullmatch(target['event_sha256']) and HEX40.fullmatch(target['source_commit']),'ACK must reference a published source event')
            require(value.get('ack_status') in self.contract['ack_statuses'],'invalid ACK status')
        else:require('ack_for' not in value and 'ack_status' not in value,'only ACK can assert acknowledgement')
        require(len(encoded(value))<=self.maximum,'event bytes bound');return value

    @staticmethod
    def payload_hash(value):return sha(encoded({k:v for k,v in value.items() if k not in ('event_id','sequence','created_at_utc')}))

    def blob(self,commit,path,maximum=None):
        require(HEX40.fullmatch(commit),'full pinned source commit required');relative_path(path)
        maximum=self.maximum if maximum is None else maximum
        entries=git(self.root,'ls-tree','-z',commit,'--',path).split(b'\0');entries=[v for v in entries if v]
        require(len(entries)==1,'reference is not an exact Git file')
        header,name=entries[0].split(b'\t',1);mode,kind,_=header.split()
        require(mode in (b'100644',b'100755') and kind==b'blob' and name.decode()==path,'reference must be a regular Git blob, not symlink/tree/gitlink')
        size=int(git(self.root,'cat-file','-s',commit+':'+path).decode());require(size<=maximum,'source Git blob exceeds remaining metadata bound')
        raw=git(self.root,'show',commit+':'+path);require(len(raw)==size,'Git blob size mismatch');return raw

    def verify_refs(self,refs):
        total=0
        for ref in refs:
            self.validate_ref(ref)
            require(ref['repo']==self.contract['repository']['full_name'],'automatic verification supports only this Framework repository')
            require(ref['path'].startswith('docs/ep_l2/') and Path(ref['path']).suffix.lower() in ('.json','.md','.csv','.txt','.yaml','.yml','.py'),'automatic verification permits declared EP-L2 text metadata only; no trace/raw/binary/DB')
            remaining=self.limits['max_referenced_metadata_bytes']-total;require(remaining>0,'reference metadata budget exhausted')
            raw=self.blob(ref['commit'],ref['path'],remaining);require(sha(raw)==ref['sha256'],'referenced metadata SHA mismatch');total+=len(raw)
        return dict(status='EXACT_GIT_BLOB_SHA_VERIFIED',reference_count=len(refs),total_metadata_bytes=total,scope='MESSAGE_METADATA_ONLY_NOT_SCIENTIFIC_ACCEPTANCE')

    def source_event(self,owner,event_id,commit,expected_sha=None):
        require(owner in self.contract['lanes'] and EVENT_ID.fullmatch(event_id) and event_id.startswith(owner+'-'),'invalid source owner/event ID')
        branch=self.contract['lanes'][owner]['branch'];require(not branch.startswith('-'),'unsafe configured branch')
        # Both are local read-only refs; fetch remains an explicit caller action.
        require(HEX40.fullmatch(commit),'full pinned source commit required')
        remote=self.contract['repository']['git_remote']
        remote_ref='refs/heads/'+branch
        observed=git(self.root,'ls-remote','--exit-code',remote,remote_ref).decode().splitlines()
        require(len(observed)==1,'remote owner branch readback missing/ambiguous')
        head,refname=observed[0].split();require(HEX40.fullmatch(head) and refname==remote_ref,'invalid remote owner readback')
        # Query is read-only; missing local objects require an explicit fetch.
        result=subprocess.run(['git','-C',str(self.root),'merge-base','--is-ancestor',commit,head],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
        require(result.returncode==0,'source commit not proven in actual remote owner branch; explicitly fetch first')
        path=PROTOCOL+'/events/'+owner+'/'+event_id+'.json';raw=self.blob(commit,path)
        if expected_sha is not None:require(sha(raw)==expected_sha,'source event SHA mismatch')
        value=self.validate_event(json.loads(raw));require(value['owner']==owner and value['event_id']==event_id,'Git path/event owner mismatch');return value,raw

    def event_files(self,root):
        root=Path(root)
        if not root.exists():return []
        require(not root.is_symlink(),'symlink event directory');files=[]
        with os.scandir(root) as entries:
            for entry in entries:
                require(len(files)<MAX_SCAN,'event directory scan bound; explicit archival/index required')
                require(entry.is_file(follow_symlinks=False) and entry.name.endswith('.json'),'unexpected/symlink event entry')
                files.append(Path(entry.path))
        return sorted(files)

    def own_events(self):
        result=[]
        for path in self.event_files(safe_target(self.base,'events/'+self.lane)):
            value=self.validate_event(json.loads(small_bytes(path,self.maximum)));require(value['owner']==self.lane and path.stem==value['event_id'],'foreign own event')
            result.append(value)
        require(len({v['sequence'] for v in result})==len(result),'owner sequence collision')
        return result

    def emit(self,kind,recipients,subject,body,refs,dedup_key,extra=None):
        with self.lock():
            state=self.state();events=self.own_events();sequence=max([state.get('last_emitted_sequence',0)]+[v['sequence'] for v in events])+1
            value=dict(schema=self.contract['event_schema'],event_id=self.lane+'-'+str(sequence).zfill(8)+'-'+uuid.uuid4().hex[:12],owner=self.lane,sequence=sequence,kind=kind,created_at_utc=utc(),campaign_id=self.contract['campaign_id'],recipients=recipients,subject=subject,body=body,refs=refs,dedup_key=dedup_key)
            if extra:
                require(set(extra)<=set(self.contract['event_optional']) and not set(extra)&set(value),'extra cannot override event ownership/required fields')
                value.update(extra)
            self.validate_event(value);fingerprint=self.payload_hash(value)
            prior=next((v for v in events if v['dedup_key']==dedup_key),None)
            if prior:
                require(self.payload_hash(prior)==fingerprint,'dedup key reused with changed payload');return dict(status='DUPLICATE_IDENTICAL_NOOP',event=prior)
            require(len(events)<MAX_SCAN,'owner event scan bound; explicit archive/index required')
            raw=encoded(value);immutable(self.path('events',event_id=value['event_id']),raw)
            immutable(self.cache('local_owner_events',event_id=value['event_id']),raw)
            state['last_emitted_sequence']=sequence;state['outgoing_dedup'][dedup_key]=dict(event_id=value['event_id'],payload_sha256=fingerprint);self.save_state(state)
            return dict(status='EMITTED_LOCAL_PREVIEW_PENDING_EXPLICIT_GIT_PUBLICATION',event=value,event_sha256=sha(raw),writer=self.binding,science_or_execution_authority=False)

    def import_event(self,owner,event_id,commit,expected_sha):
        value,raw=self.source_event(owner,event_id,commit,expected_sha)
        require(self.lane in value['recipients'],'event not addressed to consumer')
        with self.lock():
            path=self.cache('local_import_cache',sender=owner,event_id=event_id);created=immutable(path,raw)
            provenance=safe_target(self.mailbox,self.lane+'/state/imports/'+owner+'/'+event_id+'.json')
            metadata=dict(owner=owner,event_id=event_id,event_sha256=sha(raw),source_commit=commit,consumer=self.lane,repo=self.contract['repository']['full_name'])
            if provenance.exists():
                old=json_read(provenance);require(old['event_sha256']==sha(raw),'conflicting imported bytes')
            else:immutable(provenance,encoded(metadata))
        return dict(status='IMPORTED' if created else 'DUPLICATE_IDENTICAL_NOOP',provenance=metadata,scientific_acceptance=False)

    def collect(self):
        collected={};total=0;total_bytes=0
        for sender in self.contract['lanes']:
            locations=[safe_target(self.mailbox,sender+'/events'),safe_target(self.mailbox,self.lane+'/inbox/'+sender),safe_target(self.base,'events/'+sender)]
            for directory in locations:
                for path in self.event_files(directory):
                    total+=1;require(total<=MAX_SCAN,'total foreground scan bound; consume indexed batches/archive explicitly')
                    remaining=self.limits['max_referenced_metadata_bytes']-total_bytes;require(remaining>0,'foreground metadata byte budget exhausted')
                    raw=small_bytes(path,min(self.maximum,remaining));total_bytes+=len(raw);v=self.validate_event(json.loads(raw))
                    require(v['owner']==sender and path.stem==v['event_id'],'event owner/path mismatch')
                    if self.lane not in v['recipients']:continue
                    key=sender+'/'+v['event_id'];digest=sha(raw)
                    require(key not in collected or collected[key]['sha256']==digest,'conflicting event copies')
                    proof=None;meta=safe_target(self.mailbox,self.lane+'/state/imports/'+sender+'/'+v['event_id']+'.json')
                    if meta.exists():
                        x=json_read(meta);require(x['event_sha256']==digest,'import provenance changed');proof=x['source_commit']
                    collected[key]=dict(event=v,sha256=digest,source_commit=proof)
        rows=sorted(collected.values(),key=lambda r:(r['event']['owner'],r['event']['sequence']))
        by_sequence={}
        for row in rows:
            v=row['event'];key=(v['owner'],v['sequence']);require(key not in by_sequence or by_sequence[key]==v['event_id'],'sender sequence collision');by_sequence[key]=v['event_id']
        return rows

    def check(self,consume=False,maximum=None):
        maximum=maximum or self.limits['max_events_per_check'];require(0<maximum<=self.limits['max_events_per_check'],'check event bound')
        with self.lock() if consume else _no_lock():
            state=self.state();pending=[];late=[];working_dedup=copy.deepcopy(state['seen_dedup_keys'])
            for row in self.collect():
                v=row['event'];key=v['owner']+'/'+v['event_id'];old=state['seen_event_ids'].get(key)
                require(old is None or old==row['sha256'],'previously seen event changed')
                if old is not None:continue
                dedup=working_dedup.get(v['dedup_key']);fingerprint=self.payload_hash(v)
                require(dedup is None or dedup['payload_sha256']==fingerprint,'logical delivery conflict')
                if dedup is None:
                    working_dedup[v['dedup_key']]=dict(event_id=v['event_id'],payload_sha256=fingerprint)
                    if v['sequence']<=state['last_sequence_by_sender'].get(v['owner'],0):late.append(row)
                    else:pending.append(row)
            selected=pending[:maximum];late_selected=late[:max(0,maximum-len(selected))]
            if consume:
                for row in selected:
                    v=row['event'];key=v['owner']+'/'+v['event_id'];state['seen_event_ids'][key]=row['sha256'];state['seen_dedup_keys'][v['dedup_key']]=dict(event_id=v['event_id'],payload_sha256=self.payload_hash(v));state['last_sequence_by_sender'][v['owner']]=max(state['last_sequence_by_sender'].get(v['owner'],0),v['sequence'])
                self.save_state(state)
        return dict(status='BOUNDED_CHECK',consumer=self.lane,events=selected,late_unseen_preserved=late_selected,late_unseen_remaining=len(late)-len(late_selected),refs_validation='FORMAT_ONLY_NOT_CONTENT_VERIFIED',remaining_unconsumed=max(0,len(pending)-len(selected)),cursor_updated=consume,acknowledgement_emitted=False,preview_warning='source_commit null is local preview only; ACK requires exact published commit independently imported')

    def ack(self,owner,event_id,commit,expected_sha,status,body,refs,confirmed_reference_review=False):
        require(status not in ('VALIDATED','APPLIED') or confirmed_reference_review,'VALIDATED/APPLIED needs explicit owner reference-review confirmation; CLI does not verify artifact contents')
        value,raw=self.source_event(owner,event_id,commit,expected_sha)
        require(self.lane in value['recipients'],'cannot ACK an event addressed to another lane')
        require(owner!=self.lane,'self-ACK is not another lane joining')
        target=dict(owner=owner,event_id=event_id,event_sha256=sha(raw),source_commit=commit)
        if status in ('VALIDATED','APPLIED'):
            require(status!='APPLIED' or refs,'APPLIED needs a published output evidence reference; CLI applies no work')
            verification=self.verify_refs(value['refs']+refs)
            body=dict(message=body,reference_validation=verification,owner_declares_reference_review_complete=True,ack_is_not_scientific_or_execution_acceptance=True)
        return self.emit('ACK',[owner],'ACK '+event_id,body,refs,self.lane+':ACK:'+owner+':'+event_id+':'+status,dict(ack_for=target,ack_status=status))

    def status(self,body=None,expected_sha=None):
        path=self.path('status')
        if body is None:
            return dict(owner=self.lane,status=json_read(path,self.maximum) if path.exists() else None,absence='NO_SELF_REPORTED_STATUS' if not path.exists() else None,process_or_lease_state_inferred=False)
        require(isinstance(body,dict) and set(body)=={'activity','current_task','blocking_dependencies'},'status body requires activity/task/dependencies only')
        require(body['activity'] in self.contract['activity_values'] and isinstance(body['current_task'],str) and isinstance(body['blocking_dependencies'],list),'invalid status projection')
        # Reject unknown/CAS-conflicting projection before emitting an event.
        previous_id='INITIAL'
        with self.lock():
            if path.exists():
                old=small_bytes(path,self.maximum);prior=json.loads(old)
                require(prior.get('owner')==self.lane and prior.get('campaign_id')==self.contract['campaign_id'],'foreign status projection')
                if all(prior.get(k)==v for k,v in body.items()):return dict(status='DUPLICATE_IDENTICAL_NOOP',projection=prior)
                require(expected_sha is not None and sha(old)==expected_sha,'status replacement needs exact --expected-status-sha')
                previous_id=prior['last_emitted_event_id']
            else:require(expected_sha is None,'cannot replace nonexistent status')
        emitted=self.emit('STATUS',[x for x in self.contract['lanes'] if x!=self.lane],'Status: '+body['activity'],body,[],self.lane+':STATUS:'+previous_id+':'+sha(encoded(body)))
        event=emitted['event'];projection=dict(schema=self.contract['status_schema'],owner=self.lane,campaign_id=self.contract['campaign_id'],updated_at_utc=event['created_at_utc'],activity=body['activity'],last_emitted_event_id=event['event_id'],last_sequence=event['sequence'],current_task=body['current_task'],blocking_dependencies=body['blocking_dependencies'])
        with self.lock():
            if path.exists():
                old=small_bytes(path,self.maximum)
                if json.loads(old)==projection:return dict(status='DUPLICATE_IDENTICAL_NOOP',projection=projection)
                require(expected_sha is not None and sha(old)==expected_sha,'status replacement needs exact --expected-status-sha')
            else:require(expected_sha is None,'cannot replace nonexistent status')
            atomic(path,encoded(projection))
        return dict(status='OWN_STATUS_RECORDED_NOT_REMOTE_PROCESS_PROOF',projection=projection,scientific_acceptance=False)


@contextmanager
def _no_lock():yield


def body_arg(args):
    require(not (args.body_file and args.body_json),'choose body file or JSON, not both')
    if args.body_file:
        p=Path(args.body_file).resolve();root=Path(git(Path.cwd(),'rev-parse','--show-toplevel').decode().strip()).resolve()
        require(p.is_relative_to(root/PROTOCOL),'body file must be explicit metadata inside own lane protocol directory')
        raw=small_bytes(p,32768).decode()
    else:raw=args.body_json or '{}'
    require(len(raw)<=32768,'body argument bound');return json.loads(raw)


def refs_arg(value):
    require(len(value)<=65536,'refs argument bound');return json.loads(value)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--lane',required=True);ap.add_argument('--worktree');ap.add_argument('--contract',default=str(Path(__file__).with_name('CONTRACT.json')))
    sub=ap.add_subparsers(dest='command',required=True)
    check=sub.add_parser('check');check.add_argument('--consume',action='store_true');check.add_argument('--max-events',type=int)
    emit=sub.add_parser('emit');emit.add_argument('--kind',choices=['REQUEST','DELIVERY'],required=True);emit.add_argument('--to',nargs='+',required=True);emit.add_argument('--subject',required=True);emit.add_argument('--dedup-key',required=True);emit.add_argument('--work-key');emit.add_argument('--correlation-id')
    ack=sub.add_parser('ack');ack.add_argument('--source-lane',required=True);ack.add_argument('--event-id',required=True);ack.add_argument('--source-commit',required=True);ack.add_argument('--event-sha256',required=True);ack.add_argument('--ack-status',choices=['RECEIVED','VALIDATED','APPLIED','BLOCKED','REJECTED'],required=True);ack.add_argument('--confirm-reference-review',action='store_true')
    imp=sub.add_parser('import-event');imp.add_argument('--source-lane',required=True);imp.add_argument('--event-id',required=True);imp.add_argument('--source-commit',required=True);imp.add_argument('--event-sha256',required=True)
    status=sub.add_parser('status');status.add_argument('--set',action='store_true');status.add_argument('--expected-status-sha')
    for child in (emit,ack,status):child.add_argument('--body-json');child.add_argument('--body-file');child.add_argument('--refs-json',default='[]')
    args=ap.parse_args(argv);require(Path(args.contract).resolve()==Path(__file__).with_name('CONTRACT.json').resolve(),'CLI uses only the adjacent reviewed contract, not arbitrary owner mapping');contract=json_read(args.contract,65536);client=Client(contract,args.lane,args.worktree)
    if args.command=='check':result=client.check(args.consume,args.max_events)
    elif args.command=='emit':result=client.emit(args.kind,args.to,args.subject,body_arg(args),refs_arg(args.refs_json),args.dedup_key,{k:v for k,v in {'work_key':args.work_key,'correlation_id':args.correlation_id}.items() if v})
    elif args.command=='ack':result=client.ack(args.source_lane,args.event_id,args.source_commit,args.event_sha256,args.ack_status,body_arg(args),refs_arg(args.refs_json),args.confirm_reference_review)
    elif args.command=='import-event':result=client.import_event(args.source_lane,args.event_id,args.source_commit,args.event_sha256)
    else:result=client.status(body_arg(args) if args.set else None,args.expected_status_sha)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2));return result


if __name__=='__main__':
    try:main()
    except (ValueError,TypeError,OSError,KeyError,json.JSONDecodeError,subprocess.TimeoutExpired) as error:
        print(json.dumps(dict(status='REJECTED_NO_EXECUTION_AUTHORITY',error=str(error)),ensure_ascii=False),file=sys.stderr);raise SystemExit(2)

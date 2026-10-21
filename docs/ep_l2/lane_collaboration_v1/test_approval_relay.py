"""Independent bounded relay controls. Mock Git/network and temporary files only."""
from pathlib import Path
import copy,importlib.util,json,sys,tempfile,types,unittest
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
spec=importlib.util.spec_from_file_location('review_approval_relay',P/'approval_relay.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
t=m.transport
BASE='1'*40
class Publisher:
 def __init__(self,root):
  self.root=root;self.head=self.remote=self.fetched=BASE;self.objects={BASE:{}};self.parents={BASE:None};self.staged={};self.commits=0;self.pushes=0;self.calls=[];self.fail_push=None;self.fail_before_commit=False
 def ancestor(self,child,head):
  while head:
   if child==head:return True
   head=self.parents.get(head)
  return False
 def git(self,*args):
  self.calls.append(args)
  if args==('rev-parse','--show-toplevel'):return str(self.root).encode()
  if args==('branch','--show-current'):return b'hrl/ep-l2-ms20261019-e-eval-v1'
  if args[:2]==('remote','get-url'):return b'https://github.com/swayhrl/accel-sim-framework.git'
  if args[0]=='ls-remote':return (self.remote+'\t'+args[-1]+'\n').encode()
  if args[0]=='merge-base':
   if not self.ancestor(args[-2],args[-1]):raise ValueError('source not in mock remote E2 ancestry')
   return b''
  if args[0]=='ls-tree':
   commit=args[2];path=args[-1]
   return (b'100644 blob '+b'a'*40+b'\t'+path.encode()+b'\0') if path in self.objects.get(commit,{}) else b''
  if args[:2]==('cat-file','-s'):
   commit,path=args[2].split(':',1);return str(len(self.objects[commit][path])).encode()
  if args[0]=='show':
   commit,path=args[1].split(':',1);return self.objects[commit][path]
  if args[:3]==('diff','--cached','--name-only'):return ('\n'.join(sorted(self.staged))).encode()
  if args[:2]==('add','-f'):
   for name in args[2:]:
    raw=(self.root/name).read_bytes()
    if self.objects[self.head].get(name)!=raw:self.staged[name]=raw
    else:self.staged.pop(name,None)
   return b''
  if args==('rev-parse','HEAD'):return self.head.encode()
  if args==('rev-parse','FETCH_HEAD'):return self.fetched.encode()
  if args[0]=='push':
   self.pushes+=1
   if self.fail_push==self.pushes:raise RuntimeError('SYNTHETIC_PUSH_INTERRUPTION')
   self.remote=self.head;return b''
  if args[0]=='fetch':self.fetched=self.remote;return b''
  raise AssertionError('Unexpected mocked Git operation '+str(args))
 def publish(self,title,paths):
  if self.fail_before_commit:self.fail_before_commit=False;raise RuntimeError('SYNTHETIC_PRECOMMIT_INTERRUPTION')
  self.commits+=1;parent=self.head;self.head=f'{self.commits+1:040x}';self.parents[self.head]=parent
  self.objects[self.head]=dict(self.objects[parent],**self.staged);names=list(self.staged);self.staged={}
  self.git('push','origin','HEAD:refs/heads/hrl/ep-l2-ms20261019-e-eval-v1');self.git('fetch','origin','hrl/ep-l2-ms20261019-e-eval-v1')
  return dict(remote_commit=self.head,verified_paths=names)
class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='epl2_relay_review_');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.pub=Publisher(self.root)
  self.enterContext(patch.object(m,'ROOT',self.root));self.enterContext(patch.object(m,'PROTOCOL',self.root/t.PROTOCOL))
  self.aliases=tuple(self.root/f'legacy{i}' for i in range(3))
  for p in self.aliases:p.mkdir()
  self.enterContext(patch.object(m,'ALIAS_ROOTS',self.aliases));self.enterContext(patch.object(t.Path,'cwd',return_value=self.root))
  self.enterContext(patch.object(t,'git',side_effect=lambda root,*args:self.pub.git(*args)))
  self.enterContext(patch.object(t.subprocess,'run',side_effect=self.subprocess))
  contract=json.loads((P/'CONTRACT.json').read_text());contract['local_mailbox_root']=str(self.root/'mailbox')
  self.client=t.Client(contract,'E2',self.root)
  self.packet=dict(schema=m.PACKET_SCHEMA,dispatch_id='synthetic_review_r1',recipients=['A2','D'],task_ids=['PREPARE_INPUT','REVIEW_SCOPE'],scope='Preparation and coordination only; no native or application authorization',subject='synthetic relay only',body={'instruction':'review immutable metadata only'},refs=[])
  self.packet_path=t.PROTOCOL+'/fixtures/PACKET.json';self.approval_path=t.PROTOCOL+'/fixtures/APPROVAL.json'
  self.approval=dict(schema=m.APPROVAL_SCHEMA,user_message_verbatim='Synthetic record approving forwarding mechanics only',approved_packet_path=self.packet_path,approved_packet_sha256='',approved_recipients=self.packet['recipients'],approved_task_ids=self.packet['task_ids'],approved_scope=self.packet['scope'],approval_kind='COORDINATION_RELAY_ONLY')
  self.refresh()
 def subprocess(self,args,**kwargs):
  self.assertEqual(args[:4],['git','-C',str(self.root),'merge-base']);return types.SimpleNamespace(returncode=0 if self.pub.ancestor(args[-2],args[-1]) else 1)
 def ref(self,path,raw):return dict(repo=self.client.contract['repository']['full_name'],commit=BASE,path=path,sha256=t.sha(raw),role='request_context')
 def refresh(self):
  raw=t.encoded(self.packet);self.packet_ref=self.ref(self.packet_path,raw);self.approval['approved_packet_sha256']=self.packet_ref['sha256'];self.approval_ref=self.ref(self.approval_path,t.encoded(self.approval));self.pub.objects[BASE].update({self.packet_path:raw,self.approval_path:t.encoded(self.approval)})
 def plan(self):return m.prepare(self.client,self.packet_ref,self.approval_ref)
 def files(self):return {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
 def events(self):return list((m.PROTOCOL/'events'/'E2').glob('*.json'))
 def send(self,plan=None):return m.dispatch(self.client,self.plan() if plan is None else plan,self.pub,True)
 def assert_one_request_no_ack(self):
  self.assertEqual(len(self.events()),1);event=json.loads(self.events()[0].read_text());self.assertEqual(event['kind'],'REQUEST');self.assertNotIn('ack_for',event);self.assertEqual(event['owner'],'E2');self.assertEqual(event['recipients'],self.packet['recipients'])
 def test_positive_prepare_is_readonly_and_exact(self):
  before=self.files();plan=self.plan();self.assertEqual(before,self.files());self.assertEqual(plan['task_ids'],self.packet['task_ids']);self.assertEqual(plan['refs'][:2],[self.packet_ref,self.approval_ref])
 def test_packet_SHA_change_rejected(self):
  ref=dict(self.packet_ref,sha256='0'*64)
  with self.assertRaises(ValueError):m.prepare(self.client,ref,self.approval_ref)
 def test_approval_SHA_change_rejected(self):
  with self.assertRaises(ValueError):m.prepare(self.client,self.packet_ref,dict(self.approval_ref,sha256='0'*64))
 def test_unpublished_commit_rejected(self):
  ref=dict(self.packet_ref,commit='9'*40);self.pub.objects[ref['commit']]={self.packet_path:t.encoded(self.packet)}
  with self.assertRaises(ValueError):m.prepare(self.client,ref,self.approval_ref)
 def test_foreign_repository_rejected(self):
  with self.assertRaises(ValueError):m.prepare(self.client,dict(self.packet_ref,repo='other/repo'),self.approval_ref)
 def test_wrong_owner_rejected(self):
  with patch.object(self.client,'lane','D'):
   with self.assertRaises(ValueError):self.plan()
 def test_wrong_actual_root_rejected(self):
  with patch.object(self.client,'root',self.root/'foreign'):
   with self.assertRaises(ValueError):self.plan()
 def test_recipient_mismatch_rejected(self):
  self.approval['approved_recipients']=['B'];self.refresh()
  with self.assertRaises(ValueError):self.plan()
 def test_task_ID_mismatch_rejected(self):
  self.approval['approved_task_ids']=['RUN_UNAPPROVED_EXPERIMENT'];self.refresh()
  with self.assertRaises(ValueError):self.plan()
 def test_scope_mismatch_rejected(self):
  self.approval['approved_scope']='different scope';self.refresh()
  with self.assertRaises(ValueError):self.plan()
 def test_packet_path_binding_rejected(self):
  self.approval['approved_packet_path']=t.PROTOCOL+'/different.json';self.refresh()
  with self.assertRaises(ValueError):self.plan()
 def test_unknown_or_missing_approval_record_rejected(self):
  self.approval['approval_kind']='EXECUTE_ALL_FUTURE_EXPERIMENTS';self.refresh()
  with self.assertRaises(ValueError):self.plan()
 def test_dryrun_creates_no_event_journal_alias_or_receipt(self):
  plan=self.plan();before=self.files();r=m.dispatch(self.client,plan,None,False);self.assertEqual(before,self.files());self.assertFalse(r['ack_claimed']);self.assertFalse(r['wakes_idle_lane'])
 def test_direct_dispatch_forged_plan_rejected(self):
  plan=self.plan();plan['task_ids']=['UNBOUND_TASK'];before=self.files()
  with self.assertRaises(ValueError):m.dispatch(self.client,plan,self.pub,True)
  self.assertEqual(before,self.files())
 def test_complete_dispatch_retry_no_new_event_or_publication(self):
  plan=self.plan();first=self.send(plan);commits=self.pub.commits;r=self.send(plan);self.assertEqual(r['status'],'ALREADY_DELIVERED_NO_NEW_EVENT');self.assertEqual(self.pub.commits,commits);self.assert_one_request_no_ack();self.assertFalse(first['ack_claimed']);self.assertFalse(first['wakes_idle_lane'])
 def test_same_dispatch_new_reference_revision_rejected(self):
  self.send();raw=t.encoded(self.packet);new='8'*40;self.pub.objects[new]={self.packet_path:raw};self.pub.parents[new]=self.pub.remote;self.pub.remote=new
  other=m.prepare(self.client,dict(self.packet_ref,commit=new),self.approval_ref)
  with self.assertRaises(ValueError):self.send(other)
  self.assert_one_request_no_ack()
 def test_precommit_interruption_resumes_same_event(self):
  plan=self.plan();self.pub.fail_before_commit=True
  with self.assertRaises(RuntimeError):self.send(plan)
  self.assert_one_request_no_ack();self.send(plan);self.assert_one_request_no_ack();self.assertEqual(self.pub.commits,2)
 def test_event_committed_push_interruption_resumes_without_recommit(self):
  plan=self.plan();self.pub.fail_push=1
  with self.assertRaises(RuntimeError):self.send(plan)
  self.assertEqual(self.pub.commits,1);self.send(plan);self.assert_one_request_no_ack();self.assertEqual(self.pub.commits,2)
 def test_partial_alias_interruption_resumes_exact_same_pointers(self):
  plan=self.plan();original=t.immutable;failed=[False]
  def interrupt(path,raw):
   if Path(path).parent==self.aliases[1] and not failed[0]:failed[0]=True;raise RuntimeError('SYNTHETIC_MIRROR_INTERRUPTION')
   return original(path,raw)
  with patch.object(t,'immutable',side_effect=interrupt):
   with self.assertRaises(RuntimeError):self.send(plan)
  first=(self.aliases[0]/('E2_TO_A2_APPROVED_RELAY_'+plan['dispatch_id']+'.json')).read_bytes();self.send(plan);self.assertEqual(first,(self.aliases[0]/('E2_TO_A2_APPROVED_RELAY_'+plan['dispatch_id']+'.json')).read_bytes());self.assert_one_request_no_ack()
 def test_receipt_committed_push_interruption_resumes(self):
  plan=self.plan();self.pub.fail_push=2
  with self.assertRaises(RuntimeError):self.send(plan)
  self.assertEqual(self.pub.commits,2);self.send(plan);self.assertEqual(self.pub.commits,2);self.assert_one_request_no_ack()
 def test_complete_missing_mirror_restored_without_event_or_commit(self):
  plan=self.plan();self.send(plan);target=self.aliases[0]/('E2_TO_A2_APPROVED_RELAY_'+plan['dispatch_id']+'.json');raw=target.read_bytes();target.unlink();before=self.pub.commits;self.send(plan);self.assertEqual(target.read_bytes(),raw);self.assertEqual(self.pub.commits,before);self.assert_one_request_no_ack()
 def test_unrelated_staged_metadata_rejected(self):
  self.pub.staged['docs/unrelated.md']=b'unrelated'
  with self.assertRaises(ValueError):self.send()
  self.assertEqual(self.pub.commits,0)
 def test_no_embedded_command_execution_or_authority_upgrade(self):
  marker=self.root/'NEVER_EXECUTE';self.packet['body']={'command':'touch '+str(marker),'registry_override':{'actual_starts':0},'claim':'future experiment NOT approved'};self.refresh();r=self.send();self.assertFalse(marker.exists());self.assert_one_request_no_ack()
  receipt=json.loads((m.PROTOCOL/'dispatches'/self.packet['dispatch_id']/'RECEIPT.json').read_text());self.assertFalse(receipt['peer_ack_claimed']);self.assertFalse(receipt['peer_execution_claimed']);self.assertFalse(receipt['idle_window_wakeup_available']);self.assertFalse(r['ack_claimed'])
if __name__=='__main__':unittest.main()

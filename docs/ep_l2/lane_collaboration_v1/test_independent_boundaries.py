"""Independent bounded transport controls. Temporary fixtures only, zero apps."""
import copy,importlib.util,json,os,stat,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('independent_coordination',P/'coordination.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
CONTRACT=json.loads((P/'CONTRACT.json').read_text())
class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='epl2_transport_review_');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.c=copy.deepcopy(CONTRACT);self.c['local_mailbox_root']=str(self.root/'mailbox')
  self.enterContext(patch.object(m.Path,'cwd',return_value=self.root))
  self.enterContext(patch.object(m,'git',side_effect=self.git))
  self.client=m.Client(self.c,'E2',self.root)
 def git(self,root,*args):
  if args==('rev-parse','--show-toplevel'):return str(self.root).encode()
  if args==('branch','--show-current'):return self.c['lanes']['E2']['branch'].encode()
  if args[:2]==('remote','get-url'):return b'git@github.com:swayhrl/accel-sim-framework.git'
  if args and args[0]=='ls-remote':return ('9'*40+'\t'+args[-1]+'\n').encode()
  raise AssertionError('Unexpected read-only Git query '+str(args))
 def event(self,owner='B',seq=1,key=None,body='test',recipients=None):
  return dict(schema=self.c['event_schema'],event_id=owner+'-'+str(seq).zfill(8)+'-'+f'{seq:012x}',owner=owner,sequence=seq,kind='REQUEST',created_at_utc='2026-10-21T12:00:00Z',campaign_id=self.c['campaign_id'],recipients=recipients or ['E2'],subject='bounded fixture',body=body,refs=[],dedup_key=key or owner+':fixture:'+str(seq))
 def put(self,event,where='mailbox'):
  if where=='mailbox':p=Path(self.c['local_mailbox_root'])/event['owner']/'events'/(event['event_id']+'.json')
  elif where=='repo':p=self.client.base/'events'/event['owner']/(event['event_id']+'.json')
  else:p=Path(self.c['local_mailbox_root'])/'E2'/'inbox'/event['owner']/(event['event_id']+'.json')
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.encoded(event));return p
 def snapshot(self):return {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file() and not p.is_symlink()}
 def test_readonly_check_does_not_advance_or_ack(self):
  self.put(self.event());before=self.snapshot();r=self.client.check();self.assertEqual(before,self.snapshot());self.assertFalse(r['cursor_updated']);self.assertFalse(r['acknowledgement_emitted'])
 def test_identical_mirrors_delivered_once(self):
  e=self.event();self.put(e);self.put(e,'repo');self.put(e,'inbox');self.assertEqual(len(self.client.check()['events']),1)
 def test_changed_mirror_rejected(self):
  e=self.event();self.put(e);e['body']='changed';self.put(e,'repo')
  with self.assertRaises(ValueError):self.client.check()
 def test_consume_does_not_fabricate_ack(self):
  self.put(self.event());r=self.client.check(True);self.assertFalse(r['acknowledgement_emitted']);self.assertFalse((self.client.base/'events'/'E2').exists())
 def test_seen_event_not_redelivered(self):
  self.put(self.event());self.client.check(True);self.assertFalse(self.client.check()['events'])
 def test_changed_seen_event_rejected(self):
  e=self.event();p=self.put(e);self.client.check(True);e['body']='tampered';p.write_bytes(m.encoded(e))
  with self.assertRaises(ValueError):self.client.check()
 def test_same_batch_changed_dedup_rejected(self):
  self.put(self.event(seq=1,key='B:same',body='one'));self.put(self.event(seq=2,key='B:same',body='two'))
  with self.assertRaises(ValueError):self.client.check(True)
 def test_same_batch_identical_dedup_once(self):
  self.put(self.event(seq=1,key='B:same'));self.put(self.event(seq=2,key='B:same'));self.assertEqual(len(self.client.check()['events']),1)
 def test_foreign_owner_extra_rejected(self):
  with self.assertRaises(ValueError):self.client.emit('REQUEST',['D'],'x','x',[],'E2:foreign',dict(owner='B',event_id='B-00000001-000000000001',dedup_key='B:foreign'))
 def test_emit_dedup_no_repeated_work(self):
  a=self.client.emit('REQUEST',['D'],'x',{'data':'ok'},[],'E2:one');b=self.client.emit('REQUEST',['D'],'x',{'data':'ok'},[],'E2:one');self.assertEqual(a['event']['event_id'],b['event']['event_id']);self.assertEqual(b['status'],'DUPLICATE_IDENTICAL_NOOP')
 def test_emit_changed_dedup_rejected(self):
  self.client.emit('REQUEST',['D'],'x','one',[],'E2:one')
  with self.assertRaises(ValueError):self.client.emit('REQUEST',['D'],'x','two',[],'E2:one')
 def test_owner_mismatch_constructor_rejected(self):
  with self.assertRaises(ValueError):m.Client(self.c,'B',self.root)
 def test_foreign_root_rejected(self):
  with self.assertRaises(ValueError):m.Client(self.c,'E2',self.root/'foreign')
 def test_inactive_support_rejected(self):
  with self.assertRaises(ValueError):m.Client(self.c,'BA',self.root)
 def test_ack_wrong_recipient_rejected(self):
  event=self.event(recipients=['C'])
  with patch.object(self.client,'source_event',return_value=(event,m.encoded(event))):
   with self.assertRaises(ValueError):self.client.ack('B',event['event_id'],'1'*40,'2'*64,'RECEIVED','ok',[])
 def test_ack_local_unpublished_commit_rejected(self):
  event=self.event();raw=m.encoded(event)
  def run(args,**kw):return types.SimpleNamespace(returncode=1)
  with patch.object(m.subprocess,'run',side_effect=run),patch.object(self.client,'blob',return_value=raw):
   with self.assertRaises(ValueError):self.client.source_event('B',event['event_id'],'1'*40,m.sha(raw))
 def test_ack_published_pin_creates_only_own_ack(self):
  e=self.event();raw=m.encoded(e)
  with patch.object(self.client,'source_event',return_value=(e,raw)):
   r=self.client.ack('B',e['event_id'],'1'*40,m.sha(raw),'RECEIVED','read',[])
  self.assertEqual(r['event']['owner'],'E2');self.assertEqual(r['event']['ack_for']['event_sha256'],m.sha(raw));self.assertFalse((self.client.base/'events'/'B').exists())
 def test_parent_symlink_reader_escape_rejected(self):
  outside=self.root/'outside';outside.mkdir();(outside/'events').mkdir();e=self.event();(outside/'events'/(e['event_id']+'.json')).write_bytes(m.encoded(e));mail=Path(self.c['local_mailbox_root']);mail.mkdir();(mail/'B').symlink_to(outside,target_is_directory=True)
  with self.assertRaises(ValueError):self.client.check()
 def test_final_symlink_rejected(self):
  target=self.root/'plain';target.write_text('{}');p=self.root/'link';p.symlink_to(target)
  with self.assertRaises((ValueError,OSError)):m.small_bytes(p,100)
 def test_nonregular_read_rejected_before_read(self):
  fifo=self.root/'fifo';os.mkfifo(fifo)
  # A mocked read prevents any real blocking even on an unsafe implementation.
  class Stream:
   def __enter__(self):return self
   def __exit__(self,*args):return False
   def read(self,*args):raise AssertionError('nonregular metadata reached read')
  with patch.object(m.os,'open',return_value=99),patch.object(m.os,'fstat',return_value=types.SimpleNamespace(st_size=0,st_mode=stat.S_IFIFO)),patch.object(m.os,'close'),patch.object(m.os,'fdopen',return_value=Stream()):
   with self.assertRaises(ValueError):m.small_bytes(fifo,100)
 def test_oversized_rejected_before_decode(self):
  p=self.root/'large';p.write_bytes(b'x'*101)
  with self.assertRaises(ValueError):m.small_bytes(p,100)
 def test_embedded_commands_inert(self):
  marker=self.root/'NEVER_EXECUTE';body={'command':'touch '+str(marker),'shell':'$(false)','registry_override':{'remaining_start_capacity':999}}
  with patch.object(m.subprocess,'run',side_effect=AssertionError('emit must not invoke subprocess')):r=self.client.emit('REQUEST',['D'],'data only',body,[],'E2:inert')
  self.assertFalse(marker.exists());self.assertEqual(r['event']['body'],body);self.assertFalse(r['science_or_execution_authority'])
 def test_git_blob_size_rejected_before_show(self):
  calls=[]
  def git(root,*args):
   calls.append(args)
   if args[0]=='ls-tree':return b'100644 blob '+b'1'*40+b'\tdocs/small.json\0'
   return b'65537'
  with patch.object(m,'git',side_effect=git):
   with self.assertRaises(ValueError):self.client.blob('1'*40,'docs/small.json')
  self.assertEqual(len(calls),2);self.assertEqual([c[0] for c in calls],['ls-tree','cat-file'])
 def test_metadata_path_escape_rejected(self):
  for path in ('../x','/etc/passwd','a/../x','a/.git/config','a\\x'):
   with self.subTest(path=path):
    with self.assertRaises(ValueError):m.relative_path(path)
if __name__=='__main__':unittest.main()

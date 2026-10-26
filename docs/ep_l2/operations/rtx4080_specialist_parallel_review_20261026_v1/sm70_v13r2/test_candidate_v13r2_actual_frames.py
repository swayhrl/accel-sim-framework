from pathlib import Path
import importlib.util,io,tarfile,gzip,hashlib,json,struct,inspect,ast,time
O=Path(__file__).parent;C=O/'candidate_v13r2'
spec=importlib.util.spec_from_file_location('sm70_frame_r2',C/'library_copy_v12_nas.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=O/'frame_fixture_v13r2';(root/'synthetic').mkdir(parents=True,exist_ok=True)
payload=b'CPU bounded member-frame semantics fixture\n'*16
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as tar:
 ti=tarfile.TarInfo('tiny.trace');ti.size=len(payload);ti.mtime=0;tar.addfile(ti,io.BytesIO(payload))
archive=root/'synthetic/tiny.tgz';archive.write_bytes(buf.getvalue());base={'archive_path':str(archive),'archive_identity':m.identity(archive),'archive_sha256':hashlib.sha256(buf.getvalue()).hexdigest(),'members':[{'relative_path':'archive_objects/tiny','archive_member':'tiny.trace','size':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}]}
class Capture:
 def __init__(self):self.buffer=io.BytesIO()
def parse(data):
 f=io.BytesIO(data);events=[]
 while True:
  h=f.read(8)
  if not h:break
  assert len(h)==8;n=struct.unpack('!Q',h)[0];event=json.loads(f.read(n));events.append(event)
  if event['event']=='CHUNK':assert f.read(event['size'])==payload
 return events
saved_task=m.TASK;saved_stdout=m.sys.stdout;saved_pace=m.adaptive_io_pace
results=[];tests=[]
try:
 m.TASK=root;m.adaptive_io_pace=lambda n,rate:None
 for alias in [False,True]:
  manifest=json.loads(json.dumps(base))
  if alias:manifest['_qualified_fuse_alias_context']={'fixture_only_not_production_approval':True}
  out=Capture();m.sys.stdout=out;m.source_archive_send_frozen_v10({'manifest':manifest,'skip':{'archive_objects/tiny':0}},testing=True)
  events=parse(out.buffer.getvalue());fe=next(e for e in events if e['event']=='FILE_END');assert events[-1]['event']=='SOURCE_DONE'
  # This is the existing receiver's semantic join; no bool-field dependency.
  assert [(e['path'],e['size'],e['sha256']) for e in events if e['event']=='FILE_END']==[('archive_objects/tiny',len(payload),hashlib.sha256(payload).hexdigest())]
  if alias:
   assert fe['source_before_after_identity_unchanged'] is None
   assert fe['stable_fields_excluding_FUSE_inode'] is True
   assert fe['policy']=='EXACT_ROOT_FUSE_ALIAS_PLUS_ARCHIVE_AND_MEMBER_SHA'
   assert fe['whole_archive_proof']=='PENDING_UNTIL_SOURCE_DONE'
   tests.append({'name':'actual_alias_length_framed_FILE_END_nullable_full_identity_stable_scope_pending_archive','status':'PASS'})
  else:
   assert fe['source_before_after_identity_unchanged'] is True
   assert all(k not in fe for k in ['stable_fields_excluding_FUSE_inode','policy','whole_archive_proof'])
   tests.append({'name':'actual_nonalias_archive_FILE_END_original_fields_unchanged','status':'PASS'})
  tests.append({'name':'actual_'+('alias' if alias else 'nonalias')+'_SOURCE_DONE_after_fixture_archive_and_member_SHA','status':'PASS'})
  results.append({'alias_fixture':alias,'events':events,'wire_bytes':len(out.buffer.getvalue())})
finally:m.TASK=saved_task;m.sys.stdout=saved_stdout;m.adaptive_io_pace=saved_pace
src=inspect.getsource(m.migrate);assert 'source_before_after_identity_unchanged' not in src and 'stable_fields_excluding_FUSE_inode' not in src
tests.append({'name':'receiver_does_not_consume_old_identity_boolean_or_new_policy_fields','status':'PASS'})
old_ast=ast.parse((O/'candidate_v13/library_copy_v12_nas.py').read_text());new_ast=ast.parse((C/'library_copy_v12_nas.py').read_text())
def func(tree,name):return ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
for name in ['source_send','migrate','install_nas_write_boundary','same_source']:
 assert func(old_ast,name)==func(new_ast,name);tests.append({'name':'R2_AST_unchanged_'+name,'status':'PASS'})
out={'schema':'SM70_V13R2_ACTUAL_LENGTH_FRAMED_CPU_FIXTURE_V1','status':'PASS','tests':tests,'tests_passed':len(tests),'frames':results,'source_archive_payload_read_bytes_production':0,'synthetic_archive_bytes':len(buf.getvalue()),'synthetic_member_bytes':len(payload),'production_locks_or_SOURCE_not_touched':True,'new_transfer_or_qualification':False,'all_fixture_paths_under_private_NAS':True}
(O/'CANDIDATE_V13R2_ACTUAL_FRAME_FIXTURE_V1.json').write_text(json.dumps(out,indent=2)+chr(10))
print(json.dumps({'status':'PASS','actual_frame_tests':len(tests),'synthetic_archive_bytes':len(buf.getvalue())}))

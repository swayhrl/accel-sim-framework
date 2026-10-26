from pathlib import Path
import json,hashlib,ast,copy,subprocess,sys,time,os,importlib.util
O=Path(__file__).parent;C=O/'candidate_v13r2';F=Path('/root/share/mnt164/huangrulin/traces/receipts/sm70_nas_only_alias_resume_20261026_v1/code/d02b914457f8a5cb7857ba5b2c14e7bc739b9e0f2c1867cd2d4a8965c94402a4')
spec=importlib.util.spec_from_file_location('sm70_candidate',C/'library_copy_v12_nas.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
proof=json.loads(Path('/root/share/mnt164/huangrulin/traces/receipts/sm70_source_inode_rebind_qualification_20261026_v1/RESULT.json').read_text());expected=proof['observed_archive_identity'];tests=[]
def check(name,actual,want=True):
 assert actual==want,(name,actual,want);tests.append({'name':name,'status':'PASS','actual':actual,'expected':want})
check('exact_same_identity',m.fuse_alias_metadata_equal(expected,expected))
drift=dict(expected,inode=expected['inode']+123)
check('only_positive_FUSE_inode_drift',m.fuse_alias_metadata_equal(expected,drift))
for k in expected:
 if k=='inode':continue
 changed=copy.deepcopy(expected);v=changed[k];changed[k]=v+1 if isinstance(v,int) else v+'_changed'
 check('reject_metadata_change_'+k,m.fuse_alias_metadata_equal(expected,changed),False)
bad=dict(expected,unexpected=1);check('reject_extra_identity_field',m.fuse_alias_metadata_equal(expected,bad),False)
bad=dict(expected);bad.pop('nlink');check('reject_missing_identity_field',m.fuse_alias_metadata_equal(expected,bad),False)
for value in [0,-1,'97510165',None]:
 bad=dict(expected,inode=value);check('reject_invalid_inode_'+str(value),m.fuse_alias_metadata_equal(expected,bad),False)
orig=m.subprocess.check_output
try:
 for label,src,fs,allowed in [('genuine','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs',True),('wrong_remote','other:/same','fuse.sshfs',False),('wrong_fs','admin-wcx@10.208.130.164:/home/shared','ext4',False)]:
  m.subprocess.check_output=lambda *a,**kw:json.dumps({'filesystems':[{'source':src,'fstype':fs}]})
  try:m._genuine164_archive_mount('/frozen/path');actual=True
  except RuntimeError:actual=False
  check('mount_'+label,actual,allowed)
finally:m.subprocess.check_output=orig
orig_mount=m._genuine164_archive_mount
try:
 m._genuine164_archive_mount=lambda p:True
 manifest={'archive_path':m.EXACT_ARCHIVE_ALIAS_PATH,'archive_sha256':m.EXACT_ARCHIVE_ALIAS_SHA,'_qualified_fuse_alias_context':{'archive_path':m.EXACT_ARCHIVE_ALIAS_PATH,'archive_sha256':m.EXACT_ARCHIVE_ALIAS_SHA,'source_proof_sha256':m.SOURCE_PROOF_SHA,'manifest_sha256':m.EXACT_MANIFEST_SHA}}
 check('approved_context_only_inode_drift',m._approved_archive_same_source(expected,drift,manifest))
 wrong=copy.deepcopy(manifest);wrong['_qualified_fuse_alias_context']['source_proof_sha256']='b'*64
 try:m._approved_archive_same_source(expected,drift,wrong);actual=True
 except RuntimeError:actual=False
 check('reject_unbound_source_proof_context',actual,False)
 check('no_alias_context_keeps_old_strict_inode',m._approved_archive_same_source(expected,drift,{}),False)
 check('synthetic_mode_keeps_old_strict_inode',m._approved_archive_same_source(expected,drift,manifest,testing=True),False)
finally:m._genuine164_archive_mount=orig_mount
p=subprocess.Popen([sys.executable,'-B','-c',"import sys;sys.stderr.write('EXACT_CPU_SENDER_FAILURE_SENTINEL\\n');sys.exit(2)"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
m.start_sender_stderr_capture(p);assert p.stdout.read()==b'';d=m.sender_eof_diagnostic(p)
check('EOF_preserves_real_sender_returncode',d['sender_returncode']==2)
check('EOF_preserves_real_sender_stderr','EXACT_CPU_SENDER_FAILURE_SENTINEL' in d['sender_stderr_utf8']);p.stdout.close();p.stderr.close()
p=subprocess.Popen([sys.executable,'-B','-c',"import os,time;os.close(1);time.sleep(0.2)"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
m.start_sender_stderr_capture(p);assert p.stdout.read()==b'';start=time.monotonic();d2=m.sender_eof_diagnostic(p,wait_seconds=.01)
check('EOF_diagnostic_bounded_if_child_not_yet_exited',time.monotonic()-start<1 and d2['sender_returncode'] is None);p.wait(timeout=2);p.stdout.close();p.stderr.close()
def funcs(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
old=funcs(F/'library_copy_v12_nas.py');new=funcs(C/'library_copy_v12_nas.py')
unchanged=['install_nas_write_boundary','safe','same_source','hash_file','publish_bytes','source_send','verify_tree','verify_committed','restore_native','nas_native_budget']
for name in unchanged:check('AST_unchanged_'+name,old[name]==new[name])
s=(C/'library_copy_v12_nas.py').read_text()
check('retained_range_whole_SHA_gate_preserved',"hash_file(data,gate=g)==c['sha256']" in s)
check('archive_physical_EOF_preserved',"physical[0]==m['archive_identity']['size']" in s)
check('archive_full_SHA_gate_preserved',"archive_hash.hexdigest()==m['archive_sha256']" in s)
check('every_member_whole_SHA_gate_preserved',"offset==row['size'] and h.hexdigest()==row['sha256']" in s)
check('tree_closed_reopened_whole_SHA_gate_preserved',"hash_file(partial,gate=g)==row['sha256']" in s)
check('metadata_preflight_before_all_retained_range_SCAN',s.index("if not testing:qualified_archive_request({'manifest':manifest,'skip':{}})")<s.index('for row in manifest[\'members\']:',s.index('def migrate(')))
check('candidate_has_no_Root_approval_file',not (C/'ROOT_APPROVAL.json').exists())

# Real-predicate CPU mocks exercise qualified_archive_request before any byte reader.
class FakeBytes:
 def __init__(self,raw):self.raw=raw
 def read_bytes(self):return self.raw
saved={k:getattr(m,k) for k in ['EXACT_MANIFEST','EXACT_MANIFEST_SHA','SOURCE_PROOF','SOURCE_PROOF_SHA','read','root_approval','identity','observe_nas_health','install_nas_write_boundary','_genuine164_archive_mount']}
try:
 frozen={'archive_path':m.EXACT_ARCHIVE_ALIAS_PATH,'archive_sha256':m.EXACT_ARCHIVE_ALIAS_SHA,'archive_identity':proof['frozen_archive_identity']}
 fr=json.dumps(frozen,sort_keys=True).encode();fm=FakeBytes(fr);m.EXACT_MANIFEST=fm;m.EXACT_MANIFEST_SHA=hashlib.sha256(fr).hexdigest()
 fp={'status':'PASS_FROZEN_ARCHIVE_WHOLE_SHA_EQUAL_NEW_INODE','manifest_sha256':m.EXACT_MANIFEST_SHA,'manifest_not_modified':True,'Source_KEEP':True,'release_bytes':0,'archive_sha256':frozen['archive_sha256'],'bytes_read':frozen['archive_identity']['size'],'frozen_archive_identity':frozen['archive_identity'],'observed_archive_identity':expected}
 pr=json.dumps(fp,sort_keys=True).encode();pf=FakeBytes(pr);m.SOURCE_PROOF=pf;m.SOURCE_PROOF_SHA=hashlib.sha256(pr).hexdigest()
 current=dict(drift);m.read=lambda p:json.loads(p.read_bytes());m.root_approval=lambda:{'source_alias_approved':True};m.identity=lambda p:dict(current);m.observe_nas_health=lambda:None;m.install_nas_write_boundary=lambda a:None
 m._genuine164_archive_mount=lambda p: True if p==m.EXACT_ARCHIVE_ALIAS_PATH else (_ for _ in ()).throw(RuntimeError('wrong mount or path'))
 request={'manifest':copy.deepcopy(frozen),'skip':{}}
 alias=m.qualified_archive_request(request)
 check('actual_qualified_predicate_allows_only_new_inode',alias['manifest']['archive_identity']==current)
 for key in ['archive_path','archive_sha256','source_host']:
  bad=copy.deepcopy(request);bad['manifest'][key]='changed'
  try:m.qualified_archive_request(bad);allowed=True
  except RuntimeError:allowed=False
  check('actual_qualified_reject_manifest_'+key,allowed,False)
 saved_raw=fm.raw;fm.raw=b'changed manifest bytes'
 try:m.qualified_archive_request(request);allowed=True
 except RuntimeError:allowed=False
 check('actual_qualified_reject_frozen_manifest_bytes_change',allowed,False);fm.raw=saved_raw
 saved_raw=pf.raw;pf.raw=b'changed source proof'
 try:m.qualified_archive_request(request);allowed=True
 except RuntimeError:allowed=False
 check('actual_qualified_reject_source_proof_bytes_change',allowed,False);pf.raw=saved_raw
 for key in ['size','mtime_ns','ctime_ns','dev','uid','gid','mode']:
  current=dict(drift);current[key]+=1
  try:m.qualified_archive_request(request);allowed=True
  except RuntimeError:allowed=False
  check('actual_qualified_reject_stable_metadata_'+key,allowed,False)
 current=dict(drift);m._genuine164_archive_mount=lambda p:(_ for _ in ()).throw(RuntimeError('foreign mount'))
 try:m.qualified_archive_request(request);allowed=True
 except RuntimeError:allowed=False
 check('actual_qualified_reject_mount_change',allowed,False)
finally:
 for k,v in saved.items():setattr(m,k,v)
# More than pipe capacity must drain continuously before stdout protocol EOF.
p=subprocess.Popen([sys.executable,'-B','-c',"import os,sys;os.write(2,b'X'*300000+b'END_BIG_STDERR_SENTINEL');sys.exit(2)"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
m.start_sender_stderr_capture(p);start=time.monotonic();assert p.stdout.read()==b'';diag=m.sender_eof_diagnostic(p);elapsed=time.monotonic()-start
check('large_stderr_no_pipe_deadlock',elapsed<5 and diag['sender_returncode']==2)
check('large_stderr_memory_bounded64KiB',diag['sender_stderr_captured_bytes']<=65536 and diag['sender_stderr_total_bytes']==300023)
check('large_stderr_tail_and_truncation_retained','END_BIG_STDERR_SENTINEL' in diag['sender_stderr_utf8'] and diag['sender_stderr_may_be_truncated'] and diag['sender_stderr_drainer_finished']);p.stdout.close();p.stderr.close()
check('both_sender_spawn_branches_start_continuous_drain',s.count('stderr=subprocess.PIPE);start_sender_stderr_capture(p);p.stdin.write')==2)
check('no_competing_direct_stderr_read_in_receiver',"p.stderr.read()" not in s)

out={'schema':'SM70_PRIVATE_V13_CPU_FIXTURE_RESULT_V1','status':'PASS','tests':tests,'tests_passed':len(tests),'source_archive_payload_read_bytes':0,'retained_range_payload_read_bytes':0,'new_transfer_or_hash_started':False,'new_GPU_or_simulation_started':False,'EOF_exit2_diagnostic':d,'EOF_live_child_bounded_diagnostic':d2,'all_fixture_children_reaped':True,'qualification_scope':'Metadata-only FUSE identity predicates and diagnostics; not archive/body integrity qualification'}
(O/'CANDIDATE_V13R2_CPU_FIXTURE_RESULT_V1.json').write_text(json.dumps(out,indent=2)+chr(10))
print(json.dumps({'status':'PASS','tests':len(tests),'all_fixture_children_reaped':True}))

"""Only private CPU sandbox; no real ledger/module model launch."""
import sys,pathlib,json,hashlib,tempfile,tarfile,io,copy,ast,os
H=pathlib.Path(__file__).resolve().parent;T=H/'package/tools';sys.path.insert(0,str(T))
import ep_perf_common_v2 as c
import ep_perf_native_wv_modes_draft as e
import ep_perf_frontend as f
import ep_perf_postprocess as p
import ep_perf_archive as a
import mode_aware_terminal as parser
rows=[]
def check(label,fn):
 fn();rows.append(dict(label=label,PASS=True))
def rejects(fn):
 try:fn()
 except Exception:return
 raise AssertionError('expected HOLD/rejection')
check('unchanged_parser_all_dependencies',lambda:parser.verify())
check('bounded_two_cohort_engine',lambda:rejects(lambda:e.spec_path('EP_PERF_SCAN_UNAUTHORIZED')))
check('frontend_requires_native',lambda:rejects(lambda:f.main(['experiment','run-native','EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY','--project','EP_L2'])))
os.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'
check('frontend_wrong_cohort_before_authority',lambda:rejects(lambda:f.main(['experiment','inspect','EP_PERF_SCAN_UNAUTHORIZED','--project','EP_L2'])))
check('frontend_unknown_operation_before_authority',lambda:rejects(lambda:f.main(['experiment','retry','EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY','--project','EP_L2'])))
text=(T/'ep_perf_native_wv_modes_draft.py').read_text();tree=ast.parse(text);run=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='run_native')
consume=[x.lineno for x in ast.walk(run)if isinstance(x,ast.Call)and isinstance(x.func,ast.Name)and x.func.id=='transaction'and x.args and isinstance(x.args[0],ast.Constant)and x.args[0].value=='CONSUME_EXACT_ONE_BEFORE_FORK_NO_REFUND'][0]
fork=[x.lineno for x in ast.walk(run)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=='Popen'][0]
check('AST_consume_precedes_only_launcher_fork',lambda:None if consume<fork else (_ for _ in ()).throw(AssertionError()))
with tempfile.TemporaryDirectory(dir=H,prefix='cpu_sandbox_')as tmp:
 root=pathlib.Path(tmp);c.ROOT=root/'runtime';c.NATIVE=root/'native';c.REG=c.NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';c.EPOCH=c.NATIVE/'control/CURRENT_SCIENCE_EPOCH.json'
 (c.REG.parent/'request_history').mkdir(parents=True)
 q=dict(budget=2,remaining=2,consumed={},admitted_specs={},state='ARMED')
 peer=dict(budget=227,remaining=0,consumed={'OLD':dict(state='CLOSED_ACCEPTED')},state='RUNNING')
 reg=dict(registered_future_requests={c.GOAL:q,'OLD':peer},old_source_history=['frozen'],qualification_history=['frozen'],new_scientific_budget_remaining=2,protected='unchanged')
 c.put(c.REG,reg);c.put(c.EPOCH,dict(epoch=2,state='NATIVE_SCIENCE_ACTIVE',holder=os.uname().nodename,native_registry_sha256=c.sha(c.REG),new_budget_remaining=2))
 before=copy.deepcopy(reg)
 def own(reg):reg['registered_future_requests'][c.GOAL]['remaining']-=1;reg['registered_future_requests'][c.GOAL]['consumed']['ONE']=dict(consumed=1)
 c.transaction('CPU_TEST_ONLY',own)
 new=c.read(c.REG)
 check('sandbox_fresh_scope_charge_preserves_old227',lambda:None if new['registered_future_requests']['OLD']==before['registered_future_requests']['OLD']and new['registered_future_requests'][c.GOAL]['remaining']==1 else (_ for _ in ()).throw(AssertionError()))
 def bad(reg):reg['registered_future_requests']['OLD']['remaining']=999
 digest=c.sha(c.REG)
 check('sandbox_foreign_mutation_rejected_before_registry_write',lambda:rejects(lambda:c.transaction('BAD_CPU_TEST_ONLY',bad)))
 assert c.sha(c.REG)==digest
 for name in ['safe_member']:
  check('archive_path_escape_rejected',lambda:rejects(lambda:a.safe_member('../escape')))
 blob=b'bounded SourceKEEP fixture\n';src=root/'fixture.tar'
 with tarfile.open(src,'w')as stream:
  member=tarfile.TarInfo('nested/fixture.txt');member.size=len(blob);stream.addfile(member,io.BytesIO(blob))
 st=src.stat();row=dict(member='nested/fixture.txt',bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),mode=0o600,uid=os.getuid(),gid=os.getgid(),mtime_ns=1234567890000000000,atime_ns=1234567890000000000)
 mf=root/'manifest.json';c.put(mf,dict(archive_sha256=c.sha(src),members=[row]))
 check('actual_fresh_native_restore_SHA_and_metadata',lambda:a.restore(src,mf,root/'fresh_target',len(blob)))
 check('restore_byte_limit_negative',lambda:rejects(lambda:a.restore(src,mf,root/'bad_target',len(blob)-1)))
 check('restore_existing_target_negative',lambda:rejects(lambda:a.restore(src,mf,root/'fresh_target',len(blob))))
 badmf=root/'bad_manifest.json';c.put(badmf,dict(archive_sha256='0'*64,members=[row]))
 check('restore_archive_SHA_negative',lambda:rejects(lambda:a.restore(src,badmf,root/'bad_sha',len(blob))))
 # Closed row is idempotently observed; no archive/model/charge path.
 p.authority=lambda:(dict(registered_future_requests={p.GOAL:dict(consumed={'CLOSED':dict(state='CLOSED_ACCEPTED')})}),{})
 check('postprocess_closed_row_idempotent',lambda:None if p.postprocess('CLOSED')['already_closed'] else (_ for _ in ()).throw(AssertionError()))
result=dict(status='PASS_PRIVATE_CPU_ACTIVATION_AND_ARCHIVE_COMPONENT_CONTROLS',checks=rows,count=len(rows),model_starts=0,real_registry_writes=0,original_tools_modified=False,application_NI='NOT_EXECUTED',parser_application_positive='NOT_EXECUTED',scope='new activation deltas; preserves prior full Host/parser synthetic controls as frozen evidence')
(H/'CPU_ACTIVATION_CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

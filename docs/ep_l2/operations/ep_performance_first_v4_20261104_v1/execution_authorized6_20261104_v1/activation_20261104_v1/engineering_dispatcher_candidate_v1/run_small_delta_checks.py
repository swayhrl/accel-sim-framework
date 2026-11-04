from pathlib import Path
import ast,copy,fcntl,hashlib,importlib.util,json,os,sys,time,subprocess
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;p=O/'finite_main_exact6_candidate.py'
ast.parse(p.read_text());sp=importlib.util.spec_from_file_location('candidate_exact6_delta_only',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def dump(p,d):Path(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
points=[dict(group='A1',cohort='A1_S',mode='S'),dict(group='A1',cohort='A1_WV',mode='WV_ZERO_RO'),dict(group='A3',cohort='A3_S',mode='S'),dict(group='A3',cohort='A3_WV',mode='WV_ZERO_RO'),dict(group='B',cohort='B_W',mode='W_ONLY'),dict(group='B',cohort='B_WV',mode='WV_ZERO_RO')]
initial=m.stage_decisions(points,{},{});assert [c for c,d in initial.items()if d['status']=='WAIT']==['B_WV'];assert sum(d['status']=='RELEASE'for d in initial.values())==5
rows={'B_W':dict(state='CLOSED_ACCEPTED')}
for view in [dict(accepted=True,archived=False,two_restores_complete=False),dict(accepted=True,archived=True,two_restores_complete=False)]:
 assert m.stage_decisions(points,rows,{'B_W':view})['B_WV']['status']=='WAIT'
release=m.stage_decisions(points,rows,{'B_W':dict(accepted=True,archived=True,two_restores_complete=True)});assert release['B_WV']['status']=='RELEASE'
failed=m.stage_decisions(points,{'B_W':dict(state='CLOSED_UNACCEPTED')},{})
assert failed['B_WV']['status']=='HOLD'and all(failed[c]['status']=='RELEASE'for c in ['A1_S','A1_WV','A3_S','A3_WV'])
consumed=m.stage_decisions(points,{'A1_S':dict(state='UNACCEPTED_ENGINEERING_FAILURE')},{})
assert consumed['A1_S']['status']=='CONSUMED'
assert m.concurrency_capacity(9,5)and not m.concurrency_capacity(10,0)and not m.concurrency_capacity(0,10)
# Verify inherited structure consumed by E.poll/group_call/claim/closed_view.
source=Path(m.PREV).read_text();tree=ast.parse(source);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='Executor')
funcs={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
poll=ast.get_source_segment(source,funcs['poll']);assert "v['log']"in poll and "v['log_path']"in poll and "v['process']"in poll
assert set(['CLOSED_ACCEPTED','CLOSED_UNACCEPTED'])<=set(m.TERMINAL)
# CPU delta: avoid both fresh actual snapshot occupancy and own pending/running CPU.
obj=m.Executor.__new__(m.Executor);cpus=sorted(os.sched_getaffinity(0));assert len(cpus)>=3
obj.m=dict(host_cpu_candidates=cpus[:3]);obj.running={'pending':dict(cpu=cpus[1])}
snapshot=dict(current_request=m.REQUESTS['A1'],occupied_model_or_claim_cpus=[cpus[0]],foreign_metadata_errors=[])
obj.group_call=lambda *a,**k:subprocess.CompletedProcess([],0,json.dumps(snapshot),'')
cpu,_=obj.available_cpu(dict(group='A1',cohort='A1_S'));assert cpu==cpus[2]
# Missing schema rejects before inherited writer, without opening any approved claim file.
written=[];original=m.E.Executor.claim;m.E.Executor.claim=lambda *a:written.append(True)
obj.group_call=lambda *a,**k:subprocess.CompletedProcess([],2,'','missing required runtime fields: host_cpu')
try:obj.claim(dict(group='A1',cohort='A1_S'),cpus[0])
except Exception as exc:assert 'PRECLAIM_SCHEMA_OR_SCOPE_HOLD'in str(exc)
else:raise AssertionError('missing schema claim accepted')
assert not written
m.E.Executor.claim=original
# Asynchronous accept never calls wait and keeps outer lock only in the Main process.
F=O/'delta_fixture';F.mkdir(exist_ok=True);(F/'native_logs').mkdir(exist_ok=True)
class Fake:
 pid=99999999
 def __init__(self):self.rc=None
 def poll(self):return self.rc
 def wait(self,*a,**k):raise AssertionError('scheduler blocked on archive child')
fake=Fake();obj.accepting=None;obj.pending_accept=['B_W'];obj.C=F;obj.m={'accept_serial_lock':str(F/'ACCEPT.lock')};obj.native=lambda *a,**k:fake;obj.event=lambda *a,**k:None;obj.states={}
obj.accept_one();assert obj.accepting and obj.accepting['cohort']=='B_W'
fd=obj.accepting['lock'].fileno();assert fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC
other=(F/'ACCEPT.lock').open('a+b')
try:fcntl.flock(other,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:lockheld=True
else:raise AssertionError('parent async lock was not held')
other.close()
obj.poll_accept();assert obj.accepting is not None
fake.rc=0;obj.rows=lambda:({},dict(B_W=dict(state='CLOSED_UNACCEPTED')));obj.closed_view=lambda c,r:dict(archived=True,accepted=False,two_restores_complete=True)
obj.poll_accept();assert obj.accepting is None
receipt=dict(schema='EP_PFV4_EXACT6_DISPATCHER_SMALL_DELTA_CHECKS_V1',status='PASS',executor_ref=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),AST_and_import_PASS=True,initial_independent_release_count=5,only_initial_wait='B_WV',B_requires_W_CLOSED_ACCEPTED_full_archive_two_distinct_restores=True,B_failure_does_not_block_A1_A3=True,consumed_failure_never_reforks=True,globalcap10_boundaries_PASS=True,actual_snapshot_and_pending_CPU_avoidance_PASS=True,claim_schema_precedes_inherited_writer=True,inherited_running_keys=['process','log','log_path','cpu'],inherited_group_call_requires='manifest groups[g].runtime_root',inherited_TERMINAL=list(m.TERMINAL),async_accept_no_wait=True,outer_accept_lock_parent_held_FD_CLOEXEC=True,real_native_calls=0,real_model_forks=0,real_registry_or_claim_writes=0,old_engineering_suites_rerun=0,automatic_Git_publication=False)
dump(O/'SMALL_DELTA_CHECKS.json',receipt);print(json.dumps(receipt))


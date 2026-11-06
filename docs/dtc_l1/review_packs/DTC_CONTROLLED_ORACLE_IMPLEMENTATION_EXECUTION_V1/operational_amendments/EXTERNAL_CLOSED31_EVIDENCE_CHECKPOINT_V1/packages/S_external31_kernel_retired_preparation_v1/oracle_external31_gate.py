"""External closed31 admission after actual kernel retirement, not science.

Inert import. No ptrace, signal, owner function call, exec, model or mutation.
Unresolved ONCE is permitted ONLY under this exact retired-kernel evidence and
Root's no-tracer-progress single-pass release; it never grants B/new science.
"""
from pathlib import Path
import hashlib,json,os,re,time
BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1')
ROOT=BASE/'initial8';OWNER=1498278;START=977758783;TRACER=438646
GOV=BASE/'control/OWNER_RECOVERY_AND_CLOSEOUT.lock'
REQUEST='DTC_ORACLE_INITIAL8_20261106_V1'
IMAGE_SHA='3f1f097bf58b22fc8d5688d4e4c2402e04925d8b61dac5ef2129e43c5817a23e'
S17_SHA='d0d344e4dc50e299d5f72fb361ce5856f4c2960ea4132c5424f43c80cc13b507'
RAW_SHA='3c0a592fe2e15a8b6f2f39801765b9a26e1f1dc5fc9203408a9a33666db5806e'
BOUNDARY_SHA='c6dde4c16aee52820e81397d6ada96ab799dc75c4aa77f930f2b8fe7138e63b8'
HOST_KERNEL='6.8.0-45-generic'
class Hold(RuntimeError):pass
def need(x,reason):
 if not x:raise Hold(reason)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def pin(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p));return p
def start(pid):return int(Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19])
def field(text,name):
 match=re.search('^'+re.escape(name)+r':\s*(.*?)\s*$',text,re.M)
 need(match is not None,'MISSING_PROC_FIELD:'+name);return match.group(1)

def fresh_kernel():
 p=Path('/proc',str(OWNER));before=sorted(int(x.name)for x in(p/'task').iterdir())
 tasks=[]
 for tid in before:
  t=p/'task'/str(tid);status=(t/'status').read_text()
  tasks.append(dict(tid=tid,state=field(status,'State').split()[0],wchan=(t/'wchan').read_text().strip(),
                    start_ticks=int((t/'stat').read_text().rsplit(')',1)[1].split()[19])))
 after=sorted(int(x.name)for x in(p/'task').iterdir());need(before==after,'TASK_SET_CHANGED_DURING_SNAPSHOT')
 tracer=Path('/proc',str(TRACER));ts=(tracer/'status').read_text();ownerstatus=(p/'status').read_text()
 return dict(owner_pid=OWNER,owner_start_ticks=start(OWNER),kernel_release=os.uname().release,
             tasks=tasks,task_ids_before=before,task_ids_after=after,
             syscall=(p/'syscall').read_text(),kernel_stack=(p/'stack').read_text(),
             owner_tracer_pid=int(field(ownerstatus,'TracerPid')),
             tracer_pid=TRACER,tracer_start_ticks=start(TRACER),tracer_state=field(ts,'State'),
             tracer_wchan=(tracer/'wchan').read_text().strip(),
             tracer_cmdline_sha256=hashlib.sha256((tracer/'cmdline').read_bytes()).hexdigest(),
             observed_monotonic_ns=time.monotonic_ns(),process_or_tracer_actions=0)

def validate_kernel_snapshot(facts,boundary,expected_tracer):
 need(facts['kernel_release']==HOST_KERNEL,'ACTUAL_REVIEWED_HOST_KERNEL_RELEASE')
 need(facts['owner_pid']==OWNER and facts['owner_start_ticks']==START,'ORIGINAL_OWNER_PID_START')
 expected={x['tid']for x in boundary['tasks']};observed={x['tid']for x in facts['tasks']}
 need(len(expected)==103 and len(observed)==len(facts['tasks'])==103 and observed==expected,
      'EXACT_FRESH_103_TASKS_REQUIRED')
 need(facts['task_ids_before']==facts['task_ids_after']==sorted(expected),'FRESH_TASK_SET_STABILITY')
 need(all(x['state']=='Z'for x in facts['tasks']if x['tid']!=OWNER),'OLD_PYTHON_ARCHIVE_THREAD_STILL_RUNNABLE')
 need(next(x for x in facts['tasks']if x['tid']==OWNER)['wchan']=='de_thread','OWNER_NOT_IN_DETHREAD')
 need(facts['syscall'].split()[0]=='59'and facts['syscall'].split()[1:4]==boundary['observed_syscall'].split()[1:4],
      'ORIGINAL_INFLIGHT_EXEC59_PAYLOAD_POINTERS_REQUIRED')
 need(all(x in facts['kernel_stack']for x in ['de_thread+','begin_new_exec+','__x64_sys_execve+']),
      'COMMITTED_KERNEL_EXEC_STACK_REQUIRED')
 need(facts['owner_tracer_pid']==facts['tracer_pid']==TRACER
      and facts['tracer_start_ticks']==expected_tracer['start_ticks']
      and facts['tracer_cmdline_sha256']==expected_tracer['cmdline_sha256'],'ORIGINAL_TRACER_IDENTITY')
 return dict(status='PASS_FRESH_KERNEL_RETIREMENT_FACTS_NOT_SCIENCE_GRANT',old_python_tasks_zombie=102,
             old_archive_408874_zombie=next(x['state']=='Z'for x in facts['tasks']if x['tid']==408874),
             tracer_sleep_park_supplemental=facts['tracer_wchan']=='hrtimer_nanosleep')

def verify_governance_fd(context,expected_path):
 need(context['governance_lock']==str(expected_path),'SAME_GLOBAL_GOVERNANCE_PATH')
 fd=context['governance_lock_fd'];st=os.fstat(fd)
 info=Path('/proc/self/fdinfo',str(fd)).read_text()
 need([st.st_dev,st.st_ino]==context['governance_lock_device_inode']
      and os.readlink('/proc/self/fd/'+str(fd))==str(expected_path)
      and re.search(r'FLOCK\s+\S+\s+WRITE\s+'+str(os.getpid())+r'\s',info),
      'REAL_CALLER_HELD_GOVERNANCE_EX_FLOCK')
 return dict(actual_caller_PID=os.getpid(),actual_EX_flock=True,device=st.st_dev,inode=st.st_ino)

def inspect_retirement_basis(config):
 """Pure read of real evidence; does not itself authorize any closure."""
 boundary=rd(pin(config['kernel_boundary_proof']));need(config['kernel_boundary_proof']['sha256']==BOUNDARY_SHA,'EXACT_D_FACTUAL_BOUNDARY')
 manifest=rd(pin(config['future_image_manifest']));image=pin(manifest['image'])
 need(manifest['image']['sha256']==IMAGE_SHA and manifest['owner']==dict(pid=OWNER,start_ticks=START)
      and manifest['phase']=='CLOSEOUT_A_NO_SCIENTIFIC_START'and manifest['postprocess_workers']==1,
      'ONLY_FROZEN_3F1_CLOSEOUT_IMAGE_ALLOWED')
 for ref in manifest['source_pins']:pin(ref)
 image_review=rd(pin(manifest['independent_review']))
 need(image_review['status']=='PASS'and image_review['subject_source_sha256']==IMAGE_SHA
      and image_review['scope']=='SAME_PID_EXEC_OWNER_CLOSEOUT_A','FROZEN_IMAGE_INDEPENDENT_QUALIFICATION')
 image_source=image.read_text()
 # Actual exact3f1 source, not an invented alternate image: this is its tested
 # same-GOV busy-retry path, plus the unchanged S17 session's acquired flock.
 need("transient=isinstance(e,BlockingIOError)"in image_source
      and "getattr(module,adapter.get('class','CloseoutSession'))(adapter['config'])"in image_source,
      'FUTURE_IMAGE_MUST_WAIT_FOR_SAME_SESSION_MUTEX')
 cfg=manifest['consumer_adapter']['config']
 pin(manifest['consumer_adapter'])
 need(cfg['governance_lock']==str(GOV)and cfg['new_scientific_starts']==0
      and manifest['consumer_adapter']['sha256']==S17_SHA,'FUTURE_IMAGE_SAME_GOV_ZERO_SCIENCE')
 request=rd(pin(config['raw_exec_request']));pin(request['raw_helper'])
 need(request['raw_helper']['sha256']==RAW_SHA and request['owner']==manifest['owner']
      and request['CPU_fixture_only']is False,'EXACT_NATIVE_PAYLOAD_SOURCE_REQUIRED')
 need(request['argv'][:4]==['/usr/bin/python3','-I','-S','-B']and request['argv'][4]==str(image)
      and request['argv'][-1]==config['future_image_manifest']['sha256']
      and request['preserve_fds']==manifest['preserve_fds'],'ORIGINAL_PAYLOAD_ENTERS_ONLY_QUALIFIED_IMAGE')
 journal=rd(pin(config['inflight_raw_journal']));once=rd(pin(config['global_ONCE']))
 need(journal['schema']=='DTC_PRODUCTION_NATIVE_RAW_EXEC_JOURNAL_V1'
      and journal['owner_pid']==OWNER and journal['owner_start_ticks']==START
      and journal['inferior_C_or_Python_function_calls']==0 and journal['automatic_retry']is False
      and 'EXECVE_REGISTERS_PREPARED_ONE_ATTEMPT'in journal['stages'], 'ORIGINAL_EXEC_JOURNAL_NOT_A_NEW_ATTEMPT')
 need(journal['argv_sha256']==hashlib.sha256(b'\0'.join(x.encode()for x in request['argv'])+b'\0').hexdigest()
      and journal['environment_sha256']==request['private_environment']['sha256'], 'ORIGINAL_PAYLOAD_ARGV_ENV_BINDING')
 need(once['actual_image_PID']==OWNER and once['actual_image_start']==START
      and once['image_manifest_sha256']==config['future_image_manifest']['sha256']
      and once['release_sha256']==request['Main_release']['sha256'],'GLOBAL_ONCE_ORIGINAL_TRANSITION_BINDING')
 need(config['inflight_raw_journal']==boundary['journal_pin'],'EXACT_REVIEWED_INFLIGHT_JOURNAL_REQUIRED')
 facts=fresh_kernel();predicate=validate_kernel_snapshot(facts,boundary,config['original_tracer'])
 return dict(schema='EXTERNAL31_READONLY_RETIREMENT_BASIS_V1',status='READONLY_FACTS_ONLY_NOT_EXECUTION_RELEASE',
             predicate=predicate,facts=facts,config_pins={k:config[k]for k in ['kernel_boundary_proof','future_image_manifest','raw_exec_request','inflight_raw_journal','global_ONCE']},
             future_image_waits_on_same_governance=True,new_scientific_starts_permitted=False)

def verify_closeout_admission(context,config):
 """S17 hook: acquire GOV first, then fresh every cohort; no owner substitute."""
 need(context['execution_mode']=='EXTERNAL_POSTPROCESS_ONLY'and context['request']==REQUEST
      and context['stage_root']==str(ROOT)and context['caller_pid']==os.getpid()!=OWNER
      and context['caller_start_ticks']==start(os.getpid()),'EXTERNAL_CLOSED_ONLY_ACTUAL_CALLER')
 verify_governance_fd(context,GOV)
 auth=rd(pin(config['authorization']))
 need(auth['status']=='AUTHORIZED_CLOSED_ONLY'and auth['scope']=='EXTERNAL_FIXED31_KERNEL_RETIRED_SINGLE_PASS'
      and auth['execution_mode']=='EXTERNAL_POSTPROCESS_ONLY'and auth['runner_sha256']==S17_SHA
      and auth['admission_verifier']==dict(path=__file__,sha256=sha(__file__)),'EXACT_MAIN_CLOSED31_SOURCE_RELEASE')
 need(auth['no_owner_or_tracer_advancement_until_driver_exits']is True
      and auth['pending_ONCE_exception_closed_only']is True
      and auth['new_scientific_starts']==auth['new_scientific_requests']==0
      and auth['not_a_scientific_owner_or_B_release']is True,'MAIN_CONTROL_ACTION_EXCLUSION_NOT_SCIENCE_AUTHORITY')
 need(auth['fixed31_snapshot']==config['fixed31_snapshot']and auth['kernel_boundary_proof']==config['kernel_boundary_proof']
      and auth['future_image_manifest']==config['future_image_manifest']and auth['raw_exec_request']==config['raw_exec_request']
      and auth['inflight_raw_journal']==config['inflight_raw_journal']and auth['global_ONCE']==config['global_ONCE'],
      'MAIN_RELEASE_ALL_ACTUAL_PROOF_BINDINGS')
 review=rd(pin(config['independent_review']))
 need(review['status']=='PASS'and review['scope']=='EXTERNAL31_KERNEL_RETIRED_CLOSED_ONLY'
      and review['subject_verifier_sha256']==sha(__file__)and review['S17_source_sha256']==S17_SHA
      and review['subject_driver_sha256']==auth['driver_source_sha256'],
      'INDEPENDENT_KERNEL_EXCEPTION_AND_SOURCE_REVIEW_REQUIRED')
 snapshot=rd(pin(config['fixed31_snapshot']))
 need(len(snapshot['rows'])==len({x['cohort']for x in snapshot['rows']})==31
      and set(auth['authorized_closed_cohorts'])=={x['cohort']for x in snapshot['rows']},'FIXED31_ONCE_NO_LATER_TAIL_ADMISSION')
 basis=inspect_retirement_basis(config);now=time.monotonic_ns()
 return dict(status='PASS',request=REQUEST,governance_lock=str(GOV),caller_pid=os.getpid(),caller_start_ticks=start(os.getpid()),
             execution_mode='EXTERNAL_POSTPROCESS_ONLY',original_closer_threads_excluded=True,owner_recovery_excluded=True,
             new_scientific_starts_permitted=False,independent_quiescence_or_retirement_review='PASS',
             observed_monotonic_ns=now,valid_until_monotonic_ns=now+30*10**9,
             kernel_retirement_basis=basis,pending_ONCE_exception='CLOSED31_ONLY_NO_OWNER_OR_TRACER_FORWARD',
             actual_target_or_tracer_actions=0,scientific_requests_registered=0)

if __name__=='__main__':print(json.dumps(dict(status='CPU_PREPARATION_ONLY_NO_ACTION')))

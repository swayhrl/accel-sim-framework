"""Isolated actual frozen AST dispatch counterexample; no fork/ptrace/signals.

This is NOT a forced kernel PID-reuse test or whole-guard qualification. It
executes the unchanged retire/stop dispatch fragment with declared synthetic
wait statuses; resume/capture/ptrace/image are recording stubs only.
"""
from common import *
from mapping_roles import require
import ast,signal,io,types

def main():
 source=PACK/'tools/guarded_process.py';text=source.read_text();tree=ast.parse(text)
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_guarded')
 loop=next(n for n in ast.walk(fun) if isinstance(n,ast.While) and isinstance(n.test,ast.Name) and n.test.id=='alive')
 first=next(i for i,n in enumerate(loop.body) if isinstance(n,ast.If) and ast.unparse(n.test)=='child not in owned')
 fragment=loop.body[first:]
 synthetic_pid=12345;root=11111;calls=[]
 states={synthetic_pid:dict(exe='/usr/bin/cat',closed=True)}
 owned={root,synthetic_pid};confirmed={root:dict(start_ticks=10),synthetic_pid:dict(start_ticks=11)}
 ns=dict(os=os,signal=signal,json=json,require=require,now=now,Path=Path,ctypes=__import__('ctypes'),time=__import__('time'),pid=root,owned=owned,states=states,alive={root,synthetic_pid},exits={},ownership=types.SimpleNamespace(confirmed=confirmed),quarantined=[],parents={},main_rc=None,eventlog=io.StringIO())
 for name in ['resume','capture','ptr','image']:
  ns[name]=(lambda name:lambda *a,**kw:calls.append(dict(call=name,args=list(a),kwargs=kw)))(name)
 wrapper=ast.Module(body=[ast.For(target=ast.Tuple(elts=[ast.Name(id='child',ctx=ast.Store()),ast.Name(id='status',ctx=ast.Store())],ctx=ast.Store()),iter=ast.Name(id='synthetic_waits',ctx=ast.Load()),body=fragment,orelse=[])],type_ignores=[])
 ast.fix_missing_locations(wrapper)
 ns['synthetic_waits']=[(synthetic_pid,0),(synthetic_pid,(signal.SIGSTOP<<8)|0x7f)]
 exec(compile(wrapper,str(source)+':ISOLATED_FROZEN_DISPATCH_AST','exec'),ns)
 unexpected=[c for c in calls if c['call']=='resume' and c['args']==[synthetic_pid]]
 assert synthetic_pid in owned and synthetic_pid in states and synthetic_pid not in confirmed and unexpected
 result=dict(status='FAIL_REQUIRED_FAIL_CLOSED_RETIRED_PID_DISPATCH',source_sha256=sha(source),source_start_line=fragment[0].lineno,source_end_line=fragment[-1].end_lineno,fragment_is_unchanged_frozen_AST=True,synthetic_waits='exit0 retirement then fresh-generation SIGSTOP before parent event',PID_and_status_synthetic=True,kernel_PID_reuse_forced=False,whole_guard_qualification=False,process_creation_ptrace_or_signal_calls=0,simulator_starts=0,owned_retains_retired_PID=synthetic_pid in owned,states_retains_retired_PID=synthetic_pid in states,confirmed_no_longer_contains_retired_PID=synthetic_pid not in confirmed,unexpected_unconfirmed_resume_calls=unexpected,all_stub_calls=calls,actual_PID_reuse_in_performance='NOT_ESTABLISHED',finding='The real frozen retire/dispatch control-flow resumes this synthetic fresh stop without fresh parent-event/PID-start_ticks confirmation. Direct classify() negative was insufficient.')
 write(RAW/'RETIRED_PID_FROZEN_AST_COUNTEREXAMPLE.json',result,exclusive=True)
 write(PACK/'RETIRED_PID_FROZEN_AST_COUNTEREXAMPLE.json',result)
 print(result['status'])
if __name__=='__main__':main()

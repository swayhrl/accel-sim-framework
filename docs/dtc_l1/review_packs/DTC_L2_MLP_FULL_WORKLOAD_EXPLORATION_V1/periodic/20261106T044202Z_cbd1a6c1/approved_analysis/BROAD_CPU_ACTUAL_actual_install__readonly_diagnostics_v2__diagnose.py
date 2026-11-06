from pathlib import Path
import sys,os,json,datetime
def apply(directory):
 assert os.getpid()==1498278 and int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];s=main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1;frame=s['frame'];a=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED;b=main.DTC_STRACE_BROAD_SHARED_DISPATCH_V1;t=main.DTC_FUTURE_MEMORY_AGING_FACADE_095_V1;g=t.coupling['gate'];q=s['engine'].registered()[2]
 def safe(x,depth=0):
  if x is None or isinstance(x,(int,float,bool,str)):return x
  if depth>4:return repr(x)[:500]
  if isinstance(x,dict):return {str(k):safe(v,depth+1)for k,v in x.items()}
  if isinstance(x,(list,tuple,set)):return [safe(v,depth+1)for v in x]
  return repr(x)[:500]
 stack=[];f=sys._current_frames()[main.DTC_L2_MLP_ADDON_THREAD.ident]
 while f and len(stack)<12:stack.append(dict(function=f.f_code.co_name,file=f.f_code.co_filename,line=f.f_lineno));f=f.f_back
 d=getattr(a.state,'last_decision',{})or{};v=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='READONLY_ACTUAL_MAIN_BROAD_RUNTIME_DIAGNOSTICS_V2',phase=s['phase'],main_armed=s['armed'],B_armed=b['armed'],B_last_hold=b.get('last_hold'),B_last_proof_present=b.get('last_proof')is not None,leaf_installed=a.original is b['leaf'],owner_frame_last_issue=s['owner_frame_state'].get('last_issue'),owner_frame_enabled=s['owner_frame_state']['enabled'],owner_frame_reference_installed=t.facade.resources is s['owner_frame_state']['wrapper'],owner_frame_witnesses=s['owner_frame_state'].get('eligible_pending_witnesses'),IR_reader_status=s['IR_hooks']['reader'].last_status,IR_reader_issue=s['IR_hooks']['reader'].last_issue,guard_attribute_names=list(g.__dict__),guard_last_issue=getattr(g,'last_issue',None),RuntimeFrames_last_issue=getattr(t.frames,'last_issue',None),RuntimeFrames_attribute_names=list(t.frames.__dict__),aging_last_phase=d.get('phase'),aging_protected_bytes=getattr(a.state,'protected',None),pending_count=len(frame.f_locals.get('pending',[])),claims_count=len(frame.f_locals['claims']),claims=frame.f_locals['claims'],running=list(frame.f_locals['running'].values()),scheduler_stack=stack,budget=q['budget'],remaining=q['remaining'],models_started=0)
 text=json.dumps(safe(v),sort_keys=True,indent=2)+'\n';p=Path(directory)/'ACK.json'
 with p.open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
 return dict(path=str(p),status=v['status'])

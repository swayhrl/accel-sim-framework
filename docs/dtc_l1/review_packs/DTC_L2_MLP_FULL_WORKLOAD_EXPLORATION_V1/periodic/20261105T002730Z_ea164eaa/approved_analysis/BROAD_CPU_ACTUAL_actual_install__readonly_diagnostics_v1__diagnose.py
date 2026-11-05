from pathlib import Path
import sys,os,json,datetime
def apply(directory):
 assert os.getpid()==1498278 and int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];s=main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1;frame=s['frame'];a=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED;b=getattr(main,'DTC_STRACE_BROAD_SHARED_DISPATCH_V1');t=main.DTC_FUTURE_MEMORY_AGING_FACADE_095_V1;g=t.coupling['gate'];q=s['engine'].registered()[2]
 def obj(x):return x.__dict__ if hasattr(x,'__dict__')else x
 v=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='READONLY_ACTUAL_MAIN_BROAD_RUNTIME_DIAGNOSTICS',phase=s['phase'],main_armed=s['armed'],B_armed=b['armed'],B_last_hold=b.get('last_hold'),B_last_proof_present=b.get('last_proof')is not None,owner_frame_last_issue=s['owner_frame_state'].get('last_issue'),owner_frame_witnesses=s['owner_frame_state'].get('eligible_pending_witnesses'),IR_reader_status=s['IR_hooks']['reader'].last_status,IR_reader_issue=s['IR_hooks']['reader'].last_issue,aging_state=obj(a.state),aging_last_decision=getattr(a.state,'last_decision',None),guard_attributes={k:obj(v)for k,v in g.__dict__.items()if k not in ['aging','original','wrapper','original_provider','prior_provider','original_choose','owner','frames','runtime_frames']},RuntimeFrames_attributes={k:obj(v)for k,v in t.frames.__dict__.items()if k in ['last_issue','last_frame','last_status']},pending=[dict(cohort=x['cohort'],program=x['program'],profile=x['profile'],cell=x['cell'])for x in frame.f_locals.get('pending',[])],claims=frame.f_locals['claims'],running=list(frame.f_locals['running'].values()),cool=frame.f_locals.get('cool'),budget=q['budget'],remaining=q['remaining'],callbacks_queued_by_diagnostic=0,models_started=0)
 p=Path(directory)/'ACK.json'
 with p.open('x')as f:json.dump(v,f,sort_keys=True,indent=2,default=repr);f.write('\n');f.flush();os.fsync(f.fileno())
 return dict(path=str(p),status=v['status'])

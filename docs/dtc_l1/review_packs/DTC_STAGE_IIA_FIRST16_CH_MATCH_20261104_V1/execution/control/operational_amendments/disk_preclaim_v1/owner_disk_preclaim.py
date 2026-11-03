"""Owner-private disk-before-claim admission; no model, spec or authority mutation."""
from pathlib import Path
import sys,os,threading,json,hashlib,datetime
P=Path;R=P('/root/data/dtc_stage_iia_first16_20261104_v1')
MARKER='DTC_STAGEII_FIRST16_DISK_PRECLAIM_V1'
def gated_choose(original,resource,pending,sample,claims,**kwargs):
    choice=original(pending,sample,claims,**kwargs)
    if choice is None:return None
    matches=[s for s in pending if s['cohort']==choice['cohort']]
    assert len(matches)==1,'PRECLAIM_CANDIDATE_NOT_EXACT'
    admission=resource(matches[0],True)
    if not all(admission.get(k) is True for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass']):return None
    return choice
def apply(directory):
    assert os.getpid()==1498278 and threading.current_thread()is threading.main_thread()
    assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
    main=sys.modules['__main__'];state=getattr(main,'DTC_STAGEII_FIRST16_OWNER_ADDON_V1');assert state['phase']=='ACKED' and not hasattr(main,MARKER)
    th=state['thread'];assert th.is_alive()and th.name=='DTC_STAGEII_FIRST16_ONLY'
    frame=sys._current_frames()[th.ident]
    while frame is not None and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/stage2_ops.py'):frame=frame.f_back
    assert frame is not None
    res=frame.f_locals['res'];held=frame.f_locals['lock'];original=res.choose_dispatch
    assert P(original.__code__.co_filename)==R/'tools/stage2_resources.py'
    plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes())
    for pin in plan['source_pins']:assert hashlib.sha256(P(pin['path']).read_bytes()).hexdigest()==pin['sha256']
    # Take only the new first16 scheduler RLock, not either retained global owner lock.
    # This changes future admission only; existing model workers remain untouched.
    with held:
        q=frame.f_locals['e'].registered()[2]
        before=dict(budget=q['budget'],remaining=q['remaining'],consumed_UUIDs={k:v['uuid']for k,v in q['consumed'].items()})
        assert q['budget']==16
        def wrapper(pending,sample,claims,**kwargs):return gated_choose(original,res.resources,pending,sample,claims,**kwargs)
        receipt=dict(schema='DTC_STAGEII_FIRST16_DISK_PRECLAIM_AMENDMENT_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,source_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),execution_plan_sha256=hashlib.sha256((R/'control/EXECUTION_PLAN.json').read_bytes()).hexdigest(),source_pins_unchanged=True,before=before,science_engine_spec_guard_and_model_identity_unchanged=True,existing_models_signaled=0,new_authority_grants=0,new_dispatchers=0,only_adds_disk_check_before_future_claim=True)
        # Source, receipt and previous callable remain retained by the owner marker.
        setattr(main,MARKER,dict(original=original,wrapper=wrapper,receipt=receipt))
        res.choose_dispatch=wrapper
        p=P(directory)/'APPLIED.json'
        with p.open('x')as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
        return receipt

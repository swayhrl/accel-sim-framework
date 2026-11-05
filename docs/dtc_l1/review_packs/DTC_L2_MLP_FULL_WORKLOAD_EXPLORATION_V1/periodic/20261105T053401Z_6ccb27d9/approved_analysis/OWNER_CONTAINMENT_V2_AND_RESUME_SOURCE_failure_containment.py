"""Exact engineering-only failure guards. No action until explicitly called."""
import copy

def verify_old_consumption(before,after):
    """A real old model may append its natural receipt during installation."""
    for cohort,old in before.items():
        current=after[cohort]
        assert current['uuid']==old['uuid']
        assert all(current.get(k)==v for k,v in old.items()),'OLD_CONSUMPTION_REWRITTEN'
        assert set(current)-set(old)<= {'execution_receipt'},'UNKNOWN_OLD_CONSUMPTION_EXTENSION'
    return True

def install_execution_guards(frame,cohorts,engine,reason):
    """Guard both global call sites before cleanup can change older routes.

    The owner must hold its aging lock. A stale pending/decision can still
    reach safe()/worker(), so removing the reader is insufficient.
    """
    allowed=frozenset(cohorts);assert len(allowed)==4
    old_safe=frame.f_globals['safe'];old_worker=frame.f_globals['worker']
    evidence=dict(cohorts=sorted(allowed),reason=reason,model_starts=0,automatic_spent_retry=False)
    def hold(c):
        try:
            consumed=c in engine.registered()[2]['consumed']
        except Exception as error:
            return dict(state='ENGINEERING_PRESERVE',cohort=c,error='ENGINEERING_INSTALL_GUARD_IDENTITY_UNKNOWN '+repr(error),model_retries=0)
        return dict(state='SPENT_ENGINEERING_PRESERVE'if consumed else'ZERO_START_ENGINEERING',cohort=c,
            error='ENGINEERING_INSTALL_FAILED_CLOSED '+reason,model_starts=0,model_retries=0,automatic_retry_or_fallback=False)
    def safe(c):return hold(c)if c in allowed else old_safe(c)
    def worker(c):return hold(c)if c in allowed else old_worker(c)
    frame.f_globals['safe']=safe;frame.f_globals['worker']=worker
    evidence.update(old_safe=old_safe,old_worker=old_worker,safe=safe,worker=worker)
    return evidence

def install_admission_guard(frame,cohorts):
    """Apply after best-effort cleanup to retain the final chooser reference."""
    allowed=frozenset(cohorts);assert len(allowed)==4
    res=frame.f_locals['res'];previous=res.choose_dispatch
    def choose(pending,*args,**kwargs):
        if not any(s['cohort']in allowed for s in pending):return previous(pending,*args,**kwargs)
        kept=[s for s in pending if s['cohort']not in allowed]
        if not kept:return None
        value=previous(kept,*args,**kwargs)
        assert value is None or value['cohort']not in allowed,'ENGINEERING_FAILURE_GUARD_BAD_OLD_CHOICE'
        return value
    res.choose_dispatch=choose
    return dict(previous=previous,wrapper=choose,cohorts=sorted(allowed),model_starts=0)

def best_effort(actions):
    results=[]
    for name,fn in actions:
        try:fn();results.append(dict(action=name,status='RESTORED'))
        except BaseException as error:results.append(dict(action=name,status='RESTORE_ERROR_PRESERVED',error=repr(error)))
    return results

"""Pure fixed-matrix pipeline policy for Main's existing owner scheduler.

No controller, threads, subprocess, registry mutation, or model starts. These
functions select legal rows only. Main supplies current strictly accepted and
archived/restored statuses; speedups never influence population release.
"""
import copy

QUALIFIERS={'OFF_MATCHED':'vectorAdd','M_DATAREAD':'vectorAdd','L2_DATAREAD':'ATAX','L1_DATAREADY':'MVT'}
ACCEPTED='ACCEPTED_STRICT_ARCHIVE_NATIVE_RESTORE'

def qualify_release(result, mode, require_exposure):
    return bool(result and result.get('classification')==ACCEPTED and
                result.get('natural_complete_input')is True and
                result.get('source_binary_input_config_identity_pass')is True and
                result.get('strict_lifecycle_conservation_pass')is True and
                result.get('archive_sha_pass')is True and result.get('native_restore_sha_pass')is True and
                result.get('independent_review_pass')is True and
                result.get('mode')==mode and
                (not require_exposure or result.get('actual_mechanism_exposure',0)>0))

def initial_ready_rows(matrix_rows, qualified_modes, statuses, spent_plan_ids, active_plan_ids):
    """OFF qualifier first; independent released modes then overlap safely."""
    initial=[r for r in matrix_rows if r['initial_fixed8']and r['mode']in set(qualified_modes)|{'OFF_MATCHED'}]
    if not qualified_modes:return []
    def result(mode,program):
        row=next(r for r in initial if r['mode']==mode and r['program']==program)
        return statuses.get(row['plan_id'])
    baseline_ok=qualify_release(result('OFF_MATCHED','vectorAdd'),'OFF_MATCHED',False)
    available=[]
    for row in initial:
        mode=row['mode'];qualifier=row['program']==QUALIFIERS[mode]
        if row['plan_id']in set(spent_plan_ids)|set(active_plan_ids):continue
        if mode=='OFF_MATCHED':
            if qualifier or baseline_ok:available.append(copy.deepcopy(row))
        elif baseline_ok and (qualifier or qualify_release(result(mode,QUALIFIERS[mode]),mode,True)):
            available.append(copy.deepcopy(row))
    return available

def core32_extension_gate(matrix_rows, qualified_modes, statuses, independent_source_safety_pass):
    """Return explicit released/held modes and actual matching-OFF deficit.

    Negative speedup and exact equality are permitted. A real initial failure
    or absent evidence blocks only unsupported extension, never erases its row.
    All released modes share the same immutable build's OFF population.
    """
    initial=[r for r in matrix_rows if r['initial_fixed8']]
    off=[r for r in initial if r['mode']=='OFF_MATCHED']
    off_ok=len(off)==8 and all(qualify_release(statuses.get(r['plan_id']),'OFF_MATCHED',False)for r in off)
    released=[];held={}
    for mode in qualified_modes:
        rows=[r for r in initial if r['mode']==mode]
        reasons=[]
        if not off_ok:reasons.append('MATCHED_OFF_FIXED8_NOT_STRICT_COMPLETE')
        if len(rows)!=8 or not all(qualify_release(statuses.get(r['plan_id']),mode,False)for r in rows):
            reasons.append('MODE_FIXED8_NOT_STRICT_COMPLETE')
        if not any(qualify_release(statuses.get(r['plan_id']),mode,True)for r in rows):
            reasons.append('MODE_NO_ACTUAL_EXPOSURE')
        if not independent_source_safety_pass.get(mode,False):reasons.append('INDEPENDENT_SAFETY_NOT_RELEASED')
        if reasons:held[mode]=reasons
        else:released.append(mode)
    return dict(released_modes=released,held_modes=held,matched_OFF_fixed8_complete=off_ok,
                full_additional_request_budget=24*(1+len(qualified_modes))if released else 0,
                currently_released_additional_cells=24*(1+len(released))if released else 0,
                shared_OFF_must_not_be_reregistered=True,
                population_selected_by_speedup=False,all_historical_failures_preserved=True)

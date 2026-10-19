"""Incremental V2 policy. Pure checks; no compiler, remote worker or new registry.

Environment review is not a lease. A remote worker must use the original E
dispatcher, not a copied JSON/flock. No remote execution transport is implied.
"""
import copy
import hashlib
import json

AUTHORITY = 'b2e5328aca825d6e9ebfe09e46fa208957834636'
PRIOR_AUTHORITY = 'd9263fa2431592b33e900d9b48c6f20029d8b544'
RESERVATIONS = {'seven_workload_common_S_F': 14, 'two_workload_remove_W_V_R': 6,
 'two_workload_W_only': 2, 'one_workload_T_only_M_only_on_WV': 2,
 'one_workload_fixed_victim_on_WR': 1, 'two_workload_local_diagnostics': 6,
 'one_workload_static_WB64': 1, 'contingency': 8}
SWITCHES = {'S': (0,0,0,0), 'F': (1,1,1,1), 'F_MINUS_W': (0,1,1,1),
 'F_MINUS_V': (1,0,1,1), 'F_MINUS_R': (1,1,0,0), 'W_ONLY': (1,0,0,0),
 'WV_T': (1,1,1,0), 'WV_M': (1,1,0,1),
 'F_FIXED_V64': (1,'FIXED64',1,1), 'F_L2_DATA_FREE': (1,1,1,1)}
COMBINATION_GATES = {'shared_payload_lifecycle', 'shared_directory_cost_and_full',
 'pinned_victim_wb_completion_identity', 'ro_tag_reuse_late_sector_identity',
 'ro_victim_same_address_and_host_invalidation', 'backpressure_complete_quiescence',
 'tm_trigger_default_off_and_illegal_combinations'}
GIB = 2**30
GROUP_BUCKET = {'MAIN':'seven_workload_common_S_F','REMOVE_ONE':'two_workload_remove_W_V_R',
 'W_ONLY':'two_workload_W_only','RO_FACTORIAL':'one_workload_T_only_M_only_on_WV',
 'FIXED_VICTIM':'one_workload_fixed_victim_on_WR','LOCAL_DIAGNOSTIC':'two_workload_local_diagnostics',
 'STATIC_CAPACITY':'one_workload_static_WB64'}


def check(condition, reason):
    if not condition: raise ValueError(reason)


def amend(item, at_unix):
    """Idempotently amend the same ledger; never rewrite an old attempt."""
    if item.get('authority_commit') == AUTHORITY:
        check(item['maximum_actual_starts'] == 40 and item['reservations'] == RESERVATIONS,
              'inconsistent V2 amendment')
        return False
    check(item['authority_commit'] == PRIOR_AUTHORITY and item['maximum_actual_starts'] == 24,
          'unknown prior campaign policy')
    check(item['campaign_id'] == 'EPL2_MECHANISM_STUDY_20261019_V1', 'wrong campaign')
    check(item['start_deadline_unix'] == 1792576800 and item['screen_maximum'] == 6,
          'deadline/screen changed')
    check(item['additional_results_max_bytes'] == 6*GIB and
          item['old_plus_new_results_max_bytes'] == 20*GIB, 'output budget changed')
    history = {k: copy.deepcopy(item[k]) for k in
               ('authority_commit','maximum_actual_starts','reservations')}
    actual = sum(a.get('actual_start') is True for a in item['attempts'])
    check(actual == item['actual_starts'], 'actual-start recount mismatch; reconcile first')
    history.update(at_unix=at_unix, actual_starts_at_adoption=actual,
                   new_authority_commit=AUTHORITY, new_maximum_actual_starts=40)
    item.setdefault('policy_amendments', []).append(history)
    item.update(authority_commit=AUTHORITY, maximum_actual_starts=40,
                reservations=copy.deepcopy(RESERVATIONS), planned_scientific_conditions=32,
                reserved_canaries_repairs_retries=8, old_prepared_queue_status='PREPARED_SUPERSEDED_ORDER')
    return True


def charged_bucket(attempt, reservations):
    # Old charged attempts retain their exact original rows, consuming the
    # common contingency reserve and total40 instead of disappearing.
    bucket = attempt['budget_bucket']
    return bucket if bucket in reservations else 'contingency'


def global_gate(data, kind, cpu, memory):
    rows = [r for group in ('runs','resource_leases') for r in data[group].values()
            if r['status'] in ('RESERVED','RUNNING')]
    if kind in ('simulation','screen'):
        check(sum(r['status'] in ('RESERVED','RUNNING') for r in data['runs'].values()) < 4,
              'global shared simulator quota full')
    check(sum(r['cpu_units'] for r in rows)+cpu <= 8, 'global shared CPU quota full')
    check(sum(r['memory_bytes'] for r in rows)+memory <= 32*GIB,
          'global shared memory reservation quota full')
    check(not any(r.get('kind') == 'ENGINEERING_PILOT' for r in rows),
          'exclusive engineering pilot active')


def validate_matrix(matrix):
    check(matrix['authority']==AUTHORITY and matrix['campaign_id']=='EPL2_MECHANISM_STUDY_20261019_V1',
          'wrong matrix authority')
    cells=matrix['conditions']
    check(len(cells)==32 and len({r['condition_id'] for r in cells})==32, 'exact32 unique conditions required')
    for group,bucket in GROUP_BUCKET.items():
        check(sum(r['group']==group for r in cells)==RESERVATIONS[bucket], 'incorrect matrix group count: '+group)
    check(len({r['workload'] for r in cells if r['group']=='MAIN'})==7, 'seven main inputs required')
    for cell in cells:
        check(cell['group'] in GROUP_BUCKET, 'unknown matrix group')
        check(cell['total_payload_slots']==1168 and cell['descriptors']==512 and
              cell['shared_directory_entries']==128 and cell['line_mshr']==128 and
              cell['banks']==4 and cell['ops_per_bank_physical_cycle']==1, 'matrix physical budget mismatch')
        if cell['profile'] in SWITCHES:
            check(tuple(cell[k] for k in ('W','V','T','M'))==SWITCHES[cell['profile']], 'matrix mode mismatch')
    return cells


def condition_check(item,spec,digest):
    record=item['full_system_matrix']
    check(digest(record['path'])==record['sha256'], 'D matrix publication changed')
    cells=validate_matrix(record['matrix'])
    cell=next((row for row in cells if row['condition_id']==spec.get('condition_id')),None)
    check(cell is not None,'explicit V2 planned condition required; contingency needs E review')
    check(cell['workload']==spec['identity']['workload'] and cell['profile']==spec['profile'],
          'different V2 condition/input/profile')
    check(spec['comparison_group']=='V2_'+cell['group']+'_'+cell['workload'], 'different V2 comparison group')
    bucket=spec['budget_bucket']
    if bucket=='contingency':
        check(bool(spec.get('contingency_review')), 'canary/repair/retry needs explicit E reason')
    else:check(bucket==GROUP_BUCKET[cell['group']], 'different V2 condition budget bucket')
    q=item['qualifications'][spec['qualification_id']]['qualification']
    check(item.get('final_source_identity')==q['source_identity'], 'final common binary not frozen/matching')
    return cell


def comparison_allowed(item,chosen,spec,digest):
    if item['authority_commit']==AUTHORITY:
        condition_check(item,spec,digest)
        return True
    return spec['comparison_group'] in chosen['comparison_groups']


def combination_qualification(q, digest):
    profiles = q['supported_profiles']
    full = q.get('full_system_v2')
    requested = set(profiles) & (set(SWITCHES)-{'S'})
    check(not requested or full is not None, 'full-system combination qualification missing')
    if full is None: return
    check(full['authority_commit'] == AUTHORITY and full['fixed_policy'] is True,
          'full-system fixed policy/source scope missing')
    check(full['victim_scope'] == 'CLEAN_DIRTY_PENDING_INFLIGHT', 'CLEAN_ONLY is not full victim')
    check(full['resource_budget'] == {'data_slots':1168,'line_bytes':128,'resident_tags':1024,
          'banks':4,'bank_ops':1,'descriptors':512,'line_mshrs':128,'shared_wad_tvd':128},
          'full-system resource budget mismatch')
    for name in COMBINATION_GATES:
        gate = q['gates'][name]
        check(gate['status'] == 'PASS' and gate['production_driven'] is True and
              digest(gate['evidence_path']) == gate['evidence_sha256'],
              'missing/changed native combination gate: '+name)
    for profile,gate_name in {'F_L2_DATA_FREE':'full_data_free_finite_residual_service',
                              'F_FIXED_V64':'fixed_victim_equal_budget_and_cost'}.items():
        if profile in profiles:
            gate=q['gates'][gate_name]
            check(gate['status']=='PASS' and gate['production_driven'] is True and
                  digest(gate['evidence_path'])==gate['evidence_sha256'],
                  'missing/changed profile-specific native gate: '+gate_name)
    for name, profile in profiles.items():
        if name in SWITCHES:
            check(tuple(profile['research_switches'][key] for key in ('W','V','T','M')) == SWITCHES[name],
                  'incorrect combination/ablation semantics: '+name)
    # F-MINUS-W needs its own true static-copy control, not a disabled allocator.
    if 'F_MINUS_W' in profiles:
        check(full.get('minus_w_preserves_vr_and_static16_copy') is True,
              'DEPENDENT_CONTROL_UNSUPPORTED: F_MINUS_W')


def environment_review(candidate, review, original_storage_identity, now, digest):
    """Validate E's independently collected evidence; F self-report alone fails.

    Device numbers are host-local, so independence needs physical backing proof,
    not comparing st_dev, hostname or a path string between two machines.
    """
    check(candidate['campaign_id'] == 'EPL2_MECHANISM_STUDY_20261019_V1' and
          candidate['authority_commit'] == AUTHORITY, 'wrong environment authority')
    check(review['reviewed_by'] == 'E' and review['independent_observation'] is True,
          'independent E environment observation required')
    check(review['candidate_sha256'] == hashlib.sha256(
          json.dumps(candidate,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
          'environment candidate changed')
    check(0 <= now-review['measured_unix'] <= 300 and review['expires_unix'] > now and
          review['expires_unix'] <= review['measured_unix']+300, 'stale environment observation')
    check(candidate['host_identity'] == review['host_identity'] and
          candidate['host_identity']['boot_id'] and candidate['host_identity']['hostname'],
          'environment host/boot changed')
    check(review['physical_backing_verified'] is True and original_storage_identity and
          review['physical_storage_identity'] != original_storage_identity,
          'filesystem alias or unproved physical independence')
    for key in ('quota_verified','write_probe_fsynced','all_write_destinations_closed',
                'input_config_oracle_identity_closed','compiler_vendor_libraries_recorded',
                'io_owner_coordination_pass','authorized_dispatch_entry_verified'):
        check(review[key] is True, 'environment requirement missing: '+key)
    check(bool(review['evidence']), 'independent environment evidence absent')
    for entry in review['evidence']:
        check(digest(entry['path']) == entry['sha256'], 'environment evidence changed')
    check(review['effective_memory_available_bytes'] >= 64*GIB and
          review['effective_cpu_units'] >= 2, 'environment RAM/CPU floor')
    check(review['share_available_bytes'] >= 40*GIB, 'environment Share floor')
    check(bool(review['write_filesystems']), 'write filesystem budgets absent')
    for fs in review['write_filesystems']:
        check(fs['writable'] is True and fs['free_inodes'] > 0 and fs['peak_growth_bytes'] > 0,
              'unusable/unbudgeted write filesystem')
        check(min(fs['available_bytes'],fs['quota_available_bytes'])-
              fs['pending_growth_bytes']-fs['peak_growth_bytes'] >= 48*GIB,
              '48GiB floor after per-filesystem quota and peak writes')
    return {'status':'ENVIRONMENT_REVIEW_PASS_NOT_A_LEASE',
            'host_identity':review['host_identity'],'expires_unix':review['expires_unix'],
            'physical_storage_identity':review['physical_storage_identity']}

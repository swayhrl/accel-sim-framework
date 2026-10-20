#!/usr/bin/env python3
"""Bounded source/log consistency check; never executes/builds a simulator.

This checks exact Git objects and an existing failed diagnostic. Arithmetic
below is an audit of its recorded masks/footprint, not a runtime model or
native qualification. Run with --framework-repo and --core-repo containing the
three frozen commits. Output is written only to the explicitly named file.
"""
import argparse
import hashlib
import json
import re
import subprocess

A = '156adbbb5ddcd49e8adb96939837372936ac451e'
CORE = '27ec10bda848e4929181c60a7cbb40d6b007945c'
FIXTURE = '8027ec558b9704d41cb8268131e7e6aca3ae7775'
BASE = 'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2/'
PACK = 'docs/ep_l2/review_packs/MS20261020_A_VRW_REACHABILITY_AND_PEER_HANDOFF_r35/'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', repo, *args])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--framework-repo', required=True)
    p.add_argument('--core-repo', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    sources, checks, anchors = {}, [], []

    def read(repo, commit, path):
        b = git(repo, 'show', commit + ':' + path)
        sources[commit + ':' + path] = hashlib.sha256(b).hexdigest()
        return b.decode()

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(dict(name=name, status='PASS', scope='SOURCE_LOG_CONSISTENCY_ONLY'))

    def contains(commit, path, text, needle, label):
        check(label, needle in text)
        anchors.append(dict(commit=commit, path=path,
                            line=text[:text.index(needle)].count('\n') + 1,
                            text=needle))

    review_text = read(a.framework_repo, A, BASE + 'VRW_REACHABILITY_REVIEW_r35.json')
    review = json.loads(review_text)
    check('exact_A_r35_review', hashlib.sha256(review_text.encode()).hexdigest() ==
          '2904f7b6b8d63c74f1fa8601ed7da6abed08ac5f6276f83c4e81821985a84bbd')
    check('exact_production_Core', review['production_source_identity']['core_source_commit'] == CORE)
    check('test_only_Core_has_no_production_source_delta', not git(
        a.core_repo, 'diff', '--name-only', CORE, FIXTURE, '--', 'src').strip())
    tx_path = 'src/gpgpu-sim/ep-l2-ro-transactions.h'
    tx = read(a.core_repo, CORE, tx_path)
    needles = [
        ('e = entry(); e.live = e.attached = true;', 'new_admission_resets_entry'),
        ('reuse_seen(false)', 'entry_constructor_clears_reuse'),
        ('e.required |= mask; e.reuse_seen = true;', 'successful_merge_sets_sticky_reuse'),
        ('return m_features.tag_detach && e.attached && !e.reuse_seen && (e.required&~e.ready);',
         'can_detach_requires_no_reuse'),
        ('if (!m_features.tag_detach || !e.attached || e.reuse_seen ||', 'detach_also_enforces_reuse'),
        ('return e.required & ~(e.issued | e.ready);', 'lower_needed_excludes_issued_and_ready'),
        ('e.live = false;', 'retirement_ends_lifetime_without_clearing_bit'),
        ('out.request = waiter_request(w);', 'response_returns_actual_descriptor_request'),
        ('if (!e.response_chosen)', 'response_choice_is_held'),
    ]
    for needle, label in needles:
        contains(CORE, tx_path, tx, needle, label)
    # Exclude equality comparisons; any additional assignment requires review.
    check('only_reuse_assignment_is_successful_merge',
          re.findall(r'\breuse_seen\s*=(?!=)\s*([^;]+);', tx) == ['true'])
    check('single_entry_reset_site', tx.count('e = entry();') == 1)
    lp = 'src/gpgpu-sim/l2cache.cc'
    l2 = read(a.core_repo, CORE, lp)
    contains(CORE, lp, l2, 'mf->get_addr() + SECTOR_SIZE * i, mf->get_access_type(),',
             'sector_child_address')
    contains(CORE, lp, l2, 'mf->get_sid(), mf->get_tpc(), mf, mf->get_streamID());',
             'sector_children_preserve_parent_pointer_and_origin')
    pop = l2.split('mem_fetch *memory_sub_partition::pop() {', 1)[1].split(
        'mem_fetch *memory_sub_partition::top()', 1)[0]
    check('partition_pop_does_not_assemble_parent', 'get_original_mf' not in pop and 'return mf;' in pop)
    rp = 'src/gpgpu-sim/ep-l2-ro-runtime.inc'
    runtime = read(a.core_repo, CORE, rp)
    for needle, label in [
        ('unsigned mask=m->get_access_sector_mask().to_ulong(),missing=needed(m,h);', 'merge_missing_uses_scheduled_mask'),
        ('issue(m,h,missing,time,events);', 'merge_issues_only_missing_sectors'),
        ('m->get_wid(),m->get_sid(),m->get_tpc(),NULL,m->get_streamID());', 'lower_packet_has_valid_origin_and_no_parent'),
        ('packet->set_ro_lower_packet();packet->set_ep_l2_payload_identity(h.payload_id,h.generation);', 'lower_packet_binds_landing_generation'),
        ('if(tx->live(h) && tx->can_detach(h)){index=i;return true;}', 'detachment_scans_eligible_tag_indices'),
        ('if(cycle!=physical_cycle())', 'response_uses_physical_GPU_cycle'),
    ]:
        contains(CORE, rp, runtime, needle, label)
    mf = read(a.core_repo, CORE, 'src/gpgpu-sim/mem_fetch.cc')
    check('new_mem_fetch_has_new_UID', 'm_request_uid = sm_next_mf_request_uid++;' in mf)
    port = read(a.core_repo, CORE, 'src/gpgpu-sim/ep-l2-ro-store-port.h')
    check('fill_UID_and_response_UID_are_distinct_clients',
          'GENERIC,m_return_uid)' in port and 'request->get_request_uid():0' in port)
    log = read(a.framework_repo, A, PACK + 'A_SHARED_VRW_GDB_r34_failed_fixture_gdb.log')
    check('exact_recorded_GDB_log', hashlib.sha256(log.encode()).hexdigest() ==
          'b8a3befea35c3b73adb9cd5df851bb312cfd55d93cf1fbec8465641da635a19f')
    rows = re.findall(r'VRW_A0\|([^\n]+)', log)
    state = dict((k, int(v)) for k, v in (part.split('=') for part in rows[0].split('|')))
    check('captured_A0_not_detachable', state['attached'] == state['reuse_seen'] == 1)
    check('duplicate_has_no_missing_lower_sector',
          state['required'] & ~(state['issued'] | state['ready']) == 0)
    check('recorded_packets_did_not_grow', 'VRW_LOCAL|before=20' in log and
          'VRW_STATE|ro_packets=20' in log and 'VRW_STATE|ro_bytes=640' in log)
    check('five_waiters_consistent_with_four_children_and_duplicate', state['waiters'] == 4 + 1)
    fixture_path = 'tests/ep_l2/ms_victim/test_vrw_interleave.cc'
    fixture = read(a.core_repo, FIXTURE, fixture_path)
    contains(FIXTURE, fixture_path, fixture, 'const H newer=g.submit_ro(0);', 'original_wait_requires_new_packet')
    contains(FIXTURE, fixture_path, fixture, 'assert(f.cache->ep_l2_descriptor_count_used()==18);', 'original_18_descriptor_expectation_is_unreached')
    contains(FIXTURE, fixture_path, fixture, 'f.expected[full_uid]=f.memory.at(ro_base);', 'original_reference_tracks_parent_instead_of_children')
    plan = json.loads(read(a.core_repo, FIXTURE,
        'docs/ep_l2/ms_victim/full_system_v2_r1/vrw_input/STIMULUS.json'))
    ro_lines = {int(s, 16) for s in plan['readonly_lines']}
    write_lines = {int(s, 16) for s in plan['write_lines']}
    check('synthetic_whole_epoch_line_sets_disjoint', len(ro_lines) == 17 and
          len(write_lines) == 144 and ro_lines.isdisjoint(write_lines))
    result = dict(schema='C_VRW_SOURCE_AND_RECORDED_FAILURE_CONSISTENCY_V1',
        scope='STATIC_SOURCE_EXISTING_LOG_AND_EXACT_INTEGER_ACCOUNTING_NOT_NATIVE_TEST',
        status='PASS', checks=checks, anchors=anchors, source_sha256=sources,
        observed_GDB_state=state,
        original_failed_prefix=dict(RO_packets_observed=20, RO_bytes_observed=640,
            A0_waiters_observed=5, RO_descriptors_inferred_if_no_returns=4+16+1,
            extra_lower_needed_from_recorded_masks=0),
        proposed_split128=dict(lower_packets=4, lower_bytes=128, requester_descriptors=5,
            child_responses=4, singleton_responses=1, parent_responses=0,
            runtime_status='NOT_COMPILED_NOT_RUN'),
        proposed_joint32=dict(lower_RO_packets=18, lower_RO_bytes=576,
            total_lower_read_packets_before_final_hit_read=19,
            total_lower_read_bytes_before_final_hit_read=608,
            RO_descriptors_before_returns=18, runtime_status='NOT_COMPILED_NOT_RUN'),
        simulator_builds=0, simulator_runs=0, application_starts=0)
    with open(a.output, 'x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(f'{len(checks)} source/log consistency checks PASS; simulator executions=0')


if __name__ == '__main__':
    main()

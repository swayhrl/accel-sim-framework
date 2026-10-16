"""Read exact candidate Git objects, emit static audit/minimal patch; never build/run."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

CANDIDATE = '62dc1d179b5516e68b21b695c7a9c5d0667e9671'
PUBLICATION = 'c93d900e1f968a3b69990dc29b78d50fc18f35ac'
PARENT = '126394be46b15f55b9756d43eb9ca9a9baae1c84'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--candidate-worktree', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)

    def git(*command):
        return subprocess.check_output(['git', *command], cwd=args.core)

    def source(name, rev=CANDIDATE):
        return git('show', rev + ':' + name).decode()

    changed = git('diff', '--name-only', PARENT, CANDIDATE).decode().splitlines()
    files = {name: source(name) for name in changed}
    paths = ('src/gpgpu-sim/ep-l2-ft-cache.inc', 'src/gpgpu-sim/gpu-cache.h',
             'src/gpgpu-sim/l2cache.h', 'src/gpgpu-sim/l2cache.cc',
             'src/gpgpu-sim/gpu-sim.cc', 'tests/ep_l2/test_ft_host_prefill.cc')
    ft, header, partition_h, partition, gpu, host_test = [files[n] for n in paths]
    checks = []

    def check(name, ok, scope='STATIC_SOURCE_ONLY'):
        checks.append({'name': name, 'status': 'PASS' if ok else 'FAIL', 'scope': scope})

    check('candidate_publication_exact_tree', git('rev-parse', CANDIDATE + '^{tree}') ==
          git('rev-parse', PUBLICATION + '^{tree}'))
    check('native_gpu_cache_cc_byte_unchanged', source('src/gpgpu-sim/gpu-cache.cc') ==
          source('src/gpgpu-sim/gpu-cache.cc', PARENT))
    legacy = '    // if(!m_config.trace_driven_mode)'
    check('legacy_non_FT_memcpy_tail_byte_unchanged', gpu[gpu.index(legacy):] ==
          source('src/gpgpu-sim/gpu-sim.cc', PARENT)[source('src/gpgpu-sim/gpu-sim.cc', PARENT).index(legacy):])
    check('physical_clock_helper', 'return m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle;' in ft)
    check('FT_access_physical_clock', 'const unsigned long long physical_cycle = ft_physical_cycle();' in ft)
    access = ft[ft.index('enum cache_request_status l2_cache::ft_access'):ft.index('void l2_cache::send_write_request')]
    check('FT_access_no_bank_request_native_time', 'false, time,' not in access and 'true, time,' not in access)
    check('physical_births', 'p.born = physical_cycle;' in access and 'p.victim_address, physical_cycle' in access)
    check('monotonic_bank_clock_assertion', 'FT bank clock must be physical and monotonic' in header)
    check('fill_physical_native_tag_offset_separate', 'mf, m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle);' in partition and
          'm_L2cache->fill(mf, m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle +' in partition)
    prefill = ft[ft.index('bool l2_cache::ft_try_force_tag_access'):ft.index('void l2_cache::descriptor_admitted')]
    check('prefill_gate_no_bank_request', 'm_ep_l2_payload.request(' not in prefill)
    check('prefill_quiescent_cache', all(x in prefill for x in ('!ft_drained()', 'mshr_entries_used()', '!miss_queue_empty()', 'pending_operations()')))
    check('prefill_partition_hardware_closure', '!l2_char_no_resource_leak()' in partition)
    check('prefill_refuses_dirty_reserved_pinned', all(x in prefill for x in ('HIT_RESERVED', 'block_is_modified(index)', 'old.pins', 'RESIDENT_DIRTY')))
    check('prefill_selected_index_postcondition', 'actual_index == index' in prefill)
    check('prefill_partial_sector_identity', 'slot.ready_sector_mask |= mask;' in prefill and 'if (mask.test(sector)) slot.versions[sector] = 0;' in prefill)
    check('prefill_full_width_partial_endpoints', 'dst_start_addr & ~new_addr_type(31)' in gpu and '(dst_start_addr + count - 1)' in gpu)
    check('producer_host_test_actual_entry_and_WB', all(x in host_test for x in ('gpu->perf_memcpy_to_gpu', 'PREFILL_DIRTY_VICTIM', 'observed_wb.size()==1', 'WTERMSIG(status)==SIGABRT')))
    check('producer_host_test_real_reply_and_sector', 'sp->top() == expected' in host_test and 'get_ft_wb_data()[(expected->get_addr()/32)%4] == 0' in host_test)
    check('producer_host_test_later_epoch_scope_explicit', 'gpu_tot_sim_cycle += 1000000' in host_test)
    block = ('  unsigned long long ft_bank_grants_for_test(unsigned bank) const {\n'
             '    return m_L2cache->ep_l2_payload_bank_grants(bank);\n  }\n')
    before = partition_h.count(block)
    check('unique_bank_observation_method', before == 1, 'DEFINITE_CXX_REDEFINITION_CHECK_NO_COMPILER')
    assert before == 2, 'Candidate changed: reassess instead of applying a stale fix'
    fixed = partition_h.replace(block + '\n', '', 1)
    assert fixed.count(block) == 1
    patch = ''.join(difflib.unified_diff(partition_h.splitlines(True), fixed.splitlines(True),
        fromfile='a/src/gpgpu-sim/l2cache.h', tofile='b/src/gpgpu-sim/l2cache.h'))
    patch_path = args.out / 'REMOVE_DUPLICATE_BANK_OBSERVER.patch'
    patch_path.write_text(patch)
    actual_parent = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.candidate_worktree, text=True).strip()
    assert actual_parent == CANDIDATE, 'Do not check a patch against an unrecorded parent'
    result = subprocess.run(['git', 'apply', '--check', str(patch_path.resolve())],
                            cwd=args.candidate_worktree, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = {'candidate': CANDIDATE, 'core_publication': PUBLICATION, 'R0_parent': PARENT,
        'kind': 'INDEPENDENT_STATIC_AUDIT_NOT_RUNTIME_QUALIFICATION',
        'status': 'COMPILE_BLOCKER_FOUND_MINIMAL_PATCH_PREPARED', 'binary_sha256': None,
        'runtime_tests_executed': 0, 'source_files': [
            {'path': n, 'sha256': hashlib.sha256(s.encode()).hexdigest()} for n,s in sorted(files.items())],
        'checks': checks, 'duplicate_observer': {'source_lines': [i+1 for i,l in enumerate(partition_h.splitlines()) if 'unsigned long long ft_bank_grants_for_test(' in l],
            'definitions_before': before, 'definitions_after_patch': fixed.count(block),
            'patched_file_sha256': hashlib.sha256(fixed.encode()).hexdigest(),
            'patch_apply_check_exit': result.returncode, 'patch_apply_check_parent': actual_parent,
            'candidate_worktree_modified': False},
        'scope_change_from_lane5_a945': 'Lane1 supports later quiescent clean host prefill rather than rejecting all post-GPU epochs; full address and partial endpoints added. New test addresses that path. No independent runtime PASS inherited.',
        'next': 'Lane1 removes duplicate observer in official source and publishes a new exact candidate; rebind audit/gate plan. Same official build entry and all current resource gates remain mandatory.'}
    (args.out/'SOURCE_AUDIT.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    (args.out/'R0_TO_CANDIDATE.diff').write_bytes(git('diff', PARENT, CANDIDATE))
    print(json.dumps({'status': report['status'], 'static_checks': len(checks),
                      'pass': sum(c['status']=='PASS' for c in checks), 'fail': sum(c['status']=='FAIL' for c in checks),
                      'patch_check': result.returncode, 'runtime_tests': 0}))


if __name__ == '__main__':
    main()

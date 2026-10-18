"""Fail-closed exact output-only delta allowlist against c0a5e2c3."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

BASE = 'c0a5e2c31e407c57e3a4af3ce529c921e8059a05'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--core', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    def git(*items):
        return subprocess.check_output(['git', '-C', str(args.core), *items])
    assert not git('status', '--porcelain').strip()
    changed = git('diff', '--name-only', BASE, 'HEAD').decode().splitlines()
    expected = {'CMakeLists.txt', 'src/gpgpu-sim/shader.cc', 'src/gpgpu-sim/shader.h',
                'tests/dtc_l1_normal_export_probe.cc'}
    assert set(changed) == expected, changed
    def old(path):
        return git('show', BASE + ':' + path).decode()
    def new(path):
        return (args.core / path).read_text()
    cc = new('src/gpgpu-sim/shader.cc')
    methods = [
        '''// Normal-statistics delegation only; reuse the original cumulative observer.
void ldst_unit::print_dtc_l1_invalidation_summary(FILE *fp) const {
  if (m_config->dtc_l1_invalidate_on_source_event)
    m_dtc_invalidation.print(fp);
}

''',
        '''void shader_core_ctx::print_dtc_l1_invalidation_summary(FILE *fp) const {
  m_ldst_unit->print_dtc_l1_invalidation_summary(fp);
}

''',
        '''void simt_core_cluster::print_dtc_l1_invalidation_summary(FILE *fp) const {
  for (unsigned i = 0; i < m_config->n_simt_cores_per_cluster; ++i)
    m_core[i]->print_dtc_l1_invalidation_summary(fp);
}

''']
    block = '''  if (m_shader_config->dtc_l1_invalidate_on_source_event) {
    // One cumulative snapshot at this existing normal statistics boundary.
    // UINT64_MAX in the unchanged per-SM rows means UNDEFINED_NO_EVENT.
    fprintf(fout, "DTC_INVALIDATE_V1_SNAPSHOT_BEGIN version=1 sms=%u "
                  "cycle=%llu no_event_cycle_sentinel=%llu\\n",
            m_shader_config->num_shader(),
            (unsigned long long)global_cycle(),
            (unsigned long long)UINT64_MAX);
    for (unsigned i = 0; i < m_shader_config->n_simt_clusters; ++i)
      m_cluster[i]->print_dtc_l1_invalidation_summary(fout);
    fprintf(fout, "DTC_INVALIDATE_V1_SNAPSHOT_END version=1 sms=%u "
                  "cycle=%llu\\n", m_shader_config->num_shader(),
            (unsigned long long)global_cycle());
  }

'''
    for fragment in methods + [block]:
        assert cc.count(fragment) == 1
        cc = cc.replace(fragment, '', 1)
    assert cc == old('src/gpgpu-sim/shader.cc'), 'nonallowlisted shader implementation change'
    declaration = '  void print_dtc_l1_invalidation_summary(FILE *fp) const;\n'
    header = new('src/gpgpu-sim/shader.h')
    assert header.count(declaration) == 3
    assert header.replace(declaration, '') == old('src/gpgpu-sim/shader.h')
    wiring = '''    add_executable(dtc_l1_normal_export_probe tests/dtc_l1_normal_export_probe.cc)
    target_include_directories(dtc_l1_normal_export_probe PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/libcuda
        ${CUDAToolkit_INCLUDE_DIRS})
    target_compile_options(dtc_l1_normal_export_probe PRIVATE -fno-access-control)
    target_link_libraries(dtc_l1_normal_export_probe PRIVATE cudart ${CMAKE_DL_LIBS})
'''
    cmake = new('CMakeLists.txt')
    assert cmake.count(wiring) == 1 and cmake.replace(wiring, '') == old('CMakeLists.txt')
    probe = new('tests/dtc_l1_normal_export_probe.cc')
    assert 'gpu->gpu_print_stat(0)' in probe
    assert 'm_dtc_invalidation.print(' not in probe
    assert 'gpu->cycle(' not in probe and 'gpu->launch(' not in probe
    protected = ['src/gpgpu-sim/gpu-sim.cc', 'src/gpgpu-sim/gpu-sim.h',
                 'src/gpgpu-sim/dtc-l1-common.h', 'src/gpgpu-sim/dtc-l1-invalidation.h',
                 'src/gpgpu-sim/gpu-cache.cc', 'src/gpgpu-sim/gpu-cache.h']
    records = []
    for path in protected:
        data = (args.core / path).read_bytes()
        assert data == git('show', BASE + ':' + path)
        records.append({'path': path, 'sha256': sha(data), 'byte_identical_to_base': True})
    files = []
    for path in sorted(expected):
        data = (args.core / path).read_bytes()
        previous = None if path.startswith('tests/') else git('show', BASE + ':' + path)
        files.append({'path': path, 'sha256': sha(data), 'base_sha256': sha(previous) if previous else None,
                      'git_blob': git('rev-parse', 'HEAD:' + path).decode().strip(),
                      'allowance': 'new CPU test' if path.startswith('tests/') else
                                   'new test target only' if path == 'CMakeLists.txt' else
                                   'only exact const delegates/framed printing block' if path.endswith('.cc') else
                                   'only three const method declarations'})
    result = {'status': 'PASS_EXACT_PRINT_ONLY_SOURCE_ALLOWLIST', 'base_core': BASE,
              'new_core': git('rev-parse', 'HEAD').decode().strip(), 'changed_files': files,
              'production_added_lines': {'shader.cc': 30, 'shader.h': 3},
              'exact_fragment_removal_recovers_base': True,
              'all_other_tracked_paths_unchanged': True, 'protected_files': records,
              'gpu_print_stat_and_public_cache_L2_DRAM_code_unchanged': True,
              'old_seven_CTest_targets_unchanged': True, 'new_observer_or_counter': False,
              'mechanism_or_timing_changes': False, 'runtime_or_debug_option_changes': False,
              'new_methods_const_and_read_only': True,
              'scope': 'only output path, declarations, CPU test and its build wiring; no state machine/performance repair'}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()

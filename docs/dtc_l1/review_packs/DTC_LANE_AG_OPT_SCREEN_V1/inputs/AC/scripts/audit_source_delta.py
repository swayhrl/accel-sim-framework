"""Exact changed-path contract and source-level OFF recovery to immutable X2."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
BASE='e32afdcf44be3374ff36d22568ed01a075459b6f'
PARENT='c0a5e2c31e407c57e3a4af3ce529c921e8059a05'
TOKENS=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/|[{}]',re.S)

def block(text,signature):
    start=text.index(signature); opening=text.index('{',start); depth=0
    for token in TOKENS.finditer(text,opening):
        if token.group()=='{': depth+=1
        elif token.group()=='}':
            depth-=1
            if not depth: return text[start:token.end()]
    raise AssertionError('unclosed body '+signature)

def main():
    p=argparse.ArgumentParser();p.add_argument('--core',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    def git(*args):return subprocess.check_output(['git','-C',str(a.core),*args])
    assert not git('status','--porcelain').strip()
    assert git('rev-parse',BASE+'^').decode().strip()==PARENT
    head=git('rev-parse','HEAD').decode().strip()
    git('merge-base','--is-ancestor',BASE,head)
    expected={'CMakeLists.txt','src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h',
              'src/gpgpu-sim/dtc-l1-collect-wb.h','tests/dtc_l1_collect_wb_pipeline_probe.cc','tests/dtc_l1_collect_wb_resource_test.cc'}
    assert set(git('diff','--name-only',BASE,head).decode().splitlines())==expected
    def old(path):return git('show',BASE+':'+path).decode()
    def new(path):return (a.core/path).read_text()
    def remove(text,fragment):
        assert text.count(fragment)==1,fragment
        return text.replace(fragment,'',1)
    cc=new('src/gpgpu-sim/shader.cc'); baseline=old('src/gpgpu-sim/shader.cc')
    source_unchanged=[]
    for signature in ['bool ldst_unit::dtc_l1_oo_select_ready(', 'bool ldst_unit::dtc_l1_finite_service_active(',
                      'bool ldst_unit::dtc_l1_service_collect(', 'void ldst_unit::dtc_l1_service_retired(',
                      'void ldst_unit::cycle(', 'void ldst_unit::invalidate(',
                      'bool ldst_unit::dtc_l1_oo_memory_cycle(', 'void ldst_unit::dtc_l1_oo_issue_lower_requests(',
                      'bool ldst_unit::dtc_l1_oo_consume_response(', 'void ldst_unit::dtc_l1_oo_complete_instruction(',
                      'bool ldst_unit::dtc_l1_io_writeback_head(', 'void ldst_unit::issue(',
                      'bool opndcoll_rfu_t::writeback(', 'void ldst_unit::print_dtc_l1_invalidation_summary(']:
        now=block(cc,signature); assert now==block(baseline,signature),signature
        source_unchanged.append({'signature':signature,'sha256':hashlib.sha256(now.encode()).hexdigest()})
    signature='bool ldst_unit::dtc_l1_oo_writeback_ready('
    wb=block(cc,signature)
    wb=wb.replace('''  const bool ready = m_config->dtc_l1_collect_wb_pipeline
                         ? dtc_l1_oo_pipeline_wb_candidate(&uid)
                         : dtc_l1_oo_select_ready(&uid);''','''  const bool ready = dtc_l1_oo_select_ready(&uid);''')
    for fragment in [
      '''    if (m_config->dtc_l1_collect_wb_pipeline)
      m_dtc_collect_wb.retired(service_cycle, uid, false);
''',
      '''    if (m_config->dtc_l1_collect_wb_pipeline)
      m_dtc_collect_wb.attempted(service_cycle, false);
''']:
        wb=remove(wb,fragment)
    for fragment in [
      '''  if (m_config->dtc_l1_collect_wb_pipeline)
    m_dtc_collect_wb.attempted(service_cycle, true);
''',
      '''  if (m_config->dtc_l1_collect_wb_pipeline)
    m_dtc_collect_wb.retired(service_cycle, uid, true);
''']:
        wb=remove(wb,fragment)
    gate='''  if (m_config->dtc_l1_collect_wb_pipeline) {
    assert(m_dtc_collect_wb.result_valid && m_dtc_collect_wb.result_uid == uid);
    assert(entry->service.collect_done_cycle != UINT64_MAX &&
           !entry->service.sectors_left);
    if (service_cycle <= entry->service.collect_done_cycle) return false;
  } else if (!dtc_l1_service_collect(entry->service, entry->references)) return false;'''
    assert gate in wb
    wb=wb.replace(gate,'''  if (!dtc_l1_service_collect(entry->service, entry->references)) return false;''')
    assert wb==block(baseline,signature),'OFF WB body differs'
    cc=cc.replace(block(cc,signature),wb,1)
    first=cc.index('// The ON pipeline uses the original full-admission/readiness/fence predicates.')
    last=cc.index('bool ldst_unit::dtc_l1_oo_writeback_ready()',first)
    # Explicitly named new ON-only helper region; actual bytes are hash-bound.
    helpers=cc[first:last]; assert helpers.count('ldst_unit::dtc_l1_oo_pipeline_')==3
    cc=cc[:first]+cc[last:]
    for cls in ['ldst_unit','shader_core_ctx','simt_core_cluster']:
        method=block(cc,'void '+cls+'::print_dtc_l1_collect_wb_stats(')
        cc=remove(cc,method+'\n\n')
    gate=block(cc,'  if (m_shader_config->dtc_l1_collect_wb_pipeline) {')
    cc=remove(cc,gate+'\n\n')
    initgate=block(cc,'  if (config->dtc_l1_collect_wb_pipeline) {')
    assert 'm_dtc_collect_wb.configure(config->dtc_l1_physical_lines)' in initgate
    cc=remove(cc,initgate+'\n')
    external=block(cc,'  if (config->dtc_l1_collect_wb_pipeline) {')
    assert 'DTC_COLLECT_WB_EXTERNAL_CACHE_CONSTRUCTOR_STOP' in external
    cc=remove(cc,external+'\n')
    cc=remove(cc,'''  // Independent collection stage, including cycles where another client wins
  // WB arbitration. Uses only the unchanged absolute-cycle 4-sector port.
  if (m_config->dtc_l1_collect_wb_pipeline) dtc_l1_oo_pipeline_collect();
''')
    assert cc==baseline,'non-allowlisted shader change'
    h=new('src/gpgpu-sim/shader.h')
    for fragment in ['#include "dtc-l1-collect-wb.h"\n','  bool dtc_l1_collect_wb_pipeline;\n',
                     '  dtc_l1::collect_wb_pipeline m_dtc_collect_wb;\n',
                     '  bool dtc_l1_oo_pipeline_eligible(unsigned uid) const;\n',
                     '  void dtc_l1_oo_pipeline_collect();\n',
                     '  bool dtc_l1_oo_pipeline_wb_candidate(uint64_t *uid) const;\n']:
        h=remove(h,fragment)
    declaration='  void print_dtc_l1_collect_wb_stats(FILE *fp) const;\n'
    assert h.count(declaration)==3;h=h.replace(declaration,'')
    assert h==old('src/gpgpu-sim/shader.h')
    cfg=new('src/gpgpu-sim/gpu-sim.cc')
    cfg=remove(cfg,'''  option_parser_register(opp, "-gpgpu_dtc_l1_collect_wb_pipeline", OPT_BOOL,
                         &dtc_l1_collect_wb_pipeline,
                         "Opt-in bounded collection/WB overlap: PAPER_OO + finite V1 only", "0");
''')
    assert cfg==old('src/gpgpu-sim/gpu-sim.cc')
    cmake=new('CMakeLists.txt');start=cmake.index('    add_executable(dtc_l1_collect_wb_pipeline_probe\n');end=cmake.index('endif()',start)
    cmake=cmake[:start]+cmake[end:];assert cmake==old('CMakeLists.txt')
    changed=[]
    for path in sorted(expected):
        data=(a.core/path).read_bytes()
        changed.append({'path':path,'sha256':hashlib.sha256(data).hexdigest(),'git_blob':git('rev-parse',head+':'+path).decode().strip()})
    result={'status':'PASS_EXACT_AC_ALLOWLIST_AND_SOURCE_OFF_RECOVERY','base_core':BASE,'base_direct_parent':PARENT,'new_core':head,
            'changed_files':changed,'shader_recovered_to_base_byte_for_byte':True,'header_recovered_to_base_byte_for_byte':True,
            'parser_recovered_to_base_byte_for_byte':True,'build_wiring_recovered_to_base_byte_for_byte':True,
            'unchanged_production_functions':source_unchanged,
            'all_other_tracked_paths_byte_identical':True,'original_seven_ctest_sources_unchanged':True,
            'K1_observer_and_normal_section_contract_unchanged':True,
            'scope':'ON bounded collection/WB staging + ON-only counters/normal export + one default0 parser bool + tests; no cache/finite-service/identity/clock changes'}
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()

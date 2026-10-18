#!/usr/bin/env python3
"""Recover the exact fixed AC source by removing only fixed AE integration pieces."""
from common import *
import importlib.util

AC='83aca449135703c176cfab29ae43e1245d00a557'
AE='ae83cc510f301cfe7937ad77318e332b2ab324e8'
def main():
 records=[]
 def exact(path,expected,definition):
  actual=(CORE/path).read_bytes()
  assert actual==expected,(path,'UNREVIEWED_SHARED_FILE_CHANGE_STOP')
  records.append(dict(path=path,sha256=sha(CORE/path),comparison=definition))
 def old(commit,path):return blob(CORE_REPO,commit,path).decode()
 ae=old(AE,'src/gpgpu-sim/shader.cc')
 validation=ae[ae.index('  dtc_l1::check_tag_hash_bankrow('):ae.index('  m_memory_config = mem_config;',ae.index('  dtc_l1::check_tag_hash_bankrow('))]
 external='''  if (config->dtc_l1_tag_hash_bankrow) {
    fprintf(stderr, "TAG_HASH_BANKROW_EXTERNAL_CACHE_CONSTRUCTOR_STOP\\n");
    abort();
  }
'''
 assert external in ae
 cc=old(AC,'src/gpgpu-sim/shader.cc')
 cc=cc.replace('  if (config->dtc_l1_collect_wb_pipeline) {',validation+'  if (config->dtc_l1_collect_wb_pipeline) {',1)
 cc=cc.replace('    dtc_config.selected_mode = dtc_l1::mode::PAPER_OO;\n','    dtc_config.selected_mode = dtc_l1::mode::PAPER_OO;\n    dtc_config.tag_hash_bankrow = m_config->dtc_l1_tag_hash_bankrow;\n',1)
 anchor='''  init(icnt, mf_allocator, core, operand_collector, scoreboard, config,
       mem_config, stats, sid, tpc);'''
 # The production file has two init calls; external constructor is the one
 # following the K1 external-constructor abort, exactly as fixed AE.
 start=cc.index('OO_K1_EXTERNAL_CACHE_CONSTRUCTOR_UNSUPPORTED_STOP')
 at=cc.index(anchor,start);cc=cc[:at]+external+cc[at:]
 exact('src/gpgpu-sim/shader.cc',cc.encode(),'EXACT_FIXED_AC_PLUS_THREE_UNCHANGED_AE_ADDITIONS')
 h=old(AC,'src/gpgpu-sim/shader.h').replace('  bool dtc_l1_collect_wb_pipeline;','  bool dtc_l1_tag_hash_bankrow;\n  bool dtc_l1_collect_wb_pipeline;',1)
 exact('src/gpgpu-sim/shader.h',h.encode(),'EXACT_FIXED_AC_PLUS_AE_BOOL')
 cfg=old(AC,'src/gpgpu-sim/gpu-sim.cc').replace('  dtc_l1::register_source_invalidation_option(','  dtc_l1::register_tag_hash_bankrow_option(opp, &dtc_l1_tag_hash_bankrow);\n  dtc_l1::register_source_invalidation_option(',1)
 exact('src/gpgpu-sim/gpu-sim.cc',cfg.encode(),'EXACT_FIXED_AC_PLUS_AE_REGISTRATION')
 cm=old(AC,'CMakeLists.txt');own=old('adbcc8ec279dfce754e24281cdd6d76bf18c7779','CMakeLists.txt')
 begin=own.index('    # AG qualification of the fixed, independently published AE frontend test.')
 block=own[begin:own.index('endif()',begin)]
 cm=cm.replace('    add_executable(dtc_l1_collect_wb_pipeline_probe\n',block+'    add_executable(dtc_l1_collect_wb_pipeline_probe\n',1)
 exact('CMakeLists.txt',cm.encode(),'FIXED_AC_AND_PREVIOUSLY_CPU_QUALIFIED_AE_TEST_REGISTRATIONS')
 for commit,paths in [(AC,['src/gpgpu-sim/dtc-l1-collect-wb.h','tests/dtc_l1_collect_wb_pipeline_probe.cc','tests/dtc_l1_collect_wb_resource_test.cc']),
     (AE,['src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/dtc-l1-tag-index.h','tests/dtc_l1_tag_hash_bankrow_test.cc'])]:
  for path in paths:exact(path,blob(CORE_REPO,commit,path),'BYTE_IDENTICAL_PUBLISHED_'+commit)
 changed=git(CORE,'diff','--name-only',X2).splitlines()
 assert set(changed)=={r['path'] for r in records}
 helper=PACK/'inputs/AC/scripts/audit_source_delta.py'
 spec=importlib.util.spec_from_file_location('ac_source',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 original=old(X2,'src/gpgpu-sim/shader.cc');protected=[]
 for row in json.loads((PACK/'inputs/AC/SOURCE_DELTA.json').read_text())['unchanged_production_functions']:
  signature=row['signature'];a=module.block(original,signature);b=module.block(cc,signature);assert a==b,signature
  protected.append(dict(signature=signature,sha256=hashlib.sha256(a.encode()).hexdigest(),status='BYTE_IDENTICAL_X2'))
 write(PACK/'COMBINED_SOURCE_REVIEW.json',dict(status='PASS_EXACT_AC_AE_UNION_NO_MECHANISM_CONFLICT',
     base=X2,AC=AC,AE=AE,AD='NOT_MERGED_HOLD_UNQUALIFIED',AF='NOT_MERGED',
     shared_conflicts=['CMakeLists.txt','shader.h bool declarations','shader.cc independent initialization guards'],
     conflict_resolution='BOTH EXACT ADDITIONS_RETAINED; NO PRODUCER_SCIENTIFIC_CONTRACT_CHANGE',
     files=records,protected=protected,additional_data_bytes_per_SM_AC_ON=163840,
     additional_data_bytes_per_SM_AC_OFF=0,new_collection_ports=0,all_other_paths_unchanged=True))
 print('PASS: exact AC/AE union; 14 protected X2 bodies; three textual conflicts reviewed, no mechanism changes')

if __name__=='__main__':main()

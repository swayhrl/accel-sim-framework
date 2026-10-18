#!/usr/bin/env python3
"""Summarize only AF-owned CPU results/source. No workload or simulator run."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

PACK=Path(__file__).resolve().parents[1]
CORE=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-af-victim-fallback-core-174-v1')
RAW=Path('/workspace/dtc-lane-af-victim-fallback-174-v1/cpu')
BUILD=Path('/workspace/builds/dtc-lane-af-cpu-174-v1')
BASE='e32afdcf44be3374ff36d22568ed01a075459b6f'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def g(*args):return subprocess.check_output(['git','-C',str(CORE),*args])
def save(name,o): (PACK/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
head=g('rev-parse','HEAD').decode().strip()
assert not g('status','--porcelain').strip()
cases=[json.loads(s) for s in (RAW/'af_test.stdout').read_text().splitlines()]
renamed=[json.loads(s) for s in (RAW/'renamed_pool_witness.stdout').read_text().splitlines()]
cases+=renamed[1:]
assert len(cases)==17 and all(x['status']=='PASS' for x in cases)
assert (RAW/'base_probe.stdout').read_bytes()==(RAW/'af_probe.stdout').read_bytes()
suite=ET.parse(RAW/'ctest_final.xml').getroot()
assert suite.attrib['tests']=='9' and suite.attrib['failures']=='0'
first=ET.parse(RAW/'ctest_attempt1_loader_failure.xml').getroot()
assert first.attrib['failures']=='1'
save('CPU_CASES.json',{'status':'PASS_17_BOUNDED_SYNTHETIC_CASES','cases':cases,
 'expected_new_negative_child_SIGABRT':3,'main_test_stderr_sha256':digest(RAW/'af_test.stderr'),
 'default_off_trace_lines':len((RAW/'af_probe.stdout').read_text().splitlines()),
 'default_off_AF_vs_X2_byte_equal':True,'trace_sha256':digest(RAW/'af_probe.stdout'),
 'trace_scope':'Four deterministic header API sequences: finite/nonfinite x K0/K1; not full-input timing equivalence',
 'source_sha256':{'default_off_probe.cc':digest(PACK/'scripts/default_off_probe.cc'),
                  'renamed_pool_witness.cc':digest(PACK/'scripts/renamed_pool_witness.cc')}})
save('CPU_CHECKS.json',{'status':'PASS_BOUNDED_CPU_WITH_PARTIAL_FULL_INTEGRATION',
 'core_base':BASE,'core_commit':head,'ctest_pass':9,'ctest_total':9,
 'ctests':[dict(name=t.attrib['name'],status='PASS') for t in suite.findall('testcase')],
 'ctest_xml_sha256':digest(RAW/'ctest_final.xml'),'synthetic_cases_pass':17,
 'actual_production_option_parser':'PASS omitted/default0, explicit0, explicit1',
 'default_OFF_CPU_differential':'PASS exact X2 vs AF 524-line probe',
 'K1_and_Ref_generation_sector_and_finite_lifecycle':'PASS_BOUNDED_HEADER_AND_EXISTING_INTEGRATION_TESTS',
 'WB_denial':'PARTIAL_CONTROLLED_NO_RETIRE_HEADER_WITNESS_PLUS_UNCHANGED_PRODUCTION_GATE_SOURCE',
 'candidate_queue_full':'PARTIAL_UNCHANGED_UPSTREAM_GATE_SOURCE_NOT_ACTUAL_QUEUE_INJECTION',
 'unsupported_mode_runtime_gate':'SOURCE_CHECKED_CONSTRUCT_ABORT; NOT_EXERCISED_WITH_REAL_LDST_OBJECT',
 'full_simulator_runs':0,'GPU_or_native_workload_runs':0,'real_input_opportunity_evidence':'UNAVAILABLE',
 'real_input_speedup':'UNKNOWN','new_performance_arm_registered':False,
 'compile_parallel_limit':2,'CTest_parallelism':1,'negative_child_parent_waits':True,
 'statistics_schema_changes':False,'counter_terminal_export':'UNAVAILABLE_NOT_ADDED_TO_SHARED_STATS',
 'scope':'CPU PASS does not establish workload timing/value correctness, real opportunity frequency, or hardware timing/PPA.'})
save('ENGINEERING_FAILURE_PRESERVED.json',{'status':'RESOLVED_TEST_RUNTIME_SEARCH_PATH',
 'first_ctest_pass':8,'first_ctest_total':9,'failed_test':'dtc_l1_reclaimable_victim_option_test',
 'error':'undefined symbol: _ZTI12cache_config',
 'cause':'Inherited LD_LIBRARY_PATH selected /usr/local/cuda-11.8/lib64/libcudart.so rather than the AF Core library.',
 'fix':'CTest environment pins LD_LIBRARY_PATH to the AF cudart target directory; production policy unchanged.',
 'fix_core_commit':head,'final_ctest_pass':9,'first_xml_sha256':digest(RAW/'ctest_attempt1_loader_failure.xml'),
 'first_stdout_sha256':digest(RAW/'ctest_attempt1_loader_failure.stdout'),
 'bound_loader_evidence_sha256':digest(RAW/'af_option_bound_loader.txt'),
 'original_artifacts_preserved_in_AF_raw_root':True})
def timev(name):
    text=(RAW/name).read_text(); out={}
    for key in ['User time (seconds)','System time (seconds)','Elapsed (wall clock) time (h:mm:ss or m:ss)',
                'Maximum resident set size (kbytes)','Swaps','Exit status']:
        m=re.search(r'^\s*'+re.escape(key)+r':\s*(.*)$',text,re.M)
        assert m,(name,key)
        out[key]=m.group(1)
    return out
base_size=json.loads((RAW/'base_sizes.stdout').read_text())
save('RESOURCE_AND_BINARY_IDENTITY.json',{
 'status':'CPU_BUILD_AND_TEST_RESOURCE_RECORD_NOT_GPU_COST',
 'build':timev('build.stderr'),'rebuild':timev('rebuild.stderr'),'ctest_final':timev('ctest_final.stderr'),
 'maximum_compile_jobs_requested':2,'maximum_CTest_jobs_requested':1,
 'max_RSS_scope':'GNU time per-command child maximum, not aggregate two-compiler peak RSS',
 'host_sizeof_X2':base_size,'host_sizeof_AF':renamed[0],
 'host_sizeof_not_RTL_bits':True,'full_core_library_built':True,'trace_executable_built_or_run':False,
 'artifacts':[{'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p)} for p in
     [BUILD/'libcudart.so',BUILD/'dtc_l1_reclaimable_victim_option_test',
      BUILD/'dtc_l1_reclaimable_victim_fallback_test',RAW/'af_probe',RAW/'renamed_pool_witness']],
 'compile_commands_sha256':digest(BUILD/'compile_commands.json'),
 'notes':'Shared host pressure is not attributable to AF. No zero-shared-swap or zero-shared-OOM claim; timev Swaps is process scoped.'})
paths=g('diff','--name-only',BASE,head).decode().splitlines()
rows=[]
for p in paths:
 data=g('show',head+':'+p);assert data==(CORE/p).read_bytes()
 rows.append({'repository':'Core','commit':head,'path':p,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
for p in ['src/gpgpu-sim/dtc-l1-invalidation.h','tests/dtc_l1_source_invalidation_integration_test.cc',
          'tests/dtc_l1_finite_service_test.cc','docs/dtc_l1/DTC_L1_SPEC.md']:
 data=g('show',head+':'+p);assert data==g('show',BASE+':'+p)
 rows.append({'repository':'Core_unchanged_reference','commit':head,'path':p,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
out=io.StringIO();w=csv.DictWriter(out,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
(PACK/'SOURCE_SHA256.tsv').write_text(out.getvalue())
(PACK/'CORE_DELTA.patch').write_bytes(g('diff','--unified=0',BASE,head,'--'))
source=CORE/'src/gpgpu-sim'
def unchanged_block(path,marker,ending):
    a=g('show',BASE+':'+path).decode();b=(CORE/path).read_text()
    def block(text):
        start=text.index(marker);return text[start:text.index(ending,start)+len(ending)]
    return block(a)==block(b)
checks={
 'default0_registration':'"-gpgpu_dtc_l1_reclaimable_victim_fallback", OPT_BOOL' in (source/'gpu-sim.cc').read_text(),
 'only_PAPER_OO_on':'dtc_l1_reclaimable_victim_fallback &&' in (source/'shader.cc').read_text(),
 'old_statistics_contract_unchanged':all([
    unchanged_block('src/gpgpu-sim/shader.cc','void ldst_unit::get_dtc_l1_stats(', '\n}\n'),
    unchanged_block('src/gpgpu-sim/shader.cc','void gpgpu_sim::shader_print_dtc_l1_stats(', '\n}\n'),
    unchanged_block('src/gpgpu-sim/dtc-l1-common.h','struct paper_frontend_stats {','\n};')]),
 'invalidation_contract_unchanged':not g('diff',BASE,head,'--','src/gpgpu-sim/dtc-l1-invalidation.h').strip(),
 'frozen_spec_unchanged':not g('diff',BASE,head,'--','docs/dtc_l1/DTC_L1_SPEC.md').strip(),
 'old_CTests_unchanged':all(not g('diff',BASE,head,'--','tests/'+n+'.cc').strip() for n in
   ['dtc_l1_m1_common_test','dtc_l1_bad_generation_test','dtc_l1_completion_accounting_test',
    'dtc_l1_finite_service_test','dtc_l1_source_invalidation_test','dtc_l1_source_invalidation_integration_test','dtc_l1_k0_equivalence_test']),
}
assert all(checks.values())
save('SOURCE_SCOPE_AUDIT.json',{'status':'PASS_CANDIDATE_ONLY_DELTA','core_base':BASE,'core_commit':head,
 'changed_paths':paths,'checks':checks,'additional_free_variables':['requested default-off fallback boolean only'],
 'new_stats_schema_or_IO_sector_policy':False,'real_input_data_reads':0})
print(json.dumps({'status':'PASS_AF_CPU_EVIDENCE_COLLECTION','core_commit':head,'CPU_cases':len(cases),'ctest_pass':9}))

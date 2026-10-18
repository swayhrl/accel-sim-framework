"""Audit actual final CPU outputs and build identity; no build or simulator run."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser()
for name in ('core','raw','pack'):ap.add_argument('--'+name,required=True,type=Path)
a=ap.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=a.core,text=True).strip()
log=a.raw/'ctest-authorized-qualified.log';text=log.read_text()
assert '100% tests passed, 0 tests failed out of 9' in text
assert len(re.findall(r'^\d/9 Test #\d: .*Passed',text,re.M))==9
header='\n'.join(line[3:] for line in text.splitlines() if line.startswith('8: '))
ldst='\n'.join(line[3:] for line in text.splitlines() if line.startswith('9: '))
for n in (4,5,8,9):
 for on in (0,1):assert f'PASS fanout={n} progressive={on} quota=4 plus1=preserved' in header
for name in ('PASS late_merge slot_reuse generation K1 old_return final_ref external_dependency',
             'PASS multiple_allocations partial_allocation tag_victim last_ref',
             'PASS fail_closed sizeof_config=56 sizeof_service_entry=48 sizeof_oo=816'):
 assert name in header
assert 'PASS real_LDST legal_4x32 sectors duplicate illegal stale_generation plus1 own_ready late_merge partial_admission collection RF_WB_backpressure ledger_retire K1 final_ref fence_sidecar normal_export_repeat_readonly kernels=0 gpu_cycle_calls=0 threads_started=0 payload_values=UNPROVEN' in ldst
assert ldst.count('OO response identity/address mismatch')==3
assert ldst.count('OO fill must match the original physical generation')==1
prefix='DTC_PROGRESSIVE_WAKE_V1'
def fields(line):
 pairs=[piece.split('=',1) for piece in line.split()[1:]]
 row={key:int(value) for key,value in pairs};assert len(row)==len(pairs);return row
summary=[fields(line) for line in ldst.splitlines() if line.startswith(prefix+' ')]
ldst_rows=[fields(line) for line in ldst.splitlines() if line.startswith(prefix+'_LDST ')]
assert len(summary)==len(ldst_rows)==3 and all(row==summary[0] for row in summary) and all(row==ldst_rows[0] for row in ldst_rows)
assert summary[0]==dict(sm=0,broadcasts=1,first_notify_cycle_sum=11,last_notify_cycle_sum=13,span_sum=2,
 own_dep0_linewide_blocked_entry_cycles=12,notified_frontend_ready_entries=10,notified_frontend_ready_entry_cycles=122,late_merges=1)
assert ldst_rows[0]==dict(sm=0,admitted_notified_collectable=10,admitted_returns_to_retire_sum=120,retired=10)
hist=[fields(line) for line in ldst.splitlines() if line.startswith(prefix+'_FANOUT ')]
assert len(hist)==99
for row in hist:assert row['sm']==0 and row['count']==(1 if row['bin']==10 else 0)
assert 'DTC_PROGRESSIVE_WAKE_V1_LINE ' not in ldst
services={}
for key,value in re.findall(r'^DTC_SERVICE_V1_(\w+) = (\d+)$',ldst,re.M):
 value=int(value)
 if key in services:assert services[key]==value
 services[key]=value
assert services['fully_ready_to_complete_sum']==112
assert services['ready_to_collect_sum']==101 and services['collection_cycles']==10 and services['wb_wait']==1
assert services['fully_ready_to_complete_sum']==services['ready_to_collect_sum']+services['collection_cycles']+services['wb_wait']
assert services['map_loss_to_free_sum']==21 and services['map_loss_to_free_count']==1
invalidation=[fields(line) for line in ldst.splitlines() if line.startswith('DTC_INVALIDATE_V1_SUMMARY ')]
assert len(invalidation)==3 and all(row==invalidation[0] for row in invalidation)
assert invalidation[0]['first_request_cycle']==11 and invalidation[0]['first_ordinary_commit_cycle']==14
layout_line=next(line for line in ldst.splitlines() if line.startswith('AD_HOST_LAYOUT '));layout=fields(layout_line)
assert layout==dict(physical_line=96,entry=64,config=56,service=48,frontend=816,ldst=3392)
buildlog=(a.raw/'build-pass-3-authorized-cpu-only.log').read_text()
objects=re.findall(r'Building CXX object (.*)',buildlog)
assert len(objects)==3 and sum('progressive_' in row for row in objects)==2 and sum('cuda-sim.cc.o' in row for row in objects)==1
trace=(a.raw/'configure-only-after-mapping.exec.log').read_text()
executed=[line for line in trace.splitlines() if 'execve(' in line and line.endswith(' = 0')]
compiler_probes=[line for line in executed if re.search(r'execve\("[^\"]*/(?:nvcc|cc1plus|g\+\+|c\+\+|gcc|cc)"',line)]
assert len(compiler_probes)==4
assert all('"-E"' in line or '"--version"' in line or '"__cmake_determine_cuda"' in line for line in compiler_probes)
assert all('"-c"' not in line for line in compiler_probes)
assert not git('status','--porcelain')
source_cpp_identical=not git('diff','731be8548ad0fcc167ebfc49d5f1867f22034b4c','HEAD','--','src','tests')
assert source_cpp_identical and git('diff','731be8548ad0fcc167ebfc49d5f1867f22034b4c','HEAD','--name-only')=='CMakeLists.txt'
for source,name in [('off-differential-qualified/OFF_DIFFERENTIAL.json','FINAL_OFF_DIFFERENTIAL.json'),
 ('mode-guard-qualified/EXISTING_LIBRARY_MODE_GUARD.json','FINAL_MODE_GUARD.json'),
 ('normal-progressive-qualified/EXISTING_NORMAL_ON_EXPORT.json','FINAL_NORMAL_EXPORT.json')]:
 src=a.raw/source;assert json.loads(src.read_text())['status'].startswith('PASS_');(a.pack/name).write_bytes(src.read_bytes())
(a.pack/'ADDITIONAL_BUILD_AUTHORIZATION.json').write_bytes((a.raw/'ADDITIONAL_BUILD_AUTHORIZATION.json').read_bytes())
artifacts={}
for name in ('build-pass-3-authorized-cpu-only.log','ctest-authorized-final.log','ctest-authorized-qualified.log','ldst-authorized-linear.log',
 'configure-only-after-mapping.log','configure-only-after-mapping.exec.log','build/dtc_l1_ad_cpu.config','cpu-component-linear.config'):
 p=a.raw/name;artifacts[name]=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
binaries={}
for name in ('libcudart.so','dtc_l1_progressive_wakeup_test','dtc_l1_progressive_ldst_test','dtc_l1_normal_export_probe'):
 p=a.raw/'build'/name;binaries[name]=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
result=dict(status='PASS_CPU_COMPONENT_QUALIFICATION_WITH_SCOPE_LIMITS',core_head=git('rev-parse','HEAD'),
 fixed_base='e32afdcf44be3374ff36d22568ed01a075459b6f',
 built_Cpp_source_commit='731be8548ad0fcc167ebfc49d5f1867f22034b4c',embedded_build_string='gpgpu-sim_git-commit-731be854_modified_0.0.',
 final_vs_built_delta='CMake CPU test runtime config only; all production and test C++ files byte-identical',
 Cpp_source_identity_verified=source_cpp_identical,ctest_passed=9,ctest_total=9,
 total_object_build_attempts=3,user_authorized_original_attempts=2,user_authorized_additional_CPU_builds=1,
 authorized_incremental_object_compilations=objects,
 dependency_refresh='CMake ptxsim depends on gen_build_string: unchanged cuda-sim.cc rebuilt for new version string, libptxsim/libcudart relinked. No production mechanism source changed.',
 postbuild_configure='Generated supported one-channel linear CPU config; no object compilation/link/build. CUDA metadata/preprocessor/version probes executed, explicitly recorded.',
 postbuild_configure_compiler_metadata_probes=compiler_probes,
 initial_attempt_after_authorized_build='8/9 because inherited IPOLY mapping invalid for fixture1 channel; failure retained; final CTest uses generated linear config and is9/9',
 actual_metrics=summary[0],actual_ldst=ldst_rows[0],actual_service=services,actual_invalidation=invalidation[0],actual_host_layout=layout,
 metric_scope='Three identical snapshots: twice production aggregate printer then actual gpu_print_stat. All10 cacheable consumers actually retired in CPU fixture; common boundary120 vs ready boundary112 are different intervals, not performance.',
 resources=dict(derived_default_OO_incremental_persistent_host_bytes_per_SM=33112,excludes='allocator/list overhead and temporary assertion maps; no payload capacity increase'),
 artifacts=artifacts,binaries=binaries,full_simulators_started=0,GPU_cycle_calls=0,simulation_threads_started=0,native_benchmarks=0,
 scope_limit='Real production header and actual LDST component methods with prepared metadata/PIB/sector/RF state. Full SASS issue/coalescer/interconnect/hardware workload and payload/value ISA correctness not established; no performance claim.')
(a.pack/'FINAL_CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],core=result['core_head'],ctest='9/9',common_to_retire=120,ready_to_complete=112,build_attempts=3)))

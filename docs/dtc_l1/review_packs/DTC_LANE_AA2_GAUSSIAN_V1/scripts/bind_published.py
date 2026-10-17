"""Bind immutable X/V/Z2 evidence and audit the candidate runtime, CPU only."""
from common import *


def main():
    xref='refs/remotes/origin/hrl/iscas2027-dtc-lane-x-implementation-174-v1'
    zref='refs/remotes/origin/hrl/iscas2027-dtc-lane-z2-u-evidence-174-v1'
    xcommit=git(FW_REPO,'rev-parse',xref)
    zcommit=git(FW_REPO,'rev-parse',zref)
    xpack='docs/dtc_l1/review_packs/DTC_LANE_X_OPTIN_INVALIDATION_V1'
    zpack='docs/dtc_l1/review_packs/DTC_LANE_Z2_U_EVIDENCE_V1'
    proven=[]
    for name in ['SOURCE_AND_BINARY_IDENTITY.json','SOURCE_EVENT_AUDIT.json','CORNER_CASE_CHECKS.json',
                 'GIT_DELIVERY.json','LATEST_REPORT.md','DEFAULT_OFF_EQUIVALENCE_PLAN.md','FLUSH_STATE_TRANSITION.md']:
        proven.append(copy_blob(FW_REPO,xcommit,xpack+'/'+name,PACK/'inputs/X'/name))
    for name in ['K1_INTERPRETATION_V2.md','FORMULA_VALIDATION.json']:
        proven.append(copy_blob(FW_REPO,zcommit,zpack+'/'+name,PACK/'inputs/Z2'/name))
    identity=json.loads((PACK/'inputs/X/SOURCE_AND_BINARY_IDENTITY.json').read_text())
    assert identity['built_core_sha']==CANDIDATE_CORE
    assert identity['new_option']==K_OPTION and identity['option_default']==0
    assert identity['lane_v_contract_sha']==V_SHA
    assert identity['framework_build_source_sha']=='0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc'
    assert identity['full_performance_jobs_dispatched']==0
    assert CANDIDATE_CORE!='f8b34dd7a738caddf4f23dd417e34c0b63c206d9'
    runtime=next(r for r in identity['binaries'] if r['path'].endswith('/accel-sim.out'))
    library=next(r for r in identity['binaries'] if r['path'].endswith('/libcudart.so'))
    actual=[]
    for r in [runtime,library]:
        assert Path(r['path']).stat().st_size==r['size_bytes']
        assert sha(r['path'])==r['sha256']
        actual.append(dict(**r,AA2_rehash='PASS',purpose='CANDIDATE_NOT_ADMITTED_OR_EXECUTED'))
    assert identity['embedded_core_build_string'].encode() in Path(library['path']).read_bytes()
    env={'PATH':'/usr/bin:/bin','LANG':'C','LD_LIBRARY_PATH':identity['runtime_loader_pin']['required_ld_library_path']}
    result=subprocess.run(['/usr/bin/ldd',runtime['path']],env=env,capture_output=True,text=True)
    write(ROOT/'CANDIDATE_LDD.json',dict(argv=['/usr/bin/ldd',runtime['path']],environment=env,
          exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,no_workload_executed=True))
    assert result.returncode==0 and 'not found' not in result.stdout
    match=re.search(r'libcudart\.so\s+=>\s+(\S+)',result.stdout)
    assert match and Path(match[1]).resolve()==Path(library['path']).resolve()
    code_trees={}
    for directory in ['gpu-simulator','util']:
        built=git(FW_REPO,'rev-parse',identity['framework_build_source_sha']+':'+directory)
        orchestration=git(FW_REPO,'rev-parse',AA_SHA+':'+directory)
        assert built==orchestration==identity['framework_code_trees_unchanged_from_build'][directory]
        code_trees[directory]=built
    # The supplied Z2 published contract has a fixed content hash and source V.
    zhash=sha(PACK/'inputs/Z2/K1_INTERPRETATION_V2.md')
    assert zhash=='bad86ae9be5ab7958171fcddf1b9790f8ec1e66d030eb5d490bee9b5a1f67d7d'
    fixed_z='35ff4bc3660dc7653be5d9a3d5a166b610effcf9'
    subprocess.run(['git','-C',str(FW_REPO),'merge-base','--is-ancestor',fixed_z,zcommit],check=True)
    write(PACK/'PUBLISHED_BINDINGS.json',dict(utc=now(),provenance=proven,
          X_review_fetch_back_commit=xcommit,X_core_fetch_back_commit=CANDIDATE_CORE,
          X_functional_Core=True,X_default_OFF=True,V_contract_commit=V_SHA,
          Z2_contract_id='Z2_K1_SOURCE_REQUEST_V2',Z2_binding_commit=fixed_z,
          Z2_remote_fetch_back_commit=zcommit,Z2_contract_sha256=zhash,
          candidate_artifacts=actual,runtime_pinned_library_resolution=True,
          candidate_LDD_receipt_sha256=sha(ROOT/'CANDIDATE_LDD.json'),
          Framework_build_source=identity['framework_build_source_sha'],Framework_code_trees=code_trees,
          executable_preregistration_complete=False,launch_admitted=False,
          Y2_gate='PENDING_EXACT_PUBLISHED_GATE',all_four_same_event_observer='UNRESOLVED_SOURCE_ONLY_ON_K1'))
    # Exact source-only observation; no claim that host overhead equals GPU cycles.
    shader=blob(CORE_REPO,CANDIDATE_CORE,'src/gpgpu-sim/shader.cc').decode()
    header=blob(CORE_REPO,CANDIDATE_CORE,'src/gpgpu-sim/dtc-l1-invalidation.h').decode()
    excerpts=[]
    for text,path,first,last in [(shader,'src/gpgpu-sim/shader.cc',3665,3671),
           (shader,'src/gpgpu-sim/shader.cc',4014,4031),
           (shader,'src/gpgpu-sim/shader.cc',5169,5180),
           (header,'src/gpgpu-sim/dtc-l1-invalidation.h',22,32)]:
        excerpts.append(dict(path=path,first_line=first,last_line=last,
                              text='\n'.join(text.splitlines()[first-1:last])))
    assert 'if (m_config->dtc_l1_invalidate_on_source_event)\n    m_dtc_invalidation.print(fp);' in shader
    assert 'Original K0 ordinary request' in shader
    write(PACK/'OBSERVER_CONTRACT_AUDIT.json',dict(status='HOLD_SHARED_OBSERVER_CONTRACT_UNRESOLVED',
          core=CANDIDATE_CORE,K_option=K_OPTION,default_value=0,excerpts=excerpts,
          source_request_count_hook='source_invalidation_observer::request at LDST source request',
          actual_counter_availability=dict(K0='NO_SOURCE_INVALIDATION_SUMMARY_PRINTED',K1='DTC_INVALIDATE_V1_SUMMARY_PER_SM_CUMULATIVE'),
          summary_print_guard='K_OPTION==1',detailed_records_limit_option='-gpgpu_dtc_l1_debug_event_limit',
          detailed_records_default=0,aggregate_counters_bounded_by_detail_limit=False,
          source_requested_policy='SAME_NEW_BINARY_SAME_OPTIONS_EXCEPT_K_TAG_SAME_EVENT_OBSERVATION_CONTRACT_AND_OVERHEAD',
          author_time_model='ZERO_ADDITIONAL_SIMULATED_CYCLES_AT_SOURCE_REQUEST',
          host_overhead_equal_to_simulated_cycles=False,
          AA2_accepts_observer_parity=False,requires_independent_gate_or_scientific_resolution=True,
          no_Core_modification_or_second_Core_requested=True))
    print('Bound published functional X Core/runtime, V and Z2; no simulation admitted.')


if __name__=='__main__':main()

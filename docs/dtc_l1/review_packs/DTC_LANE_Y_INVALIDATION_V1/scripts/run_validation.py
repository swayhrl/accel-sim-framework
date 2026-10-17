#!/usr/bin/env python3
"""CPU-only reproducible validation; always fails closed for current STOP Core.
No commands in this runner dispatch a simulator, trace replay or GPU workload.
"""
import argparse
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from datetime import datetime, timezone, timedelta

HERE=Path(__file__).resolve().parent
PACK=HERE.parent
sys.path.insert(0,str(HERE))
from reference_model import subset

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--core-repo',type=Path,required=True)
    ap.add_argument('--core-source',type=Path,required=True)
    ap.add_argument('--core-sha',required=True)
    ap.add_argument('--frozen-sha',required=True)
    ap.add_argument('--external',type=Path,required=True)
    ap.add_argument('--framework-repo',type=Path,required=True)
    ap.add_argument('--lane-v-sha',required=True)
    args=ap.parse_args()
    ext=args.external.resolve();ext.mkdir(parents=True,exist_ok=True)
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    receipts=[];rows=[];reference=[];production=[];options=[];failures=[]
    def cmd(argv, label, expected=0, cwd=None, check=True):
        completed=subprocess.run([str(x) for x in argv],cwd=cwd,text=True,capture_output=True)
        stdout=ext/(label+'.stdout');stderr=ext/(label+'.stderr')
        stdout.write_text(completed.stdout);stderr.write_text(completed.stderr)
        item=dict(label=label,argv=[str(x) for x in argv],cwd=str(cwd or Path.cwd()),
                  expected_exit_code=expected,exit_code=completed.returncode,
                  stdout_path=str(stdout),stdout_sha256=sha(stdout),stderr_path=str(stderr),stderr_sha256=sha(stderr))
        receipts.append(item)
        if check and completed.returncode!=expected:
            failures.append(item)
            dump(PACK/'HARNESS_FAILURE.json',dict(unexpected_failures=failures,status='FAIL_CLOSED_HARNESS_ERROR'))
            raise RuntimeError('Unexpected command exit: '+label+'; do not use stale binaries or results')
        return completed
    def git(*argv):
        r=cmd(['git','-C',args.core_repo,*argv],'git_'+str(len(receipts)))
        if r.returncode:raise RuntimeError(r.stderr)
        return r.stdout.strip()
    v_remote=cmd(['git','-C',args.framework_repo,'ls-remote','--heads','origin','hrl/iscas2027-dtc-lane-v-semantic-audit-174-v1'],'lane_v_remote').stdout.strip()
    assert v_remote.split()[0]==args.lane_v_sha
    assert args.lane_v_sha=='26abd496417d9392245052e54fbd9ba27c6ffd96', 'New contract requires explicit semantic review'
    v_bindings=[]
    for name in ['K1_SEMANTIC_CONTRACT.md','SOURCE_EVENT_MAP.md','OPEN_QUESTIONS.md','WRITE_VISIBILITY_RISK_MATRIX.tsv','LATEST_REPORT.md']:
        path='docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/'+name
        data=subprocess.check_output(['git','-C',str(args.framework_repo),'show',args.lane_v_sha+':'+path])
        blob=subprocess.check_output(['git','-C',str(args.framework_repo),'rev-parse',args.lane_v_sha+':'+path],text=True).strip()
        v_bindings.append(dict(commit=args.lane_v_sha,path=path,blob=blob,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),access='git_object_only'))
    dump(PACK/'CONTRACT_BINDING.json',dict(lane_v_commit=args.lane_v_sha,lane_v_remote_observation=v_remote,files=v_bindings,review_scope='K1 sections 1-6 and V01-V10 independently read; no implementation authorization inferred',reference_model_scope='OO lifetime subset; IO abstract shadow model only; no timing or ISA value proof'))
    published=git('ls-remote','--heads','origin','hrl/iscas2027-dtc-lane-x-invalidate-optin-core-174-v1')
    assert published.split()[0]==args.core_sha, 'Lane X HEAD moved: fetch and re-audit instead of aliasing'
    assert git('rev-parse',args.core_sha)==args.core_sha
    source_head=cmd(['git','-C',args.core_source,'rev-parse','HEAD'],'source_head').stdout.strip()
    assert source_head==args.core_sha
    assert cmd(['git','-C',args.core_source,'status','--porcelain','--untracked-files=no'],'source_clean_before').stdout==''
    diff=git('diff','--name-only',args.frozen_sha,args.core_sha).splitlines()
    executable_diff=[p for p in diff if not p.startswith('docs/')]
    assert not executable_diff, 'Current runner audits documentation-only STOP, not a later implementation'
    source_items={}
    for rel in ['src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','src/option_parser.cc']:
        current=git('rev-parse',args.core_sha+':'+rel)
        frozen=git('rev-parse',args.frozen_sha+':'+rel)
        assert current==frozen
        source_items[rel]=dict(published_blob=current,frozen_blob=frozen,identical=True,sha256=sha(args.core_source/rel))
    findings=[
        ('CLUSTER_TICK','src/gpgpu-sim/gpu-sim.cc',2515,2527,['if (m_config.gpgpu_flush_l1_cache)','get_not_completed() == 0','cache_invalidate()']),
        ('CACHE_PREFERENCE','src/gpgpu-sim/gpu-sim.cc',1749,1755,['cache_config !=','cache_invalidate()']),
        ('MEMBAR','src/gpgpu-sim/shader.cc',6874,6890,['pendingWrites(warp_id)','flush_l1()','cache_invalidate()']),
        ('DTC_NOT_INVALIDATED','src/gpgpu-sim/shader.cc',4012,4015,['m_L1D->invalidate()']),
        ('DEFERRED_CONVENTIONAL_TAG','src/gpgpu-sim/gpu-cache.cc',1268,1286,['m_invalidate_pending = true','!conventional_miss_lifecycle_active()','m_tag_array->invalidate()']),
        ('CONVENTIONAL_DRAIN_SCOPE','src/gpgpu-sim/gpu-cache.h',1472,1478,['m_miss_queue.empty()','m_extra_mf_fields.empty()','m_mshrs.empty()'])]
    audited=[]
    for name,path,start,end,fragments in findings:
        excerpt='\n'.join((args.core_source/path).read_text().splitlines()[start-1:end])
        assert all(fragment in excerpt for fragment in fragments),name
        audited.append(dict(id=name,path=path,first_line=start,last_line=end,excerpt=excerpt))
    dump(PACK/'SOURCE_AUDIT.json',dict(core=args.core_sha,frozen=args.frozen_sha,changed_paths=diff,executable_changed_paths=executable_diff,blobs=source_items,findings=audited,independent_static_audit=True))
    for case in json.loads((PACK/'inputs/events.json').read_text())['cases']:
        for mode in case['modes']:
            label=case['id']+'_'+mode
            argv=[sys.executable,HERE/'reference_model.py','--cases',PACK/'inputs/events.json','--case',case['id'],'--mode',mode]
            run=cmd(argv,'reference_'+label,case.get('expected_exit_code',0))
            observation=json.loads(run.stdout)
            assert observation['status']=='REFERENCE_ONLY_PASS'
            # Deliberately wrong final free count must fail the independent checker.
            negative=cmd(argv+['--corrupt-expected'],'reference_bad_expected_'+label,1)
            observation['failure_negative_exit_code']=negative.returncode
            reference.append(observation)
            rows.append(dict(id=label,layer='REFERENCE_ONLY',input='inputs/events.json#'+case['id'],expected='EXPECTED_AND_OBSERVED.json#reference/'+label,expected_exit_code=case.get('expected_exit_code',0),observed_exit_code=run.returncode,negative_exit_code=negative.returncode,status='PASS_PROVISIONAL_MODEL_ONLY',uncovered='Production source predicate; K1 integration; IO orphan mechanism; bank RMW timing; SASS load values'))
    binaries={}
    for lineage,source in [('published_x',args.core_source/'src/gpgpu-sim'),('frozen',ext/'frozen')]:
        if lineage=='frozen':
            source.mkdir(exist_ok=True)
            blob=subprocess.check_output(['git','-C',str(args.core_repo),'show',args.frozen_sha+':src/gpgpu-sim/dtc-l1-common.h'])
            (source/'dtc-l1-common.h').write_bytes(blob)
        binary=ext/('core_probe_'+lineage)
        binary.unlink(missing_ok=True)
        cmd(['g++','-std=c++14','-Wall','-Wextra','-Werror','-UNDEBUG','-I'+str(source),HERE/'core_cpu_probe.cc','-o',binary],'compile_'+lineage)
        binaries[lineage]=dict(path=str(binary),sha256=sha(binary),header_sha256=sha(source/'dtc-l1-common.h'))
        for case in json.loads((PACK/'inputs/core_probes.json').read_text())['cases']:
            run=cmd([binary,case['id']],lineage+'_'+case['id'],case['exit_code'])
            observed=json.loads(run.stdout) if run.returncode==0 else dict(assertion_matched=case['expected_assert'] in run.stderr)
            expected=case.get('expected',dict(assertion_matched=True))
            subset(expected,observed)
            exp_path=ext/'checker_expected.json';obs_path=ext/'checker_observed.json'
            bad=copy.deepcopy(expected)
            key=next(iter(bad));bad[key]=['INTENTIONAL_WRONG_EXPECTATION']
            dump(exp_path,bad);dump(obs_path,observed)
            negative=cmd([sys.executable,HERE/'check_json.py',exp_path,obs_path],'bad_expected_'+lineage+'_'+case['id'],1)
            production.append(dict(lineage=lineage,id=case['id'],input=dict(argv=[str(binary),case['id']],source='scripts/core_cpu_probe.cc#'+case['id']),expected=expected,observed=observed,expected_exit_code=case['exit_code'],exit_code=run.returncode,failure_negative_exit_code=negative.returncode,scope='common_header_not_K1_invalidation'))
            rows.append(dict(id=lineage+'_'+case['id'],layer='PRODUCTION_COMMON_HEADER',input='scripts/core_cpu_probe.cc#'+case['id'],expected='inputs/core_probes.json#'+case['id'],expected_exit_code=case['exit_code'],observed_exit_code=run.returncode,negative_exit_code=negative.returncode,status='PASS_EXISTING_LIFETIME_ONLY',uncovered='source-triggered K1 invalidation not implemented'))
    for case in json.loads((PACK/'inputs/core_probes.json').read_text())['cases']:
        pair=[p for p in production if p['id']==case['id']]
        assert pair[0]['observed']==pair[1]['observed'] and pair[0]['exit_code']==pair[1]['exit_code']
    # Full library compilation is optional only if the caller did not build it yet.
    # This runner builds it explicitly; it never executes the library simulator entrypoint.
    build=ext/'full-core-build'
    cmd(['cmake','-S',args.core_source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCUDAToolkit_ROOT=/usr/local/cuda-11.8','-DGPGPUSIM_BUILD_DTC_L1_TESTS=ON','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'],'configure_full_core')
    cmd(['cmake','--build',build,'--target','cudart','dtc_l1_m1_common_test','dtc_l1_bad_generation_test','dtc_l1_completion_accounting_test','dtc_l1_finite_service_test','-j4'],'build_full_core')
    for test in ['dtc_l1_m1_common_test','dtc_l1_bad_generation_test','dtc_l1_completion_accounting_test','dtc_l1_finite_service_test']:
        r=cmd([build/test],'upstream_'+test)
        production.append(dict(id=test,lineage='published_x',expected_exit_code=0,exit_code=r.returncode,scope='upstream_regression_not_independent_invalidation'))
    library=build/'libcudart.so'
    options_bin=ext/'options_cpu_probe'
    cmd(['g++','-std=c++17','-DCUDART_VERSION=11080','-I'+str(args.core_source/'src'),'-I'+str(args.core_source/'libcuda'),'-I/usr/local/cuda-11.8/include',HERE/'options_cpu_probe.cc','-L'+str(build),'-Wl,-rpath,'+str(build),'-lcudart','-o',options_bin],'compile_options_probe')
    option_cases=[('default',[],0,'LANE_Y_OPTIONS_ONLY flush_l1=0'),('io_flush',['-gpgpu_dtc_l1_mode','2','-gpgpu_flush_l1_cache','1'],0,'LANE_Y_OPTIONS_ONLY flush_l1=1'),('oo_flush_finite',['-gpgpu_dtc_l1_mode','3','-gpgpu_flush_l1_cache','1','-gpgpu_dtc_l1_finite_service','1'],0,'LANE_Y_OPTIONS_ONLY flush_l1=1'),('reject_unknown',['-lane_y_nonexistent_option','1'],1,''),('new_option_off_absent',['-gpgpu_dtc_l1_invalidate_on_source_event','0'],1,''),('new_option_on_absent',['-gpgpu_dtc_l1_invalidate_on_source_event','1'],1,'')]
    binding=cmd(['env','LD_LIBRARY_PATH='+str(build),'ldd',options_bin],'options_dynamic_binding')
    assert str(library) in binding.stdout, 'Options probe did not load the independently built published Core library'
    for label,argv,rc,expected in option_cases:
        run=cmd(['env','LD_LIBRARY_PATH='+str(build),options_bin,*argv],'options_'+label,rc)
        assert not expected or expected in run.stdout
        selected=[line for line in run.stdout.splitlines() if any(token in line for token in ['-gpgpu_dtc_l1_mode','-gpgpu_dtc_l1_finite_service','-gpgpu_flush_l1_cache','LANE_Y_OPTIONS_ONLY'])]
        if rc == 0:
            parsed={line.split()[0]:line.split()[1] for line in selected if line.startswith('-')}
            expected_values={'-gpgpu_dtc_l1_mode':'0','-gpgpu_dtc_l1_finite_service':'0','-gpgpu_flush_l1_cache':'0'}
            expected_values.update(dict(zip(argv[::2],argv[1::2])))
            subset(expected_values,parsed)
            dump(ext/'checker_expected.json',dict(expected_values, **{'-gpgpu_dtc_l1_mode':'WRONG'}))
            dump(ext/'checker_observed.json',parsed)
            negative=cmd([sys.executable,HERE/'check_json.py',ext/'checker_expected.json',ext/'checker_observed.json'],'options_bad_expected_'+label,1)
        else:
            expected_values={'unknown_option_rejected':True}
            parsed={'unknown_option_rejected':("Unknown Option: '"+argv[0]+"'") in run.stderr}
            subset(expected_values,parsed)
            negative=None
        options.append(dict(id=label,argv=argv,expected_values=expected_values,observed_values=parsed,expected_echo=expected,observed_echo=selected,expected_exit_code=rc,exit_code=run.returncode,failure_negative_exit_code=negative.returncode if negative else rc,scope='actual_gpgpu_sim_config_registration_options_only_no_GPU_init'))
        rows.append(dict(id='options_'+label,layer='PRODUCTION_LIBRARY_OPTIONS_ONLY',input='options_cpu_probe '+ ' '.join(argv),expected=str(expected_values),expected_exit_code=rc,observed_exit_code=run.returncode,negative_exit_code=negative.returncode if negative else rc,status='PASS_PARSER_OBSERVATION_NOT_K0_PROOF',uncovered='No new K0 OFF execution path or complete input replay'))
    assert cmd(['git','-C',args.core_source,'status','--porcelain','--untracked-files=no'],'source_clean_after').stdout==''
    dump(PACK/'BUILD_AND_COMMAND_RECEIPTS.json',dict(core=args.core_sha,full_library=dict(path=str(library),sha256=sha(library),dynamic_binding_checked=True),compile_commands_sha256=sha(build/'compile_commands.json'),cmake_cache_sha256=sha(build/'CMakeCache.txt'),binaries=binaries,options_binary=dict(path=str(options_bin),sha256=sha(options_bin)),commands=receipts,unexpected_failures=failures,raw_logs_committed=False))
    dump(PACK/'EXPECTED_AND_OBSERVED.json',dict(schema=1,reference=reference,production=production,options=options,unexpected_failures=failures,reference_is_production_evidence=False,full_simulations_dispatched=0))
    for case in json.loads((PACK/'inputs/k1_contract_cases.json').read_text())['cases']:
        rows.append(dict(id=case['id'],layer='LANE_V_REQUIRED_PRODUCTION_ACCEPTANCE',input='inputs/k1_contract_cases.json#'+case['id'],expected=case['expected'],expected_exit_code=0,observed_exit_code='NOT_RUN',negative_exit_code='NOT_IMPLEMENTED',status='FAIL_CLOSED',uncovered=case['missing']))
    fieldnames=['id','layer','input','expected','expected_exit_code','observed_exit_code','negative_exit_code','status','uncovered']
    for label in ['K0_NEW_INVALIDATION_SWITCH_OFF','K1_SOURCE_EVENT_INVALIDATION','K1_OLD_CONSUMER_VALUE_SAFETY','K1_INFLIGHT_VALUE_SAFETY','K1_SAME_MULTI_BANK_RMW']:
        rows.append(dict(id=label,layer='REQUIRED_GATE',input='Lane X STOP Core '+args.core_sha,expected='implemented option and Lane V bound production behavior',expected_exit_code=0,observed_exit_code='NOT_RUN',negative_exit_code='NOT_IMPLEMENTED',status='FAIL_CLOSED',uncovered='No production K1 interface in released Core'))
    with (PACK/'TEST_MATRIX.tsv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat()
    gate=dict(schema=1,goal='DTC_LANE_Y_INDEPENDENT_INVALIDATION_VALIDATION_174_V1',as_of=now,status='FAIL_CLOSED',lane_aa_authorized=False,full_simulation_dispatch_owner='Lane AA',full_simulations_dispatched=0,production_code_modified=False,core_commit=args.core_sha,frozen_core_commit=args.frozen_sha,core_release='DOCUMENTATION_ONLY_SCIENTIFIC_STOP',lane_v_contract_commit=args.lane_v_sha,lane_v_binding_status='REVIEWED_CONTRACT_FOR_REVIEW_NOT_IMPLEMENTATION_PASS',reference_cases=len(reference),independent_production_probes=len([p for p in production if 'expected' in p]),upstream_regressions=4,k0=dict(new_switch_exists=False,new_switch_off_runtime_proven=False,existing_code_blob_identical=True,cpu_common_regression_paired=True,whole_input_equivalence_proven=False,recommendation='Lane AA must rerun K0 on full identical inputs as strict pair if a later implementation cannot establish frozen-equivalent OFF semantics; old results cannot substitute'),k1=dict(old_consumer_value_safety_proven=False,inflight_return_value_safety_proven=False,state_safety_proven=False,source_event_contract_bound=True),blockers=['Lane X published STOP without K0/K1 interface','Lane V K1-01 through K1-08 production acceptance not executed','Old consumers and in-flight value/order safety not established'],unexpected_test_failures=len(failures),runner_expected_exit_code=3)
    dump(PACK/'VALIDATION_GATE.json',gate)
    print(json.dumps(dict(status=gate['status'],reference_comparisons=len(reference),production_probes=len([p for p in production if 'expected' in p]),upstream_regressions=4,unexpected_failures=len(failures))))
    return 1 if failures else 3

if __name__=='__main__':sys.exit(main())

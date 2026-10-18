#!/usr/bin/env python3
"""Run actual X2 CPU normal-print probe; no trace program or GPU cycles."""
from common import *
import importlib.util
import re
import xml.etree.ElementTree as ET


def main():
    assert (BUILD/'combined-preview/libcudart.so').is_file()
    # Current AG source may still be uncommitted until all CPU gates pass.
    build=BUILD/'combined-preview'
    probe=build/'dtc_l1_normal_export_probe'
    library=build/'libcudart.so'
    config=PACK/'inputs/AA5/inputs/CPU_EXPORT_FIXTURE_BASE.config'
    parser_file=PACK/'inputs/AA5/inputs/X2/scripts/parse_normal_export.py'
    spec=importlib.util.spec_from_file_location('x2_parser',parser_file)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    dest=RAW/'cpu-qualification'/'combined-preview-normal'
    dest.mkdir(parents=True,exist_ok=False)
    cases=[];outputs={}
    for flag,scenario,topology in [('omitted','events','1'),('0','events','1'),
        ('1','no_event','1'),('1','events','1'),('1','events','8')]:
        label='_'.join([flag,scenario,topology]);work=dest/label;work.mkdir()
        env=dict(os.environ);env.pop('LD_PRELOAD',None)
        env['LD_LIBRARY_PATH']=str(build);env['CUDA_VISIBLE_DEVICES']=''
        argv=[str(probe),str(config),flag,scenario,topology]
        r=subprocess.run(argv,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
        (work/'stdout').write_bytes(r.stdout);(work/'stderr').write_bytes(r.stderr)
        assert r.returncode==0,(label,r.stderr[-2000:])
        text=r.stdout.decode()
        assert 'kernels=0 gpu_cycle_calls=0 simulation_threads_started=0 print_state_unchanged=1' in text
        assert re.findall(r'^X2_CPU_LOADED_LIBRARY path=(.*)$',text,re.M)==[str(library.resolve())]
        parsed=mod.parse_normal_export(text,k1=flag=='1')
        if flag=='1':
            assert parsed['snapshots']==3 and parsed['cycle']==22 and len(parsed['rows'])==64
            if scenario=='events':
                row=parsed['rows'][0]
                assert row['requests']==4 and row['ordinary_commits']==2
                assert row['changed']==2 and row['retained_at_event']==row['reclaimed_at_event']==1
            else:assert all(r['requests']==r['ordinary_commits']==0 for r in parsed['rows'])
        else:assert not parsed['available'] and 'rows' not in parsed
        outputs[label]=text
        cases.append(dict(label=label,argv=argv,returncode=0,stdout_sha256=sha(work/'stdout'),
            stderr_sha256=sha(work/'stderr'),K1_export_available=parsed['available']))
    # Omitted-vs-zero config echo differs; compare only actual public boundaries.
    def frames(text):
        return re.findall(r'X2_CPU_NORMAL_BOUNDARY_BEGIN[^\n]*\n(.*?)X2_CPU_NORMAL_BOUNDARY_END',text,re.S)
    assert frames(outputs['omitted_events_1'])==frames(outputs['0_events_1'])
    result=dict(status='PASS_AG_PREVIEW_REAL_X2_NORMAL_PRINT_CPU',core_base=X2,qualification_source='UNCOMMITTED_EXACT_AE_DELTA_PLUS_CMAKE_CPU_TESTS',framework=FRAMEWORK_BUILD,
        probe=dict(path=str(probe),sha256=sha(probe)),library=dict(path=str(library),sha256=sha(library)),
        config_sha256=sha(config),parser_sha256=sha(parser_file),cases=cases,
        actual_entrypoint='compiled gpgpu_sim::gpu_print_stat(0)',original_X2_metadata_expected=True,
        original_or_canary_simulations_started=0,GPU_cycle_calls=0,simulation_threads_started=0,
        AG_combined_core_qualification=True)
    write(PACK/'COMBINED_PREVIEW_NORMAL_EXPORT_CPU.json',result)
    junit=BUILD/'combined-preview-ctest.xml'
    tests=ET.parse(junit).findall('.//testcase')
    assert len(tests)==14 and not any(t.find('failure') is not None for t in tests)
    write(PACK/'COMBINED_PREVIEW_14_CTEST.json',dict(status='PASS_14_OF_14_INCLUDING_7_ORIGINAL_X2',core_base=X2,qualification_source='UNCOMMITTED_EXACT_AE_DELTA_PLUS_CMAKE_CPU_TESTS',
        tests=[t.attrib['name'] for t in tests],junit_sha256=sha(junit),log_sha256=sha(BUILD/'combined-preview-ctest.log'),
        test_sources_modified=False,simulation_attempts=0))
    print(json.dumps(dict(status=result['status'],normal_CPU_cases=len(cases),original_CTests=7,total_CTests=14,simulation_attempts=0)))


if __name__=='__main__':main()

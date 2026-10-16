#!/usr/bin/env python3
"""Preregister the five authorized same-input arms before any new performance."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
from collect_service_closure_attempts import sha
from collect_service_closure_matched import effective_options


def save(p,value):
    with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--admission',required=True); ap.add_argument('--output-dir',required=True)
    a=ap.parse_args(); admission=Path(a.admission).resolve(); gate=json.loads(admission.read_text())
    assert gate['status']=='DERIVED_INPUT_ADMITTED_FOR_SOURCE_PROFILE_SCOPE' and all(gate['checks'].values())
    out=Path(a.output_dir).resolve(); out.mkdir(exist_ok=False)
    fw=Path(__file__).resolve().parents[2]; evidence=fw/'docs/dtc_l1/iscas2027/service_closure_174_v1'
    raw=Path('/workspace/dtc-service-closure-174-v1')
    original_plan=list(csv.DictReader((evidence/'review_pack/r2/REGISTERED_ROWS_V2.tsv').open(),delimiter='\t'))
    root=out/'attempts'; root.mkdir()
    cfg=out/'config'; cfg.mkdir(); specs=out/'specs'; specs.mkdir()
    frozen=out/'execution_sources'; frozen.mkdir()
    for name in ['service_closure_attempt.py','run_hotspot_derived_174.py','collect_hotspot_derived_174.py',
                 'collect_service_closure_attempts.py','collect_service_closure_matched.py','service_closure_scientific_disposition.py']:
        shutil.copy2(Path(__file__).with_name(name),frozen/name); (frozen/name).chmod(0o444)
    # Fixed existing174 nonbinding global budget, common to all new arms.
    (cfg/'COMMON_LOWER_CAP.config').write_text('-gpgpu_dtc_l1_lower_outstanding_cap 32768\n'); (cfg/'COMMON_LOWER_CAP.config').chmod(0o444)
    sg1=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-sg1-wholeline/docs/dtc_l1/iscas2027/granularity/sg1/config')
    for name in ['SG1_B16_N_OVERLAY.config','SG1_TC80_N_OVERLAY.config']:
        shutil.copy2(sg1/name,cfg/name); (cfg/name).chmod(0o444)
    tracecfg=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config')
    head=subprocess.check_output(['git','-C',str(fw),'rev-parse','HEAD'],text=True).strip()
    result=[]; arms={}; owned=Path(gate['owned_input_directory'])
    for arm in gate['new_arms_fixed_before_performance']:
        finite=arm in ('IO256','OO128'); short='IO' if arm=='IO256' else 'OO' if arm=='OO128' else 'TRAD96'
        template_row=next(r for r in original_plan if r['workload']=='Hotspot1' and r['arm']==short)
        assert sha(Path(template_row['spec_path']))==template_row['spec_sha256']
        template=json.loads(Path(template_row['spec_path']).read_text())
        base=fw/'configs/dtc_l1/fast64'/('FAST64_'+short+'.config' if finite else 'FAST64_BASE.config')
        overlay=evidence/'config/FINITE_PRIMARY_COMMON.config' if finite else evidence/'config/TRAD96_P256_M512.config' if arm=='TRAD96' else cfg/('SG1_B16_N_OVERLAY.config' if arm=='B16-N' else 'SG1_TC80_N_OVERLAY.config')
        paths=[base,overlay,cfg/'COMMON_LOWER_CAP.config',tracecfg]
        spec=dict(label='HS_SOURCE_PROFILE_V2_'+arm.replace('-','_'),workload='Hotspot_SOURCE_PROFILE_V2',arm=arm,phase='DERIVED_QUALIFIED_PRIMARY',
            classification='SOURCE_PROFILE_DERIVED_INPUT_SIMULATION_NOT_HISTORICAL_NATIVE_FIDELITY',
            core=template['core'],build_framework=template['build_framework'],orchestrator_framework=head,
            runtime=template['runtime'],runtime_sha256=template['runtime_sha256'],finite_service=finite,
            dtc_mode=short.lower() if finite else 'base',expected_mode=2 if arm=='IO256' else 3 if arm=='OO128' else 1,
            input_bundle_sha256=gate['bundle_sha256'],input_interpretation=gate['input_interpretation'],
            admission_receipt=str(admission),admission_receipt_sha256=sha(admission),
            trace_list=str(owned/'kernelslist.g'),trace_list_sha256=sha(owned/'kernelslist.g'),expected_instructions=377291004,
            expected_kernel_names=['_Z14calculate_tempiPfS_S_iiiiffffff'],
            members=[dict(path=str(owned/'kernel-1.traceg'),sha256=sha(owned/'kernel-1.traceg'),bytes=(owned/'kernel-1.traceg').stat().st_size)],
            configs=[dict(path=str(p),sha256=sha(p)) for p in paths])
        assert sha(Path(spec['runtime']))==spec['runtime_sha256']
        if finite:spec['expected_active_pib']=256 if arm=='IO256' else 128
        else:
            ways=24 if arm=='TRAD96' else 20 if arm=='TC80-N' else 4
            spec.update(expected_dl1=f'N:32:128:{ways},L:T:m:L:L,A:512:8,16:0,32',expected_mshr=512 if arm=='TRAD96' else 32,expected_pib=256 if arm=='TRAD96' else 8)
        path=specs/(spec['label']+'.json');save(path,spec);path.chmod(0o444);arms[arm]=spec
        result.append(dict(label=spec['label'],arm=arm,workload=spec['workload'],input_bundle_sha256=gate['bundle_sha256'],spec_path=str(path),spec_sha256=sha(path),gate='INDEPENDENT_DERIVED_R0_PASS_AND_EXISTING_R1_FIXED_SERVICE',action='PREREGISTERED_BEFORE_ANY_DERIVED_PERFORMANCE'))
    options={arm:effective_options(spec) for arm,spec in arms.items()}
    union=set().union(*(set(v) for v in options.values()))
    differences={k:{arm:v.get(k) for arm,v in options.items()} for k in union if len({json.dumps(v.get(k)) for v in options.values()})>1}
    allowed=lambda k:k.startswith('-gpgpu_dtc_l1_') or k.startswith('-gpgpu_cache:dl1') or k=='-gpgpu_unified_l1d_size'
    assert all(allowed(k) for k in differences),differences
    for opt,value in {'-gpgpu_n_clusters':['64'],'-gpgpu_n_cores_per_cluster':['1'],'-gpgpu_clock_domains':['1410.0:1410.0:1410.0:850.0'],'-network_mode':['2'],'-gpgpu_dtc_l1_lower_outstanding_cap':['32768'],'-gpgpu_shmem_num_banks':['32'],'-gpgpu_shmem_warp_parts':['1'],'-gpgpu_adaptive_cache_config':['0'],'-gpgpu_l1_cache_write_ratio':['0']}.items():
        assert all(v.get(opt)==value for v in options.values()),(opt,value)
    assert all(len({json.dumps(s[k],sort_keys=True) for s in arms.values()})==1 for k in ['members','trace_list','trace_list_sha256','expected_instructions','expected_kernel_names','input_bundle_sha256'])
    with (out/'REGISTERED_DERIVED_ROWS.tsv').open('x') as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(result)
    save(out/'PAIRING_CONTRACT.json',dict(utc=datetime.now(timezone.utc).isoformat(),status='PREREGISTERED_COMMON_INPUT_PLATFORM_ROI_CYCLE_AND_STATISTICS',
        plan_sha256=sha(out/'REGISTERED_DERIVED_ROWS.tsv'),admission_sha256=sha(admission),effective_options=options,declared_design_differences=differences,
        runtime_cores={arm:dict(core=s['core'],binary_sha256=s['runtime_sha256'],build_framework=s['build_framework']) for arm,s in arms.items()},
        common_budget='Global lower cap32768 follows existing174 primary contract, now explicit on new conventional arms; these are new attempts, not reuse of old8192-cap baselines.',
        design_scope='Different conventional and finite DTC cores/binaries are declared legal implementations. Core delta is finite-service opt-in; common parser/buildFramework, 64SM, clocks, shared-bank paths, original control/width/output order, and unchanged ISA. No equal total area/metadata/native equivalence claim.',
        execution_sources={p.name:sha(p) for p in frozen.iterdir()},baseline_service='Conventional cache/PIB/MSHR service unchanged. Finite IO/OO uses already qualified fixed174 service, not an artificial conventional20cycle match.',
        necessity='B16-N/IO256/OO128 main comparison plus paper capacity TC80-N and strengthened TRAD96. No IO128/WAIT128 or modern arm.',
        input_scope='SOURCE_PROFILE_RECONSTRUCTION_V2_ONLY; original Hotspot lineage/44-row plan/three holds unchanged; no mixed-input ratios or GM12.'))
    print(json.dumps(dict(plan=str(out/'REGISTERED_DERIVED_ROWS.tsv'),rows=len(result),common_platform=True,design_differences=sorted(differences))))


if __name__=='__main__':main()

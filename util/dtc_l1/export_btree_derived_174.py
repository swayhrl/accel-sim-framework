#!/usr/bin/env python3
"""Immutable checkpoint for the new namespace; never mixes original input rows."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from collect_btree_derived_174 import review, BUNDLE
from collect_service_closure_attempts import collect, sha
from collect_service_closure_matched import effective_options,contract_checks


def table(p,rows):
    with p.open('x') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)


def export_matched128(completed,out):
    io,oo=completed['IO128'],completed['OO128']
    runs=[Path(r['run_dir']) for r in [io,oo]]
    specs=[json.loads((p/'SPEC.json').read_text()) for p in runs]
    checks=contract_checks(*specs,*(effective_options(s,p) for s,p in zip(specs,runs)))
    services=[json.loads(r['service_metrics']) for r in [io,oo]]
    for field in ['retired','collected_sectors']:
        checks['same_'+field]=services[0]['DTC_SERVICE_V1_'+field]==services[1]['DTC_SERVICE_V1_'+field]>0
    assert all(checks.values()),checks
    rows=[]
    for arm,r,v in zip(['IO128','OO128'],[io,oo],services):
        get=lambda key:v['DTC_SERVICE_V1_'+key]
        assert get('samples')==64*int(r['cycles'])
        rows.append(dict(arm=arm,attempt_uuid=r['attempt_uuid'],cycles=r['cycles'],input_bundle_sha256=BUNDLE,
            active_pib_entries=128,physical_lines=640,retired=get('retired'),retirement_unit='CACHEABLE_WARP_INSTRUCTION',
            mean_ready_to_complete=get('fully_ready_to_complete_sum')/get('retired'),
            mean_ready_to_collect=get('ready_to_collect_sum')/get('retired'),mean_collection=get('collection_cycles')/get('retired'),
            mean_post_collection_wb_wait=get('wb_wait')/get('retired'),
            mean_map_loss_to_free=get('map_loss_to_free_sum')/get('map_loss_to_free_count') if get('map_loss_to_free_count') else 'NA_NO_EVENTS',
            mean_pib_entries_per_sm=get('pib_integral')/get('samples'),mean_physical_lines_per_sm=get('physical_integral')/get('samples'),
            collected_32b_sectors=get('collected_sectors'),all_sm_core_cycle_samples=get('samples'),
            scope='CONDITIONAL_E_LIST_SAME128_DEPTH_NOT_EQUAL_TOTAL_METADATA_AREA_OR_NATIVE'))
    table(out/'MATCHED128_METRICS.tsv',rows)
    with (out/'MATCHED128_AUDIT.json').open('x') as f:
        json.dump(dict(checks=checks,input_bundle_sha256=BUNDLE,io128_cycles_over_oo128_cycles=int(io['cycles'])/int(oo['cycles']),scope='SAME_NEW_INPUT_ONLY_NO_CROSS_INPUT_DENOMINATORS'),f,indent=2);f.write('\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--registration',required=True);ap.add_argument('--output-dir',required=True)
    a=ap.parse_args(); reg=Path(a.registration);root=reg/'attempts';out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=False)
    contract=json.loads((reg/'PAIRING_CONTRACT.json').read_text());plan=reg/'REGISTERED_DERIVED_ROWS.tsv'
    assert sha(plan)==contract['plan_sha256'];rows=list(csv.DictReader(plan.open(),delimiter='\t'))
    starts={}; state=[]; sealed=[];reviews=[]; completed={}
    for p in root.glob('*/RUN_START.json'):
        s=json.loads(p.read_text()); label=s['spec']['label'];assert label not in starts; starts[label]=p
    for row in rows:
        assert sha(Path(row['spec_path']))==row['spec_sha256'];spec=json.loads(Path(row['spec_path']).read_text());p=starts.get(row['label'])
        assert spec['input_bundle_sha256']==BUNDLE
        if p:
            assert json.loads(p.read_text())['spec']==spec
            result=collect(p.parent)
            strict=p.parent/'DERIVED_STRICT_VALIDATION_V1.json'
            if (p.parent/'RUN_TERMINAL.json').exists():
                # The frozen per-attempt collector is authoritative. New exports
                # verify source identity and recollect rather than invent a PASS.
                if strict.exists():
                    receipt=json.loads(strict.read_text()); actual=review(p.parent)
                    assert receipt['collector_sha256']==contract['execution_sources']['collect_btree_derived_174.py']
                    assert receipt==actual
                    reviews.append(receipt);result=receipt['terminal_review']
                    shutil.copy2(strict,out/(result['attempt_uuid']+'.strict.json'))
                    if result['status']=='PASS_CHECKED_SCOPE':completed[row['arm']]=result
                else:result['status']='TERMINAL_AWAITING_STRICT_RECEIPT'
            state.append(dict(arm=row['arm'],label=row['label'],input_bundle_sha256=BUNDLE,
                attempt_uuid=result['attempt_uuid'],status=result['status'],cycles=result['cycles'],instructions=result['instructions'],
                scientific_promotion='CONDITIONAL_E_LIST_DERIVED_INPUT_ONLY_NOT_CAPTURE_OR_NATIVE_EQUIVALENCE',
                spec_sha256=row['spec_sha256'],core=spec['core'],binary_sha256=spec['runtime_sha256'],
                terminal_sha256=result['terminal_sha256'],stdout_sha256=result['stdout_sha256'],raw_dir=str(p.parent),
                scientific_checks=result['scientific_checks'],service_metrics=result['service_metrics']))
            files=['RUN_START.json','SPEC.json','PID.json','immutable_runner.py']
            if (p.parent/'RUN_TERMINAL.json').exists():files+=['RUN_TERMINAL.json','resource.time','simulator.stdout','simulator.stderr']
            for name in files:
                f=p.parent/name
                if f.exists():sealed.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f)))
        else:raise ValueError('Expected registered row was not started: '+row['label'])
    assert set(starts)=={r['label'] for r in rows}
    pairs=[]
    for arm in ['IO256','OO128']:
        for baseline in ['B16-N','TC80-N','TRAD96']:
            if len(completed)==6 and arm in completed and baseline in completed:
                x,y=completed[arm],completed[baseline]
                assert x['instructions']==y['instructions']=='444467849'
                pairs.append(dict(input_bundle_sha256=BUNDLE,arm=arm,baseline=baseline,numerator_attempt=y['attempt_uuid'],denominator_attempt=x['attempt_uuid'],
                    baseline_cycles=y['cycles'],design_cycles=x['cycles'],baseline_over_design=float(y['cycles'])/float(x['cycles']),
                    scope='ONE_CONDITIONAL_E_LIST_DERIVED_INPUT_ONLY_NO_CAPTURE_OR_NATIVE_EQUIVALENCE_OR_AGGREGATE'))
    table(out/'DERIVED_ROWS_STATE.tsv',state);table(out/'RAW_RECEIPT_HASHES.tsv',sealed)
    if pairs:table(out/'SAME_DERIVED_INPUT_PAIRS.tsv',pairs)
    if len(completed)==6:
        export_matched128(completed,out)
    shutil.copy2(plan,out/plan.name);shutil.copy2(reg/'PAIRING_CONTRACT.json',out/'PAIRING_CONTRACT.json')
    summary=dict(utc=datetime.now(timezone.utc).isoformat(),input_bundle_sha256=BUNDLE,
        statuses={s:sum(r['status']==s for r in state) for s in sorted({r['status'] for r in state})},
        current_original_plan='UNCHANGED_SEPARATE44_ROWS',old_hotspot='PROMOTION_HOLD_AND_THREE_OLD_ROWS_FORBIDDEN',
        means='NONE',source_scope='CONDITIONAL_E_LIST_FAMILY_NOT_CAPTURE_ELF_OR_NATIVE_EQUIVALENCE',
        collector_source_sha256=sha(Path(__file__)),complete=len(completed)==6)
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    table(out/'FILES_SHA256.tsv',[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir()) if p.is_file()])
    print(json.dumps(summary))


if __name__=='__main__': main()

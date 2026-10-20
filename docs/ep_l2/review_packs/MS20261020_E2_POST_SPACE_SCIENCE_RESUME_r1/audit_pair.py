"""Independently recheck accepted native receipts and deliver exact counters to D."""
from pathlib import Path
import sys, json, time
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[3]/'util/ep_l2/mechanism_e'))
import coordinator as c, runner

def audit(workload):
    coord=c.Coordinator();s=coord.snapshot();pairid='V2_MAIN_'+workload+'_S_F_MAIN61'
    pair=s['accepted_pairs'][pairid];assert pair['status']=='CURRENT_ACCEPTED'
    existing=c.HANDOFF/'inbox'/('E2_TO_D_INCREMENTAL_'+pairid+'.json')
    published=json.loads(existing.read_text());assert published['accepted_pair']==pair
    checks={}
    for side,e in pair['endpoints'].items():
        assert c.digest(e['path'])==e['sha256']
        r=json.loads(Path(e['path']).read_text());n=r['native_exit_evidence']
        assert c.digest(Path(e['path']).parent/'NATIVE_EXIT.json')==r['native_exit_receipt_sha256']
        assert json.loads((Path(e['path']).parent/'NATIVE_EXIT.json').read_text())==n
        assert n['native_process']==r['process']
        assert n['exit_code']==0 and n['wait_status']==0 and n['stop_reason'] is None and n['exited_normally']
        selection=s['input_selections'][r['selection_id']]
        assert c.digest(selection['path'])==selection['sha256']
        expected=selection['selection']['full_input_identity']['expected_full_instructions']
        assert r['summary']['instructions']==expected and r['summary']['slices']==64
        assert runner.validate_summary(r['summary'],r['identity'])['status']=='PASS'
        assert r['complete_input_verified'] and r['independent_acceptance']=='PASS' and r['status']=='COMPLETE_VALID'
        assert r['source_identity']==s['final_source_identity']
        coord.require_no_hold(s,r['qualification_id'])
        checks[side]=dict(attempt=e['attempt_id'],exit_code=0,wait_status=0,native_process=n['native_process'],
                          cycles=r['summary']['cycles'],instructions=expected,slices=64,validation=r['validation'],
                          source_identity=r['source_identity'],input_identity=r['identity'],
                          mechanism_metrics=r['mechanism_metrics'],raw_sha256=r['raw_log_sha256'],
                          result_directory=str(Path(e['path']).parent),receipt_path=e['path'],receipt_sha256=e['sha256'])
    report=dict(status='PASS',at_unix=time.time(),pair=pair,endpoint_checks=checks)
    c.write_json(P/(workload+'_POST_PAIR_INDEPENDENT_AUDIT.json'),report)
    notice=dict(schema='E2_TO_D_ACCEPTED_PAIR_NATIVE_AND_MECHANISM_DETAIL_V1',at_unix=time.time(),pair_id=pairid,
                status='CURRENT_ACCEPTED',source_identity=s['final_source_identity'],accepted_pair=pair,
                endpoint_native_closure_and_mechanism_metrics=checks,remote_publication=published['remote_publication'],
                source_cumulative_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],
                analysis_request='Analyze this accepted pair incrementally now, including neutral/regressive results. Preserve denominator and interpretation limits; overlapping waits are not additive stall cycles.')
    c.write_json(P/(workload+'_D_MECHANISM_DETAIL_NOTICE.json'),notice)
    for folder in ['inbox','events']:
        dest=c.HANDOFF/folder/('E2_TO_D_'+workload+'_POST_SPACE_ACCEPTED_MECHANISM_DETAIL.json')
        assert not dest.exists(),'never overwrite a prior delivered scientific notice'
        c.write_json(dest,notice)
    print(json.dumps(dict(workload=workload,status='PASS',cycles_S=pair['cycles_left'],cycles_F=pair['cycles_right'],
                         ratio_S_F=pair['ratio_left_over_right'],instructions=[v['instructions'] for v in checks.values()],
                         remote_publication=published['remote_publication'],actual_starts=s['actual_starts'],
                         remaining=s['remaining_start_capacity'],usage=c.output_usage())),flush=True)
    return report

if __name__=='__main__':audit(sys.argv[1])

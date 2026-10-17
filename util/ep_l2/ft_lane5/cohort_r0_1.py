"""Aggregate only five currently accepted same-release full-application pairs."""
import argparse
import json
import math
from pathlib import Path

from acceptance import load_current_authority,current_manifest,require_current_result
from campaign_r0 import csv_write
from package_r0 import freeze_checksums
from run import digest,require

REPO=Path(__file__).resolve().parents[3]
ORDER=('sad','vectorAdd_4M','cfd_097k','convolutionSeparable','FWT_7_21')


def collect(state):
    manifest=current_manifest(state);accepted=[r for r in manifest['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED']
    require(len(accepted)==10 and {r['workload'] for r in accepted}==set(ORDER),'Incomplete current five-pair cohort; geomean forbidden')
    rows=[];sources=[];all_runs=[]
    require(len({(r['core_source_commit'],r['framework_source_commit'],r['binary_sha256']) for r in accepted})==1,'Mixed producing releases')
    for workload in ORDER:
        arms=[r for r in accepted if r['workload']==workload]
        require(len(arms)==2 and {r['mode'] for r in arms}=={'B16_BANKED','U_WB16'},'Missing/duplicate mode')
        b=next(r for r in arms if r['mode']=='B16_BANKED');u=next(r for r in arms if r['mode']=='U_WB16')
        for key in ('core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','instructions'):
            require(b[key]==u[key],'Pair dimension mismatch '+key)
        for key in ('epoch_range','termination_contract','ideal_vector'):
            require(b['identity'][key]==u['identity'][key],'Pair contract mismatch '+key)
        require(b['identity']['epoch_range']=={'scope':'full_application','epochs':'all'} and not any(b['identity']['ideal_vector'].values()),'Non-primary cohort input')
        bf=dict(b['identity']['feature_vector']);uf=dict(u['identity']['feature_vector']);require(bf.pop('unified_wb') is False and uf.pop('unified_wb') is True and bf==uf,'Different paired geometry/features')
        require(bf['wbuf_entries']==16 and bf['payload_capacity_per_slice']==1168 and bf['bank_count']==4 and bf['ops_per_bank_cycle']==1 and not any(bf[k] for k in ('ro','tvd','adaptive_policy')),'Unqualified primary feature')
        for r in (b,u):
            require_current_result(r['identity'],r['raw_log_sha256'],r['observed_cycles'],r['instructions'],state)
            directory=Path('/workspace/results/ep_l2_ft20261016')/r['run_key'];require(digest(directory/'raw.log')==r['raw_log_sha256'],'Raw changed after acceptance')
            proof=r['independent_review'];require(digest(REPO/proof['path'])==proof['sha256'],'Independent review changed');pack=(REPO/proof['path']).parent
            for line in (pack/'SHA256SUMS').read_text().splitlines():
                sha,name=line.split('  ',1);require(digest(pack/name)==sha,'Frozen pair artifact changed')
            all_runs.append({'workload':workload,'mode':r['mode'],'status':'CURRENT_ACCEPTED','run_key':r['run_key'],**{k:r[k] for k in ('core_source_commit','framework_source_commit','binary_sha256','runtime_config_sha256','trace_content_sha256','raw_log_sha256','instructions')},'cycles':r['observed_cycles']})
        rows.append({'workload':workload,'B16_cycles':b['observed_cycles'],'U_WB16_cycles':u['observed_cycles'],'speedup_B16_over_U_WB16':b['observed_cycles']/u['observed_cycles'],'cycle_reduction_percent':100*(1-u['observed_cycles']/b['observed_cycles']),'B16_run_key':b['run_key'],'U_WB16_run_key':u['run_key']});sources.append({'workload':workload,'rows':[b,u]})
    return rows,sources,all_runs


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists(),'Frozen cohort exists')
    state=load_current_authority();rows,sources,runs=collect(state) # No output before full5/current acceptance.
    a.out.mkdir(parents=True);csv_write(a.out/'PAIRED_RESULTS.csv',rows);csv_write(a.out/'BASELINE_RESULTS.csv',[r for r in runs if r['mode']=='B16_BANKED']);csv_write(a.out/'MECHANISM_RESULTS.csv',[r for r in runs if r['mode']=='U_WB16'])
    summary={'status':'ALL5_CURRENT_ACCEPTED_SAME_RELEASE','workloads':list(ORDER),'pairs':5,'runs':10,'geometric_mean_speedup_B16_over_U_WB16':math.exp(sum(math.log(r['speedup_B16_over_U_WB16']) for r in rows)/5),'improved':sum(r['U_WB16_cycles']<r['B16_cycles'] for r in rows),'ties':sum(r['U_WB16_cycles']==r['B16_cycles'] for r in rows),'regressed':sum(r['U_WB16_cycles']>r['B16_cycles'] for r in rows),'current_authority':state['binding'],'scope':'Declared five development workloads only; same official repaired producing binary; full applications and ordinary symbolic32B sector/lifecycle qualification, no numeric SASS output; TVD/RO/Ideal excluded; no C1 headroom capacity-attribution claim'}
    (a.out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');(a.out/'SOURCE_MANIFEST.json').write_text(json.dumps({'pairs':sources},indent=2,sort_keys=True)+'\n');(a.out/'README.md').write_text('# Repaired R0.1 five-pair cohort\n\nAll five predeclared full-application pairs are currently scientifically accepted on the same producing release. Geomean is computed only after all10 accepted rows and every frozen raw/review hash verify. Negative control, ties and regressions are retained. Consumers must fetch current V2 to detect later withdrawal.\n\nData correctness is independently qualified symbolic sector versions/request/hardware lifecycle, not numerical SASS payload output. TVD/RO/Ideal are separate. Copy/borrowing/bank event changes alone do not prove a capacity cause; untrusted C1 legacy headroom is excluded.\n');freeze_checksums(a.out);print(json.dumps(summary))


if __name__=='__main__':main()

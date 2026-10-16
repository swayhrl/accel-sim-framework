#!/usr/bin/python3
"""Audit only the new Lane6 V2 bridge against live published old-run withdrawal."""
import argparse
import json
from pathlib import Path
import subprocess
import current_pair_intake as consumer


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--framework-repo',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();repo=args.framework_repo.resolve();assert not args.output.exists()
    state=consumer.fetch_state(repo);context=consumer.bridge(repo,state);observations=[]
    for row in state['manifest']['rows']:
        if row['original_terminal_status']!='COMPLETE_VALID':continue
        run={'identity':row['identity'],'workload':row['workload'],'mode':row['mode'],'run_key':row['run_key'],'status':row['original_terminal_status'],'raw_log_sha256':row['raw_log_sha256'],'summary':{'cycles':row['observed_cycles'],'instructions':row['instructions']}}
        try:context.check_run(run)
        except ValueError as error:
            consumer.require('qualification withdrawn' in str(error) or 'suspended' in str(error),'Unexpected denial reason')
            observations.append({'run_key':row['run_key'],'identity':row['identity'],'raw_log_sha256':row['raw_log_sha256'],'consumer_status':'REJECTED_BY_CURRENT_V2','reason':str(error)})
        else:raise ValueError('Old withdrawn record unexpectedly accepted')
    consumer.require(len(observations)==6,'This revision audits the six retained old records only; newer valid results require a new intake revision')
    legacy=json.loads((consumer.R3/'REJECTED_OLD_SAD_ADAPTER.json').read_text())
    try:consumer.consume(repo,legacy,state)
    except ValueError as error:consumer.require('qualification withdrawn' in str(error) or 'suspended' in str(error),'Native path denied for unrelated reason')
    else:raise ValueError('Old native sad pair unexpectedly accepted')
    context.assert_fresh()
    result={'status':'PASS_V2_BRIDGE','authority':state['binding'],'schema':state['manifest']['schema_version'],'supersession_evidence':state['manifest']['supersession_evidence'],
        'actual_withdrawn_rows_rejected':observations,'original_native_sad_intake':'REJECTED_BY_CURRENT_V2_BEFORE_SUMMARY','accepted_pairs':0,'geomean':None,'formal_performance_figures':[],
        'scope':'New consumer integration only. No Lane5 original62 tests/runner inspections, Lane6 old30 tests, raw-body audit or simulator rerun.',
        'published_manifest_generation':state['manifest']['generation'],'production_binary':None}
    with args.output.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'status':'PASS_V2_BRIDGE','authority':state['binding'],'rejected_runs':len(observations),'native_old_sad_denied':True,'accepted_pairs':0}))

if __name__=='__main__':main()

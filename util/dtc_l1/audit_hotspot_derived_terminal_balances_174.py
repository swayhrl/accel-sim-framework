#!/usr/bin/env python3
"""Additional terminal resource audit; preserve every original strict receipt."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from collect_service_closure_attempts import sha
from collect_hotspot_derived_174 import review, BUNDLE


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--registration',required=True);ap.add_argument('--output-dir',required=True)
    a=ap.parse_args();reg=Path(a.registration);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    plan=list(csv.DictReader((reg/'REGISTERED_DERIVED_ROWS.tsv').open(),delimiter='\t'));labels={r['label'] for r in plan}
    for start in (reg/'attempts').glob('*/RUN_START.json'):
        s=json.loads(start.read_text());run=start.parent;spec=s['spec']
        if not (run/'DERIVED_STRICT_VALIDATION_V1.json').exists():continue
        assert spec['label'] in labels and spec['input_bundle_sha256']==BUNDLE
        strict=json.loads((run/'DERIVED_STRICT_VALIDATION_V1.json').read_text());assert strict==review(run)
        text=(run/'simulator.stdout').read_text();m=dict(re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',text,re.M))
        n=lambda k:int(m.get('DTC_L1_'+k,'-1'))
        echoes=re.findall(r'^-gpgpu_dtc_l1_lower_outstanding_cap\s+(\d+)\s',text,re.M)
        checks=dict(strict_pass=strict['terminal_review']['status']=='PASS_CHECKED_SCOPE',lower_drained=n('lower_outstanding')==0,
                    configured_cap=bool(echoes) and echoes[-1]=='32768')
        if spec['finite_service']:
            mode=spec['dtc_mode']; acquired='lower_credit_acquired';released='lower_credit_released'
            checks.update(lower_created_issued_returned=n(mode+'_lower_created')==n(mode+'_lower_issued')==n(mode+'_lower_responses')>0,
                credits_match_created=n(acquired)==n(released)==n(mode+'_lower_created'),
                dependencies_closed=n(mode+'_completion_dependency_count')==n(mode+'_completion_dependency_closed')>0,
                inflight_drained=n(mode+'_inflight_current')==0,pib_drained=n(mode+'_pib_occupancy')==0)
            service=json.loads(strict['terminal_review']['service_metrics']);v=lambda k:service['DTC_SERVICE_V1_'+k]
            checks['all64_cycle_integral']=v('samples')==64*int(strict['terminal_review']['cycles'])
            checks['residence_components']=v('fully_ready_to_complete_sum')==v('ready_to_collect_sum')+v('collection_cycles')+v('wb_wait')
        else:
            acquired='lower_requests_acquired';released='lower_requests_released'
            checks.update(conventional_credit_balance=n(acquired)==n(released)>0,
                conventional_cap_statistic=n('lower_outstanding_cap')==32768,
                conventional_pib_balance=n('pib_admits')==n('pib_retires')>0,conventional_pib_drained=n('pib_occupancy')==0)
        assert all(checks.values()),(spec['label'],checks)
        receipt=dict(schema='DERIVED_TERMINAL_RESOURCE_BALANCES_V1',input_bundle_sha256=BUNDLE,label=spec['label'],arm=spec['arm'],
            attempt_uuid=s['attempt_uuid'],original_strict_sha256=sha(run/'DERIVED_STRICT_VALIDATION_V1.json'),
            stdout_sha256=sha(run/'simulator.stdout'),checks=checks,status='PASS_RESOURCE_BALANCES',
            acquired_counter='DTC_L1_'+acquired,released_counter='DTC_L1_'+released,acquired=n(acquired),released=n(released),
            lower_outstanding=n('lower_outstanding'),lower_cap_full_events=n('lower_cap_full_events'),
            source_sha256=sha(Path(__file__)),scope='ADDITIONAL_CHECKS_PRESERVE_ORIGINAL_TERMINAL_AND_STRICT_RECEIPTS')
        target=out/(s['attempt_uuid']+'.resource_balances.json')
        if target.exists():assert json.loads(target.read_text())==receipt
        else:
            with target.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
        print(json.dumps(dict(arm=spec['arm'],status=receipt['status'],acquired=n(acquired),released=n(released))),flush=True)


if __name__=='__main__':main()

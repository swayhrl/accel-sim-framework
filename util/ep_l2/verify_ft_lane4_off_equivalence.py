#!/usr/bin/env python3
"""Freeze a legacy all-OFF application equivalence check, never a B16 row."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from run_ft_lane4_diagnostic import parse_terminal

ROOT=Path(__file__).resolve().parents[2]
FAMILIES=('summary','slice','kernel','bank','l1','dram','window')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    statuses=[];audits=[];metrics=[];raw_index=[]
    parser=ROOT/'util/ep_l2/parse_epl2_b0.py'
    for label,root in [('control',a.control),('candidate',a.candidate)]:
        r=json.loads((root/'run_status.json').read_text());i=r['identity']
        assert r['status']=='COMPLETE_VALID' and r['mode']=='OFF'
        assert r['campaign_class']=='HISTORICAL_DIAGNOSTIC' and not i['feature_vector']['finite_wbuf']
        assert not any(i['ideal_vector'].values())
        assert sha(root/'raw.log')==r['raw_log_sha256'] and sha(root/'accel-sim.out')==i['binary_sha256']
        audit=json.loads((root/'input_audit.json').read_text());spec=json.loads((root/'input_spec.json').read_text())
        assert spec['identity']==i
        for cfg in audit['configs']:
            assert sha(root/cfg['name'])==cfg['sha256']
        metrics.append(parse_terminal(root/'raw.log',i['ideal_vector']))
        out=a.out/label
        command=[sys.executable,str(parser),str(root/'raw.log'),'--out',str(out),
                 '--framework-commit',i['framework_source_commit'],'--core-commit',i['core_source_commit'],
                 '--source-log',str(root/'raw.log')]
        subprocess.run(command,check=True,capture_output=True,text=True)
        write(a.out/(label+'_RUN_STATUS.json'),r)
        write(a.out/(label+'_INPUT_AUDIT.json'),audit)
        raw_index.append(dict(label=label,run_key=r['run_key'],path=str(root/'raw.log'),sha256=r['raw_log_sha256'],
                              run_status_sha256=sha(root/'run_status.json'),input_spec_sha256=sha(root/'input_spec.json')))
        statuses.append(r);audits.append(audit)
    assert audits[0]==audits[1], 'Scientific inputs changed'
    for field in ['runtime_config_sha256','trace_content_sha256','workload','epoch_range','feature_vector','ideal_vector','termination_contract']:
        assert statuses[0]['identity'][field]==statuses[1]['identity'][field], 'uncontrolled identity change: '+field
    for field in ['cycles','instructions']:assert metrics[0][field]==metrics[1][field], 'all-OFF regression: '+field
    checks=[]
    for family in FAMILIES:
        name='target_'+family+'.csv';old=sha(a.out/'control'/name);new=sha(a.out/'candidate'/name)
        assert old==new, 'CSV all-OFF regression: '+family
        checks.append(dict(family=family,control_sha256=old,candidate_sha256=new,status='BYTE_IDENTICAL'))
    write(a.out/'CSV_EQUALITY.json',checks)
    write(a.out/'RAW_LOG_INDEX.json',raw_index)
    report=dict(status='PASS',classification='LATEST_CANDIDATE_ALL_OFF_EQUIVALENCE_OLD_STATIC_NOT_B16',
                producing_tool_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
                parser_sha256=sha(parser),control_key=statuses[0]['run_key'],candidate_key=statuses[1]['run_key'],
                control_identity=statuses[0]['identity'],candidate_identity=statuses[1]['identity'],
                cycles=metrics[1]['cycles'],instructions=metrics[1]['instructions'],seven_csv_families='BYTE_IDENTICAL',
                same_scientific_inputs=True,scope='Only vectorAdd_4M full application in old static mode; not independent qualification of B16 or ideal-ON application modes')
    write(a.out/'OFF_EQUIVALENCE.json',report)
    (a.out/'README.md').write_text('''# Latest diagnostic binary all-OFF equivalence

This supplement adds one actual full-application vectorAdd_4M legacy all-OFF
control to FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2. Both source identities and
binary hashes are explicit. Scientific configs, trace, environment, vectors,
epoch and terminal contract match. Cycles/instructions and all seven parsed
CSV families are exact; raw logs and parser bytes are bound by SHA256.

The candidate includes Lane1 runtime-ready parent 126394be plus the Lane4
ideal changes, with all ideal bits OFF and finite-WBUF mode OFF. This verifies
legacy behavior on this application only. It is not a new B16 performance
baseline, an independent shared-release qualification, or numeric SASS output
validation. Formal diagnostic cells still require Lane1 common integration
and Lane5 same-binary release qualification/baseline specs.
''')
    (a.out/'SHA256SUMS').write_text(''.join(f'{sha(f)}  {f.relative_to(a.out)}\n' for f in sorted(a.out.rglob('*')) if f.is_file() and f.name!='SHA256SUMS'))
    print(json.dumps(report))


if __name__=='__main__':main()

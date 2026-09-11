#!/usr/bin/env python3
from __future__ import annotations
import csv,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];TOOL=ROOT/'util/dtc_l1/prepare_fast64_7_review_pack_v1.py'
with tempfile.TemporaryDirectory() as d:
 d=Path(d);ledger=d/'ledger.tsv'
 def emit(states):
  with ledger.open('w',encoding='utf-8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=('stage','current_state'),delimiter='\t');w.writeheader();w.writerows({'stage':f'FAST64.{n}','current_state':states[n]} for n in range(7))
 emit(['PASS']*7); ok=subprocess.run([str(TOOL),'--stage-ledger',str(ledger),'--output-dir',str(d/'out')],text=True,capture_output=True);assert ok.returncode==0,ok.stderr;assert (d/'out'/'tier_a_evidence_index.tsv').is_file()
 emit(['PASS']*6+['ACTIVE']);bad=subprocess.run([str(TOOL),'--stage-ledger',str(ledger),'--output-dir',str(d/'bad')],text=True,capture_output=True);assert bad.returncode!=0 and 'PRIOR_PASS_REQUIRED' in bad.stderr
print('FAST64_7_REVIEW_PACK_V1_REGRESSION_PASS')

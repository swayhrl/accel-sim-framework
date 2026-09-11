#!/usr/bin/env python3
"""Fail-closed FAST64.7 review-pack skeleton; no scientific synthesis."""
from __future__ import annotations
import argparse,csv,json,os,tempfile
from pathlib import Path
NEEDED=tuple(f"FAST64.{n}" for n in range(7))
FILES=("FAST12_summary.tsv","structural_pressure.tsv","live_misses.tsv","traffic_pressure.tsv","io_oo_mechanism.tsv","sensitivity_summaries.tsv","aggregate_membership.tsv","limitations_boundary.md","tier_a_evidence_index.tsv","tier_c_auxiliary_evidence_index.tsv","raw_log_result_manifest.tsv")
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage-ledger',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
 with a.stage_ledger.open(encoding='utf-8',newline='') as f: lines=f.readlines()
 header=next((n for n,line in enumerate(lines) if line.startswith('stage\tcurrent_state')),None)
 if header is None: raise RuntimeError('FAST64_7_LEDGER_SCHEMA_INVALID')
 rows=list(csv.DictReader(lines[header:],delimiter='\t'))
 states={r.get('stage'):r.get('current_state',r.get('status')) for r in rows}
 missing=[s for s in NEEDED if states.get(s)!='PASS']
 if missing: raise RuntimeError('FAST64_7_PRIOR_PASS_REQUIRED='+','.join(missing))
 if a.output_dir.exists(): raise RuntimeError('OUTPUT_ALREADY_EXISTS')
 tmp=Path(tempfile.mkdtemp(prefix='.fast64_7.',dir=a.output_dir.parent))
 try:
  (tmp/'REVIEW_PACK_STATUS.json').write_text(json.dumps({'status':'SKELETON_PENDING_ACCEPTED_INPUTS','prior_stages':NEEDED},indent=2)+'\n',encoding='utf-8')
  for name in FILES: (tmp/name).write_text('# populated only by accepted FAST64.7 synthesis\n',encoding='utf-8')
  os.replace(tmp,a.output_dir)
 except Exception:
  import shutil;shutil.rmtree(tmp,ignore_errors=True);raise
 print('FAST64_7_REVIEW_PACK_V1_PREPARED output='+str(a.output_dir))
if __name__=='__main__':main()

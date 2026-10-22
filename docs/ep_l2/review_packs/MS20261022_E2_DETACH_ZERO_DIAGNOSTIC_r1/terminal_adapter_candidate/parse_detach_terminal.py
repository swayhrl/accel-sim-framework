"""Candidate parser CLI run only by original runner after real native exit.

No embedded invented source/schema binding. Resolve only registered exact new Q,
then use its E sealed adapter binding. Root must review integration before use.
"""
import argparse
import json
from pathlib import Path
import detach_validation


def main():
 from coordinator import Coordinator, digest, require, tooling_binding, write_json
 tooling_binding()
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
 spec=json.loads(Path('input_spec.json').read_text());audit=json.loads(Path('input_audit.json').read_text())
 coord=Coordinator();item=coord.snapshot();coord.require_no_hold(item,spec['qualification_id'])
 row=item['qualifications'][spec['qualification_id']]
 require(digest(row['path'])==row['sha256']==spec['qualification_id'],'exact new Q changed')
 binding=row['qualification']['detach_observer_diagnostic']['validation_scope']
 detach_validation.configure_binding(binding)
 summary=detach_validation._ADAPTER.parse(args.raw,spec,row,audit)
 write_json(args.out,summary)

if __name__=='__main__':main()

"""Original four-argument runner CLI; newr5 scope route only, default unbound."""
import argparse,json
from pathlib import Path
import tagpressure_validation

def main():
 from coordinator import Coordinator,digest,require,tooling_binding,write_json
 import detach_diagnostic_policy
 tooling_binding();p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 spec=json.loads(Path('input_spec.json').read_text(),object_pairs_hook=tagpressure_validation.unique);audit=json.loads(Path('input_audit.json').read_text(),object_pairs_hook=tagpressure_validation.unique)
 require(spec.get('scientific_scope')==tagpressure_validation.SCI_SCOPE,'newr5 CLI cannot parse another scientific scope')
 coord=Coordinator();item=coord.snapshot();coord.require_no_hold(item,spec['qualification_id']);row=item['qualifications'][spec['qualification_id']]
 require(digest(row['path'])==row['sha256']==spec['qualification_id'],'exact newr5 Q changed')
 # Shared dispatcher must contain the separately reviewed newr5 branch. Original
 # r4 branch cannot satisfy this module's newsource binding/checks.
 detach_diagnostic_policy.prepare_validator(row,spec,digest)
 require(tagpressure_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,'newr5 scope not explicitly bound')
 write_json(a.out,tagpressure_validation._ADAPTER.parse(a.raw,spec,row,audit))
if __name__=='__main__':main()

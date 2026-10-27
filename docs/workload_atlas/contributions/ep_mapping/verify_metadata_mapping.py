"""Verify the saved independent EP/DTC mapping using metadata only."""
from pathlib import Path
import json, hashlib, collections
root=Path(__file__).resolve().parent
data=json.loads((root/'EP_FROZEN_INPUT_MAPPING.json').read_text())
counts=collections.Counter()
for x in data['inputs']:
    actual=[]
    for row in x['dtc_candidates']:
        members=sorted([dict(name=y['relative_path'],sha256=y['sha256'],bytes=y['size']) for y in row['source_members_sha256']], key=lambda y:y['name'])
        encoded=json.dumps(members,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
        digest=hashlib.sha256(encoded).hexdigest()
        assert digest==row['ep_formula_content_sha256']
        if digest==x['historical_identity']['trace_content_sha256']:
            actual.append(row['input_digest'])
            for q in x['independent_per_member_comparison_qualification_records']:
                old=q['input_scope_admission'].get('trace_content_manifest',[])
                if old: assert sorted(old,key=lambda y:y['name'])==members
    assert actual==x['matching_dtc_inputs']
    counts[x['classification']]+=1
assert len(data['inputs'])==8
assert sum(bool(x['matching_dtc_inputs']) for x in data['inputs'])==7
assert counts=={'SAME_REGISTERED_TRACE_SELECTED':3,'SAME_REGISTERED_TRACE_ALTERNATE':3,'SAME_REGISTERED_TRACE_UNRESOLVED':1,'DIFFERENT_DERIVED_TRACE':1}
print('PASS: 8 EP inputs; 7 exact registered member-set mappings; 3 selected, 3 alternate, 1 unresolved, 1 distinct derived')

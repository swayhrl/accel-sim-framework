#!/usr/bin/env python3
import csv,json
from pathlib import Path

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r81-legal-vocab-v1')
fixture=json.loads((WT/'util/vm_tlb/awma/r81_legal_vocab/fixture.json').read_text())
rows=[]

def matches(value,schema):
    kind=schema.get('type')
    if kind=='object':
        if not isinstance(value,dict):return False
        if not set(schema.get('required',[])).issubset(value):return False
        if schema.get('additionalProperties') is False and not set(value).issubset(schema.get('properties',{})):return False
        return all(matches(v,schema['properties'][k]) for k,v in value.items())
    if kind=='array':
        if not isinstance(value,list):return False
        if len(value)<schema.get('minItems',0) or len(value)>schema.get('maxItems',10**9):return False
        return all(matches(v,schema['items']) for v in value)
    if kind=='string':
        return isinstance(value,str) and (value in schema['enum'] if 'enum' in schema else True)
    if kind=='integer':return isinstance(value,int) and not isinstance(value,bool)
    if kind=='boolean':return isinstance(value,bool)
    raise ValueError(f'unexpected schema type {kind}')

for cohort,requests in fixture['cohorts'].items():
    results=json.loads((ROOT/'raw/reference'/cohort/'REQUEST_RESULTS.json').read_text())
    assert len(results)==len(requests)==4
    for fixed,result in zip(requests,results):
        assert fixed['id']==result['request_id']
        parsed=None
        try:parsed=json.loads(result['generated_text'])
        except json.JSONDecodeError:pass
        valid=parsed is not None and matches(parsed,fixed['schema'])
        rows.append({'cohort':cohort,'request_id':fixed['id'],
          'stop_reason':result['stop_reason'],'generated_tokens':result['generated_count'],
          'json_parseable':parsed is not None,'schema_valid':valid,
          'grammar_matcher_terminated':result['grammar_terminated'],
          'task_answer_accuracy':'NOT_EVALUATED'})
with (ROOT/'GRAMMAR_VALIDITY.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows)
print(json.dumps({'requests':len(rows),'schema_valid':sum(r['schema_valid'] for r in rows),
                  'truncated':sum(r['stop_reason']=='MAX_128_TRUNCATED' for r in rows)}))
if not all(r['schema_valid'] for r in rows):raise SystemExit(2)

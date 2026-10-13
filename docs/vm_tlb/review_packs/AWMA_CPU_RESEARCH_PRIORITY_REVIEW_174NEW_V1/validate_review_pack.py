#!/usr/bin/env python3
"""Check document/table integrity, not scientific performance."""
import csv, json
from pathlib import Path
P=Path(__file__).resolve().parent
required=['README.md','FINAL_RESEARCH_JUDGMENT.md','R27R3_FURTHER_DIAGNOSTIC_DECISION.md',
          'DYNAMIC_HANDOFF_EVIDENCE.md','PAPER_EXPERIMENT_GROUPS.tsv','CANDIDATE_MINIMAL_TESTS.md',
          'AI_ARCH_EXISTING_EVIDENCE_NOTE.md','SOURCE_REGISTER.tsv','OPEN_ISSUES.md',
          'NUMERIC_COORDINATE_RECHECK.json','MODEL_CONFIG_READ_RECEIPT.json','RAW_DATA_INDEX.tsv']
assert all((P/n).is_file() and (P/n).stat().st_size for n in required)
tables={}
for path in P.glob('*.tsv'):
    rows=list(csv.reader(path.open(encoding='utf-8'),delimiter='\t'))
    assert rows and len(set(rows[0]))==len(rows[0])
    assert all(len(r)==len(rows[0]) for r in rows), (path.name, len(rows[0]), [(i+1,len(r)) for i,r in enumerate(rows) if len(r)!=len(rows[0])])
    tables[path.name]={'columns':len(rows[0]),'data_rows':len(rows)-1}
groups=list(csv.DictReader((P/'PAPER_EXPERIMENT_GROUPS.tsv').open(encoding='utf-8'),delimiter='\t'))
assert len(groups)==6 and len({r['id'] for r in groups})==6
actual=[r for r in groups if r['material_evidence'].startswith('PAPER_AUTHOR')]
assert len(actual)==5 and len({r['source_title'] for r in actual})==3
assert any('backward' in r['phase_derivative'] for r in actual)
assert any('MeshGraphNets' in r['model_input'] for r in actual)
assert groups[-1]['verification']=='VERIFIED_CAPABILITY_NOT_COUNTED_AS_EXPERIMENT'
assert json.loads((P/'NUMERIC_COORDINATE_RECHECK.json').read_text())['status']=='PASS'
cfg=json.loads((P/'MODEL_CONFIG_READ_RECEIPT.json').read_text())
assert cfg['matches_accepted_config_sha'] and not cfg['read_tensor_storage']
out={'status':'PASS','tables':tables,'verified_actual_paper_groups':5,'distinct_primary_papers':3,
     'qualified_run_candidates':0,'checks':'Document/schema + published coordinate arithmetic; not new scientific execution.',
     'operations':{'GPU':0,'CUDA_JIT':0,'AccelSim':0,'model_runs':0,'performance_runs':0},
     'handoff_commit':'e32c47d4b54dac25bce94cc8020657e8932f3d26',
     'handoff_tree':'8a5eb49d7de8ff2e3ec78f2f7caaac110d5ba947',
     'coordination_readonly_commit':'4e5953c189792dd5a4ac5c13c33ba922b8c2a1e9'}
(P/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))

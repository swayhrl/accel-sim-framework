"""Attach full-input oracle evidence, never infer L2 blocking or mechanism effect."""
import csv
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[3]/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d'
UNKNOWN = 'UNKNOWN'
EXTRA = ['RO_input_evidence', 'RO_oracle_scope', 'RO_certified_lines',
         'RO_certified_read_lane_references', 'RO_native_blocked_request_intersection']

def enrich(rows, evidence):
    for row in rows:
        row.update({key: UNKNOWN for key in EXTRA})
        for item in evidence.get('inputs', []):
            if row['workload'] != item['workload'] or row.get('trace') not in item['matching_trace_hashes']:
                continue
            candidate = Path(item['candidate_path'])
            if hashlib.sha256(candidate.read_bytes()).hexdigest() != item['candidate_sha256']:
                raise ValueError('changed full-input oracle candidate')
            row.update(RO_input_evidence='FULL_EPOCH_MODEL_ORACLE_CANDIDATE_PENDING_C_E_REVIEW',
                       RO_oracle_scope=item['scope'], RO_certified_lines=item['certified_lines'],
                       RO_certified_read_lane_references=item['certified_read_lane_references'])
            # Read-lane references are not cache requests, hits or blocked UIDs.
            # Keep this UNKNOWN until actual qualified L2 measurements exist.
    return rows

def main():
    index=OUT/'RO_INPUT_EVIDENCE.json'
    if not index.exists(): return
    table=OUT/'OPPORTUNITY_TABLE.csv'
    rows=list(csv.DictReader(table.open()))
    enrich(rows,json.loads(index.read_text()))
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with table.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,restval=UNKNOWN)
        writer.writeheader();writer.writerows(rows)
    print('attached input-only RO evidence; native opportunity/trigger/cycles unchanged')

if __name__=='__main__': main()

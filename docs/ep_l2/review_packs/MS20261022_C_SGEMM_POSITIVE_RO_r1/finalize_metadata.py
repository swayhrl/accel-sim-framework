#!/usr/bin/env python3
"""Validate completed oracle artifacts; never opens a trace body."""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import datetime

HERE = Path(__file__).resolve().parent
RAW = Path('/workspace/ep_l2_ms20261019_e_results/C_SGEMM_RO_POSITIVE_20261022_r1')
EXPECTED = '1b0739908e3aef52cedea68962172ccac55f0c2d4c651623cb8fb0655475db06'
checks = []


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def verify(name, condition):
    if not condition: raise ValueError(name)
    checks.append(name)


def dump(name, body):
    (HERE/name).write_text(json.dumps(body,ensure_ascii=False,indent=2)+'\n')


run = json.loads((RAW/'RUN_RECEIPT.json').read_text())
verify('completed offline child', run['status']=='COMPLETE_OFFLINE_MODEL_PROOF_NOT_E_QUALIFIED')
m = json.loads((RAW/'oracle/manifest.json').read_text())
single = json.loads((RAW/'oracle/SINGLE_PASS_RECEIPT.json').read_text())
verify('one complete exact body read and combined actual SHA', single['body_opens']==1 and single['complete'] and single['bytes_read']==2216170035 and single['exact_input_sha256']==EXPECTED)
verify('exact original parser closure', single['instruction_records']==51847488)
verify('fixed complete epoch and canonical128B domain', m['epoch']=='whole_commandlist' and m['kernel_count']==1 and m['scope']=='TRACE_MODEL_CLOSED_WORLD' and m['address_domain']=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS')
verify('no unresolved memory agent/opcode', not m['unresolved_opcodes'])
verify('own measured body and small command binding', m['kernels'][0]['sha256']==EXPECTED and m['commandlist_sha256']=='0a0d21711ff3f3de1604fc0a243d5be2df5155147bb09bc4533bd017b62f5913')
verify('no later host update in exact initial-prefix-only commandlist', m['host_updates_excluded']==[])
for name,digest in m['artifacts'].items():
    verify('generated artifact SHA: '+name, sha(RAW/'oracle'/name)==digest)
db = sqlite3.connect('file:'+str(RAW/'oracle/oracle.sqlite3')+'?mode=ro',uri=True)
verify('SQLite integrity',db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
rows=list(db.execute('SELECT address,reads,writes,atomics FROM lines ORDER BY address'))
verify('denominator equals original completed database', len(rows)==single['unique_global_lines'])
read_lines=sum(r>0 for a,r,w,t in rows); read_refs=sum(r for a,r,w,t in rows)
verify('read denominators agree',read_lines==single['read_containing_global_lines'] and read_refs==single['global_read_lane_line_references'])
cert=[a for a,r,w,t in rows if r>0 and w==0 and t==0]
verify('every certified line excludes all stores/atomics',len(cert)==m['counts'].get('CERTIFIED_RO_lines',0))
verify('all reason line counts close',sum(n for k,n in m['counts'].items() if k.endswith('_lines'))==len(rows))
verify('all reason read reference counts close',sum(n for k,n in m['counts'].items() if k.endswith('_read_lane_references'))==read_refs)
ranges=[]
for text in (RAW/'oracle/certified_ranges.csv').read_text().splitlines()[1:]:
    a,b=map(lambda s:int(s,16),text.split(','))
    verify('range alignment/order '+str(len(ranges)),a%128==0 and b%128==0 and a<=b and (not ranges or a>ranges[-1][1]))
    ranges.append((a,b))
expanded=[f'{line:016x}' for a,b in ranges for line in range(a,b+128,128)]
verify('exact ranges equal all and only certified database rows',expanded==cert)
db.close()
verify('three new offline adapter controls passed',json.loads((RAW/'adapter_controls/CONTROL_RESULTS.json').read_text())['status']=='PASS_OFFLINE_PYTHON_ONLY')
verify('original lease released after child exit',json.loads((RAW/'LEASE_RELEASED.json').read_text())['status']=='RELEASED')
for name in ['manifest.json','coverage.csv','exclusion.csv','certified_ranges.csv']:
    dest=HERE/'oracle'/name;dest.parent.mkdir(exist_ok=True)
    dest.write_bytes((RAW/'oracle'/name).read_bytes())
for name,path in [('SINGLE_PASS_RECEIPT.json',RAW/'oracle/SINGLE_PASS_RECEIPT.json'),('ADAPTER_CONTROLS.json',RAW/'adapter_controls/CONTROL_RESULTS.json'),('RUN_RECEIPT.json',RAW/'RUN_RECEIPT.json'),('LEASE.json',RAW/'LEASE.json'),('LEASE_RELEASED.json',RAW/'LEASE_RELEASED.json')]:
    (HERE/name).write_bytes(path.read_bytes())
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import coordinator
central=coordinator.Coordinator().snapshot()
verify('no application starts charged by C certification',central['actual_starts']==50)
raw_files={str(p.relative_to(RAW)):dict(bytes=p.stat().st_size,allocated_bytes=p.stat().st_blocks*512,sha256=sha(p)) for p in RAW.rglob('*') if p.is_file()}
artifacts={name:dict(path=str((HERE/'oracle'/name).relative_to(HERE.parents[3])),sha256=sha(HERE/'oracle'/name)) for name in ['manifest.json','certified_ranges.csv','coverage.csv','exclusion.csv']}
coverage=dict(schema='C_SGEMM_POSITIVE_RO_COVERAGE_V1',batch_id='EPL2_RO_POSITIVE_QUALIFICATION_PREPARATION_20261022_r1',
              task_id='C-SGEMM-POSITIVE-RO-CERTIFICATION-r1',owner='C',
              result='POSITIVE_MODEL_CERTIFICATE_CANDIDATE' if cert else 'ZERO_CERTIFIABLE_LINES_IN_THIS_EXACT_MODEL',
              status='PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED',
              exact_input=dict(commandlist_sha256=m['commandlist_sha256'],body_sha256=EXPECTED,body_bytes=2216170035,
                               composite_trace_sha256='694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb',
                               instruction_records_measured=single['instruction_records'],
                               active_lane_instructions=1658916864,active_lane_instruction_lineage='Saved complete D/E grammar proof reused by exact newly measured body SHA; not freshly recomputed lane-instruction denominator',
                               commandlist=m['commandlist'],kernels=m['kernels'],epoch='whole_commandlist'),
              denominators=dict(unique_global_lines=len(rows),read_containing_global_lines=read_lines,
                                global_read_lane_line_references=read_refs,
                                global_write_lane_line_references=single['global_write_lane_line_references'],
                                global_atomic_lane_line_references=single['global_atomic_lane_line_references']),
              certified_RO_lines=len(cert),certified_RO_read_lane_line_references=m['counts'].get('CERTIFIED_RO_read_lane_references',0),
              fraction_of_read_containing_lines=len(cert)/read_lines if read_lines else None,
              fraction_of_read_lane_line_references=m['counts'].get('CERTIFIED_RO_read_lane_references',0)/read_refs if read_refs else None,
              coverage_and_exclusions=m['counts'],unresolved_opcodes=m['unresolved_opcodes'],host_updates_excluded=m['host_updates_excluded'],
              certified_range_count=len(ranges),range_semantics='inclusive128B line bases; width-crossing lines counted per touched line/lane reference',
              artifacts=artifacts,raw_artifacts_root=str(RAW),original_generator_source=single['source_identity'],
              combined_hash_adapter_sha256=single['adapter_sha256'],exact_published_qualification_producer=run['producer_commit'],
              source_domain_assumptions=m['assumptions'],assumption_limits='Conditional closed-world trace-model proof; no physical alias/hidden-writer/numeric/captured-source proof.',
              actual_cost=dict(wall_seconds=single['elapsed_seconds'],peak_worker_RSS_bytes=single['self_maxrss_bytes'],
                               SQLite_page_cache_bytes=16777216,worker_address_space_cap_bytes=268435456,
                               generated_raw_logical_bytes=sum(x['bytes'] for x in raw_files.values()),
                               generated_raw_allocated_bytes=sum(x['allocated_bytes'] for x in raw_files.values()),
                               body_opens=1,body_read_bytes=single['bytes_read'],separate_body_hash_passes=0,
                               current_API_output_usage=coordinator.output_usage(),actual_starts=central['actual_starts'],lease_id=run['lease_id'],lease_status='RELEASED'),
              next_owners=dict(A2='Bind exact published candidate manifest/ranges once to same-main61 schema/domain/source/native applicability; no native/build.',
                               D='Incremental candidate/control decision using actual coverage; no proof of miss/pendingTag/detach/performance from offline coverage.',
                               E2='Independent new positive-certificate qualification, exact source/main/profile/input/domain/current CLIENT_CONTRACT binding and resources; decide baseline invariance/reuse and minimal future1-or2start proposal for user approval.'),
              old_results='Old accepted empty-fallback S/F and all historical Q/results remain byte-identical. This is a new explicit candidate condition, not retroactive adoption.',
              runtime_or_native_or_numeric_qualification=False,new_simulator_native_build_starts=0,
              backup='Not needed for positive candidate; no backup body scanned or run. If ZERO retain original metadata-only Conv option without new work.')
dump('RO_COVERAGE.json',coverage)
dump('ARTIFACTS_RAW_IDENTITY.json',dict(root=str(RAW),files=raw_files,large_trace_copies=0,SQLite_not_copied_to_Git=True))
dump('VALIDATION.json',dict(status='PASS_OFFLINE_ARTIFACT_AND_MODEL_CONSISTENCY_NOT_E_QUALIFICATION',checks=checks,check_count=len(checks),trace_body_bytes_read_by_finalizer=0))
dump('RECEIPT.json',dict(schema='C_POSITIVE_RO_FINAL_RECEIPT_V1',at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        status=coverage['status'],result=coverage['result'],coverage_file='RO_COVERAGE.json',
                        exact_producer_commit=run['producer_commit'],batch=coverage['batch_id'],task=coverage['task_id'],
                        real_request_source=json.loads(Path('/workspace/ep_l2_ms20261019_c_ro_v1/RO_POSITIVE_REQUEST.json').read_text()),
                        resource_lease=run['lease_id'],lease_released=True,actual_work=coverage['actual_cost'],
                        unchanged='Original Goal/Core/production source/Tag+MSHR+descriptor capacities/RO protocol, Conv/FWT proofs, old accepted empty fallback, R35FAIL/jointUNRUN/HOLD/INCOMPLETE/withdrawals all preserved.',
                        dependent_delivery='Immediate exact-commit metadata DELIVERY to E2/D/A2 after publication; no all-lane barrier.'))
print(json.dumps(dict(result=coverage['result'],certified_lines=len(cert),read_containing_lines=read_lines,read_references=read_refs,
                      certified_read_references=coverage['certified_RO_read_lane_line_references'],ranges=len(ranges),checks=len(checks)),indent=2))

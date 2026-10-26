#!/usr/bin/env python3
"""Independent preservation gate: exact historical161 + frozen source bytes only."""
import hashlib,pathlib
from audit_common_v1 import need,canonical,AuditError
N=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1')
ROOT=N/'auto161_pipeline_20261026_v1/root'
ROOT_ACCEPTANCE_SHA='71189b911b93201e043f6a5eeb32a62b2db16d1be3beb125bf515f2fcbe84881'
BASELINE_SHA='e33e12d0757ebe896ea69f894d83609eb9edc069de3a61f67453e3511315fbde'
QUEUE=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/QUEUE.json')
STOP=QUEUE.parent/'STOP_AFTER_CURRENT'
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates')
SDK=B/'sdk42_default50k_microwindow_20261026_v1/boundary_window_controller_candidate_v3.py'
ORDINARY=B/'cpu_post_parallel_20261026_v1/capture_ordinary_parallel2_nas_candidate_v2.py'
def preservation(reader,scope_ids,baseline_path=ROOT/'PRODUCTION_PRESERVATION_BASELINE_V1.json',baseline_sha=BASELINE_SHA,queue_path=QUEUE,stop_path=STOP,sdk_path=SDK,worker_path=ORDINARY):
 raw=reader.bytes(baseline_path);need(hashlib.sha256(raw).hexdigest()==baseline_sha,'BASELINE_PIN_CHANGED')
 base=reader.obj(baseline_path);frozen=base['historical161_rows']
 need(len(frozen)==161 and len({x['id'] for x in frozen})==161,'BASELINE_NOT_EXACT161')
 need(set(scope_ids)=={x['id'] for x in frozen},'BASELINE_SCOPE_DIFFERENT')
 q=reader.obj(queue_path);selected=[x for x in q if x['id'] in scope_ids]
 need(len(selected)==161 and len({x['id'] for x in selected})==161,'HISTORICAL_DUPLICATE_OR_MISSING')
 f={x['id']:x for x in frozen};need(all(x==f[x['id']] for x in selected),'HISTORICAL161_CHANGED')
 need(hashlib.sha256(reader.bytes(sdk_path)).hexdigest()==base['current_SDK_controller_sha256'],'EXISTING_SDK_CONTROLLER_CHANGED')
 need(hashlib.sha256(reader.bytes(worker_path)).hexdigest()==base['current_ordinary_worker_sha256'],'EXISTING_ORDINARY_WORKER_CHANGED')
 stop_path=pathlib.Path(stop_path)
 stop_now=hashlib.sha256(reader.bytes(stop_path)).hexdigest() if stop_path.exists() else None
 global_now=hashlib.sha256(reader.bytes(queue_path)).hexdigest()
 return {'historical161_unchanged':True,'frozen_worker_and_SDK_controller_unchanged':True,'global_QUEUE_hash_changed_observation':global_now!=base['QUEUE_file_sha256_at_baseline'],'STOP_hash_changed_observation':stop_now!=base['STOP_sha256'],'STOP_current_sha256':stop_now,'global_queue_and_STOP_are_not_strict_gates':'Independent authorized tasks may legitimately advance; observations do not attribute a writer','scientific_registry_not_written_by_checker':True}

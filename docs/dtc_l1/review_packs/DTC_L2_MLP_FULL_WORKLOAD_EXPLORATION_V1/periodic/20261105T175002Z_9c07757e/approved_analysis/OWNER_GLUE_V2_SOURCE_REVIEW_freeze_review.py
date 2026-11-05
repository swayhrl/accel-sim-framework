"""Read-only source review capture; writes only this independent E directory."""
from pathlib import Path
import hashlib, json, datetime

A = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
M = Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/strace_bpf_engineering_canaries_v1')
OUT = A / 'agents/E/main_bpf_owner_glue_review_v2'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_bytes())
def put(name, obj):
    data = (json.dumps(obj, indent=2, sort_keys=True) + '\n').encode()
    with (OUT / name).open('xb') as f: f.write(data)
    return hashlib.sha256(data).hexdigest()

assert OUT.is_dir()
owner = M / 'owner_v2.py'
config = M / 'OWNER_CONFIG_V2.json'
assert sha(owner) == '213e8d53c15127a3355645b8135d33e0a862e6f0fa6cbc67b32a525de0363a10'
assert sha(config) == '921bb4ea646b674c368d2a7b993efb4969b0b6649dc1268b38f165633b7e920a'
cfg = read(config)
audit = [{'path': p, 'expected_sha256': h, 'actual_sha256': sha(p)} for p,h in cfg['source_pins'].items()]
assert all(x['expected_sha256'] == x['actual_sha256'] for x in audit)
containment = Path(cfg['modules']['containment'])
assert sha(containment) == 'f24fb29faff65d28237c63c908c2cb352a933e5035c9f829d64af109a6827ad7'
qa = M / 'FAILURE_CONTAINMENT_CPU_QUALIFICATION.json'
assert sha(qa) == 'a6572a19a8a8ead7fa7fd79f5cc00842c8a8d761cc460f97d8281f8960b95bd4'
assert read(qa)['count'] == 14 and read(qa)['status'] == 'PASS'
stage = A / 'coordinator/bpf_owner_failure_containment_v2/V2_STAGE_RECEIPT.json'
assert read(stage)['verified'] is True
assert read(stage)['owner_config_sha256'] == sha(config)
for row in read(stage)['files']:
    assert sha(row['archive_source']) == sha(row['native_target']) == row['sha256']
for source, name in [(owner,'owner.source.py'), (config,'OWNER_CONFIG.source.json'), (containment,'failure_containment.source.py')]:
    with (OUT / name).open('xb') as f: f.write(source.read_bytes())
put('SOURCE_PIN_AUDIT.json', {'status':'PASS', 'count':len(audit), 'pins':audit, 'tests_rerun':0})
review = {
 'status':'APPROVED_FOR_EXPLICIT_SAME_OWNER_CANARY_INSTALL',
 'owner_source_sha256':sha(owner), 'owner_config_sha256':sha(config),
 'actual_models_qualified':False,
 'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Independent source-only review of staged V2 concurrency and failure containment; no installation, authority mutation, model execution or component test rerun.',
 'prior_V1_review':{'path':str(A/'agents/E/main_bpf_owner_glue_review_v1/REVIEW.json'), 'sha256':'1e89f6f213ab76b4775ec0fef12161718c95dfcb633bf62b7b4d812127523797', 'status':'BLOCKED_DO_NOT_EXECUTE_V1'},
 'blocking_findings':[],
 'V1_blocker_resolution':[
  {'issue':'Whole consumed dictionary and remaining invariance rejected legitimate old natural completion.', 'resolution':'Budget remains exact +4; remaining is recomputed budget minus current consumed count. Every preexisting consumed UUID and field is immutable, only new execution_receipt may append. Old spent spec hashes remain fixed. Preexisting unspent science projection is conserved while resource SHA amendments are explicitly recorded.', 'source':'owner_v2.py:39-45,97-109; failure_containment.py:4-12'},
  {'issue':'Cached optional dispatch view could survive rollback and lose mandatory new routes.', 'resolution':'ever_exposed is set before reader publication. Any exposed failure installs exact4 safe/worker fail-closed guards before cleanup, retains mandatory B worker and E consumer, and installs exact4 admission filtering after priority cleanup. Non-scope calls delegate saved functions.', 'source':'owner_v2.py:90-91,126-155; failure_containment.py:14-49'},
  {'issue':'A cleanup exception could suppress later cleanup and misreport an authority-success/register-return gap as zero grants.', 'resolution':'Each restore action is independently contained; actual authority is queried for exact4, otherwise UNKNOWN with prepared transaction/no refund. ERROR records guard errors and never automatically retries or refunds.', 'source':'owner_v2.py:142-162; failure_containment.py:51-56'}
 ],
 'other_source_checks':[
  'Actual l2_ops safe dynamically resolves global worker, so both stale safe submission and direct worker entry are fenced; already-entered new worker retains mandatory B/E protection.',
  'Owner/main PID generation and original parent lease checks are retained. Same aging RLock and existing pool/claims/running/post/registry identities, primary MATRIX/SCOPE hashes, R and pending release tokens remain asserted.',
  'Initial no-unconsumed-claim preflight remains a real gate; a failed preflight is a no-install HOLD, not permission to bypass claims.',
  'Budget +4 does not reset or borrow old budget. Original consumed UUIDs/receipts and original scientific projections are preserved.',
  'All staged source pins match. Native/164 byte readback matches the new source. No requirement for Git/HTTPS was introduced.',
  'No new deadlock found in changed branch: same reentrant aging lock and established ScopeTransaction sync-lock ordering are retained.',
  'The 14 existing containment CPU cases are private fixtures; their PASS is evidence for helper logic only and is not actual-owner or simulation qualification.'
 ],
 'required_actual_install_and_canary_gates':[
  'The pending C callback runner must independently catch BaseException across source load, preflight, apply and cleanup; evidence-write errors must also be contained and the callback must return normally. The owner apply exception must never escape bare into the pending callback. Runner qualification is separate from this owner-source review.',
  'Main alone invokes this exact pinned owner/config once under its existing owner lease; preflight, authority reconciliation, official exact4 CPU2 scope append and operational records must succeed.',
  'Consumer readiness and same-owner future worker routes must be installed before optional engineering view exposure; exact4 role exclusion must retain the real primary350, old negative, R2 separation and primaryNONE policy.',
  'All original physical RAM/full forecast/CPU/IO/native fresh checks and versioned narrow priority remain mandatory; no old model is stopped or signaled.',
  'Each real canary must prove its declared CONTROL or BPF activation, natural completion, original strict AND CPU2/IO AND new observation strict, true164 archive and native restoration before accepted publication.',
  'Actual paired performance and host-impact results remain unqualified; broad primary BPF rollout is not approved by this review.',
  'Any failure after exposure is an observable engineering HOLD with exact4 fail-closed barriers retained; resume or disposition requires Main review, never automatic fallback/refund/retry.'
 ],
 'evidence':{'containment_source_sha256':sha(containment), 'private_CPU_qualification':str(qa), 'private_CPU_qualification_sha256':sha(qa), 'native_stage_readback':str(stage), 'native_stage_readback_sha256':sha(stage), 'source_pin_count':len(audit)},
 'actions':{'production_changes':0,'new_grants':0,'models_started':0,'signals':0,'Git_actions':0,'component_tests_rerun':0}
}
put('REVIEW.json', review)
members = [{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'MANIFEST.json']
manifest_sha=put('MANIFEST.json', {'schema':'DTC_E_SOURCE_ONLY_REVIEW_MANIFEST_V1','immutable':True,'files':members})
print(json.dumps({'review':str(OUT/'REVIEW.json'),'review_sha256':sha(OUT/'REVIEW.json'),'manifest_sha256':manifest_sha,'source_pin_count':len(audit)}))

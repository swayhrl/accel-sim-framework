from pathlib import Path
import hashlib,json,datetime,difflib
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
M=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/strace_bpf_engineering_canaries_v1')
O=A/'agents/E/main_bpf_owner_resume_review_v3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
 with(O/n).open('xb')as f:f.write(b)
 return hashlib.sha256(b).hexdigest()
p=M/'owner_resume_v3.py';c=M/'resume_after_memory_self_flock_v3/OWNER_RESUME_CONFIG_V3.json'
assert sha(p)=='a39a73e0d1c54500068c7dd0462a8cdacad24d7a6d141635fee07c9ae9731050'
assert sha(c)=='e27522afa59c1b4f62858c0cf9b79f269fb3aa196b3f1f7af43a939740385491'
cfg=read(c);pins=[{'path':k,'expected_sha256':v,'actual_sha256':sha(k)}for k,v in cfg['source_pins'].items()]
assert all(x['expected_sha256']==x['actual_sha256']for x in pins)
lineage=read(cfg['recovery_lineage_path'])
assert lineage['new_grants_authorized']==0 and lineage['statistical_union_authorized']is False
assert sha(lineage['old_memory_PREPARED_path'])==lineage['old_memory_PREPARED_sha256']
assert sha(cfg['modules']['scope_transaction'])==lineage['new_memory_transaction_source_sha256']=='2819ab151a119c44ecf71cc664aa6a02a0a2ba322a9e3a45a24b0324d226bed0'
for src,name in [(p,'owner_resume.source.py'),(c,'OWNER_RESUME_CONFIG.source.json')]:
 with(O/name).open('xb')as f:f.write(src.read_bytes())
with(O/'OWNER_V2_TO_RESUME_V3.diff').open('x')as f:f.write(''.join(difflib.unified_diff((M/'owner_v2.py').read_text().splitlines(True),p.read_text().splitlines(True),fromfile='owner_v2.py',tofile='owner_resume_v3.py')))
put('SOURCE_PIN_AUDIT.json',{'status':'PASS','pins':pins,'count':len(pins),'tests_rerun':0})
review={
 'status':'APPROVED_FOR_EXPLICIT_SAME_OWNER_CANARY_INSTALL',
 'owner_source_sha256':sha(p),'owner_config_sha256':sha(c),'actual_models_qualified':False,
 'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Read-only delta review against owner213e8; no component tests repeated, no production execution.',
 'blocking_findings':[],
 'delta_findings':[
  'Distinct RESUME_V3 marker requires previous install HOLD, ever_exposed=False, exactly4 prior registered and zero consumed; preexisting B/E routes must be absent.',
  'Registration uses only store.reconcile(); it may revalidate or complete its existing immutable COMMITTED receipt, but does not call prepare/register or issue another authority grant.',
  'Budget after equals budget before, remaining remains budget minus consumed count, new_grants=0, previously_registered_engineering_grants=4. Existing UUID/spec/science preservation checks remain.',
  'New ScopeTransaction source2819 uses current-locked-q/direct-file validation inside update_authority; the source/real-private-flock delta was separately reviewed. New PREPARED directory links old2068 via immutable recovery lineage and leaves original transaction/error/source intact.',
  'Reader exposure ordering, exposed-failure safe/worker exact4 fences, retained mandatory B/E, independent cleanup, final admission guard and actual authority observation remain unchanged from213e8.',
  'No CPU/resource relaxation is introduced. Busy CPU can legitimately defer actual dispatch; no grant implies permission to bypass physical admission.',
  'Recovery lineage explicitly preserves incident11 negatives and prohibits statistical union. This resume does not register recovery11 trials or change primary350.',
  'Config prior_owner_glue_never_executed is inherited wording; actual prior213 invocation/failure is explicitly acknowledged by mandatory runtime HOLD marker and recovery lineage. Approval does not claim213 was never executed.'
 ],
 'required_execution_gates':[
  'Main alone invokes this exact source/config using the independently contained pending callback that catches all source-load/apply/cleanup exceptions and returns normally; do not nakedly propagate Python failure through pending C callback.',
  'Fresh runtime checks must confirm existing four grants, no consumption/INTENT/claims and old CPU2 row/ACTIVE/context before new forward scope transaction. No repeat original+4 registration, refund or UUID reuse.',
  'Retain original full physical RAM/CPU/IO/native admission and same-owner model/consumer routing. All engineering trials remain excluded from primary/GM/V3 parents.',
  'Actual activation, natural completion, full original strict AND generation-specific strict, true164 archive/native restoration and paired host/performance evidence remain required before canary acceptance or any later rollout.'
 ],
 'references':{
  'prior_owner_source_sha256':'213e8d53c15127a3355645b8135d33e0a862e6f0fa6cbc67b32a525de0363a10',
  'lock_contract_review':str(A/'agents/E/incident11_recovery_contract_review_v1/REVIEW.json'),
  'lock_contract_review_sha256':'39369d436cc96ccc8b6c3029679bfb681a853754d4c25b7bfc31830e27664959',
  'recovery_lineage_path':cfg['recovery_lineage_path'],'recovery_lineage_sha256':sha(cfg['recovery_lineage_path']),
  'old_PREPARED_path':lineage['old_memory_PREPARED_path'],'old_PREPARED_sha256':lineage['old_memory_PREPARED_sha256'],'source_pin_count':len(pins)
 },
 'actions':{'production_changes':0,'new_grants':0,'models_started':0,'signals':0,'Git_actions':0,'tests_rerun':0}
}
h=put('REVIEW.json',review)
mh=put('MANIFEST.json',{'schema':'DTC_E_SOURCE_ONLY_REVIEW_MANIFEST_V1','files':[{'path':x.name,'sha256':sha(x)}for x in sorted(O.iterdir())if x.is_file()and x.name!='MANIFEST.json']})
print(json.dumps({'review':str(O/'REVIEW.json'),'review_sha256':h,'manifest_sha256':mh,'source_pins':len(pins)}))

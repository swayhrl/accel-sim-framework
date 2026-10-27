"""Coordinator deployment preflight; executes only after all explicit evidence pins exist."""
import pathlib,json,hashlib,importlib.util,datetime,os,subprocess
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=R/'control/operational_amendments/padding_only_v1';REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';OVERLAY='DTC_L2_MLP_PADDING_ONLY_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def exclusive(p,d):
 with P(p).open('x')as h:json.dump(d,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
def main():
 # Main creates this immutable request only after final source qualification and
 # GitHub API readback; this script by itself cannot manufacture authorization.
 request_path=A/'coordinator/PADDING_INSTALL_REQUEST_V1.json';request=read(request_path);assert request['status']=='MAIN_APPROVED_QUALIFIED_PUBLISHED_PILOT' and request['request']==REQ
 assert not(D/'ACTIVE_FRONTEND.json').exists()and not(D/'REGISTERED.json').exists()
 e=load('padding_install_original_native',R/'tools/l2_native.py');reg,epoch,q,plan=e.registered();lease=read(e.T/'control/BATCH_LEASE.json');assert epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE';assert lease['pid']==plan['parent_pid']==1498278
 # External coordinator stages metadata only. Real model operations still use
 # the untouched native ancestor check inside the actual owner descendants.
 owner=P('/proc')/str(lease['pid']);fields=(owner/'stat').read_text().rsplit(')',1)[1].split();assert int(fields[19])==lease['start_ticks']==plan['parent_start_ticks']and fields[0]!='Z';assert REQ in lease['additional_requests'];assert sha(plan['parent_controller_path'])==lease['controller_sha256']==plan['parent_controller_sha256'];assert os.readlink(owner/'fd'/str(lease['fd']))==str(e.N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')and 'FLOCK'in(owner/'fdinfo'/str(lease['fd'])).read_text()
 assert OVERLAY not in q.get('additional_operational_overlays',{});assert request['overlay_id']==OVERLAY
 for row in plan['source_pins']:assert sha(row['path'])==row['sha256']
 pilot=request['allowed_cohorts'];assert len(pilot)==1;cohort=pilot[0];assert cohort in q['admitted_specs']and cohort not in q['consumed'] and not(R/'control/qualification_ledger'/(cohort+'.INTENT.json')).exists()
 D.mkdir(parents=True,exist_ok=True);cfg=dict(status='ACTIVE_FUTURE_ONLY',request=REQ,overlay_id=OVERLAY,allowed_cohorts=pilot)
 for key in ['source','frontend','extra_strict','owner','history_validator','policy','certificate','QA','readback']:
  source=request[key+'_path'];assert sha(source)==request[key+'_sha256'];dest=D/P(source).name;assert not dest.exists();dest.write_bytes(P(source).read_bytes());assert sha(dest)==request[key+'_sha256'];cfg[key+'_path']=str(dest);cfg[key+'_sha256']=request[key+'_sha256']
 qa=read(cfg['QA_path']);assert qa['status']=='PASS';pub=read(cfg['readback_path']);assert pub['verified']is True and pub['commit']==request['publication_commit']
 qualified={k:cfg[k+'_sha256']for k in ['source','frontend','extra_strict','owner','history_validator']}
 assert qa['qualified_sources']==pub['qualified_sources']==qualified
 assert qa['policy_sha256']==pub['policy_sha256']==cfg['policy_sha256']and qa['certificate_sha256']==pub['certificate_sha256']==cfg['certificate_sha256']
 policy=read(cfg['policy_path']);assert policy['A_only']is True and policy['candidate_full_original']is True and policy['base_resource_source_sha256']==sha(R/'tools/l2_resources.py')
 # Support modules are pinned with the same published manifest, never inferred
 # from a mutable source directory or imported from another agent's draft.
 for row in request.get('support_files',[]):
  assert sha(row['path'])==row['sha256'];dest=D/P(row['path']).name;assert not dest.exists();dest.write_bytes(P(row['path']).read_bytes());assert sha(dest)==row['sha256']
 record={key:cfg[key]for key in ['request','overlay_id','allowed_cohorts',*[x+'_sha256'for x in ['source','frontend','extra_strict','owner','history_validator','policy','certificate','QA','readback']]]};record.update(status='ACTIVE',publication_commit=request['publication_commit'],changes_scientific_identity=False,changes_existing_supervisor=False,no_model_pause=True,stage='SINGLE_EXISTING_REGISTERED_POINT_ENGINEERING_ROLLOUT',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
 def amend(current):
  rq=current['registered_future_requests'][REQ];assert cohort not in rq['consumed']and cohort in rq['admitted_specs'];before=(rq['budget'],rq['remaining'],dict(rq['consumed']),dict(rq['admitted_specs']));assert OVERLAY not in rq.get('additional_operational_overlays',{});rq.setdefault('additional_operational_overlays',{})[OVERLAY]=record;assert before==(rq['budget'],rq['remaining'],dict(rq['consumed']),dict(rq['admitted_specs']))
 e.update_authority(amend);exclusive(D/'ACTIVE_FRONTEND.json',cfg);exclusive(D/'REGISTERED.json',dict(request=REQ,cohort=cohort,record=record,config_sha256=sha(D/'ACTIVE_FRONTEND.json'),model_starts_by_registration=0,no_old_requests_changed=True,no_budget_grants=True))
 print(json.dumps(dict(status='REGISTERED_AND_CONFIGURED_NOT_ATTACHED',cohort=cohort,deploy_directory=str(D),owner_attachment_still_required=True,router_activation_still_required=True,model_starts=0)))
if __name__=='__main__':main()

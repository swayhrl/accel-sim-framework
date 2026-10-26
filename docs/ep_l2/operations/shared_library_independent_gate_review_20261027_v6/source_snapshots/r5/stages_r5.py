"""Exact R5 five-stage adapter. Reuses frozen V3 builders, validators and R5 payload gates."""
from pathlib import Path
import os,sys,json,time,fcntl,types,hashlib
ORDER=['prepare','publish','restore','cross','finish']
MIB=2**20
def need(x,m):
 if not x:raise RuntimeError('R5_PHASE_HOLD_'+m)
def read(r,p):return json.loads(r.bounded_metadata_raw(p))
def ref(r,p):
 b=r.bounded_metadata_raw(p);return dict(path=str(p),sha256=r.digest(b),bytes=len(b))
def scope_from(r,pair,kind):
 bm=r.load_verified('bounded_resources_r5')
 return bm.Scope(r.profile(),pair['policy_ref'],pair['approval_ref'],r.code_manifest()['code_version_id'],kind)
class Control:
 def __init__(self,scope,root):self.scope=scope;self.control_root=Path(root);self.counters=scope.counters;self.samples=scope.samples;self.deadline=float('inf')
 def check(self,force=False):
  need(time.monotonic()<self.deadline,'FINITE_STAGE_DEADLINE')
  if force:self.scope.observe(True)
  return self.scope.check_block(16*MIB+65536)
 def account(self,n,direction):
  self.check(False);return self.scope.account(n,direction)
def control_resources(r,spec,specsha):
 p=r.profile();path=Path(p['native_work_root'])/'authority'/('R5_PHASE_'+spec['integration_id']+'.json');bm=r.load_verified('bounded_resources_r5')
 bm.no_links(path);a=read(r,path)
 if p['execution_scope']=='PRODUCTION':
  st=path.lstat();need(st.st_uid==0 and st.st_mode&0o022==0,'ROOT_PHASE_GRANT_PERMISSIONS')
 need(a['status']=='ROOT_APPROVED_R5_EXACT_PHASE_CONTROL'and a['spec_sha256']==specsha and a['code_version_id']==spec['code_version_id'],'ROOT_PHASE_GRANT')
 need(a['native_control_ceiling_bytes']==65536 and a['payload_writes_authorized']is False and a['science_authorized']is False,'EXACT_NATIVE_CONTROL64K_ONLY')
 root=r.library_root()/'receipts/v3_ledgers'/spec['integration_id']
 need(Path(spec['r5_nas_work_root'])==r.library_root()/'receipts/v3_ledgers','EXACT_NAS_REPORT_LEDGER_ROOT')
 return Control(scope_from(r,spec['r5_metadata_resource'],'READ_ONLY_ZERO_NATIVE'),root)
def admission(r,spec,specsha):
 res=control_resources(r,spec,specsha);res.check(True);st=r.load_verified('stages');pr=r.load_verified('public_provider_r5')
 if r.profile()['execution_scope']=='PRODUCTION':pr.post_commit_source2_guard(r,spec)
 st.closed_archives(r,spec,res)
 objects,_=st.ref_read(spec['base_all_objects_ref'],res);bundles,_=st.ref_read(spec['base_all_bundles_ref'],res)
 st.exact_frozen_scope(spec,objects,bundles,res)
 return res
def write(r,p,value):return r.load_verified('bounded_resources_r5').immutable_json(p,value)
def validate_public(r,spec,prepared):
 lib=r.library_root();target=Path(prepared['publication']['path'])
 need((lib/'catalog/CURRENT').is_symlink()and(lib/'catalog/CURRENT').resolve()==target.resolve(),'CURRENT_PREPARED_PUBLICATION')
 need((lib/'tools/trace-assets').is_symlink()and(lib/'tools/trace-assets').resolve()==(r.PACKAGE/'trace-assets-r5').resolve(),'PUBLIC_R5_WRAPPER_NOT_LEGACY')
 args=types.SimpleNamespace();doc=r.load_verified('public_provider_r5').selected_readonly_defaults(r,args)
 need(doc['policy_ref']==spec['r5_metadata_resource']['policy_ref']and doc['approval_ref']==spec['r5_metadata_resource']['approval_ref'],'ROOT_READONLY_SELECTOR_REFS')
 q=scope_from(r,spec['r5_metadata_resource'],'READ_ONLY_ZERO_NATIVE')
 need(q.policy['catalog_pins']==prepared['pins'],'SELECTOR_PREPARED_PINS')
 return True
def publish_prepared(r,spec,prepared,res):
 lib=r.library_root();st=r.load_verified('stages');writer=r.load_verified('storage').Writer(lib,res,r.load_verified('primitive'))
 p=prepared['publication'];envelope,_=st.ref_read(p,res)
 need(envelope['code_version_id']==spec['code_version_id']and envelope['semantic_spec_sha256']==r.digest(r.canon(spec))and envelope['pins']==prepared['pins'],'PREPARED_EXACT_SPEC_CODE')
 # Validate Root selector before either public pointer changes.
 args=types.SimpleNamespace();doc=r.load_verified('public_provider_r5').selected_readonly_defaults(r,args)
 need(doc['policy_ref']==spec['r5_metadata_resource']['policy_ref']and doc['approval_ref']==spec['r5_metadata_resource']['approval_ref'],'ROOT_READONLY_SELECTOR_REFS')
 need(scope_from(r,spec['r5_metadata_resource'],'READ_ONLY_ZERO_NATIVE').policy['catalog_pins']==prepared['pins'],'PREPARED_SCOPE_PINS')
 issues,_=st.ref_read(spec['issues_ref'],res);coverage,_=st.ref_read(spec['coverage_ref'],res)
 writer.json('quarantine/INPUT_ISSUES_V3.json',issues);writer.json('catalog/SUITE_COVERAGE_V3.json',coverage)
 writer.pointer('catalog/CURRENT',p['path'],spec['expected_previous_current_sha256'])
 writer.pointer('tools/trace-assets',r.PACKAGE/'trace-assets-r5',spec['expected_previous_command_sha256'])
 st.activate_aliases(spec,r.profile(),r.load_verified('primitive'));validate_public(r,spec,prepared)
 return dict(status='PASS_R5_EXACT_PREPARED_PUBLICATION_AND_WRAPPER',pins=prepared['pins'],publication=p,code_version_id=spec['code_version_id'])
def cross(r,spec,specpath,specsha,res):
 v=r.load_verified('verification_stages');st=r.load_verified('stages');work=res.control_root
 with r.Operation(resources=res)as op:
  c,envelope=r.load_public_catalog(op);scope=v._scope(r,c,envelope,spec,r.profile())
 pins=r.gate_pins(c);cwds=spec['project_cwds'];need(len(set(cwds))==len(cwds)==3,'THREE_EXACT_CWDS')
 small=scope_from(r,spec['r5_small_resource'],'EXACT_SMALL_BUNDLE32');samples=small.policy['small_materializations']
 need(len(samples)==3 and{q['cwd']for q in samples}==set(cwds),'EXACT_THREE_SMALL_CASES')
 command=r.library_root()/'tools/trace-assets';need(command.resolve()==(r.PACKAGE/'trace-assets-r5').resolve(),'TYPED_PUBLIC_COMMAND')
 writer=r.load_verified('storage').Writer(r.library_root(),res,r.load_verified('primitive'))
 attempts=work/'cross_attempts';attempts.mkdir(parents=True,exist_ok=True);attempt=attempts/('callset_'+str(time.time_ns()));attempt.mkdir();calls=[];reports=[];materialized=[]
 def invoke(args,cwd):
  rec=v._run_cli(command,args,cwd,attempt/str(len(calls)),res,1800)
  need(rec['returncode']==0,'TYPED_CROSS_CLI_FAILED')
  value=rec['value'];ev=v._cli_evidence(rec,writer,'receipts/v3_cli/'+spec['integration_id']);calls.append(ev);return value,ev
 flags=['--resource-policy',small.policy_ref['path'],'--policy-sha256',small.policy_ref['sha256'],'--root-approval',small.approval_ref['path'],'--approval-sha256',small.approval_ref['sha256'],'--integration-spec',str(specpath),'--spec-sha256',specsha]
 for sample in samples:
  cwd=sample['cwd'];listed,le=invoke(['list'],cwd);need(len(listed['assets'])==scope['assets']and{a['bundle_id']for a in listed['assets']}=={a['bundle_id']for a in c['assets']},'LIST_ALL_EXACT')
  verified,ve=invoke(['verify','--all'],cwd);dest=Path(sample['destination']);asset=next(a for a in c['assets']if a['bundle_id']==sample['bundle_id'])
  proofpath=work/('SMALL_'+r.digest(str(dest).encode())+'.json')
  if proofpath.exists():
   whole=read(r,proofpath);reused=True
  else:
   need(not dest.exists(),'UNCOMMITTED_SMALL_DEST_REQUIRES_REVIEW')
   whole,we=invoke(['materialize-small',sample['bundle_id'],'--destination',str(dest),*flags],cwd);write(r,proofpath,whole);reused=False
  reports.append(dict(cwd=cwd,verify=verified,list_evidence=le,verify_evidence=ve,reused_exact_prior_small_materialization=reused))
  materialized.append((asset,dest,whole))
 with r.Operation(resources=res)as op:
  current,ev=r.load_public_catalog(op);need(r.gate_pins(current)==pins,'CROSS_EPOCH')
  result=r.validate_cross_reports(current,reports,cwds);cmd=v._verify_public_views(r,current,res)
  native=[v._verify_materialized(r,op,current,a,d,w,res)for a,d,w in materialized]
 result.update(integration_id=spec['integration_id'],code_version_id=spec['code_version_id'],scope=scope,commandlist_full_SHA_proofs=cmd,whole_small_native_materializations=native,public_cli_extra_evidence=calls,Source_payload_writes_or_deletions=0)
 reference=write(r,work/'CROSS_PROJECT_V3.json',result)
 return dict(status=result['status'],pins=pins,report_ref=reference,scope=scope,scientific_qualification_granted=False)
def revalidate(r,spec,result,stage,res,prepared):
 st=r.load_verified('stages');work=res.control_root
 if stage=='prepare':
  env,_=st.ref_read(result['publication'],res);need(env['code_version_id']==spec['code_version_id']and env['pins']==result['pins']and env['semantic_spec_sha256']==r.digest(r.canon(spec))and result['status']=='PASS_R5_PREPARED_CATALOG_NO_ACTIVATION','PREPARE_REOPEN')
 elif stage=='publish':
  need(result['status']=='PASS_R5_EXACT_PREPARED_PUBLICATION_AND_WRAPPER'and result['pins']==prepared['pins']and result['publication']==prepared['publication'],'PUBLISH_RECEIPT_SCOPE');validate_public(r,spec,prepared)
 elif stage=='restore':
  with r.Operation(resources=res)as op:
   c,e=r.load_public_catalog(op);now=r.finish_receipt(op,c,work/'NATIVE_ALL_OBJECTS_V3.jsonl');need(now==read(r,work/'NATIVE_ALL_OBJECTS_V3.json')and result['pins']==now['pins']and Path(result['ledger_path'])==work/'NATIVE_ALL_OBJECTS_V3.jsonl'and result['native_report_ref']==ref(r,work/'NATIVE_ALL_OBJECTS_V3.json')and result['status']=='PASS_EXACT_R5_BOUNDED_ALL_OBJECTS','RESTORE_REOPEN_LEDGER')
 elif stage=='cross':
  with r.Operation(resources=res)as op:
   c,e=r.load_public_catalog(op);x,_=st.ref_read(result['report_ref'],res);r.validate_cross_reports(c,x['reports'],spec['project_cwds']);need(result['status']==x['status']and result['pins']==x['pins'],'CROSS_RECEIPT_SCOPE')
   for q in x['whole_small_native_materializations']:
    a=next(a for a in c['assets']if a['bundle_id']==q['bundle_id']);proof=read(r,work/('SMALL_'+r.digest(q['destination'].encode())+'.json'))
    r.load_verified('verification_stages')._verify_materialized(r,op,c,a,q['destination'],proof,res)
 else:
  current=r.load_verified('verification_stages').finish(r,spec,r.profile(),res);need(current==result,'FINISH_REOPEN')
def run(r,spec,specpath,specsha,requested,crash_after=None):
 need(requested in ORDER+['resume'],'STAGE');need(crash_after is None or r.profile()['execution_scope']=='QUALIFICATION','NO_PRODUCTION_FAULT_INJECTION')
 res=admission(r,spec,specsha);work=res.control_root;work.mkdir(parents=True,exist_ok=True)
 lock=(work/'R5_FIVE_PHASE.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 native_supervisor=None;old_owner=None
 try:
  # Preserve both old public-suite and legacy data-Goal ownership boundaries.
  # These are exact tiny Native control files under the separate64KiB Root grant.
  native_supervisor=(Path(r.profile()['native_work_root'])/'DATA_GOAL_SUPERVISOR.lock').open('a+b');fcntl.flock(native_supervisor,fcntl.LOCK_EX|fcntl.LOCK_NB)
  goal_control=Path(spec['legacy_goal_root'])/'control'
  if r.profile()['execution_scope']=='QUALIFICATION':goal_control.mkdir(parents=True,exist_ok=True)
  need(goal_control.is_dir(),'LEGACY_DATA_GOAL_CONTROL_REQUIRED')
  old_owner=(goal_control/'SUPERVISOR.lock').open('a+b');fcntl.flock(old_owner,fcntl.LOCK_EX|fcntl.LOCK_NB)

  prepared=None;outputs=[]
  for stage in ORDER:
   receiptpath=work/(stage+'.PHASE_RECEIPT.json');marker=work/(stage+'.MARKER.json')
   needed=requested=='resume'or stage==requested
   if not needed and not receiptpath.exists():need(ORDER.index(stage)>=ORDER.index(requested),'PREDECESSOR_REQUIRED')
   if not needed and not receiptpath.exists():continue
   seconds=spec['stage_deadlines_seconds'].get(stage,spec['stage_deadlines_seconds'].get('publish',1800));need(type(seconds)is int and 0<seconds<=7*86400,'FINITE_STAGE_BUDGET');res.deadline=time.monotonic()+seconds
   if receiptpath.exists():
    record=read(r,receiptpath);need(record.get('schema')=='SM70_EXACT_TYPED_PHASE_RECEIPT_R5'and record['stage']==stage and record['spec_sha256']==specsha and record['code_version_id']==spec['code_version_id']and record['source_KEEP']is True and record['scientific_qualification_granted']is False,'PHASE_CONTEXT')
    result=record['result'];revalidate(r,spec,result,stage,res,prepared)
   else:
    need(needed,'PREDECESSOR_RECEIPT')
    if stage=='prepare':result=r.load_verified('stages').publish(r,spec,r.profile(),res,activate=False)
    elif stage=='publish':result=publish_prepared(r,spec,prepared,res)
    elif stage=='restore':
     q=scope_from(r,spec['r5_restore_resource'],'EXACT_SINGLE_SLOT_READBACK');x=r.load_verified('public_provider_r5').bounded_restore_stage(r,q,spec)
     summary=x['result'];write(r,work/'NATIVE_ALL_OBJECTS_V3.json',summary);result=dict(status=x['status'],pins=summary['pins'],native_report_ref=ref(r,work/'NATIVE_ALL_OBJECTS_V3.json'),ledger_path=x['ledger_path'],counts=x['counts'])
    elif stage=='cross':result=cross(r,spec,specpath,specsha,res)
    else:result=r.load_verified('verification_stages').finish(r,spec,r.profile(),res)
    record=dict(schema='SM70_EXACT_TYPED_PHASE_RECEIPT_R5',stage=stage,spec_sha256=specsha,code_version_id=spec['code_version_id'],result=result,source_KEEP=True,scientific_qualification_granted=False)
    write(r,receiptpath,record)
    if crash_after==stage:
     need(r.profile()['execution_scope']=='QUALIFICATION','NO_PRODUCTION_FAULT_INJECTION');os._exit(86)
   if stage=='prepare':prepared=result
   else:validate_public(r,spec,prepared)
   marker_value=dict(schema='SM70_EXACT_TYPED_PHASE_MARKER_R5',stage=stage,receipt_ref=ref(r,receiptpath),code_version_id=spec['code_version_id'],spec_sha256=specsha)
   write(r,marker,marker_value);outputs.append(stage)
   if stage==requested:break
  return dict(status='PASS_EXACT_R5_REQUESTED_PHASES',stages=outputs,code_version_id=spec['code_version_id'],integration_id=spec['integration_id'],work=str(work),scientific_starts=0,source_KEEP=True,overall_goal_complete_claimed=False)
 finally:
  if old_owner is not None:fcntl.flock(old_owner,fcntl.LOCK_UN);old_owner.close()
  if native_supervisor is not None:fcntl.flock(native_supervisor,fcntl.LOCK_UN);native_supervisor.close()
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
def main(argv=None):
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=ORDER+['resume'],required=True);p.add_argument('--integration-spec',required=True);p.add_argument('--spec-sha256',required=True);p.add_argument('--qualification-crash-after',choices=ORDER)
 a=p.parse_args(argv)
 # phase_r5 verified the complete new package before entering this module.
 specmod=__import__('importlib.util',fromlist=['util']);path=Path(__file__).with_name('stages.py');sp=specmod.spec_from_file_location('exact_r5_spec_loader',path);m=specmod.module_from_spec(sp);sp.loader.exec_module(m)
 r,spec,profile=m.spec_load(a.integration_spec,a.spec_sha256)
 print(json.dumps(run(r,spec,a.integration_spec,a.spec_sha256,a.stage,a.qualification_crash_after),indent=2))

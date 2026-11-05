"""Pure report-only typed safety HOLD validation; no owner/resource actions."""
from pathlib import Path
import ast,hashlib,json
import archive_witness as aw
require=aw.require;sha=aw.sha
read=lambda p:json.loads(Path(p).read_bytes())
D=Path(__file__).resolve().parent
INTERFACE=read(D/'ADMISSION_HOLD_INTERFACE.json')
def shared_validator(resource_path,root,ctx):
 resource_path=Path(resource_path);h=sha(resource_path);require(any(Path(x['path'])==resource_path and x['sha256']==h for x in ctx['source_pins']),'HOLD_RESOURCE_NOT_REGISTERED_SOURCE_PIN');tree=ast.parse(resource_path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='admission_hold');require(hashlib.sha256(ast.dump(fn,include_attributes=False).encode()).hexdigest()==INTERFACE['admission_hold_AST_sha256'],'UNREVIEWED_SHARED_ADMISSION_HOLD_INTERFACE')
 literals={}
 for n in tree.body:
  if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['REQ','VARIANT_TOKENS','AUTHORITY_COMMIT']:literals[n.targets[0].id]=ast.literal_eval(n.value)
 require(literals['REQ']==ctx['request']and literals['AUTHORITY_COMMIT']=='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe','HOLD_SHARED_SCOPE');env=dict(REQ=literals['REQ'],VARIANT_TOKENS=literals['VARIANT_TOKENS'],sha=sha);exec(compile(ast.Module(body=[fn],type_ignores=[]),str(resource_path),'exec'),env);return env['admission_hold'],{'path':str(resource_path),'sha256':h,'admission_hold_AST_sha256':INTERFACE['admission_hold_AST_sha256']}
def validate_unstarted(row,spec,candidates,ctx,root=None):
 root=Path(root or ctx['root']);q=ctx['q'];cohort=row['cohort'];profile=row['variant'];holds=q.get('admission_holds',{});require(isinstance(holds,dict),'MALFORMED_ADMISSION_HOLD_CONTAINER')
 if cohort in q['consumed']:return None
 if profile not in holds and cohort not in holds:return None
 helper,hp=shared_validator(root/'tools/perf16r1_resources.py',root,ctx);v=helper(q,spec)
 if v is None:return None
 # Root's owner validates this immutable eight-cohort decision before q append.
 require(v['request']==ctx['request']and v['profile']==profile and v['classification']=='CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD'and v['decided_by']=='DTC_MAIN','ROOT_TYPED_SAFETY_HOLD_IDENTITY');require(isinstance(v['reason'],str)and v['reason']and isinstance(v['created_utc'],str)and v['created_utc'],'ROOT_HOLD_REASON_TIME');require(v.get('cycles')is None and v.get('uuid')is None,'UNUSED_HOLD_HAS_PERFORMANCE')
 dp=Path(v['decision_path']);base=root/'control/PROFILE_HOLD_DECISIONS';require(not dp.is_symlink()and dp.parent.resolve()==base.resolve()and dp.suffix=='.json','ROOT_HOLD_DECISION_NAMESPACE');require(sha(dp)==v['decision_sha256'],'ROOT_HOLD_DECISION_SHA');decision=read(dp);require(decision['schema']=='DTC_PERFV2_CODESIGN16_LAYOUT_R1_PROFILE_HOLD_DECISION_V1'and decision['request']==ctx['request']and decision['authority_commit']=='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe','ROOT_HOLD_DECISION_SCOPE');expected={c['proposed_native_cohort']for c in candidates if c['profile']==profile};scope=decision['approval_scope'];require(len(expected)==8 and len(scope['candidate_cohorts'])==8 and set(scope['candidate_cohorts'])==expected and scope['request']==ctx['request']and scope['profile']==profile,'ROOT_HOLD_APPROVAL_EXACT8')
 for k in ['profile','request','classification','reason','evidence_path','evidence_sha256','decided_by','created_utc']:require(decision[k]==v[k],'ROOT_HOLD_IMMUTABLE_VALUE:'+k)
 ep=Path(v['evidence_path']);require(sha(ep)==v['evidence_sha256'],'ROOT_HOLD_EVIDENCE_SHA');op=root/'tools/perf16r1_ops.py';require(sha(op)==v['source_ops_sha256']and any(Path(x['path'])==op and x['sha256']==v['source_ops_sha256']for x in ctx['source_pins']),'ROOT_HOLD_OPS_ACTUAL_SOURCE_PIN')
 sp=root/'control/specs'/(cohort+'.json');require(sha(sp)==q['admitted_specs'][cohort]==sha(root/'control'/(cohort+'_SPEC.json')),'UNUSED_HOLD_CANONICAL_SPEC_SHA')
 for k,z in [('cohort',cohort),('profile',profile),('structure_variant',profile),('request',ctx['request']),('input_digest',row['input_digest']),('cell','DH'),('downstream_profile','P0'),('host_cpu',None)]:require(spec.get(k)==z,'UNUSED_HOLD_SPEC_IDENTITY:'+k)
 for p in [root/'analysis'/(cohort+'.RESULT.json'),root/'control/qualification_ledger'/(cohort+'.INTENT.json'),root/'control/qualification_ledger'/(cohort+'.DONE.json')]:require(not p.exists(),'UNUSED_HOLD_HAS_ACTUAL_IDENTITY')
 return {'classification':'UNUSED_SAFETY_HOLD','decision':{'path':str(dp),'sha256':v['decision_sha256']},'evidence':{'path':str(ep),'sha256':v['evidence_sha256']},'canonical_spec':{'path':str(sp),'sha256':sha(sp)},'shared_resource':hp,'source_ops':{'path':str(op),'sha256':v['source_ops_sha256']},'matched_registry_key':v['matched_key'],'record':v,'no_model_uuid_or_cycles':True}

def accounting(rows,ctx,root=None):
 root=Path(root or ctx['root']);held={r['cohort']for r in rows if r['status']=='UNUSED_SAFETY_HOLD'};actual={r['cohort']for r in rows if r['status']in ['ACCEPTED_STRICT_ARCHIVE_RESTORE','ARCHIVED_NEGATIVE_NO_PERFORMANCE']};allco={r['cohort']for r in rows};q=ctx.get('q');issues=[];accounted=actual|held==allco;verified=False;terminal=None
 if q is not None:
  container=q.get('admission_holds',{})
  if not isinstance(container,dict):issues.append('MALFORMED_ADMISSION_HOLD_CONTAINER')
  else:
   known={r['variant']for r in rows}|allco
   if set(container)-known:issues.append('OUT_OF_SCOPE_ADMISSION_HOLD_KEYS')
 if accounted and ctx.get('source_qualified')and q is not None:
  try:
   require(actual==set(q['consumed'])and held==allco-set(q['consumed'])and q['remaining']==16-len(q['consumed']),'ACCOUNTED_GRANT_COUNTS')
   if held:
    meta=q['terminal_unused_safety_HOLD'];require(q['state']=='STOP_UNACCEPTED_WITH_UNUSED_CREDITS','UNUSED_TERMINAL_STATE');require(set(meta['cohorts'])==held and len(meta['cohorts'])==len(held)and meta['remaining_credits_preserved']==q['remaining'],'UNUSED_TERMINAL_COHORTS_CREDITS');require(meta['no_budget_refund']is True and meta['no_spec_removal']is True and meta['no_model_retries']is True,'UNUSED_TERMINAL_NO_REFUND_REMOVAL_RETRY')
    tp=root/'analysis/EXECUTION_TERMINAL.json';t=read(tp);require(t['status']=='ALL_ACTUAL_MODELS_TERMINAL_WITH_UNUSED_SAFETY_HOLD'and t['budget']==16 and t['new_prepare_disabled']is True and t['remaining_credits_preserved']==q['remaining'],'UNUSED_EXECUTION_TERMINAL');require(set(t['states'])==allco and set(t['unused_safety_HOLD'])==held,'UNUSED_EXECUTION_TERMINAL_MEMBERSHIP')
    for r in rows:require(t['states'][r['cohort']]==('UNUSED_SAFETY_HOLD'if r['cohort']in held else 'PASS_PERFV2_CODESIGN16_LAYOUT_R1_DH_STRICT_ARCHIVE_NATIVE_RESTORE'if r['accepted']else 'FAIL_PERFV2_CODESIGN16_LAYOUT_R1_DH_ARCHIVED_NO_RETRY'),'UNUSED_EXECUTION_TERMINAL_RESULT_STATE')
    terminal={'registry_terminal_unused':meta,'execution_terminal':{'path':str(tp),'sha256':sha(tp)}}
   verified=not issues
  except Exception as e:issues.append(repr(e))
 return {'all16_candidates_accounted':accounted,'all16_candidates_accounted_verified':verified,'all16_actual_scientific_closed':len(actual)==16,'actual_closed_n':len(actual),'unused_safety_HOLD_n':len(held),'unused_credit_accounting_never_means_scientific_success':True,'issues':issues,'terminal_proof':terminal}

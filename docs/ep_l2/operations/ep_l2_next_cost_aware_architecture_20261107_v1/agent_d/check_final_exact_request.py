"""Metadata-only finite request checker; no model or registration side effects."""
import json,hashlib,copy
from pathlib import Path
from identity_contracts import canonical,valid_source,need
O=Path(__file__).resolve().parent
FLAG='-gpgpu_ep_l2_victim_extension'
def check_request(r):
 valid_source(r['Source5'])
 need(r['status']=='PENDING_USER_SCOPE_APPROVAL_NOT_HOST_NATIVE_ACTIVATED','request/activation distinction')
 need(r['new_scientific_authorization']is False and r['granted_total_new_starts']==r['registered_starts']==r['consumed_starts']==0,'scope cannot self-authorize')
 need(r['proposed_total_new_starts']==5 and len(r['points'])==5,'finite exact5')
 expected={'GEMM':{0,1,2},'Stencil':{0,2}};seen={}
 for p in r['points']:
  program=p['program'];need(program in expected,'unrequested input family');mode=p['victim_extension'];need(type(mode)is int and mode in expected[program],'unrequested mode')
  need((program,mode)not in seen,'duplicate point');seen[program,mode]=p
  need(p['Source5']==r['Source5'],'different ELF/Core/Source5')
  need(p['independent_release']is True and p['other_point_completion_prerequisites']==[],'unapproved serial gate')
  need(p['budget_requested_new_complete_application_starts']==1 and p['granted_starts']==p['registered_starts']==p['consumed_starts']==0,'per-point budget')
  inp=p['input_identity'];m=p['full_effective_option_map']
  need(len(m)==p['full_config_option_count']==283 and canonical(m)==p['full_config_canonical_sha256'],'complete pinned283')
  need(m[FLAG]==str(mode),'flag/point mismatch')
  base=json.loads((O/'config_templates'/(program.upper()+'_WV_SOURCE78_EXPECTED282.json')).read_text())
  need({k:v for k,v in m.items()if k!=FLAG}==base,'unapproved old282 delta')
  frozen=json.loads((O/'EXACT_INPUT_AND_FULLCONFIG_TEMPLATES.json').read_text())['inputs'][program]
  need(inp==frozen,'input/ordered commands/kernel/observer population mismatch')
  need(inp['ordered_commands_canonical_sha256']==canonical(inp['ordered_commands']),'command SHA')
  need(p['mode']=='WV_ZERO_RO'and p['geometry']==dict(sets=32,ways=8,line_bytes=128,slices=64),'wrong resources/mode')
  z=p['resources'];need(z['hard_wall_seconds']==(86400 if program=='GEMM'else 172800),'candidate immutable hard wall')
  need(z['bound_logical_CPUs']==1 and z['hard_native_result_bytes']==67108864,'resource limit')
  need(z['restore_count']==2 and z['restore_concurrency']=='GLOBAL_SERIAL_ONE_WINDOW_TWO_DISTINCT_TARGETS_SEQUENTIALLY','restore accounting')
  need(z['new_trace_or_input_copy_bytes']==0,'unapproved new assets')
 need(set(seen)=={(p,m)for p,ms in expected.items()for m in ms},'exact independent control set')
 need(r['C']['status']=='NOT_REQUESTABLE'and r['C']['proposed_new_starts']==0,'C cannot become a scientific request')
 return {'status':'PRECISE_FIVE_POINT_METADATA_PASS_NOT_AUTHORIZATION','new_starts':0}
def main():
 r=json.loads((O/'FINAL_EXACT_EXPERIMENT_REQUEST.json').read_text());rows=[]
 def test(n,fn,reject=False):
  try:fn()
  except Exception as e:
   if not reject:raise
   rows.append(dict(name=n,status='PASS_REJECT',reason=str(e)));return
  if reject:raise AssertionError('accepted negative '+n)
  rows.append(dict(name=n,status='PASS'))
 test('actual_final_request_and5fullmaps',lambda:check_request(r))
 def mutated(n,mut):
  q=copy.deepcopy(r);mut(q);test(n,lambda:check_request(q),True)
 mutated('reject_cross_ELF',lambda q:q['points'][0]['Source5'].__setitem__('binary_sha256','0'*64))
 mutated('reject_different_input',lambda q:q['points'][0]['input_identity'].__setitem__('input_identity_sha256','0'*64))
 mutated('reject_command_order',lambda q:q['points'][0]['input_identity']['ordered_commands'].reverse())
 mutated('reject_kernel_identity',lambda q:q['points'][0]['input_identity']['ordered_kernel_identity'][0].__setitem__('sha256','0'*64))
 mutated('reject_parent_wall_override',lambda q:q['points'][0]['resources'].__setitem__('hard_wall_seconds',43200))
 mutated('reject_baseline_completion_gate',lambda q:q['points'][1].__setitem__('other_point_completion_prerequisites',['GEMM_WV_EXT0']))
 mutated('reject_silent_C_start',lambda q:q['C'].__setitem__('proposed_new_starts',1))
 mutated('reject_self_authorization',lambda q:q.__setitem__('new_scientific_authorization',True))
 mutated('reject_restore_two_concurrent_windows',lambda q:q['points'][0]['resources'].__setitem__('restore_concurrency','TWO_PARALLEL'))
 mutated('reject_unrequested_trace_copy',lambda q:q['points'][0]['resources'].__setitem__('new_trace_or_input_copy_bytes',1))
 mutated('reject_extra_point',lambda q:q['points'].append(copy.deepcopy(q['points'][0])))
 mutated('reject_wrong_flag',lambda q:q['points'][0]['full_effective_option_map'].__setitem__(FLAG,'2'))
 # Hash-correct malicious observer change must still fail the frozen full282 contract.
 def observer(q):
  p=q['points'][0];p['full_effective_option_map']['-gpgpu_ep_l2_ms_observer']='0';p['full_config_canonical_sha256']=canonical(p['full_effective_option_map'])
 mutated('reject_hash_correct_observer_delta',observer)
 def clock(q):
  p=q['points'][0];p['full_effective_option_map']['-gpgpu_clock_domains']='1132.0:1132.0:1132.0:1700.0';p['full_config_canonical_sha256']=canonical(p['full_effective_option_map'])
 mutated('reject_hash_correct_clock_delta',clock)
 out=dict(status='PASS_FINITE_NEW_REQUEST_IDENTITY_COUNTEREXAMPLES',count=len(rows),tests=rows,actual_application_models_started=0,old_loader_Host_NI_tests_repeated=False)
 (O/'FINAL_REQUEST_METADATA_CHECKS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':out['status'],'count':len(rows)}))
if __name__=='__main__':main()

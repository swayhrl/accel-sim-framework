import copy,hashlib,json,time,traceback
from pathlib import Path
import family_contract as f
P=Path(__file__).resolve().parent
index=json.loads((P/'CANDIDATE_INDEX.json').read_text())
CS=[json.loads(Path(r['path']).read_text()) for r in index['candidates']]
checks=[]
def check(name,action,reject=False,contains=None):
 try:
  out=action();ok=not reject;detail=out.get('status') if isinstance(out,dict) else 'returned'
 except f.FamilyContractError as e:
  detail=str(e);ok=reject and (contains is None or contains in detail)
 except Exception as e:
  detail=type(e).__name__+':'+str(e);ok=False
 checks.append(dict(name=name,pass_check=ok,detail=detail))
def val(c):return f.validate_candidate(c,engineering_enabled=True)
def mutate(i,fn):
 c=copy.deepcopy(CS[i]);fn(c);return c
for i,c in enumerate(CS):check('positive_exact_cell_'+c['performance_first_family_contract_id'],lambda c=c:val(c))
for start in [0,2,4]:check('positive_fair_pair_'+str(start),lambda start=start:f.validate_pair(CS[start:start+2],engineering_enabled=True))
check('positive_complete_packet',lambda:f.validate_packet(CS,engineering_enabled=True))
check('default_gate_OFF',lambda:f.validate_candidate(CS[0]),True,'default OFF')
check('truthy_gate_not_True',lambda:f.validate_candidate(CS[0],engineering_enabled=1),True,'default OFF')
check('unknown_cell_reject',lambda:val(mutate(0,lambda c:c.update(performance_first_family_contract_id='OTHER'))),True)
check('cohort_alias_reject',lambda:val(mutate(0,lambda c:c.update(cohort='UNREGISTERED_ALIAS'))),True)
check('wrong_input_reject',lambda:val(mutate(0,lambda c:c.update(input_identity_sha256='0'*64))),True)
check('wrong_mode_reject',lambda:val(mutate(0,lambda c:c.update(mode='F'))),True)
check('wrong_profile_reject',lambda:val(mutate(0,lambda c:c.update(profile='REF32x8_L100'))),True)
check('changed_reference_reject',lambda:val(mutate(0,lambda c:c['performance_first_reference_spec'].update(sha256='0'*64))),True)
check('Source92_reject',lambda:val(mutate(0,lambda c:c['source_identity'].update(core_source_commit='9'*40))),True)
check('new_ELF_reject',lambda:val(mutate(0,lambda c:c['source_identity'].update(binary_sha256='0'*64))),True)
check('binary_path_reject',lambda:val(mutate(0,lambda c:c.update(binary_path='/tmp/other.out'))),True)
for label,key,value in [('clock1700','-gpgpu_clock_domains','1132.0:1132.0:1132.0:1700.0'),('coreclock','-gpgpu_clock_domains','2264.0:1132.0:1132.0:1020.0'),('icntclock','-gpgpu_clock_domains','1132.0:2264.0:1132.0:1020.0'),('L2clock','-gpgpu_clock_domains','1132.0:1132.0:2264.0:1020.0'),('L60','-dram_latency','60'),('MissQ256','-gpgpu_cache:dl2','S:32:128:8,L:B:m:L:P,A:128:1,256:0,32'),('P2','-gpgpu_ep_l2_bank_ops','2'),('D1024','-gpgpu_ep_l2_descriptor_pool_size','1024'),('observer_option','-gpgpu_ep_l2_ms_observer','0'),('trace','-trace','/tmp/other.trace')]:
 check('reject_'+label,lambda key=key,value=value:val(mutate(0,lambda c:c['expected_effective_options'].__setitem__(key,value))),True)
check('extra_option_reject',lambda:val(mutate(0,lambda c:c['expected_effective_options'].update({'-bogus':'1'}))),True)
check('integer_option_reject',lambda:val(mutate(0,lambda c:c['expected_effective_options'].update({'-dram_latency':100}))),True)
check('geometry_reject',lambda:val(mutate(0,lambda c:c['geometry'].update(ways=4))),True)
check('heavy_observer_reject',lambda:val(mutate(0,lambda c:c['observer_env'].update(EPL2_DETACH_DIAG='1'))),True)
check('typed_M_reject',lambda:val(mutate(0,lambda c:c.update(M=0))),True)
check('scientific_permission_reject',lambda:val(mutate(0,lambda c:c.update(science_launch_permission=True))),True)
check('VectorF_certificate_missing',lambda:val(mutate(5,lambda c:c.update(ro_qualification_ref=None))),True)
check('VectorF_certificate_mismatch',lambda:val(mutate(5,lambda c:c['ro_qualification_ref'].update(sha256='0'*64))),True)
check('VectorF_certificate_option_mismatch',lambda:val(mutate(5,lambda c:c['expected_effective_options'].update({'-gpgpu_ep_l2_ro_scope':'NONE'}))),True)
check('FWT_no_RO_inheritance',lambda:val(mutate(1,lambda c:c.update(ro_qualification_ref=copy.deepcopy(CS[5]['ro_qualification_ref'])))),True)
check('pair_cross_input_reject',lambda:f.validate_pair([CS[0],CS[3]],engineering_enabled=True),True)
check('pair_missing_S_reject',lambda:f.validate_pair([CS[1],CS[1]],engineering_enabled=True),True)
check('pair_one_REF_clock_reject',lambda:f.validate_pair([CS[0],mutate(1,lambda c:c['expected_effective_options'].update({'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:850.0'}))],engineering_enabled=True),True)
check('packet_incomplete_reject',lambda:f.validate_packet(CS[:5],engineering_enabled=True),True)
check('packet_duplicate_cell_reject',lambda:f.validate_packet(CS[:5]+[CS[0]],engineering_enabled=True),True)
check('packet_extra_cell_reject',lambda:f.validate_packet(CS+[CS[0]],engineering_enabled=True),True)
check('source_keep_reject',lambda:val(mutate(0,lambda c:c.update(source_keep=False))),True)
check('missing_reference_failclosed',lambda:f.load_exact({'path':str(P/'does_not_exist.json'),'sha256':'0'*64}),True)
check('candidate_no_mutation',lambda: {'status':'PASS'} if CS==[json.loads(Path(r['path']).read_text()) for r in index['candidates']] else (_ for _ in ()).throw(f.FamilyContractError('mutated')))
refs=[]
for name in ['family_contract.py','test_family_contract.py','CANDIDATE_INDEX.json']:
 p=P/name;refs.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
receipt=dict(schema='EP_PF_HOST_FAMILY_ENGINEERING_CPU_CONTROLS_V1',status='PASS_PURE_HOST_CONTRACT_ENGINEERING_NOT_COMPLETE_HOST_NATIVE_QUALIFICATION'if all(c['pass_check'] for c in checks) else 'FAIL',checks=checks,passed=sum(c['pass_check'] for c in checks),total=len(checks),refs=refs,science_launch_permission=False,real_registry_writes=0,native_route_changes=0,model_starts=0,accepted_Source_or_ELF_changes=0,trace_body_reads=0)
(P/'HOST_FAMILY_ENGINEERING_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status=receipt['status'],passed=receipt['passed'],total=receipt['total'],failures=[c for c in checks if not c['pass_check']])))
assert all(c['pass_check'] for c in checks)
